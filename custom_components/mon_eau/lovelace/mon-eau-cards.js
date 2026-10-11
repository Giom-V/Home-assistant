// custom_components/mon_eau/lovelace/mon-eau-cards.js
// Cartes Lovelace packagées avec l'intégration Mon Eau.

const ME_VERSION = "1.0.0";

// ────────────────────────────────────────────────────────────────────
// Utilitaires
// ────────────────────────────────────────────────────────────────────

const STR = {
  fr: {
    tap_water: "Eau du robinet",
    compliant: "Eau conforme",
    non_compliant: "Eau non conforme",
    stale: "Données anciennes",
    unknown: "État inconnu",
    sampled: "prélevé",
    source_ars: "source ARS",
    source_hubeau: "source Hub'eau",
    nitrates: "Nitrates",
    pesticides: "Pesticides totaux",
    bacterio: "Bactériologie",
    ars_conclusion: "Conclusion sanitaire",
    level: "Hauteur",
    flow: "Débit",
    water_temp: "Température de l'eau",
    oxygen: "Oxygène dissous",
    ph: "pH",
    river_nitrates: "Nitrates",
    realtime: "temps réel",
    observed: "observé · 24 h",
    forecast: "prévision Vigicrues",
    now: "maintenant",
    vigilance: "Vigilance",
    depth: "Profondeur",
    ngf: "Niveau NGF",
    groundwater: "Nappe phréatique",
    days30: "niveau · 30 j",
    drought: "Sécheresse",
    no_restriction: "Aucune restriction",
    decree: "Arrêté",
    to: "au",
    see_pdf: "voir le PDF",
    other_usages: "autres usages",
    dry_streams: "assecs observés",
    resource_nappe: "nappe",
    resource_riviere: "rivières",
    resource_eau_potable: "eau potable",
    gravite_vigilance: "vigilance",
    gravite_alerte: "alerte",
    gravite_alerte_renforcee: "alerte renf.",
    gravite_crise: "crise",
    forbidden: "Interdit",
    restricted: "Restreint",
    allowed: "Autorisé",
    bathing: "Baignade",
    season_closed: "saison fermée",
    reopen: "réouverture",
    classification: "Classement",
    bath_ok: "Baignade autorisée",
    bath_warn: "Qualité moyenne",
    bath_bad: "Baignade déconseillée",
    bath_forbidden: "Baignade interdite",
    last_control: "dernier contrôle",
    season: "saison",
    controls_history: "Contrôles de la saison",
    ecoli: "E. coli",
    entero: "Entérocoques",
    of_normal: "de la normale de saison",
    vs_normal: "vs normale de saison",
    fill: "Remplissage",
    historical_range: "de la plage historique",
    sit_tres_bas: "très bas",
    sit_bas: "bas",
    sit_normal: "normal",
    sit_haut: "haut",
    sit_tres_haut: "très haut",
    vit_lente: "lente",
    vit_rapide: "rapide",
    h24: "24 h",
    j7: "7 j",
    j15: "15 j",
  },
  en: {
    tap_water: "Tap water",
    compliant: "Water compliant",
    non_compliant: "Water non compliant",
    stale: "Stale data",
    unknown: "Unknown state",
    sampled: "sampled",
    source_ars: "ARS source",
    source_hubeau: "Hub'eau source",
    nitrates: "Nitrates",
    pesticides: "Total pesticides",
    bacterio: "Bacteriology",
    ars_conclusion: "Health conclusion",
    level: "Level",
    flow: "Flow",
    water_temp: "Water temperature",
    oxygen: "Dissolved oxygen",
    ph: "pH",
    river_nitrates: "Nitrates",
    realtime: "real time",
    observed: "observed · 24 h",
    forecast: "Vigicrues forecast",
    now: "now",
    vigilance: "Warning",
    depth: "Depth",
    ngf: "NGF level",
    groundwater: "Groundwater",
    days30: "level · 30 d",
    drought: "Drought",
    no_restriction: "No restriction",
    decree: "Decree",
    to: "to",
    see_pdf: "see PDF",
    other_usages: "other usages",
    dry_streams: "dry streams observed",
    resource_nappe: "groundwater",
    resource_riviere: "rivers",
    resource_eau_potable: "tap water",
    gravite_vigilance: "vigilance",
    gravite_alerte: "alert",
    gravite_alerte_renforcee: "reinf. alert",
    gravite_crise: "crisis",
    forbidden: "Forbidden",
    restricted: "Restricted",
    allowed: "Allowed",
    bathing: "Bathing",
    season_closed: "season closed",
    reopen: "reopens",
    classification: "Classification",
    bath_ok: "Bathing allowed",
    bath_warn: "Average quality",
    bath_bad: "Bathing not advised",
    bath_forbidden: "Bathing forbidden",
    last_control: "last control",
    season: "season",
    controls_history: "Season controls",
    ecoli: "E. coli",
    entero: "Enterococci",
    of_normal: "of seasonal normal",
    vs_normal: "vs seasonal normal",
    fill: "Fill level",
    historical_range: "of historical range",
    sit_tres_bas: "very low",
    sit_bas: "low",
    sit_normal: "normal",
    sit_haut: "high",
    sit_tres_haut: "very high",
    vit_lente: "slow",
    vit_rapide: "fast",
    h24: "24 h",
    j7: "7 d",
    j15: "15 d",
  },
};

const SIT_COLORS = {
  tres_bas: "var(--error-color)",
  bas: "var(--warning-color)",
  normal: "var(--success-color)",
  haut: "var(--info-color, #2196f3)",
  tres_haut: "var(--error-color)",
};

function opt(config, key) {
  return config[key] !== false;
}

// ↑↓ = rapide, ↗↘ = lente, → = stable
function arrowDir(tendance) {
  if (!tendance || tendance.direction === "stable") return "→";
  if (tendance.direction === "monte") return tendance.vitesse === "rapide" ? "↑" : "↗";
  return tendance.vitesse === "rapide" ? "↓" : "↘";
}

function trendColor(tendance) {
  if (!tendance || tendance.direction === "stable") return "var(--secondary-text-color)";
  return tendance.direction === "monte"
    ? "var(--info-color, #2196f3)"
    : "var(--warning-color, #ff9800)";
}

function deltaCm(tendance) {
  if (!tendance || tendance.direction === "stable" || tendance.delta_m === undefined) return "";
  const cm = Math.abs(tendance.delta_m) * 100;
  return cm >= 1 ? `${Math.round(cm)} cm` : "<1 cm";
}

// Une pastille par horizon : « 7 j ↘ 4 cm »
function trendChips(tendances, hass) {
  if (!tendances) return "";
  const chips = [];
  for (const cle of ["h24", "j7", "j15"]) {
    const tendance = tendances[cle];
    if (!tendance) continue;
    const delta = deltaCm(tendance);
    chips.push(`
      <span class="trend" title="${tendance.vitesse ? tr(hass, `vit_${tendance.vitesse}`) : ""}">
        <span class="trend-label">${tr(hass, cle)}</span>
        <b style="color:${trendColor(tendance)};">${arrowDir(tendance)}</b>
        ${delta ? `<span class="trend-delta">${delta}</span>` : ""}
      </span>`);
  }
  return chips.length
    ? `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;">${chips.join("")}</div>`
    : "";
}

