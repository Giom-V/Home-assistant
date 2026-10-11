# custom_components/mon_eau/api.py
"""Clients des sources : Hub'eau, orobnat (ARS), VigiEau, Vigicrues, geo.api.gouv.fr."""
from __future__ import annotations

import html as html_mod
import logging
import math
import re
from typing import Any

import aiohttp

from .const import (
    BAIGNADE_CLASSEMENTS,
    URL_BAIGNADES_COMMUNES,
    URL_BAIGNADES_SITE,
    URL_BAIGNADES_SITES,
    URL_DIS_RESULTATS,
    URL_DIS_UDI,
    URL_GEO_COMMUNES,
    URL_HYDRO_OBS_ELAB,
    URL_HYDRO_OBS_TR,
    URL_HYDRO_STATIONS,
    URL_NAPPES_CHRONIQUES,
    URL_NAPPES_CHRONIQUES_TR,
    URL_NAPPES_STATIONS,
    URL_ONDE_OBSERVATIONS,
    URL_OROBNAT_MENU,
    URL_OROBNAT_RECHERCHE,
    URL_QUALITE_ANALYSES,
    URL_QUALITE_STATIONS,
    URL_TEMP_CHRONIQUE,
    URL_TEMP_STATIONS,
    URL_VIGICRUES_GEOJSON,
    URL_VIGICRUES_PREVISION,
    URL_VIGIEAU_ZONES,
)

_LOGGER = logging.getLogger(__name__)

TIMEOUT = aiohttp.ClientTimeout(total=30)
TIMEOUT_LONG = aiohttp.ClientTimeout(total=60)  # geojson Vigicrues (~2 Mo)


class MonEauApiError(Exception):
    """Erreur réseau ou réponse invalide d'une source de données."""


async def fetch_json(
    session: aiohttp.ClientSession,
    url: str,
    params: dict[str, Any] | None = None,
    timeout: aiohttp.ClientTimeout = TIMEOUT,
) -> Any:
    """GET JSON avec gestion d'erreur uniforme et un retry sur erreur réseau."""
    derniere: Exception | None = None
    for tentative in range(2):
        try:
            async with session.get(url, params=params, timeout=timeout) as resp:
                if resp.status >= 400:
                    corps = (await resp.text())[:200]
                    raise MonEauApiError(f"HTTP {resp.status} sur {resp.url} — {corps}")
                return await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            derniere = err
            if tentative == 0:
                _LOGGER.debug("Nouvel essai après erreur réseau sur %s: %r", url, err)
    raise MonEauApiError(f"Erreur réseau ({url}): {derniere!r}") from derniere


def to_float(text: Any) -> float | None:
    """Convertit '13', '13,0', '<0,5' → float (0.0 pour '<x' : sous seuil de détection)."""
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    cleaned = str(text).strip().replace(" ", " ")
    if cleaned.startswith("<"):
        return 0.0
    cleaned = cleaned.replace(",", ".").split(" ")[0]
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_limite(text: str | None) -> float | None:
    """Extrait la valeur numérique d'une limite réglementaire type '<=50 mg/L'."""
    if not text:
        return None
    match = re.search(r"[\d.,]+", text)
    return to_float(match.group(0)) if match else None


_PETITS_MOTS = {"de", "du", "des", "la", "le", "les", "sur", "sous", "en", "et", "au", "aux", "d", "l"}
_ACRONYMES = {"cu", "ca", "cc", "gbm", "sie", "siaep", "sivom", "sivu", "smaep", "sedif", "uge"}


