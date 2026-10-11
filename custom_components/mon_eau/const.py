# custom_components/mon_eau/const.py
"""Constantes de l'intégration Mon Eau."""
from __future__ import annotations

DOMAIN = "mon_eau"

# --- Plateformes fonctionnelles (pas les Platform HA) -----------------
FEATURE_EAU_POTABLE = "eau_potable"
FEATURE_RIVIERE = "riviere"
FEATURE_NAPPE = "nappe"
FEATURE_SECHERESSE = "secheresse"
FEATURE_BAIGNADE = "baignade"
ALL_FEATURES = [
    FEATURE_EAU_POTABLE,
    FEATURE_RIVIERE,
    FEATURE_NAPPE,
    FEATURE_SECHERESSE,
    FEATURE_BAIGNADE,
]

# --- Clés de configuration -------------------------------------------
CONF_FEATURES = "features"
CONF_COMMUNE = "commune"          # {code, nom, lat, lon, departement, region}
CONF_RESEAU = "reseau"            # liste de {code, nom, quartier}
CONF_RESEAU_COMMUNE = "reseau_commune"  # True = suivre aussi « toute la commune »
CONF_HYDRO = "hydro"              # {code, libelle, lat, lon}
CONF_QUALITE = "qualite"          # {code, libelle}
CONF_TEMPERATURE = "temperature"  # {code, libelle} ou None
CONF_TRONCON = "troncon"          # {code, libelle} ou None (vigilance crues)
CONF_PIEZO = "piezo"              # {code_bss, libelle}
CONF_BAIGNADE = "baignade_site"   # {site, dptddass, libelle, commune}

# --- URLs Hub'eau -----------------------------------------------------
HUBEAU = "https://hubeau.eaufrance.fr/api"
URL_DIS_RESULTATS = f"{HUBEAU}/v1/qualite_eau_potable/resultats_dis"
URL_DIS_UDI = f"{HUBEAU}/v1/qualite_eau_potable/communes_udi"
URL_HYDRO_OBS_TR = f"{HUBEAU}/v2/hydrometrie/observations_tr"
URL_HYDRO_OBS_ELAB = f"{HUBEAU}/v2/hydrometrie/obs_elab"
URL_HYDRO_STATIONS = f"{HUBEAU}/v2/hydrometrie/referentiel/stations"
URL_TEMP_STATIONS = f"{HUBEAU}/v1/temperature/station"
URL_TEMP_CHRONIQUE = f"{HUBEAU}/v1/temperature/chronique"
URL_QUALITE_STATIONS = f"{HUBEAU}/v2/qualite_rivieres/station_pc"
URL_QUALITE_ANALYSES = f"{HUBEAU}/v2/qualite_rivieres/analyse_pc"
URL_NAPPES_STATIONS = f"{HUBEAU}/v1/niveaux_nappes/stations"
URL_NAPPES_CHRONIQUES_TR = f"{HUBEAU}/v1/niveaux_nappes/chroniques_tr"
URL_NAPPES_CHRONIQUES = f"{HUBEAU}/v1/niveaux_nappes/chroniques"
URL_ONDE_OBSERVATIONS = f"{HUBEAU}/v1/ecoulement/observations"

# --- Autres sources ---------------------------------------------------
URL_GEO_COMMUNES = "https://geo.api.gouv.fr/communes"
URL_VIGIEAU_ZONES = "https://api.vigieau.beta.gouv.fr/api/zones"
URL_VIGICRUES_GEOJSON = "https://www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson"
URL_VIGICRUES_PREVISION = "https://www.vigicrues.gouv.fr/services/v1.1/prevision.json"
URL_OROBNAT_MENU = "https://orobnat.sante.gouv.fr/orobnat/afficherPage.do"
URL_OROBNAT_RECHERCHE = "https://orobnat.sante.gouv.fr/orobnat/rechercherResultatQualite.do"
BAIGNADES = "https://baignades.sante.gouv.fr/baignades"
URL_BAIGNADES_COMMUNES = f"{BAIGNADES}/communeList.do"
URL_BAIGNADES_SITES = f"{BAIGNADES}/siteList.do"
URL_BAIGNADES_SITE = f"{BAIGNADES}/consultSite.do"