// Pour les vues compactes : l'horizon le plus marqué seulement
function trendResume(tendances, hass) {
  if (!tendances) return "";
  let meilleur = null, cleMeilleur = null;
  for (const cle of ["h24", "j7", "j15"]) {
    const tendance = tendances[cle];
    if (tendance && (!meilleur || Math.abs(tendance.delta_m) > Math.abs(meilleur.delta_m))) {
      meilleur = tendance;
      cleMeilleur = cle;
    }
  }
  if (!meilleur) return "";
  const delta = deltaCm(meilleur);
  return `${tr(hass, cleMeilleur)} ${arrowDir(meilleur)}${delta ? ` ${delta}` : ""}`;
}

function tr(hass, key) {
  const lang = (hass && hass.language || "fr").startsWith("fr") ? "fr" : "en";
  return STR[lang][key] || STR.fr[key] || key;
}

function cap(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : str;
}

function esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function fmt(value, digits = 1) {
  if (value === null || value === undefined || isNaN(value)) return "—";
  return Number(value).toLocaleString("fr-FR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  });
}

// "il y a 10 min" / "il y a 17 j" — ou date courte si trop vieux
function relTime(iso, lang = "fr") {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date)) return "";
  const diffMin = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000));
  const ago = lang === "fr" ? "il y a" : "";
  const suffix = lang === "fr" ? "" : " ago";
  if (diffMin < 60) return `${ago} ${diffMin} min${suffix}`.trim();
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 48) return `${ago} ${diffH} h${suffix}`.trim();
  const diffJ = Math.floor(diffH / 24);
  if (diffJ < 90) return `${ago} ${diffJ} ${lang === "fr" ? "j" : "d"}${suffix}`.trim();
  return dayLabel(iso, lang);
}

// chip de date "2 avr"
function dayLabel(iso, lang = "fr") {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date)) return "";
  return date.toLocaleDateString(lang === "fr" ? "fr-FR" : "en-GB", {
    day: "numeric",
    month: "short",
  });
}

function fireMoreInfo(el, entityId) {
  if (!entityId) return;
  el.dispatchEvent(new CustomEvent("hass-more-info", {
    detail: { entityId }, bubbles: true, composed: true,
  }));
}

// Entités du device, indexées par attribut mon_eau_kind
function kindMap(hass, deviceId) {
  const map = {};
  if (!deviceId) return map;
  for (const [eid, reg] of Object.entries(hass.entities || {})) {
    if (reg.device_id !== deviceId) continue;
    const st = hass.states[eid];
    const kind = st && st.attributes && st.attributes.mon_eau_kind;
    if (kind && !(kind in map)) map[kind] = st;
  }
  return map;
}

// Premier device de l'intégration portant un kind donné (pour getStubConfig)
function findDeviceByKind(hass, kind) {
  for (const [eid, reg] of Object.entries(hass.entities || {})) {
    const st = hass.states[eid];
    if (st && st.attributes && st.attributes.mon_eau_kind === kind) return reg.device_id;
  }
  return undefined;
}

// Historique numérique d'une entité → [[Date, val], ...] (cache 5 min)
const _histCache = {};
async function fetchHistory(hass, entityId, hours) {
  const key = `${entityId}_${hours}`;
  const cached = _histCache[key];
  if (cached && Date.now() - cached.at < 5 * 60000) return cached.points;
  const start = new Date(Date.now() - hours * 3600000).toISOString();
  let raw;
  try {
    raw = await hass.callApi(
      "GET",
      `history/period/${start}?filter_entity_id=${entityId}&minimal_response&no_attributes`
    );
  } catch (e) {
    return [];
  }
  const points = [];
  for (const item of (raw && raw[0]) || []) {
    const value = parseFloat(item.state ?? item.s);
    const when = item.last_changed ?? item.lc ?? item.lu;
    if (!isNaN(value) && when) points.push([new Date(when), value]);
  }
  _histCache[key] = { at: Date.now(), points };
  return points;
}

// Polyline SVG normalisée. extra = points de prévision (pointillés)
function sparkline(points, extra, color, width = 300, height = 40) {
  const all = [...points, ...(extra || [])];
  if (all.length < 2) return "";
  const t0 = all[0][0].getTime();
  const t1 = all[all.length - 1][0].getTime() || t0 + 1;
  const values = all.map((p) => p[1]);
  const vMin = Math.min(...values);
  const vMax = Math.max(...values);
  const span = vMax - vMin || 1;
  const xy = (p) => [
    (((p[0].getTime() - t0) / (t1 - t0 || 1)) * width).toFixed(1),
    (height - 5 - ((p[1] - vMin) / span) * (height - 10)).toFixed(1),
  ];
  const line = points.map((p) => xy(p).join(",")).join(" ");
  let svg = `<svg viewBox="0 0 ${width} ${height + 6}" preserveAspectRatio="none" style="width:100%;height:${height}px;display:block;">`;
  if (extra && extra.length && points.length) {
    const last = xy(points[points.length - 1]);
    const dashed = [last.join(","), ...extra.map((p) => xy(p).join(","))].join(" ");
    svg += `<line x1="${last[0]}" y1="2" x2="${last[0]}" y2="${height}" stroke="var(--divider-color)" stroke-width="1" stroke-dasharray="2,3"/>`;
    svg += `<polyline points="${dashed}" fill="none" stroke="${color}" stroke-width="1.8" stroke-dasharray="4,4"/>`;
    svg += `<circle cx="${last[0]}" cy="${last[1]}" r="2.5" fill="${color}"/>`;
  }
  svg += `<polyline points="${line}" fill="none" stroke="${color}" stroke-width="1.8"/></svg>`;
  return svg;
}

// ────────────────────────────────────────────────────────────────────
// Styles partagés (imite ha-card, suit le thème HA)
// ────────────────────────────────────────────────────────────────────