def joli_libelle(texte: str | None) -> str | None:
    """« DOUBS A BESANCON » → « Doubs à Besançon ». Ne touche pas aux textes déjà propres."""
    if not texte:
        return texte
    lettres = [c for c in texte if c.isalpha()]
    if not lettres or sum(1 for c in lettres if c.isupper()) / len(lettres) < 0.8:
        return texte
    morceaux = []
    premier = True
    for morceau in re.split(r"([\s\-'’()\[\]]+)", texte.strip()):
        if not morceau or not morceau[0].isalpha():
            morceaux.append(morceau)
            continue
        bas = morceau.lower()
        if bas == "a" and not premier:
            morceaux.append("à")
        elif bas in _PETITS_MOTS and not premier:
            morceaux.append(bas)
        elif bas in _ACRONYMES or (
            len(morceau) <= 3 and not any(v in bas for v in "aeiouyàéè")
        ):
            morceaux.append(morceau.upper())  # acronyme (GBM, CU, SIAEP...)
        else:
            morceaux.append(morceau[0].upper() + bas[1:])
        premier = False
    return "".join(morceaux)


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance haversine en km."""
    rad = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * rad / 2) ** 2
        + math.cos(lat1 * rad) * math.cos(lat2 * rad) * math.sin((lon2 - lon1) * rad / 2) ** 2
    )
    return 2 * 6371 * math.asin(math.sqrt(a))


# ======================================================================
# geo.api.gouv.fr
# ======================================================================

async def geo_search_communes(session: aiohttp.ClientSession, recherche: str) -> list[dict]:
    """Recherche par nom, ou par code postal + code INSEE si l'entrée est numérique
    (5 chiffres ambigus : 25000 est un code postal, 25056 un code INSEE)."""
    base = {
        "fields": "code,nom,codeDepartement,codeRegion,centre,codesPostaux",
        "boost": "population",
        "limit": "15",
    }
    recherche = recherche.strip()
    if recherche.isdigit():
        requetes = [{**base, "codePostal": recherche}, {**base, "code": recherche}]
    else:
        requetes = [{**base, "nom": recherche}]

    communes: dict[str, dict] = {}
    for params in requetes:
        try:
            data = await fetch_json(session, URL_GEO_COMMUNES, params)
        except MonEauApiError:
            if params is requetes[-1] and not communes:
                raise
            continue
        for c in data or []:
            centre = (c.get("centre") or {}).get("coordinates") or [None, None]
            code = c.get("code")
            if code and centre[1] is not None and code not in communes:
                communes[code] = {
                    "code": code,
                    "nom": c.get("nom"),
                    "departement": c.get("codeDepartement"),
                    "region": c.get("codeRegion"),
                    "lon": centre[0],
                    "lat": centre[1],
                    "code_postal": (c.get("codesPostaux") or [""])[0],
                }
    return list(communes.values())


# ======================================================================
# Hub'eau — eau potable
# ======================================================================

async def dis_derniers_resultats(
    session: aiohttp.ClientSession, code_commune: str, reseau_code: str | None
) -> list[dict]:
    """Résultats DIS récents : les 500 dernières lignes du réseau (ou de la commune).

    Deux pièges Hub'eau (vérifiés le 2026-10-07 sur Besançon) :
    - une campagne massive sur UN réseau (385 analyses PFAS sur Arcier le
      29/07) remplit à elle seule les 500 dernières lignes de la commune : un
      autre réseau n'y figure plus et le filtre local renvoyait vide → « Aucun
      résultat » → l'entrée restait en échec de démarrage. Le réseau est donc
      demandé à l'API (`code_reseau`), le filtre local ne reste qu'en garde-fou ;
    - `sort=desc` ne trie PAS par date de prélèvement (février avant juin) :
      on retrie ici, `rows[0]` doit être le dernier prélèvement.
    """
    params = {
        "code_commune": code_commune,
        "size": "500",
        "sort": "desc",
        "fields": ",".join(
            [
                "code_prelevement",
                "code_parametre",
                "libelle_parametre",
                "resultat_numerique",
                "resultat_alphanumerique",
                "libelle_unite",
                "limite_qualite_parametre",
                "date_prelevement",
                "conclusion_conformite_prelevement",
                "conformite_limites_bact_prelevement",
                "conformite_limites_pc_prelevement",
                "conformite_references_bact_prelevement",
                "conformite_references_pc_prelevement",
                "nom_distributeur",
                "reseaux",
            ]
        ),
    }
    if reseau_code:
        params["code_reseau"] = reseau_code
    data = await fetch_json(session, URL_DIS_RESULTATS, params)
    rows = data.get("data") or []
    if reseau_code:
        filtres = [
            r
            for r in rows
            if any(res.get("code") == reseau_code for res in (r.get("reseaux") or []))
        ]
        if filtres:  # champ `reseaux` absent ou vide : on fait confiance au filtre API
            rows = filtres
    rows.sort(key=lambda r: r.get("date_prelevement") or "", reverse=True)
    return rows


async def dis_liste_reseaux(
    session: aiohttp.ClientSession, code_commune: str
) -> list[dict]:
    """Réseaux (UDI) de la commune, avec leur quartier, via l'endpoint dédié."""
    data = await fetch_json(
        session, URL_DIS_UDI, {"code_commune": code_commune, "size": "200"}
    )
    rows = data.get("data") or []
    annees = [r.get("annee") for r in rows if r.get("annee")]
    derniere_annee = max(annees) if annees else None
    reseaux: dict[str, dict] = {}
    for row in rows:
        code = row.get("code_reseau")
        if not code or (derniere_annee and row.get("annee") != derniere_annee):
            continue
        if code not in reseaux:
            reseaux[code] = {
                "code": code,
                "nom": joli_libelle(row.get("nom_reseau")) or code,
                "quartier": joli_libelle(row.get("nom_quartier")),
            }
    return sorted(reseaux.values(), key=lambda r: r["nom"])