# --- Codes paramètres SANDRE (eau potable, vérifiés dans les données) --
PARAM_NITRATES = "1340"       # mg/L, limite <=50
PARAM_PESTICIDES = "6276"     # somme pesticides, µg/L, limite <=0,5
PARAM_E_COLI = "1449"         # n/(100mL), limite <=0
PARAM_ENTEROCOQUES = "6455"   # n/(100mL), limite <=0
DIS_PARAMS = {
    PARAM_NITRATES: "nitrates",
    PARAM_PESTICIDES: "pesticides",
    PARAM_E_COLI: "e_coli",
    PARAM_ENTEROCOQUES: "enterocoques",
}

# --- Codes paramètres SANDRE (qualité rivières) -----------------------
PARAM_TEMPERATURE = "1301"
PARAM_OXYGENE = "1311"
PARAM_PH = "1302"
PARAM_NITRATES_RIVIERE = "1340"
RIVER_QUALITY_PARAMS = {
    PARAM_TEMPERATURE: "temperature",
    PARAM_OXYGENE: "oxygene",
    PARAM_PH: "ph",
    PARAM_NITRATES_RIVIERE: "nitrates",
}

# --- Vigilance crues --------------------------------------------------
VIGILANCE_LEVELS = {1: "verte", 2: "jaune", 3: "orange", 4: "rouge"}

# --- Situation hydrologique (vs percentiles des normales) -------------
SITUATIONS_HYDRO = ["tres_bas", "bas", "normal", "haut", "tres_haut"]
NORMALES_ANNEES = 15           # profondeur d'historique QmnJ pour les normales
NORMALES_FENETRE_JOURS = 15    # ± jours autour du jour de l'année
SCAN_NORMALES = 7 * 24 * 3600
SCAN_TENDANCES = 6 * 3600
TENDANCE_HORIZONS = {"h24": 1, "j7": 7, "j15": 15}  # jours
TENDANCE_ETATS = ["stable", "monte_lente", "monte_rapide", "descend_lente", "descend_rapide"]

# --- Modèles de device (filtre des éditeurs de cartes) ----------------
MODEL_EAU_POTABLE = "Eau du robinet"
MODEL_RIVIERE = "Rivière"
MODEL_NAPPE = "Nappe phréatique"
MODEL_SECHERESSE = "Sécheresse"
MODEL_BAIGNADE = "Baignade"

# --- Sécheresse (VigiEau) ---------------------------------------------
GRAVITE_ORDRE = ["vigilance", "alerte", "alerte_renforcee", "crise"]
GRAVITE_AUCUNE = "aucune"
VIGIEAU_TYPES = {"SOU": "nappe", "SUP": "riviere", "AEP": "eau_potable"}

# --- Intervalles de polling (secondes) --------------------------------
SCAN_EAU_POTABLE = 12 * 3600
SCAN_HYDRO = 15 * 60
SCAN_VIGILANCE = 3600          # geojson ~2 Mo → 1 h max
SCAN_TEMP_CONTINUE = 3600
SCAN_QUALITE = 24 * 3600
SCAN_NAPPE = 3600
SCAN_SECHERESSE = 6 * 3600
SCAN_BAIGNADE_SAISON = 6 * 3600
SCAN_BAIGNADE_HORS_SAISON = 24 * 3600

# --- Baignade : classes de la directive 2006/7/CE ---------------------
BAIGNADE_CLASSEMENTS = {
    "1": "Excellent",
    "2": "Bon",
    "3": "Suffisant",
    "4": "Insuffisant",
    "5": "Insuffisamment de prélèvements",
    "6": "Site non classé",
}

# --- Divers -----------------------------------------------------------
ATTR_KIND = "mon_eau_kind"     # identifiant stable lu par les cartes Lovelace
STALE_DAYS_EAU_POTABLE = 60    # au-delà : données considérées anciennes
FRESH_TEMP_DAYS = 30           # station température « vivante » si mesure < 30 j
PIEZO_ACTIVE_DAYS = 60         # piézomètre « actif » si mesure < 60 j