const SHARED_CSS = `
  ha-card { padding: 16px; }
  .head { display: flex; align-items: center; gap: 10px; }
  .head ha-icon { --mdc-icon-size: 22px; }
  .badge-icon {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; flex: none;
  }
  .head .titles { flex: 1; min-width: 0; }
  .head .title { font-weight: 500; font-size: 15px; color: var(--primary-text-color); }
  .head .subtitle {
    font-size: 12px; color: var(--secondary-text-color);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .pill {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 12.5px; font-weight: 500; padding: 4px 12px; border-radius: 999px;
  }
  .muted { font-size: 12px; color: var(--secondary-text-color); }
  .chip {
    font-size: 11px; color: var(--secondary-text-color);
    background: var(--secondary-background-color); padding: 1px 6px; border-radius: 999px;
  }
  .trend {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11.5px; padding: 3px 9px; border-radius: 999px;
    background: var(--secondary-background-color);
  }
  .trend b { font-size: 13px; font-weight: 600; }
  .trend-label { color: var(--secondary-text-color); }
  .trend-delta { color: var(--secondary-text-color); }
  .tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
  .tile { background: var(--secondary-background-color); border-radius: 10px; padding: 8px 12px; cursor: pointer; }
  .tile .label { font-size: 12px; color: var(--secondary-text-color); }
  .tile .value { font-size: 21px; font-weight: 500; color: var(--primary-text-color); }
  .tile .unit { font-size: 13px; color: var(--secondary-text-color); font-weight: 400; }
  .rows { border-top: 1px solid var(--divider-color); margin-top: 12px; padding-top: 6px; }
  .row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; padding: 3px 0; color: var(--primary-text-color); cursor: pointer;
  }
  .row .label { color: var(--secondary-text-color); }
  .bar { height: 6px; border-radius: 3px; background: var(--secondary-background-color); margin: 2px 0 8px; }
  .bar > div { height: 6px; border-radius: 3px; }
  details { border-top: 1px solid var(--divider-color); margin-top: 10px; padding-top: 6px; }
  summary { font-size: 12px; color: var(--secondary-text-color); cursor: pointer; }
  details p { font-size: 12.5px; color: var(--primary-text-color); line-height: 1.5; margin: 8px 0 0; }
  .footer { margin-top: 6px; font-size: 11px; color: var(--secondary-text-color); text-align: right; }
  .compact { display: flex; align-items: center; gap: 10px; }
  .compact .badge-icon { width: 32px; height: 32px; }
  .compact .titles { flex: 1; min-width: 0; }
  .alertband { border-radius: 8px; padding: 8px 12px; margin-top: 12px; font-size: 12.5px; line-height: 1.5; }
  a { color: var(--primary-color); text-decoration: none; }
`;

// ────────────────────────────────────────────────────────────────────
// Base
// ────────────────────────────────────────────────────────────────────

class MonEauBaseCard extends HTMLElement {
  static editorModel = null;
  static editorExtras = [];

  static getConfigElement() {
    const editor = document.createElement("mon-eau-card-editor");
    editor.setOptions(this.editorModel, this.editorExtras);
    return editor;
  }

  setConfig(config) {
    if (!config || !config.device) {
      throw new Error("Configurez le device Mon Eau (option « device »).");
    }
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._kinds = kindMap(hass, this._config.device);
    this._render();
  }

  getCardSize() {
    return this._config && this._config.compact ? 1 : 4;
  }

  _shell(inner, borderColor) {
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    const border = borderColor
      ? `border: 2px solid ${borderColor};`
      : "";
    this.shadowRoot.innerHTML =
      `<style>${SHARED_CSS} ha-card { ${border} }</style><ha-card>${inner}</ha-card>`;
    this.shadowRoot.querySelectorAll("[data-entity]").forEach((el) => {
      el.addEventListener("click", () => fireMoreInfo(this, el.dataset.entity));
    });
  }
}

const EDITOR_LABELS = {
  device: { fr: "Appareil Mon Eau", en: "Mon Eau device" },
  compact: { fr: "Vue compacte (une ligne)", en: "Compact view (one line)" },
  barres: { fr: "Barres de paramètres", en: "Parameter bars" },
  conclusion: { fr: "Conclusion sanitaire ARS", en: "ARS health conclusion" },
  sparkline: { fr: "Courbe d'historique", en: "History curve" },
  sante: { fr: "Santé de la rivière", en: "River health" },
  tendances: { fr: "Tendances", en: "Trends" },
  usages: { fr: "Usages restreints", en: "Restricted usages" },
  remplissage: { fr: "Barre de remplissage", en: "Fill level bar" },
  assecs: { fr: "Assecs ONDE", en: "ONDE dry streams" },
  historique: { fr: "Historique des contrôles", en: "Controls history" },
};

class MonEauCardEditor extends HTMLElement {
  setOptions(model, extras) {
    this._model = model;
    this._extras = extras || [];
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass || !this._config) return;
    const lang = (this._hass.language || "fr").startsWith("fr") ? "fr" : "en";
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (s) => (EDITOR_LABELS[s.name] || {})[lang] || s.name;
      this._form.addEventListener("value-changed", (ev) => {
        const config = { ...this._config, ...ev.detail.value };
        this.dispatchEvent(new CustomEvent("config-changed", {
          detail: { config }, bubbles: true, composed: true,
        }));
      });
      this.appendChild(this._form);
    }
    const device = { integration: "mon_eau" };
    if (this._model) device.model = this._model;
    this._form.hass = this._hass;
    this._form.data = this._config;
    this._form.schema = [
      { name: "device", selector: { device } },
      { name: "compact", selector: { boolean: {} } },
      ...this._extras,
    ];
  }
}

// ────────────────────────────────────────────────────────────────────
// 1. mon-eau-water-card — Eau du robinet
// ────────────────────────────────────────────────────────────────────

class MonEauWaterCard extends MonEauBaseCard {
  static editorModel = "Eau du robinet";
  static editorExtras = [
    { name: "barres", selector: { boolean: {} } },
    {
      name: "conclusion",
      selector: {
        select: { options: ["auto", "toujours", "jamais"], mode: "dropdown" },
      },
    },
  ];

  static getStubConfig(hass) {
    return { device: findDeviceByKind(hass, "conformite"), barres: true };
  }

  _render() {
    const hass = this._hass;
    const k = this._kinds || {};
    const conf = k.conformite;
    const lang = (hass.language || "fr").startsWith("fr") ? "fr" : "en";
    const t = (key) => tr(hass, key);

    if (!conf) {
      this._shell(`<div class="muted">${t("tap_water")} — entité introuvable</div>`);
      return;
    }

    const attrs = conf.attributes;
    const nonConforme = conf.state === "on";
    const inconnu = conf.state !== "on" && conf.state !== "off";
    const stale = attrs.donnees_anciennes === true;

    let pillBg = "rgba(76,175,80,.15)", pillColor = "var(--success-color)",
        icon = "mdi:water-check", statusTxt = t("compliant"), border = null;
    if (nonConforme) {
      pillBg = "rgba(244,67,54,.15)"; pillColor = "var(--error-color)";
      icon = "mdi:water-alert"; statusTxt = t("non_compliant");
      border = "var(--error-color)";
    } else if (stale || inconnu) {
      pillBg = "var(--secondary-background-color)"; pillColor = "var(--secondary-text-color)";
      icon = "mdi:water-off-outline"; statusTxt = inconnu ? t("unknown") : t("stale");
    }

    const date = attrs.date_prelevement;
    const source = attrs.source === "ars_orobnat" ? t("source_ars") : t("source_hubeau");
    const meta = `${cap(t("sampled"))} ${relTime(date, lang)} · ${source}`;
    const subtitle = [attrs.reseau, attrs.distributeur].filter(Boolean).join(" · ");

    if (this._config.compact) {
      this._shell(`
        <div class="compact" data-entity="${esc(conf.entity_id)}" style="cursor:pointer;">
          <div class="badge-icon" style="background:${pillBg};color:${pillColor};">
            <ha-icon icon="${icon}"></ha-icon>
          </div>
          <div class="titles">
            <div class="title" style="font-size:14px;">${esc(statusTxt)}</div>
            <div class="subtitle">${esc(attrs.reseau || "")} · ${esc(relTime(date, lang))}</div>
          </div>
          ${this._compactNitrates(k)}
        </div>`, border);
      return;
    }

    const bars = opt(this._config, "barres")
      ? [
          this._barRow(k.nitrates, t("nitrates"), 1),
          this._barRow(k.pesticides, t("pesticides"), 2),
          this._bacterioRow(k, t),
        ].join("")
      : "";

    const modeConclusion = this._config.conclusion || "auto";
    const conclusion =
      attrs.conclusion && modeConclusion !== "jamais"
        ? `<details ${nonConforme || modeConclusion === "toujours" ? "open" : ""}>
             <summary>${t("ars_conclusion")}</summary>
             <p>${esc(attrs.conclusion)}</p>
           </details>`
        : "";

    this._shell(`
      <div class="head">
        <div class="badge-icon" style="background:${pillBg};color:${pillColor};">
          <ha-icon icon="${icon}"></ha-icon>
        </div>
        <div class="titles">
          <div class="title">${t("tap_water")}</div>
          <div class="subtitle">${esc(subtitle)}</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin:12px 0 4px;flex-wrap:wrap;">
        <span class="pill" style="background:${pillBg};color:${pillColor};cursor:pointer;"
              data-entity="${esc(conf.entity_id)}">${esc(statusTxt)}</span>
        <span class="muted">${esc(meta)}</span>
      </div>
      ${bars ? `<div style="margin-top:10px;">${bars}</div>` : ""}
      ${conclusion}`, border);
  }