# ======================================================================
# orobnat.sante.gouv.fr (ARS) — scraping défensif
# ======================================================================

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(raw: str) -> str:
    return html_mod.unescape(re.sub(r"\s+", " ", _TAG_RE.sub(" ", raw)))


async def orobnat_dernier_bulletin(
    session: aiohttp.ClientSession,
    region: str,
    departement: str,
    code_commune: str,
    reseau_code: str,
) -> dict | None:
    """Dernier bulletin ARS d'un réseau. None si échec (repli Hub'eau).

    Code réseau orobnat = code Hub'eau + '_' + département sur 3 chiffres.
    """
    dept3 = departement.zfill(3)
    reseau_orobnat = f"{reseau_code}_{dept3}"
    try:
        async with session.get(
            URL_OROBNAT_MENU,
            params={"methode": "menu", "usd": "AEP", "idRegion": region},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status >= 400:
                return None
            await resp.read()

        base = {"idRegion": region, "usd": "AEP", "departement": dept3}
        for payload in (
            {**base, "methode": "changerDepartement"},
            {**base, "methode": "changerCommune", "communeDepartement": code_commune},
        ):
            async with session.post(URL_OROBNAT_RECHERCHE, data=payload, timeout=TIMEOUT) as resp:
                if resp.status >= 400:
                    return None
                await resp.read()

        async with session.post(
            URL_OROBNAT_RECHERCHE,
            data={
                **base,
                "methode": "rechercher",
                "communeDepartement": code_commune,
                "reseau": reseau_orobnat,
                "posPLV": "0",
            },
            timeout=TIMEOUT,
        ) as resp:
            if resp.status >= 400:
                return None
            raw = (await resp.read()).decode("cp1252", errors="replace")
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.debug("orobnat injoignable: %s", err)
        return None

    return _orobnat_parse(raw)


def _orobnat_parse(raw: str) -> dict | None:
    """Date, conclusion et paramètres clés du bulletin HTML. None si non reconnu."""
    text = _strip_tags(raw)

    m_date = re.search(r"Date du prélèvement\s+(\d{2}/\d{2}/\d{4})(?:\s+(\d{1,2})h(\d{2}))?", text)
    if not m_date:
        return None
    jour, mois, annee = m_date.group(1).split("/")
    heure = m_date.group(2) or "12"
    minute = m_date.group(3) or "00"
    date_iso = f"{annee}-{mois}-{jour}T{int(heure):02d}:{minute}:00"

    m_conc = re.search(
        r"Conclusions sanitaires\s+(.{10,600}?)(?:\s+Paramètre|\s+Conformité|\s+Date du|$)", text
    )
    conclusion = m_conc.group(1).strip() if m_conc else None

    # Seules les LIMITES de qualité rendent l'eau non conforme (pas les références),
    # même logique que les codes C/N de Hub'eau. Le bulletin a des champs explicites.
    def oui_non(motif: str) -> bool | None:
        m = re.search(motif + r"\s*:?\s*(oui|non)", text, re.I)
        return None if m is None else m.group(1).lower() == "oui"

    bact = oui_non(r"Conformité bactériologique")
    pc = oui_non(r"Conformité physico-chimique")
    references = oui_non(r"Respect des références de qualité")
    conforme: bool | None = None
    if bact is not None or pc is not None:
        conforme = bact is not False and pc is not False
    elif conclusion:
        lowered = conclusion.lower()
        if "non conforme" in lowered or "non-conforme" in lowered:
            conforme = False
        elif "conforme" in lowered:
            conforme = True

    parametres: dict[str, dict] = {}
    labels = {
        "nitrates": r"Nitrates(?!\s*/)",  # exclut la ligne ratio « Nitrates/50 + Nitrites/3 »
        "e_coli": r"Escherichia coli",
        "enterocoques": r"Ent[ée]rocoques",
        "pesticides": r"(?:Total|Somme) des pesticides",
    }
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S | re.I):
        cells = [_strip_tags(c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)]
        if len(cells) < 2:
            continue
        libelle, valeur = cells[0], cells[1]
        for key, pattern in labels.items():
            if key not in parametres and re.match(pattern, libelle, re.I):
                num = to_float(valeur)
                if num is not None:
                    parametres[key] = {"valeur": num, "texte": valeur, "date": date_iso}

    return {
        "date_prelevement": date_iso,
        "conclusion": conclusion,
        "conforme": conforme,
        "conformite_bacteriologie": bact,
        "conformite_physico_chimie": pc,
        "respect_references": references,
        "parametres": parametres,
    }


# ======================================================================
# Hub'eau — hydrométrie + Vigicrues
# ======================================================================

async def hydro_dernieres_observations(
    session: aiohttp.ClientSession, code_entite: str
) -> dict:
    """Dernières observations H (m) et Q (m³/s) de la station."""
    params = {
        "code_entite": code_entite,
        "size": "20",
        "sort": "desc",
        "fields": "grandeur_hydro,resultat_obs,date_obs",
    }
    data = await fetch_json(session, URL_HYDRO_OBS_TR, params)
    result: dict[str, Any] = {"hauteur": None, "debit": None, "date_hauteur": None, "date_debit": None}
    for obs in data.get("data") or []:
        grandeur = obs.get("grandeur_hydro")
        valeur = obs.get("resultat_obs")
        if valeur is None:
            continue
        if grandeur == "H" and result["hauteur"] is None:
            result["hauteur"] = round(valeur / 1000, 3)  # mm → m
            result["date_hauteur"] = obs.get("date_obs")
        elif grandeur == "Q" and result["debit"] is None:
            result["debit"] = round(valeur / 1000, 3)  # L/s → m³/s
            result["date_debit"] = obs.get("date_obs")
        if result["hauteur"] is not None and result["debit"] is not None:
            break
    return result


async def hydro_liste_stations(
    session: aiohttp.ClientSession, departement: str
) -> list[dict]:
    """Stations hydrométriques en service du département."""
    params = {
        "code_departement": departement,
        "size": "300",
        "fields": "code_station,libelle_station,longitude_station,latitude_station,en_service",
    }
    data = await fetch_json(session, URL_HYDRO_STATIONS, params)
    return [
        {
            "code": s["code_station"],
            "libelle": joli_libelle(s.get("libelle_station")) or s["code_station"],
            "lat": s.get("latitude_station"),
            "lon": s.get("longitude_station"),
        }
        for s in data.get("data") or []
        if s.get("code_station") and s.get("en_service") in (True, None)
    ]


async def hydro_debits_journaliers(
    session: aiohttp.ClientSession, code_entite: str, date_min: str
) -> list[tuple[str, float]]:
    """Débits moyens journaliers QmnJ [(date, m³/s), ...] depuis date_min."""
    params = {
        "code_entite": code_entite,
        "grandeur_hydro_elab": "QmnJ",
        "date_debut_obs_elab": date_min,
        "size": "20000",
        "fields": "date_obs_elab,resultat_obs_elab",
    }
    data = await fetch_json(session, URL_HYDRO_OBS_ELAB, params, timeout=TIMEOUT_LONG)
    return [
        (row["date_obs_elab"], row["resultat_obs_elab"] / 1000)
        for row in data.get("data") or []
        if row.get("date_obs_elab") and row.get("resultat_obs_elab") is not None
    ]


async def hydro_hauteurs_periode(
    session: aiohttp.ClientSession, code_entite: str, date_min: str
) -> list[tuple[str, float]]:
    """Hauteurs temps réel [(date ISO, m), ...] triées croissantes depuis date_min."""
    params = {
        "code_entite": code_entite,
        "grandeur_hydro": "H",
        "date_debut_obs": date_min,
        "size": "20000",
        "fields": "date_obs,resultat_obs",
    }
    data = await fetch_json(session, URL_HYDRO_OBS_TR, params, timeout=TIMEOUT_LONG)
    points = [
        (row["date_obs"], row["resultat_obs"] / 1000)
        for row in data.get("data") or []
        if row.get("date_obs") and row.get("resultat_obs") is not None
    ]
    return sorted(points)


def stats_normales(
    debits: list[tuple[str, float]], jour_annee: int, fenetre_jours: int
) -> dict | None:
    """Percentiles saisonniers : QmnJ des jours de l'année à ± fenetre_jours (toutes années)."""
    valeurs = []
    for date, valeur in debits:
        try:
            mois, jour = int(date[5:7]), int(date[8:10])
        except (ValueError, IndexError):
            continue
        ja = (mois - 1) * 30.44 + jour  # approximation suffisante pour une fenêtre de ±15 j
        ecart = abs(ja - jour_annee)
        if min(ecart, 365 - ecart) <= fenetre_jours:
            valeurs.append(valeur)
    if len(valeurs) < 30:
        return None
    valeurs.sort()

    def pct(q: float) -> float:
        idx = q * (len(valeurs) - 1)
        bas = int(idx)
        haut = min(bas + 1, len(valeurs) - 1)
        return round(valeurs[bas] + (valeurs[haut] - valeurs[bas]) * (idx - bas), 3)

    return {
        "normale": pct(0.5),
        "p10": pct(0.10),
        "p25": pct(0.25),
        "p75": pct(0.75),
        "p90": pct(0.90),
        "echantillon": len(valeurs),
    }