  _compactNitrates(k) {
    const st = k.nitrates;
    if (!st || isNaN(parseFloat(st.state))) return "";
    return `<span class="muted" data-entity="${esc(st.entity_id)}" style="cursor:pointer;">nitrates ${fmt(parseFloat(st.state))}</span>`;
  }

  _barRow(st, label, digits) {
    if (!st) return "";
    const value = parseFloat(st.state);
    const attrs = st.attributes;
    const limite = attrs.limite;
    const texte = attrs.resultat_texte && attrs.resultat_texte.startsWith("<")
      ? esc(attrs.resultat_texte)
      : fmt(value, digits);
    let pct = null, color = "var(--success-color)";
    if (!isNaN(value) && limite) {
      pct = Math.min(100, (value / limite) * 100);
      if (pct >= 80) color = "var(--error-color)";
      else if (pct >= 50) color = "var(--warning-color)";
    }
    const right = limite
      ? `${texte} <span class="muted">/ ${fmt(limite, 1)} ${esc(attrs.unit_of_measurement || st.attributes.unit_of_measurement || "")}</span>`
      : texte;
    const bar = pct !== null
      ? `<div class="bar"><div style="width:${Math.max(2, pct).toFixed(0)}%;background:${color};"></div></div>`
      : "";
    return `
      <div class="row" data-entity="${esc(st.entity_id)}">
        <span class="label">${esc(label)}</span><span>${right}</span>
      </div>${bar}`;
  }

  _bacterioRow(k, t) {
    const ecoli = k.e_coli, entero = k.enterocoques;
    if (!ecoli && !entero) return "";
    const bad =
      (ecoli && parseFloat(ecoli.state) > 0) || (entero && parseFloat(entero.state) > 0);
    const color = bad ? "var(--error-color)" : "var(--success-color)";
    const icon = bad ? "mdi:close-circle-outline" : "mdi:check-circle-outline";
    const details = [
      ecoli && `E. coli ${fmt(parseFloat(ecoli.state), 0)}`,
      entero && `entérocoques ${fmt(parseFloat(entero.state), 0)}`,
    ].filter(Boolean).join(" · ");
    const target = (ecoli || entero).entity_id;
    return `
      <div class="row" data-entity="${esc(target)}">
        <span class="label">${t("bacterio")}</span>
        <span style="color:${color};display:inline-flex;align-items:center;gap:4px;">
          <ha-icon icon="${icon}" style="--mdc-icon-size:15px;"></ha-icon>${esc(details)}
        </span>
      </div>`;
  }
}

// ────────────────────────────────────────────────────────────────────
// 2. mon-eau-river-card — Rivière (avec mode crue)
// ────────────────────────────────────────────────────────────────────

const VIGI_COLORS = {
  jaune: "#f0b400",
  orange: "#ef7d00",
  rouge: "var(--error-color)",
};

class MonEauRiverCard extends MonEauBaseCard {
  static editorModel = "Rivière";
  static editorExtras = [
    { name: "sparkline", selector: { boolean: {} } },
    { name: "tendances", selector: { boolean: {} } },
    { name: "sante", selector: { boolean: {} } },
  ];

  static getStubConfig(hass) {
    return { device: findDeviceByKind(hass, "hauteur") };
  }

  set hass(hass) {
    this._hass = hass;
    this._kinds = kindMap(hass, this._config.device);
    this._render();
    this._loadHistory();
  }

  async _loadHistory() {
    const k = this._kinds || {};
    const vigi = k.vigilance;
    const crue = vigi && ["jaune", "orange", "rouge"].includes(vigi.state);
    const target = crue ? k.hauteur : k.debit || k.hauteur;
    if (!target) return;
    const points = await fetchHistory(this._hass, target.entity_id, 24);
    const changed = JSON.stringify(points.length && points[points.length - 1]) !==
      JSON.stringify(this._lastPoint);
    this._points = points;
    this._lastPoint = points.length ? points[points.length - 1] : null;
    if (changed || !this._sparkDone) {
      this._sparkDone = true;
      this._render();
    }
  }