def situation_hydrologique(debit: float, stats: dict) -> str:
    if debit < stats["p10"]:
        return "tres_bas"
    if debit < stats["p25"]:
        return "bas"
    if debit <= stats["p75"]:
        return "normal"
    if debit <= stats["p90"]:
        return "haut"
    return "tres_haut"


def _parse_iso(date: str):
    from datetime import datetime, timezone

    try:
        parsed = datetime.fromisoformat(date.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def calcul_tendances(
    points: list[tuple[str, float]], horizons_jours: dict[str, int]
) -> dict[str, dict] | None:
    """Variation sur chaque horizon : delta, direction (monte/descend/stable) et
    vitesse (rapide/lente) relative à l'amplitude observée sur la période."""
    from datetime import timedelta

    dates = [(_parse_iso(d), v) for d, v in points]
    dates = [(d, v) for d, v in dates if d is not None]
    if len(dates) < 2:
        return None
    valeurs = [v for _, v in dates]
    amplitude = max(valeurs) - min(valeurs)
    date_fin, valeur_fin = dates[-1]
    tendances: dict[str, dict] = {}
    for cle, jours in horizons_jours.items():
        cible = date_fin - timedelta(days=jours)
        depart = min(dates, key=lambda p: abs((p[0] - cible).total_seconds()))
        if abs((depart[0] - cible).total_seconds()) > jours * 43200:  # > 50 % de l'horizon
            continue
        delta = round(valeur_fin - depart[1], 3)
        seuil_stable = max(0.01, amplitude * 0.03)
        if abs(delta) < seuil_stable:
            direction, vitesse = "stable", None
        else:
            direction = "monte" if delta > 0 else "descend"
            vitesse = "rapide" if amplitude and abs(delta) >= amplitude * 0.25 else "lente"
        tendances[cle] = {"delta_m": delta, "direction": direction, "vitesse": vitesse}
    return tendances or None


async def vigicrues_niveaux(session: aiohttp.ClientSession) -> dict[str, dict]:
    """Carte de vigilance : {code_tronçon: {niveau, libelle, geometry}}. ~2 Mo, à throttler."""
    data = await fetch_json(session, URL_VIGICRUES_GEOJSON, timeout=TIMEOUT_LONG)
    troncons: dict[str, dict] = {}
    for feat in data.get("features") or []:
        props = feat.get("properties") or {}
        code = props.get("CdEntCru")
        if not code:
            continue
        troncons[code] = {
            "niveau": props.get("NivInfViCr"),
            "libelle": props.get("lbentcru") or code,
            "geometry": feat.get("geometry") or {},
        }
    return troncons


def vigicrues_troncon_le_plus_proche(
    troncons: dict[str, dict], lat: float, lon: float
) -> tuple[str, str] | None:
    """(code, libellé) du tronçon dont la géométrie passe au plus près du point."""
    best: tuple[float, str, str] | None = None
    for code, info in troncons.items():
        geom = info.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if geom.get("type") == "LineString":
            coords = [coords]
        for line in coords:
            for point in line[::3]:  # 1 point sur 3 suffit pour trouver le plus proche
                try:
                    d = distance_km(lat, lon, point[1], point[0])
                except (TypeError, IndexError):
                    continue
                if best is None or d < best[0]:
                    best = (d, code, info["libelle"])
    if best is None or best[0] > 30:
        return None
    return best[1], best[2]


async def vigicrues_prevision(
    session: aiohttp.ClientSession, code_station: str
) -> list[list] | None:
    """Prévisions [[iso, valeur_m], ...] — liste vide hors épisode de crue."""
    try:
        data = await fetch_json(
            session,
            URL_VIGICRUES_PREVISION,
            {"CdEntVigiCru": code_station, "TypEntVigiCru": "7", "FormatDate": "iso"},
        )
    except MonEauApiError:
        return None
    simul = data.get("Simul") or {}
    points = []
    for prev in simul.get("Prevs") or []:
        date = prev.get("DtPrev")
        valeur = prev.get("ResMoyPrev") or prev.get("ResPrev")
        if date and valeur is not None:
            points.append([date, round(float(valeur) / 1000, 3) if valeur > 100 else float(valeur)])
    return points


# ======================================================================
# Hub'eau — température continue
# ======================================================================

async def temp_liste_stations(session: aiohttp.ClientSession, departement: str) -> list[dict]:
    params = {
        "code_departement": departement,
        "size": "100",
        "fields": "code_station,libelle_station,longitude,latitude",
    }
    data = await fetch_json(session, URL_TEMP_STATIONS, params)
    return [
        {
            "code": s["code_station"],
            "libelle": joli_libelle(s.get("libelle_station")) or s["code_station"],
            "lat": s.get("latitude"),
            "lon": s.get("longitude"),
        }
        for s in data.get("data") or []
        if s.get("code_station")
    ]


async def temp_derniere_mesure(session: aiohttp.ClientSession, code_station: str) -> dict | None:
    params = {
        "code_station": code_station,
        "size": "1",
        "sort": "desc",
        "fields": "date_mesure_temp,heure_mesure_temp,resultat",
    }
    data = await fetch_json(session, URL_TEMP_CHRONIQUE, params)
    rows = data.get("data") or []
    if not rows:
        return None
    row = rows[0]
    date = row.get("date_mesure_temp")
    heure = row.get("heure_mesure_temp") or "12:00:00"
    return {
        "valeur": row.get("resultat"),
        "date": f"{date}T{heure}" if date else None,
    }


# ======================================================================
# Hub'eau — qualité des cours d'eau
# ======================================================================

async def qualite_stations_proches(
    session: aiohttp.ClientSession, lat: float, lon: float, distance: int = 30
) -> list[dict]:
    params = {
        "latitude": str(lat),
        "longitude": str(lon),
        "distance": str(distance),
        "size": "200",
        "fields": "code_station,libelle_station,latitude,longitude",
    }
    data = await fetch_json(session, URL_QUALITE_STATIONS, params)
    return [
        {
            "code": s["code_station"],
            "libelle": joli_libelle(s.get("libelle_station")) or s["code_station"],
            "lat": s.get("latitude"),
            "lon": s.get("longitude"),
        }
        for s in data.get("data") or []
        if s.get("code_station")
    ]


async def qualite_analyses_recentes(
    session: aiohttp.ClientSession,
    lat: float,
    lon: float,
    date_min: str,
    distance: int = 30,
) -> list[dict]:
    """Analyses température récentes autour d'un point (repère les stations vivantes)."""
    params = {
        "latitude": str(lat),
        "longitude": str(lon),
        "distance": str(distance),
        "code_parametre": "1301",
        "date_debut_prelevement": date_min,
        "size": "500",
        "sort": "desc",
        "fields": "code_station,libelle_station,date_prelevement",
    }
    data = await fetch_json(session, URL_QUALITE_ANALYSES, params)
    return data.get("data") or []


async def qualite_dernieres_analyses(
    session: aiohttp.ClientSession, code_station: str, codes_parametres: list[str]
) -> dict[str, dict]:
    """Dernière analyse par paramètre pour la station : {code_param: {valeur, date, unite}}."""
    params = {
        "code_station": code_station,
        "code_parametre": ",".join(codes_parametres),
        "size": "80",
        "sort": "desc",
        "fields": "code_parametre,resultat,symbole_unite,date_prelevement,heure_prelevement",
    }
    data = await fetch_json(session, URL_QUALITE_ANALYSES, params)
    result: dict[str, dict] = {}
    for row in data.get("data") or []:
        code = row.get("code_parametre")
        if not code or code in result or row.get("resultat") is None:
            continue
        date = row.get("date_prelevement")
        heure = row.get("heure_prelevement") or "12:00:00"
        result[code] = {
            "valeur": row.get("resultat"),
            "unite": row.get("symbole_unite"),
            "date": f"{date}T{heure}" if date else None,
        }
    return result


# ======================================================================
# Hub'eau — nappes phréatiques
# ======================================================================

async def nappes_liste_stations(session: aiohttp.ClientSession, departement: str) -> list[dict]:
    params = {
        "code_departement": departement,
        "size": "1000",
        "fields": "code_bss,nom_commune,date_fin_mesure,date_debut_mesure,x,y",
    }
    data = await fetch_json(session, URL_NAPPES_STATIONS, params)
    return [
        {
            "code_bss": s["code_bss"],
            "libelle": s.get("nom_commune") or s["code_bss"],
            "date_fin_mesure": s.get("date_fin_mesure"),
            "lon": s.get("x"),
            "lat": s.get("y"),
        }
        for s in data.get("data") or []
        if s.get("code_bss")
    ]


async def nappes_niveaux_journaliers(
    session: aiohttp.ClientSession, code_bss: str, date_min: str
) -> list[tuple[str, float]]:
    """Niveaux NGF validés quotidiens [(date, m NGF), ...] depuis date_min."""
    params = {
        "code_bss": code_bss,
        "date_debut_mesure": date_min,
        "size": "20000",
        "fields": "date_mesure,niveau_nappe_eau",
    }
    data = await fetch_json(session, URL_NAPPES_CHRONIQUES, params, timeout=TIMEOUT_LONG)
    return [
        (row["date_mesure"], row["niveau_nappe_eau"])
        for row in data.get("data") or []
        if row.get("date_mesure") and row.get("niveau_nappe_eau") is not None
    ]


async def nappes_derniere_mesure(session: aiohttp.ClientSession, code_bss: str) -> dict | None:
    """Dernière mesure + chronique récente (~15 j) pour les tendances.

    Temps réel horaire en priorité, repli sur la chronique validée quotidienne."""
    params = {"code_bss": code_bss, "size": "400", "sort": "desc"}
    data = await fetch_json(session, URL_NAPPES_CHRONIQUES_TR, params)
    rows = data.get("data") or []
    cle_niveau, temps_reel = "niveau_eau_ngf", True
    if not rows:
        params["size"] = "20"
        data = await fetch_json(session, URL_NAPPES_CHRONIQUES, params)
        rows = data.get("data") or []
        cle_niveau, temps_reel = "niveau_nappe_eau", False
    if not rows:
        return None

    derniere = rows[0]
    points = sorted(
        (row["date_mesure"], row[cle_niveau])
        for row in rows
        if row.get("date_mesure") and row.get(cle_niveau) is not None
    )
    return {
        "profondeur": derniere.get("profondeur_nappe"),
        "niveau_ngf": derniere.get(cle_niveau),
        "date": derniere.get("date_mesure"),
        "temps_reel": temps_reel,
        "points": points,
    }


# ======================================================================
# baignades.sante.gouv.fr — qualité des eaux de baignade
# ======================================================================

def _dept_court(departement: str) -> str:
    """'025' → '25' (les endpoints JSON veulent le code court, '2A' inclus)."""
    return departement.lstrip("0") or departement


async def baignades_communes(session: aiohttp.ClientSession, departement: str) -> list[dict]:
    """Communes du département ayant au moins un site de baignade."""
    data = await fetch_json(
        session,
        URL_BAIGNADES_COMMUNES,
        {"idCarte": "fra", "code_dept": _dept_court(departement)},
    )
    return [
        {"insee": c["insee_com"], "nom": joli_libelle((c.get("nom") or "").strip())}
        for c in data.get("communes") or []
        if c.get("insee_com")
    ]


async def baignades_sites(
    session: aiohttp.ClientSession, departement: str, insee: str
) -> list[dict]:
    """Sites de baignade d'une commune. site = dptddass + isite."""
    data = await fetch_json(
        session,
        URL_BAIGNADES_SITES,
        {"idCarte": "fra", "code_dept": _dept_court(departement), "insee_com": insee},
    )
    dptddass = departement.zfill(3)
    return [
        {
            "site": f"{dptddass}{s['isite']}",
            "dptddass": dptddass,
            "libelle": joli_libelle((s.get("nom") or "").strip()),
        }
        for s in data.get("sites") or []
        if s.get("isite")
    ]


async def baignades_site_details(
    session: aiohttp.ClientSession, dptddass: str, site: str, annee: int
) -> dict | None:
    """Saison, classement et prélèvements d'un site. None si page non reconnue."""
    try:
        async with session.get(
            URL_BAIGNADES_SITE,
            params={
                "dptddass": dptddass,
                "site": site,
                "plv": "no",
                "idCarte": "fra",
                "annee": str(annee),
            },
            timeout=TIMEOUT,
        ) as resp:
            if resp.status >= 400:
                return None
            raw = (await resp.read()).decode("cp1252", errors="replace")
    except (aiohttp.ClientError, TimeoutError) as err:
        raise MonEauApiError(f"baignades injoignable: {err}") from err
    return _baignades_parse(raw, annee)


def _jjmmaaaa_vers_iso(date: str) -> str:
    jour, mois, annee = date.split("/")
    return f"{annee}-{mois}-{jour}"


def _baignades_parse(raw: str, annee: int) -> dict | None:
    text = _strip_tags(raw)

    m_debut = re.search(r"Début de la saison\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    m_fin = re.search(r"Fin de la saison\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    if not m_debut or not m_fin:
        return None

    # Prélèvements de l'année : paires « date qualité », liens plv= dans le même ordre
    controles: list[dict] = []
    m_section = re.search(
        r"Résultats des prélèvements.{0,20}?((?:\d{2}/\d{2}/\d{4}\s+[A-Za-zéè' ]+?\s+)+)", text
    )
    if m_section:
        plv_ids = re.findall(r"[?&]plv=([0-9AB]{8,})", raw)  # « A »/« B » : Corse
        paires = re.findall(r"(\d{2}/\d{2}/\d{4})\s+([A-Za-zéè']+)", m_section.group(1))
        for idx, (date, qualite) in enumerate(paires):
            controles.append(
                {
                    "date": _jjmmaaaa_vers_iso(date),
                    "qualite": qualite,
                    "plv": plv_ids[idx] if idx < len(plv_ids) else None,
                }
            )

    # Classement de l'année en cours (souvent « site non classé » avant la fin de saison)
    m_classement = re.search(r"Classement de l'année \d{4}\s*:\s*(.+?)\s+Légende", text)
    classement_annee = m_classement.group(1).strip() if m_classement else None

    # Historique : après les 6 images de légende, une image par année (n° de classe)
    historique: dict[int, str] = {}
    classement_precedent = None
    annee_precedente = None
    j = raw.find("Historique des classements")
    if j != -1:
        k = raw.find("A partir de la saison", j)
        chunk = raw[j : k if k > j else j + 6000]
        annees = re.findall(r">\s*(20\d{2})\s*<", chunk)
        classes = re.findall(r'src="[^"]*classe(\d+)\.gif"', chunk)[6:]
        for an, classe in zip(annees, classes):
            libelle = BAIGNADE_CLASSEMENTS.get(classe)
            if libelle:
                historique[int(an)] = libelle
                if classe in ("1", "2", "3", "4"):
                    classement_precedent = libelle
                    annee_precedente = int(an)

    interdiction = bool(re.search(r"interdiction de baignade|baignade interdite", text, re.I))

    return {
        "saison_debut": _jjmmaaaa_vers_iso(m_debut.group(1)),
        "saison_fin": _jjmmaaaa_vers_iso(m_fin.group(1)),
        "annee": annee,
        "controles": controles,
        "dernier_controle": controles[-1] if controles else None,
        "classement_annee": classement_annee,
        "classement": classement_precedent,
        "annee_classement": annee_precedente,
        "historique_classements": historique,
        "interdiction": interdiction,
    }


async def baignades_controle_details(
    session: aiohttp.ClientSession, dptddass: str, site: str, plv: str, annee: int
) -> dict | None:
    """Valeurs bactério d'un prélèvement : E. coli et entérocoques avec leurs seuils."""
    try:
        async with session.get(
            URL_BAIGNADES_SITE,
            params={
                "isite": site,
                "site": site,
                "dptddass": dptddass,
                "annee": str(annee),
                "plv": plv,
            },
            timeout=TIMEOUT,
        ) as resp:
            if resp.status >= 400:
                return None
            raw = (await resp.read()).decode("cp1252", errors="replace")
    except (aiohttp.ClientError, TimeoutError):
        return None

    text = _strip_tags(raw)
    result: dict[str, dict] = {}
    motifs = {
        "enterocoques": r"Entérocoques intestinaux \(/100mL\)\s+([<>]?[\d,.]+)\s+(\d+)\s+(\d+)",
        "e_coli": r"Escherichia coli \(E\.coli\) \(/100mL\)\s+([<>]?[\d,.]+)\s+(\d+)\s+(\d+)",
    }
    for cle, motif in motifs.items():
        m = re.search(motif, text)
        if m:
            result[cle] = {
                "valeur": to_float(m.group(1)),
                "texte": m.group(1),
                "seuil_bon_moyen": int(m.group(2)),
                "seuil_moyen_mauvais": int(m.group(3)),
            }
    return result or None


# ======================================================================
# VigiEau + ONDE — sécheresse
# ======================================================================

async def vigieau_zones(session: aiohttp.ClientSession, code_commune: str) -> list[dict]:
    """Zones d'arrêté sécheresse de la commune (types SOU/SUP/AEP)."""
    try:
        data = await fetch_json(
            session, URL_VIGIEAU_ZONES, {"commune": code_commune, "profil": "particulier"}
        )
    except MonEauApiError as err:
        # 404 = aucune zone d'arrêté en cours pour la commune
        if "404" in str(err):
            return []
        raise
    return data if isinstance(data, list) else []


async def onde_resume(session: aiohttp.ClientSession, departement: str, date_min: str) -> dict:
    """Dernière campagne ONDE du département : comptage par type d'écoulement."""
    params = {
        "code_departement": departement,
        "date_observation_min": date_min,
        "size": "500",
        "sort": "desc",
        "fields": "code_station,libelle_station,date_observation,libelle_ecoulement",
    }
    data = await fetch_json(session, URL_ONDE_OBSERVATIONS, params)
    derniere_par_station: dict[str, dict] = {}
    for row in data.get("data") or []:
        code = row.get("code_station")
        if code and code not in derniere_par_station:
            derniere_par_station[code] = row
    comptages: dict[str, int] = {}
    assecs: list[str] = []
    date_campagne = None
    for row in derniere_par_station.values():
        libelle = row.get("libelle_ecoulement") or "Inconnu"
        comptages[libelle] = comptages.get(libelle, 0) + 1
        if "assec" in libelle.lower():
            assecs.append(row.get("libelle_station") or row["code_station"])
        date = row.get("date_observation")
        if date and (date_campagne is None or date > date_campagne):
            date_campagne = date
    return {
        "date_campagne": date_campagne,
        "stations_observees": len(derniere_par_station),
        "comptages": comptages,
        "assecs": sorted(assecs),
    }