  _render() {
    const hass = this._hass;
    const k = this._kinds || {};
    const lang = (hass.language || "fr").startsWith("fr") ? "fr" : "en";
    const t = (key) => tr(hass, key);
    const hauteur = k.hauteur, debit = k.debit, vigi = k.vigilance;

    if (!hauteur && !debit) {
      this._shell(`<div class="muted">Rivière — entités introuvables</div>`);
      return;
    }

    const vigiState = vigi ? vigi.state : null;
    const crue = ["jaune", "orange", "rouge"].includes(vigiState);
    const vigiColor = crue ? VIGI_COLORS[vigiState] : null;
    const station = (hauteur || debit).attributes.station || "";
    const dateObs = (hauteur || debit).attributes.date_observation;
    const deviceName = this._deviceName();

    if (this._config.compact) {
      const values = [
        hauteur && `${fmt(parseFloat(hauteur.state), 2)} m`,
        debit && `${fmt(parseFloat(debit.state), 2)} m³/s`,
      ].filter(Boolean).join(" · ");
      const temp = k.temperature
        ? ` · ${fmt(parseFloat(k.temperature.state))} °C (${dayLabel(k.temperature.attributes.date_mesure, lang)})`
        : "";
      this._shell(`
        <div class="compact" data-entity="${esc((hauteur || debit).entity_id)}" style="cursor:pointer;">
          <div class="badge-icon" style="background:rgba(33,150,243,.15);color:${vigiColor || "var(--primary-color)"};">
            <ha-icon icon="mdi:waves"></ha-icon>
          </div>
          <div class="titles">
            <div class="title" style="font-size:14px;">${esc(deviceName)} · ${values}</div>
            <div class="subtitle">${cap(t("realtime"))} ${esc(relTime(dateObs, lang))}${temp}</div>
          </div>
          ${crue ? `<span class="pill" style="background:${vigiColor}22;color:${vigiColor};">${esc(vigiState)}</span>` : ""}
        </div>`, crue ? vigiColor : null);
      return;
    }

    // Tuiles temps réel : flèche 24 h de la tendance calculée par l'intégration
    const tiles = [];
    const tendances = hauteur && hauteur.attributes.tendances;
    const fleche24 = tendances && tendances.h24
      ? `<span style="color:${trendColor(tendances.h24)};">${arrowDir(tendances.h24)}</span>`
      : "";
    if (hauteur) tiles.push(this._tile(hauteur, t("level"), "m", 2, fleche24));
    if (debit) {
      const situation = debit.attributes.situation;
      const rapport = debit.attributes.rapport_normale;
      const sub = situation && rapport
        ? `<div style="font-size:11px;margin-top:2px;color:${SIT_COLORS[situation] || "var(--secondary-text-color)"};">
             ${rapport} % ${t("of_normal")} · ${t(`sit_${situation}`)}</div>`
        : "";
      tiles.push(`
        <div class="tile" data-entity="${esc(debit.entity_id)}">
          <div class="label">${t("flow")}</div>
          <div class="value">${fmt(parseFloat(debit.state), 2)} <span class="unit">m³/s</span></div>
          ${sub}
        </div>`);
    }

    const trendRow = opt(this._config, "tendances") ? trendChips(tendances, hass) : "";

    // Sparkline : débit en temps normal, hauteur + prévision en crue
    let spark = "", sparkCaption = "";
    if (opt(this._config, "sparkline") && this._points && this._points.length > 1) {
      let extra = null;
      if (crue && vigi.attributes.prevision) {
        extra = vigi.attributes.prevision
          .map((p) => [new Date(p[0]), p[1]])
          .filter((p) => !isNaN(p[0]) && !isNaN(p[1]));
        if (!extra.length) extra = null;
      }
      const color = vigiColor || "var(--primary-color)";
      spark = sparkline(this._points, extra, color);
      sparkCaption = `
        <div style="display:flex;justify-content:space-between;" class="footer">
          <span>${cap(`${(crue ? t("level") : t("flow")).toLowerCase()} · ${t("observed")}`)}</span>
          ${extra ? `<span>${cap(t("forecast"))}</span>` : ""}
        </div>`;
    }

    // Zone santé : valeurs datées
    const rows = opt(this._config, "sante")
      ? [
          this._healthRow(k.temperature, t("water_temp"), "°C", lang),
          this._healthRow(k.oxygene, t("oxygen"), "mg/L", lang),
          this._healthRow(k.ph, t("ph"), "", lang),
          this._healthRow(k.nitrates_riviere, t("river_nitrates"), "mg/L", lang),
        ].filter(Boolean).join("")
      : "";

    const vigiBadge = crue
      ? `<span class="pill" data-entity="${esc(vigi.entity_id)}"
              style="background:${vigiColor}22;color:${vigiColor};cursor:pointer;">
           <ha-icon icon="mdi:alert-outline" style="--mdc-icon-size:14px;"></ha-icon>
           ${t("vigilance")} ${esc(vigiState)}
         </span>`
      : vigi
        ? `<span title="${t("vigilance")} verte" data-entity="${esc(vigi.entity_id)}"
                style="width:9px;height:9px;border-radius:50%;background:var(--success-color);display:inline-block;cursor:pointer;"></span>`
        : "";

    this._shell(`
      <div class="head">
        <div class="badge-icon" style="background:rgba(33,150,243,.15);color:${vigiColor || "var(--primary-color)"};">
          <ha-icon icon="mdi:waves"></ha-icon>
        </div>
        <div class="titles">
          <div class="title">${esc(deviceName)}</div>
          <div class="subtitle">${esc(station)} · ${t("realtime")} ${esc(relTime(dateObs, lang))}</div>
        </div>
        ${vigiBadge}
      </div>
      <div class="tiles">${tiles.join("")}</div>
      ${trendRow}
      ${spark ? `<div style="margin-top:8px;">${spark}</div>` : ""}
      ${sparkCaption}
      ${rows ? `<div class="rows">${rows}</div>` : ""}`, crue ? vigiColor : null);
  }

  _deviceName() {
    const hass = this._hass;
    const device = (hass.devices || {})[this._config.device];
    return device ? device.name : "Rivière";
  }

  _tile(st, label, unit, digits, arrow) {
    return `
      <div class="tile" data-entity="${esc(st.entity_id)}">
        <div class="label">${esc(label)}</div>
        <div class="value">${fmt(parseFloat(st.state), digits)}
          <span class="unit">${esc(unit)}</span> ${arrow || ""}</div>
      </div>`;
  }

  _healthRow(st, label, unit, lang) {
    if (!st || st.state === "unavailable" || st.state === "unknown") return "";
    const date = st.attributes.date_mesure;
    return `
      <div class="row" data-entity="${esc(st.entity_id)}">
        <span class="label">${esc(label)}</span>
        <span>${fmt(parseFloat(st.state))} ${esc(unit)}
          ${date ? `<span class="chip">${esc(dayLabel(date, lang))}</span>` : ""}</span>
      </div>`;
  }
}

// ────────────────────────────────────────────────────────────────────
// 3. mon-eau-groundwater-card — Nappe phréatique
// ────────────────────────────────────────────────────────────────────

class MonEauGroundwaterCard extends MonEauBaseCard {
  static editorModel = "Nappe phréatique";
  static editorExtras = [
    { name: "sparkline", selector: { boolean: {} } },
    { name: "tendances", selector: { boolean: {} } },
    { name: "remplissage", selector: { boolean: {} } },
  ];

  static getStubConfig(hass) {
    return { device: findDeviceByKind(hass, "profondeur_nappe") };
  }

  set hass(hass) {
    this._hass = hass;
    this._kinds = kindMap(hass, this._config.device);
    this._render();
    this._loadHistory();
  }

  async _loadHistory() {
    const st = (this._kinds || {}).niveau_ngf || (this._kinds || {}).profondeur_nappe;
    if (!st) return;
    const points = await fetchHistory(this._hass, st.entity_id, 30 * 24);
    this._points = points;
    if (!this._sparkDone && points.length > 1) {
      this._sparkDone = true;
      this._render();
    }
  }

  _render() {
    const hass = this._hass;
    const k = this._kinds || {};
    const lang = (hass.language || "fr").startsWith("fr") ? "fr" : "en";
    const t = (key) => tr(hass, key);
    const prof = k.profondeur_nappe, ngf = k.niveau_ngf;

    if (!prof && !ngf) {
      this._shell(`<div class="muted">${t("groundwater")} — entités introuvables</div>`);
      return;
    }

    const attrs = (prof || ngf).attributes;
    const date = attrs.date_mesure;
    const realtime = attrs.temps_reel;
    const meta = `${realtime ? t("realtime") + " " : ""}${relTime(date, lang)}`;
    const deviceName = ((hass.devices || {})[this._config.device] || {}).name || t("groundwater");
    // Tendances calculées par l'intégration sur le niveau NGF : ↗ = la nappe se recharge
    const tendances = attrs.tendances;
    const tendanceRef = tendances && (tendances.j7 || tendances.h24);
    const flecheNappe = tendanceRef
      ? `<span style="color:${trendColor(tendanceRef)};">${arrowDir(tendanceRef)}</span>`
      : "";

    if (this._config.compact) {
      const resume = trendResume(tendances, hass);
      const situationTxt = attrs.situation
        ? ` · <span style="color:${SIT_COLORS[attrs.situation]};">${t(`sit_${attrs.situation}`)}</span>`
        : "";
      this._shell(`
        <div class="compact" data-entity="${esc((prof || ngf).entity_id)}" style="cursor:pointer;">
          <div class="badge-icon" style="background:rgba(33,150,243,.15);color:var(--primary-color);">
            <ha-icon icon="mdi:arrow-collapse-down"></ha-icon>
          </div>
          <div class="titles">
            <div class="title" style="font-size:14px;">${esc(deviceName)}
              ${prof ? `· ${fmt(parseFloat(prof.state), 2)} m` : ""} ${flecheNappe}</div>
            <div class="subtitle">${esc(meta)}${resume ? ` · ${resume}` : ""}${situationTxt}</div>
          </div>
        </div>`);
      return;
    }

    const tiles = [];
    if (prof) tiles.push(`
      <div class="tile" data-entity="${esc(prof.entity_id)}">
        <div class="label">${t("depth")}</div>
        <div class="value">${fmt(parseFloat(prof.state), 2)} <span class="unit">m</span></div>
      </div>`);
    if (ngf) {
      const situation = attrs.situation;
      const ecart = attrs.ecart_normale_m;
      const sub = situation
        ? `<div style="font-size:11px;margin-top:2px;color:${SIT_COLORS[situation] || "var(--secondary-text-color)"};">
             ${ecart >= 0 ? "+" : "−"}${fmt(Math.abs(ecart), 2)} m ${t("vs_normal")} · ${t(`sit_${situation}`)}</div>`
        : "";
      tiles.push(`
        <div class="tile" data-entity="${esc(ngf.entity_id)}">
          <div class="label">${t("ngf")}</div>
          <div class="value">${fmt(parseFloat(ngf.state), 2)} <span class="unit">m</span> ${flecheNappe}</div>
          ${sub}
        </div>`);
    }

    const trendRow = opt(this._config, "tendances") ? trendChips(tendances, hass) : "";

    // Remplissage : position dans la plage historique du piézomètre
    let fillRow = "";
    const remplissage = k.remplissage;
    if (opt(this._config, "remplissage") && remplissage && !isNaN(parseFloat(remplissage.state))) {
      const taux = parseFloat(remplissage.state);
      const couleur = taux < 20 ? "var(--error-color)"
        : taux < 40 ? "var(--warning-color)"
        : "var(--primary-color)";
      fillRow = `
        <div class="row" data-entity="${esc(remplissage.entity_id)}" style="margin-top:8px;">
          <span class="label">${t("fill")}</span>
          <span>${fmt(taux, 0)} % <span class="muted">${t("historical_range")}</span></span>
        </div>
        <div class="bar"><div style="width:${Math.max(2, Math.min(100, taux)).toFixed(0)}%;background:${couleur};"></div></div>`;
    }

    const spark = opt(this._config, "sparkline") && this._points && this._points.length > 1
      ? sparkline(this._points, null, "var(--primary-color)", 300, 44)
      : "";

    this._shell(`
      <div class="head">
        <div class="badge-icon" style="background:rgba(33,150,243,.15);color:var(--primary-color);">
          <ha-icon icon="mdi:arrow-collapse-down"></ha-icon>
        </div>
        <div class="titles">
          <div class="title">${esc(deviceName)}</div>
          <div class="subtitle">${esc(attrs.code_bss || "")} · ${esc(meta)}</div>
        </div>
      </div>
      <div class="tiles">${tiles.join("")}</div>
      ${trendRow}
      ${fillRow}
      ${spark ? `<div style="margin-top:8px;">${spark}</div>` : ""}
      ${spark ? `<div class="footer">${cap(t("days30"))}</div>` : ""}`);
  }
}

// ────────────────────────────────────────────────────────────────────
// 4. mon-eau-drought-card — Sécheresse
// ────────────────────────────────────────────────────────────────────

const GRAVITES = ["vigilance", "alerte", "alerte_renforcee", "crise"];
const GRAVITE_COLORS = {
  vigilance: "#f0d264",
  alerte: "#f0b400",
  alerte_renforcee: "#ef7d00",
  crise: "var(--error-color)",
};

class MonEauDroughtCard extends MonEauBaseCard {
  static editorModel = "Sécheresse";
  static editorExtras = [
    { name: "usages", selector: { boolean: {} } },
    { name: "assecs", selector: { boolean: {} } },
  ];

  static getStubConfig(hass) {
    return { device: findDeviceByKind(hass, "gravite") };
  }

  _render() {
    const hass = this._hass;
    const k = this._kinds || {};
    const lang = (hass.language || "fr").startsWith("fr") ? "fr" : "en";
    const t = (key) => tr(hass, key);
    const grav = k.gravite;

    if (!grav) {
      this._shell(`<div class="muted">${t("drought")} — entité introuvable</div>`);
      return;
    }

    const gravite = grav.state;
    const active = GRAVITES.includes(gravite);
    const index = GRAVITES.indexOf(gravite);
    const color = active ? GRAVITE_COLORS[gravite] : "var(--success-color)";
    const severe = index >= 2;
    const deviceName = ((hass.devices || {})[this._config.device] || {}).name || t("drought");

    if (this._config.compact) {
      const label = active ? cap(t(`gravite_${gravite}`)) : t("no_restriction");
      this._shell(`
        <div class="compact" data-entity="${esc(grav.entity_id)}" style="cursor:pointer;">
          <div class="badge-icon" style="background:${active ? color + "22" : "rgba(76,175,80,.15)"};color:${color};">
            <ha-icon icon="${active ? "mdi:sun-wireless-outline" : "mdi:water-check"}"></ha-icon>
          </div>
          <div class="titles">
            <div class="title" style="font-size:14px;">${esc(deviceName)}</div>
            <div class="subtitle">${esc(label)}</div>
          </div>
        </div>`, severe ? color : null);
      return;
    }

    // Jauge 4 segments, niveau actif surligné
    const segments = GRAVITES.map((g, i) => {
      const on = active && i <= index;
      const current = g === gravite;
      const radius = i === 0 ? "4px 0 0 4px" : i === 3 ? "0 4px 4px 0" : "0";
      return `
        <div style="flex:1;text-align:center;">
          <div style="height:8px;border-radius:${radius};
                      background:${on ? GRAVITE_COLORS[g] : "var(--secondary-background-color)"};
                      ${current ? `outline:2px solid ${GRAVITE_COLORS[g]};outline-offset:1px;` : ""}"></div>
          <div style="margin-top:3px;font-size:10px;
                      color:${current ? GRAVITE_COLORS[g] : "var(--secondary-text-color)"};
                      font-weight:${current ? "500" : "400"};">${cap(t(`gravite_${g}`))}</div>
        </div>`;
    }).join("");

    // Chips par ressource
    const parType = grav.attributes.par_type || {};
    const chips = Object.entries(parType).map(([type, info]) => {
      const c = GRAVITE_COLORS[info.gravite] || "var(--secondary-text-color)";
      return `<span class="pill" style="background:${c}22;color:${c};font-size:11px;padding:3px 8px;">
        ${cap(t(`resource_${type}`))} · ${t(`gravite_${info.gravite}`) || esc(info.gravite)}</span>`;
    }).join(" ");

    // Usages : les interdits d'abord, top 3 + repli
    const usages = opt(this._config, "usages") ? (grav.attributes.usages || []).slice() : [];
    usages.sort((a, b) => this._usageRank(b) - this._usageRank(a));
    const rows = usages.slice(0, 3).map((u) => this._usageRow(u, t)).join("");
    const others = usages.length > 3
      ? `<details><summary>${usages.length - 3} ${t("other_usages")}</summary>
           ${usages.slice(3).map((u) => this._usageRow(u, t)).join("")}</details>`
      : "";

    // Arrêté + ONDE
    const zone = Object.values(parType)[0] || {};
    const arrete = zone.arrete_debut
      ? `${t("decree")} ${dayLabel(zone.arrete_debut, lang)} ${t("to")} ${dayLabel(zone.arrete_fin, lang)}
         ${zone.arrete_pdf ? `· <a href="${esc(zone.arrete_pdf)}" target="_blank" rel="noreferrer">${t("see_pdf")}</a>` : ""}`
      : "";
    const onde = opt(this._config, "assecs") ? grav.attributes.onde : null;
    const assecs = onde && onde.assecs && onde.assecs.length
      ? `<div class="muted" style="margin-top:4px;">${onde.assecs.length} ${t("dry_streams")}
           (${esc(onde.assecs.slice(0, 3).join(", "))}${onde.assecs.length > 3 ? "…" : ""})</div>`
      : "";

    this._shell(`
      <div class="head">
        <div class="badge-icon" style="background:${active ? color + "22" : "rgba(76,175,80,.15)"};color:${color};">
          <ha-icon icon="${active ? "mdi:sun-wireless-outline" : "mdi:water-check"}"></ha-icon>
        </div>
        <div class="titles">
          <div class="title">${esc(deviceName)}</div>
          <div class="subtitle">${esc(zone.zone || "")}</div>
        </div>
      </div>
      ${active
        ? `<div style="display:flex;gap:4px;margin-top:14px;">${segments}</div>
           ${chips ? `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px;">${chips}</div>` : ""}
           ${rows ? `<div class="rows">${rows}${others}</div>` : ""}
           ${arrete ? `<div class="footer" style="text-align:left;margin-top:8px;">${arrete}</div>` : ""}`
        : `<div style="margin:12px 0 4px;">
             <span class="pill" style="background:rgba(76,175,80,.15);color:var(--success-color);cursor:pointer;"
                   data-entity="${esc(grav.entity_id)}">${t("no_restriction")}</span>
           </div>`}
      ${assecs}`, severe ? color : null);
  }

  _usageRank(u) {
    const d = (u.description || "").toLowerCase();
    if (d.startsWith("interdit")) return 2;
    if (d.includes("interdit")) return 1;
    return 0;
  }

  _usageRow(u, t) {
    const d = (u.description || "").toLowerCase();
    let statut = t("allowed"), color = "var(--success-color)";
    if (d.startsWith("interdit")) {
      statut = t("forbidden"); color = "var(--error-color)";
    } else if (d.includes("interdit") || d.includes("sauf") || d.includes("restrei")) {
      statut = t("restricted"); color = "var(--warning-color)";
    }
    return `
      <div class="row" title="${esc(u.description || "")}" style="cursor:default;">
        <span class="label" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:75%;">${esc(u.nom)}</span>
        <span style="color:${color};">${statut}</span>
      </div>`;
  }
}

// ────────────────────────────────────────────────────────────────────
// 5. mon-eau-bathing-card — Baignade (saisonnière, repli automatique)
// ────────────────────────────────────────────────────────────────────

class MonEauBathingCard extends MonEauBaseCard {
  static editorModel = "Baignade";
  static editorExtras = [{ name: "historique", selector: { boolean: {} } }];

  static getStubConfig(hass) {
    return { device: findDeviceByKind(hass, "baignade") };
  }

  _render() {
    const hass = this._hass;
    const k = this._kinds || {};
    const lang = (hass.language || "fr").startsWith("fr") ? "fr" : "en";
    const t = (key) => tr(hass, key);
    const bin = k.baignade, classement = k.classement, controle = k.controle;

    if (!classement && !bin) {
      this._shell(`<div class="muted">${t("bathing")} — entité introuvable</div>`);
      return;
    }

    const cAttrs = classement ? classement.attributes : {};
    const enSaison = cAttrs.en_saison === true;
    const deviceName = ((hass.devices || {})[this._config.device] || {}).name || t("bathing");
    const classementTxt = classement && classement.state !== "unknown" ? classement.state : null;
    const annee = cAttrs.annee_classement;

    // Hors saison (ou compact) : une seule ligne — le repli est piloté par la donnée
    if (!enSaison || this._config.compact) {
      const debut = cAttrs.saison_debut ? dayLabel(cAttrs.saison_debut, lang) : "";
      const info = enSaison
        ? this._statut(k, t).txt
        : `${t("season_closed")}${debut ? ` · ${t("reopen")} ${debut}` : ""}`;
      const status = enSaison ? this._statut(k, t) : null;
      this._shell(`
        <div class="compact" data-entity="${esc((bin || classement).entity_id)}" style="cursor:pointer;">
          <div class="badge-icon" style="background:${status ? status.bg : "var(--secondary-background-color)"};
               color:${status ? status.color : "var(--secondary-text-color)"};">
            <ha-icon icon="mdi:swim"></ha-icon>
          </div>
          <div class="titles">
            <div class="title" style="font-size:14px;${enSaison ? "" : "color:var(--secondary-text-color);"}">
              ${esc(deviceName)}${enSaison ? "" : ` — ${info}`}</div>
            <div class="subtitle">${enSaison
              ? `${esc(info)} · ${esc(relTime((controle || {}).state, lang))}`
              : classementTxt ? `${t("classification")} ${annee || ""} : ${esc(classementTxt)}` : ""}</div>
          </div>
        </div>`);
      return;
    }

    // En saison : carte complète
    const status = this._statut(k, t);
    const ctrlAttrs = controle ? controle.attributes : {};
    const dateCtrl = controle && controle.state !== "unknown" ? controle.state : null;

    const tiles = [];
    if (classementTxt) tiles.push(`
      <div class="tile" data-entity="${esc(classement.entity_id)}">
        <div class="label">${t("classification")} ${annee || ""}</div>
        <div class="value" style="font-size:16px;color:${this._classementColor(classementTxt)};">${esc(classementTxt)}</div>
      </div>`);
    const saisonFin = cAttrs.saison_fin ? dayLabel(cAttrs.saison_fin, lang) : "";
    tiles.push(`
      <div class="tile">
        <div class="label">${t("season")}</div>
        <div class="value" style="font-size:16px;">${dayLabel(cAttrs.saison_debut, lang)} → ${saisonFin}</div>
      </div>`);

    const bars = [
      this._bacterioBar(ctrlAttrs.e_coli, t("ecoli"), controle),
      this._bacterioBar(ctrlAttrs.enterocoques, t("entero"), controle),
    ].filter(Boolean).join("");

    const historique = opt(this._config, "historique")
      ? (ctrlAttrs.controles || []).slice().reverse()
      : [];
    const histo = historique.length > 1
      ? `<details><summary>${t("controls_history")}</summary>
           ${historique.map((c) => `
             <div class="row" style="cursor:default;">
               <span class="label">${esc(dayLabel(c.date, lang))}</span>
               <span style="color:${this._qualiteColor(c.qualite)};">${esc(c.qualite || "")}</span>
             </div>`).join("")}</details>`
      : "";

    this._shell(`
      <div class="head">
        <div class="badge-icon" style="background:${status.bg};color:${status.color};">
          <ha-icon icon="mdi:swim"></ha-icon>
        </div>
        <div class="titles">
          <div class="title">${esc(deviceName)}</div>
          <div class="subtitle">${cap(t("season"))} ${dayLabel(cAttrs.saison_debut, lang)} → ${saisonFin}</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin:12px 0 4px;flex-wrap:wrap;">
        <span class="pill" style="background:${status.bg};color:${status.color};cursor:pointer;"
              data-entity="${esc((bin || classement).entity_id)}">${esc(status.txt)}</span>
        ${dateCtrl ? `<span class="muted">${cap(t("last_control"))} ${esc(relTime(dateCtrl, lang))}</span>` : ""}
      </div>
      ${bars ? `<div style="margin-top:10px;">${bars}</div>` : ""}
      <div class="tiles">${tiles.join("")}</div>
      ${histo}`, status.border);
  }

  _statut(k, t) {
    const bin = k.baignade, controle = k.controle;
    const attrs = bin ? bin.attributes : {};
    const qualite = (attrs.qualite_dernier_controle ||
      (controle ? controle.attributes.qualite : "") || "").toLowerCase();
    if (attrs.interdiction) {
      return { txt: t("bath_forbidden"), color: "var(--error-color)",
               bg: "rgba(244,67,54,.15)", border: "var(--error-color)" };
    }
    if (qualite.startsWith("mauvais")) {
      return { txt: t("bath_bad"), color: "var(--error-color)",
               bg: "rgba(244,67,54,.15)", border: "var(--error-color)" };
    }
    if (qualite.startsWith("moyen")) {
      return { txt: t("bath_warn"), color: "var(--warning-color)",
               bg: "rgba(255,152,0,.15)", border: null };
    }
    return { txt: t("bath_ok"), color: "var(--success-color)",
             bg: "rgba(76,175,80,.15)", border: null };
  }

  _classementColor(txt) {
    const lower = (txt || "").toLowerCase();
    if (lower.startsWith("excellent")) return "var(--success-color)";
    if (lower.startsWith("bon")) return "var(--success-color)";
    if (lower.startsWith("suffisant")) return "var(--warning-color)";
    if (lower.startsWith("insuffisant")) return "var(--error-color)";
    return "var(--primary-text-color)";
  }

  _qualiteColor(qualite) {
    const lower = (qualite || "").toLowerCase();
    if (lower.startsWith("mauvais")) return "var(--error-color)";
    if (lower.startsWith("moyen")) return "var(--warning-color)";
    return "var(--success-color)";
  }

  _bacterioBar(mesure, label, controle) {
    if (!mesure || mesure.valeur === null || mesure.valeur === undefined) return "";
    const seuil1 = mesure.seuil_bon_moyen, seuil2 = mesure.seuil_moyen_mauvais;
    if (!seuil2) return "";
    const pct = Math.min(100, (mesure.valeur / seuil2) * 100);
    let color = "var(--success-color)";
    if (mesure.valeur >= seuil2) color = "var(--error-color)";
    else if (seuil1 && mesure.valeur >= seuil1) color = "var(--warning-color)";
    return `
      <div class="row" ${controle ? `data-entity="${esc(controle.entity_id)}"` : ""}>
        <span class="label">${esc(label)}</span>
        <span>${esc(mesure.texte || String(mesure.valeur))}
          <span class="muted">/ ${seuil2} /100mL</span></span>
      </div>
      <div class="bar"><div style="width:${Math.max(2, pct).toFixed(0)}%;background:${color};"></div></div>`;
  }
}

// ────────────────────────────────────────────────────────────────────
// Enregistrement
// ────────────────────────────────────────────────────────────────────

customElements.define("mon-eau-card-editor", MonEauCardEditor);
customElements.define("mon-eau-water-card", MonEauWaterCard);
customElements.define("mon-eau-river-card", MonEauRiverCard);
customElements.define("mon-eau-groundwater-card", MonEauGroundwaterCard);
customElements.define("mon-eau-drought-card", MonEauDroughtCard);
customElements.define("mon-eau-bathing-card", MonEauBathingCard);

window.customCards = window.customCards || [];
window.customCards.push(
  {
    type: "mon-eau-water-card",
    name: "Mon Eau — Eau du robinet",
    description: "Conformité ARS, nitrates, pesticides, bactériologie.",
    preview: true,
  },
  {
    type: "mon-eau-river-card",
    name: "Mon Eau — Rivière",
    description: "Hauteur et débit temps réel, vigilance crues, santé de la rivière.",
    preview: true,
  },
  {
    type: "mon-eau-groundwater-card",
    name: "Mon Eau — Nappe phréatique",
    description: "Niveau piézométrique et tendance 30 jours.",
    preview: true,
  },
  {
    type: "mon-eau-drought-card",
    name: "Mon Eau — Sécheresse",
    description: "Niveau de restriction VigiEau, usages, assecs.",
    preview: true,
  },
  {
    type: "mon-eau-bathing-card",
    name: "Mon Eau — Baignade",
    description: "Qualité du site de baignade ARS, saisonnière à repli automatique.",
    preview: true,
  }
);

console.info(
  `%c MON EAU %c cartes v${ME_VERSION} `,
  "background:#185fa5;color:#fff;border-radius:3px 0 0 3px;padding:2px 0;",
  "background:#e6f1fb;color:#185fa5;border-radius:0 3px 3px 0;padding:2px 0;"
);
