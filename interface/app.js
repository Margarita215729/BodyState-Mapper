/* BodyState Mapper / THSI research-grade local dashboard.
   Plain vanilla JS. No frameworks, no external assets, no backend.

   CORE RULE: This is NOT a diagnostic system. No diagnoses are ever produced.
   Every output is a traceable hidden-state hypothesis with explicit uncertainty,
   missing-data notes, guardrails, and next-best measurements. Language is limited
   to: "compatible with", "may support", "hypothesis", "uncertain",
   "requires context", "not proven". */

"use strict";

const GRAPH_URL = "../outputs/astronaut_data_mapping_v1_0/integrated_evidence_graph_v1_0.json";

const CORE_GUARDRAILS = [
  "single_marker_never_equals_mechanism",
  "medication_timing_first",
  "unknown_is_not_negative_evidence",
  "symptom_report_never_equals_mechanism",
  "context_override_before_mechanism",
];

/* The mandatory safety line. Kept verbatim: "This is not a diagnosis." */
const NOT_A_DIAGNOSIS_LINE =
  "This is not a diagnosis. Outputs are traceable hidden-state hypotheses with uncertainty, missing data, guardrails, and next-best measurements.";

/* The ten report sections (Part 5). Section titles are also checked by the smoke test. */
const REPORT_SECTIONS = [
  "Plain-language summary",
  "Top candidate hidden states",
  "Evidence cards",
  "Activated graph",
  "What this does NOT prove",
  "Missing data",
  "Next best measurements",
  "Guardrails applied",
  "Traceable chains",
  "Source traceability",
];

/* ------------------------------------------------------------------ */
/* Expanded data-intake schema (Part 2). 5 collapsible sections.       */
/* Each field uses { key, label, options } — option[0] is the default  */
/* uninformative value. Field count is verified by the smoke test.     */
/* ------------------------------------------------------------------ */
const INTAKE_SECTIONS = [
  {
    id: "wearable",
    title: "A · Wearable / physiology",
    domain: "wearable",
    open: true,
    fields: [
      { key: "rhr", label: "Resting heart rate deviation", options: ["unknown", "normal", "increased", "decreased"] },
      { key: "hrv", label: "HRV deviation", options: ["unknown", "normal", "increased", "decreased"] },
      { key: "sleep_duration", label: "Sleep duration", options: ["unknown", "normal", "short", "long"] },
      { key: "sleep_frag", label: "Sleep fragmentation / WASO", options: ["unknown", "normal", "increased"] },
      { key: "activity", label: "Activity level", options: ["unknown", "normal", "low", "high"] },
      { key: "temp", label: "Skin / body temperature", options: ["unknown", "normal", "elevated", "low"] },
      { key: "spo2", label: "SpO2", options: ["unknown", "normal", "low"] },
      { key: "resp_rate", label: "Respiratory rate", options: ["unknown", "normal", "increased", "decreased"] },
    ],
  },
  {
    id: "symptoms",
    title: "B · Symptoms (self-report)",
    domain: "symptom",
    open: true,
    fields: [
      { key: "fatigue", label: "Fatigue", options: ["none", "mild", "moderate", "severe"] },
      { key: "sleepiness", label: "Sleepiness", options: ["none", "mild", "moderate", "severe"] },
      { key: "brain_fog", label: "Brain fog", options: ["none", "mild", "moderate", "severe"] },
      { key: "dizziness", label: "Dizziness", options: ["none", "mild", "moderate", "severe"] },
      { key: "pain", label: "Pain", options: ["none", "mild", "moderate", "severe"] },
      { key: "headache", label: "Headache", options: ["none", "mild", "moderate", "severe"] },
      { key: "gi", label: "GI symptoms", options: ["none", "mild", "moderate", "severe"] },
      { key: "anxiety_arousal", label: "Anxiety-like arousal", options: ["none", "mild", "moderate", "severe"] },
      { key: "mood", label: "Mood worsening", options: ["none", "mild", "moderate", "severe"] },
    ],
  },
  {
    id: "context",
    title: "C · Context",
    domain: "context",
    open: false,
    fields: [
      { key: "med_change", label: "Medication change", options: ["unknown", "no", "yes"] },
      { key: "sedative", label: "Sedative / opioid / tramadol exposure", options: ["unknown", "no", "yes"] },
      { key: "caffeine", label: "Caffeine / stimulant", options: ["unknown", "no", "yes"] },
      { key: "exertion", label: "Recent exertion", options: ["unknown", "no", "mild", "heavy"] },
      { key: "fluid", label: "Poor fluid intake", options: ["unknown", "no", "yes"] },
      { key: "illness", label: "Recent illness symptoms", options: ["unknown", "no", "yes"] },
      { key: "injury", label: "Recent injury / procedure", options: ["unknown", "no", "yes"] },
      { key: "heat", label: "Heat exposure", options: ["unknown", "no", "yes"] },
      { key: "co2", label: "High CO2 / poor ventilation", options: ["unknown", "no", "yes"] },
      { key: "noise", label: "Noise / light disruption", options: ["unknown", "no", "yes"] },
      { key: "menstrual", label: "Menstrual / hormonal context", options: ["unknown", "no", "yes"] },
    ],
  },
  {
    id: "labs",
    title: "D · Labs / biofluids",
    domain: "labs",
    open: false,
    fields: [
      { key: "cbc_crp", label: "CBC / CRP", options: ["unavailable", "normal", "abnormal"] },
      { key: "iron", label: "Hemoglobin / ferritin / TSAT", options: ["unavailable", "normal", "low"] },
      { key: "b12", label: "B12 / MMA / folate", options: ["unavailable", "normal", "abnormal"] },
      { key: "thyroid", label: "Thyroid panel", options: ["unavailable", "normal", "abnormal"] },
      { key: "glucose", label: "Glucose / insulin / metabolic", options: ["unavailable", "normal", "abnormal"] },
      { key: "urine_hydration", label: "Urine hydration markers", options: ["unavailable", "normal", "concentrated"] },
      { key: "stool_gi", label: "Stool / GI inflammation", options: ["unavailable", "normal", "abnormal"] },
      { key: "cortisol", label: "Saliva cortisol rhythm", options: ["unavailable", "normal", "flattened"] },
    ],
  },
  {
    id: "functional",
    title: "E · Functional / objective",
    domain: "functional",
    open: false,
    fields: [
      { key: "orthostatic", label: "Orthostatic HR / BP", options: ["unavailable", "normal", "abnormal"] },
      { key: "pvt", label: "PVT / reaction time", options: ["unavailable", "normal", "impaired"] },
      { key: "cpet", label: "CPET / exercise response", options: ["unavailable", "normal", "impaired"] },
      { key: "day2_decline", label: "Day-2 post-exertion decline", options: ["unavailable", "no", "yes"] },
      { key: "grip", label: "Grip strength / functional mobility", options: ["unavailable", "normal", "impaired"] },
      { key: "psg", label: "PSG / EEG sleep architecture", options: ["unavailable", "normal", "fragmented", "low_N3", "high_AHI"] },
    ],
  },
];

/* Map every field key to its domain (used for confidence governance). */
const FIELD_DOMAIN = {};
const FIELD_LABEL = {};
for (const sec of INTAKE_SECTIONS) {
  for (const f of sec.fields) { FIELD_DOMAIN[f.key] = sec.domain; FIELD_LABEL[f.key] = f.label; }
}
const INTAKE_DEFAULTS = {};
for (const sec of INTAKE_SECTIONS) for (const f of sec.fields) INTAKE_DEFAULTS[f.key] = f.options[0];

/* Values that carry no positive deviation (do not by themselves fire a hypothesis). */
const NONINFORMATIVE = new Set(["unknown", "unavailable", "no", "none", "normal"]);

/* Maps a specific (field, value) to an existing measured_parameter node id in the graph.
   Only mappings that anchor to a real graph node are listed; missing ones are skipped
   gracefully. Verified against the loaded graph at runtime. */
const SIGNAL_PARAM_NODE = {
  "rhr=increased": "elevated_heart_rate_relative_to_baseline",
  "rhr=decreased": "reduced_heart_rate_variability",
  "hrv=decreased": "reduced_hrv_relative_to_baseline",
  "hrv=increased": "higher_resting_vagally_mediated_hrv",
  "sleep_frag=increased": "insufficient_or_disrupted_sleep",
  "sleep_duration=short": "acute_sleep_deprivation",
  "temp=elevated": "core_body_temperature",
  "spo2=low": "spo2_rest_sleep_exercise",
  "resp_rate=increased": "respiratory_rate",
  "dizziness=mild": "orthostatic_dizziness",
  "dizziness=moderate": "orthostatic_dizziness",
  "dizziness=severe": "orthostatic_dizziness",
  "urine_hydration=concentrated": "urine_hydration_markers",
  "urine_hydration=unavailable": "urine_hydration_markers",
  "iron=low": "low_ferritin",
  "b12=abnormal": "b12_folate_functional_panel",
  "thyroid=abnormal": "thyroid_hormones",
  "cbc_crp=abnormal": "elevated_crp",
  "glucose=abnormal": "glucose_variability",
  "cortisol=flattened": "flattened_diurnal_cortisol_slope",
  "stool_gi=abnormal": "fecal_calprotectin_lactoferrin",
  "orthostatic=abnormal": "orthostatic_hr_bp",
  "pvt=impaired": "reaction_time_slowing",
  "cpet=impaired": "exercise_tolerance",
  "psg=fragmented": "psg_eeg_sleep_architecture_gap",
  "psg=low_N3": "n3_slow_wave_sleep_eeg",
  "psg=high_AHI": "sleep_disordered_breathing_psg",
};

/* Seven coherent rule-based demo templates (Part 2). Each is a coherent profile,
   not random noise; only the listed fields deviate, the rest stay at defaults. */
const DEMO_PROFILES = [
  {
    name: "Low recovery / sleep fragmentation",
    set: { rhr: "increased", hrv: "decreased", sleep_frag: "increased", sleep_duration: "short",
      fatigue: "moderate", sleepiness: "moderate", brain_fog: "mild", activity: "low",
      med_change: "no", exertion: "mild" },
  },
  {
    name: "Orthostatic / dehydration uncertainty",
    set: { dizziness: "moderate", rhr: "increased", fluid: "yes", urine_hydration: "unavailable",
      orthostatic: "unavailable", fatigue: "mild", med_change: "no" },
  },
  {
    name: "Pain – sleep – fatigue",
    set: { pain: "severe", sleep_frag: "increased", fatigue: "moderate", sleepiness: "mild",
      injury: "yes", med_change: "no", sedative: "no" },
  },
  {
    name: "Medication override",
    set: { med_change: "yes", sedative: "yes", fatigue: "moderate", sleepiness: "moderate",
      brain_fog: "moderate", hrv: "decreased" },
  },
  {
    name: "Inflammatory-load uncertainty",
    set: { temp: "elevated", fatigue: "moderate", mood: "mild", illness: "yes",
      cbc_crp: "unavailable", med_change: "no" },
  },
  {
    name: "Migraine / headache",
    set: { headache: "severe", pain: "severe", gi: "moderate", noise: "yes",
      brain_fog: "moderate", med_change: "no" },
  },
  {
    name: "Sparse missing-data",
    set: { fatigue: "mild" },
  },
];

/* ------------------------------------------------------------------ */
/* Candidate rules (Part 3). Each rule fires on the input vector and   */
/* returns a partial candidate; null means it did not fire. The shared */
/* post-processor then resolves graph nodes, confidence, paths, etc.   */
/* `cap` is the maximum confidence the rule itself permits.            */
/* ------------------------------------------------------------------ */
const sym = (x) => ["mild", "moderate", "severe"].includes(x);
const modSevere = (x) => ["moderate", "severe"].includes(x);

const RULES = [
  {
    id: "low_recovery_state", cap: "moderate",
    fire: (v) => v.rhr === "increased" && v.hrv === "decreased" && modSevere(v.fatigue),
    build: (v) => ({
      signals: ["rhr", "hrv", "fatigue"],
      missing_data: ["Multi-day within-person baseline trend", "Sleep-quality confirmation"],
      not_proven: ["Does not prove overtraining or illness; it is a recovery-status hypothesis."],
      guardrail_hint: [],
    }),
  },
  {
    id: "sleep_fragmentation_recovery_failure", cap: "low",
    fire: (v) => v.sleep_frag === "increased" && (sym(v.fatigue) || sym(v.sleepiness) || sym(v.brain_fog)),
    build: (v) => ({
      signals: ["sleep_frag", sym(v.fatigue) ? "fatigue" : (sym(v.sleepiness) ? "sleepiness" : "brain_fog")],
      missing_data: ["PSG confirmation (wearable sleep staging is not PSG)", "Multi-night trend"],
      not_proven: ["Wearable sleep staging cannot confirm sleep architecture; not a sleep-disorder conclusion."],
      guardrail_hint: ["wearable_sleep_stage_not_PSG"],
    }),
  },
  {
    id: "acute_sleep_loss", cap: "low",
    fire: (v) => v.sleep_duration === "short" && v.sleepiness !== "none" && (v.pvt === "impaired" || v.brain_fog !== "none"),
    build: (v) => ({
      signals: ["sleep_duration", "sleepiness"].concat(v.pvt === "impaired" ? ["pvt"] : ["brain_fog"]),
      capOverride: v.pvt === "impaired" ? "moderate" : "low",
      missing_data: ["Objective sleep-duration confirmation", "Prior-night context"],
      not_proven: ["Subjective symptoms alone cannot establish a mechanism."],
      guardrail_hint: [],
    }),
  },
  {
    id: "orthostatic_intolerance", cap: "moderate",
    fire: (v) => v.dizziness !== "none" && v.orthostatic === "abnormal",
    build: (v) => ({
      signals: ["dizziness", "orthostatic"],
      missing_data: ["Repeat orthostatic HR/BP", "Symptom timing on standing"],
      not_proven: ["Compatible with orthostatic intolerance; symptoms alone cannot confirm it."],
      guardrail_hint: [],
    }),
  },
  {
    id: "hypovolemia_dehydration_hypothesis", cap: "moderate",
    fire: (v) => v.dizziness !== "none" && v.fluid === "yes" &&
      (v.urine_hydration === "concentrated" || v.urine_hydration === "unavailable") && v.rhr === "increased",
    build: (v) => ({
      signals: ["dizziness", "fluid", "rhr"].concat(v.urine_hydration === "concentrated" ? ["urine_hydration"] : []),
      capOverride: v.urine_hydration === "unavailable" ? "low" : "moderate",
      missing_data: ["Direct hydration status (urine osmolality / plasma volume)", "Orthostatic vitals"],
      not_proven: ["Fluid intake is not hydration status; remains uncertain without direct hydration markers."],
      guardrail_hint: ["hydration_intake_not_hydration_status"],
    }),
  },
  {
    id: "hyperventilation_hypocapnia_state", cap: "low",
    fire: (v) => (v.resp_rate === "increased" || v.spo2 === "low") && (v.brain_fog !== "none" || v.fatigue !== "none"),
    build: (v) => ({
      signals: [v.resp_rate === "increased" ? "resp_rate" : "spo2", v.brain_fog !== "none" ? "brain_fog" : "fatigue"],
      missing_data: ["Capnography / end-tidal CO2", "Respiratory rate trend", "SpO2 during rest and exertion"],
      not_proven: ["A respiratory / gas-exchange uncertainty branch; not a confirmed respiratory mechanism."],
      guardrail_hint: [],
    }),
  },
  {
    id: "heat_strain", cap: "moderate",
    fire: (v) => v.heat === "yes" && v.temp === "elevated" && (v.fatigue !== "none" || v.brain_fog !== "none"),
    build: (v) => ({
      signals: ["heat", "temp", v.fatigue !== "none" ? "fatigue" : "brain_fog"],
      missing_data: ["Core temperature trend", "Environmental temperature/humidity logs"],
      not_proven: ["Environmental heat exposure must be separated from a physiologic effect."],
      guardrail_hint: ["environmental_exposure_separate_from_physiologic_effect"],
    }),
  },
  {
    id: "environmental_CO2_performance_risk", cap: "moderate",
    fire: (v) => v.co2 === "yes" && (v.headache !== "none" || v.brain_fog !== "none"),
    build: (v) => ({
      signals: ["co2"].concat(v.headache !== "none" ? ["headache"] : []).concat(v.brain_fog !== "none" ? ["brain_fog"] : []),
      capOverride: (v.headache !== "none" && v.brain_fog !== "none") ? "moderate" : "low",
      missing_data: ["Habitat CO2 / ventilation logs", "Exposure timing relative to symptoms"],
      not_proven: ["Environmental exposure must be separated from a physiologic effect; not a conclusion."],
      guardrail_hint: ["environmental_exposure_separate_from_physiologic_effect"],
    }),
  },
  {
    id: "infectious_or_inflammatory_load", cap: "low",
    fire: (v) => v.cbc_crp === "abnormal" && v.fatigue !== "none" && (v.temp === "elevated" || v.illness === "yes"),
    build: (v) => ({
      signals: ["cbc_crp", "fatigue"].concat(v.temp === "elevated" ? ["temp"] : ["illness"]),
      missing_data: ["Repeat CRP / CBC trend", "Infection symptom screen"],
      not_proven: ["An immune/inflammatory marker is not a confirmed infection without symptoms and biomarkers."],
      guardrail_hint: ["immune_marker_not_infection_without_symptoms"],
    }),
  },
  {
    id: "inflammatory_sickness_behavior", cap: "low",
    fire: (v) => v.fatigue !== "none" && v.mood !== "none" && v.cbc_crp === "unavailable",
    build: (v) => ({
      signals: ["fatigue", "mood"],
      missing_data: ["CBC / CRP (currently unavailable)", "Symptom trajectory over time"],
      not_proven: ["Low/uncertain only: an inflammatory sickness-behavior pattern is not a confirmed inflammatory state."],
      guardrail_hint: ["immune_marker_not_infection_without_symptoms"],
    }),
  },
  {
    id: "iron_deficiency_oxygen_delivery_branch", cap: "moderate",
    fire: (v) => v.iron === "low" && v.fatigue !== "none",
    build: (v) => ({
      signals: ["iron", "fatigue"],
      missing_data: ["CBC for anemia", "Reticulocyte / full iron studies"],
      not_proven: ["Low iron markers support an iron-related hypothesis but do not by themselves prove anemia or its cause."],
      guardrail_hint: [],
    }),
  },
  {
    id: "functional_B12_deficiency", cap: "low",
    fire: (v) => v.b12 === "abnormal" && (v.brain_fog !== "none" || v.fatigue !== "none"),
    build: (v) => ({
      signals: ["b12"].concat(v.brain_fog !== "none" ? ["brain_fog"] : ["fatigue"]),
      missing_data: ["MMA / homocysteine confirmation", "Repeat B12 / folate"],
      not_proven: ["An abnormal B12 / MMA value is contextual; not a standalone conclusion."],
      guardrail_hint: [],
    }),
  },
  {
    id: "thyroid_dysfunction_context", cap: "low",
    fire: (v) => v.thyroid === "abnormal" && (v.fatigue !== "none" || v.mood !== "none"),
    build: (v) => ({
      signals: ["thyroid"].concat(v.fatigue !== "none" ? ["fatigue"] : ["mood"]),
      missing_data: ["Repeat thyroid panel (TSH, free T4/T3)", "Clinical correlation"],
      not_proven: ["An abnormal thyroid value is contextual; not a standalone conclusion."],
      guardrail_hint: [],
    }),
  },
  {
    id: "pain_sleep_fatigue_branch", cap: "moderate",
    fire: (v) => modSevere(v.pain) && (v.sleep_frag === "increased" || modSevere(v.fatigue)),
    build: (v) => ({
      signals: ["pain"].concat(v.sleep_frag === "increased" ? ["sleep_frag"] : ["fatigue"]),
      missing_data: ["Temporal pain–sleep–fatigue sequence", "Analgesic timing context"],
      not_proven: ["Pain-limited performance is not muscle weakness; this is a traceable branch, not a conclusion."],
      guardrail_hint: ["pain_limited_performance_not_muscle_weakness"],
    }),
  },
  {
    id: "migraine_phenotype_branch", cap: "moderate",
    fire: (v) => v.headache !== "none" && (v.pain === "severe" || v.headache === "severe") && (v.gi !== "none" || v.noise === "yes"),
    build: (v) => ({
      signals: ["headache"].concat(v.gi !== "none" ? ["gi"] : []).concat(v.noise === "yes" ? ["noise"] : []),
      missing_data: ["Headache diary (frequency, aura, triggers)", "Sensory-sensitivity context"],
      not_proven: ["Possible migraine phenotype; a headache pattern is not a confirmed neurological conclusion."],
      guardrail_hint: [],
    }),
  },
  {
    id: "medication_context_override", cap: "moderate",
    fire: (v) => v.med_change === "yes" || v.sedative === "yes",
    build: (v) => ({
      signals: [].concat(v.med_change === "yes" ? ["med_change"] : []).concat(v.sedative === "yes" ? ["sedative"] : []),
      missing_data: ["Medication name, dose, and timing relative to signals"],
      not_proven: ["A medication / context effect must be evaluated before any mechanism inference."],
      guardrail_hint: ["context_override_before_mechanism", "medication_timing_first"],
      alwaysContext: true,
    }),
  },
  {
    id: "PEM_objective_branch", cap: "moderate",
    fire: (v) => v.exertion === "heavy" && (v.day2_decline === "yes" || v.cpet === "impaired" || modSevere(v.fatigue)),
    build: (v) => {
      const objective = v.day2_decline === "yes" || v.cpet === "impaired";
      return {
        signals: ["exertion"].concat(v.day2_decline === "yes" ? ["day2_decline"] : []).concat(v.cpet === "impaired" ? ["cpet"] : []).concat(modSevere(v.fatigue) ? ["fatigue"] : []),
        capOverride: objective ? "moderate" : "low",
        missing_data: objective ? ["Repeat 2-day CPET", "Standardized post-exertion symptom log"] : ["2-day CPET", "Day-2 post-exertion objective decline measurement"],
        not_proven: objective
          ? ["Post-exertional malaise is a specific delayed worsening; objective support raises but does not confirm it."]
          : ["Without objective day-2 decline this remains a low-confidence PEM hypothesis, distinct from normal fatigue."],
        guardrail_hint: ["PEM_not_normal_fatigue"],
      };
    },
  },
  {
    id: "deconditioning", cap: "moderate",
    fire: (v) => v.activity === "low" && (v.grip === "impaired" || v.cpet === "impaired"),
    build: (v) => ({
      signals: ["activity"].concat(v.grip === "impaired" ? ["grip"] : []).concat(v.cpet === "impaired" ? ["cpet"] : []),
      missing_data: ["Standardized functional capacity (e.g. CPET, grip dynamometry)", "Activity trend over weeks"],
      not_proven: ["Low activity is not fatigue and not a mechanism by itself; compatible with deconditioning."],
      guardrail_hint: ["low_activity_not_fatigue"],
    }),
  },
  {
    id: "low_energy_availability", cap: "low",
    fire: (v) => v.glucose === "abnormal" && (v.exertion === "mild" || v.exertion === "heavy" || v.fluid === "yes"),
    build: (v) => ({
      signals: ["glucose"].concat((v.exertion === "mild" || v.exertion === "heavy") ? ["exertion"] : ["fluid"]),
      missing_data: ["Energy availability / intake assessment", "Nitrogen balance / metabolic panel"],
      not_proven: ["A metabolic deviation with energy demand is compatible with low energy availability; not proven."],
      guardrail_hint: [],
    }),
  },
  {
    id: "sleep_architecture_recovery", cap: "moderate",
    fire: (v) => (v.psg === "fragmented" || v.psg === "low_N3") && (v.fatigue !== "none" || v.brain_fog !== "none"),
    stateId: "sleep_fragmentation_recovery_failure",
    build: (v) => ({
      signals: ["psg"].concat(v.fatigue !== "none" ? ["fatigue"] : ["brain_fog"]),
      missing_data: ["Repeat PSG / EEG", "Sleep architecture trend"],
      not_proven: ["Abnormal sleep architecture supports a recovery-failure hypothesis; not a sleep-disorder conclusion."],
      guardrail_hint: ["wearable_sleep_stage_not_PSG"],
    }),
  },
  {
    id: "sleep_disordered_breathing_branch", cap: "moderate",
    fire: (v) => v.psg === "high_AHI" && (v.fatigue !== "none" || v.brain_fog !== "none" || v.sleepiness !== "none"),
    pseudo: true,
    pseudoLabel: "Sleep-disordered breathing branch",
    build: (v) => ({
      signals: ["psg"].concat(v.sleepiness !== "none" ? ["sleepiness"] : (v.fatigue !== "none" ? ["fatigue"] : ["brain_fog"])),
      param_extra: ["sleep_disordered_breathing_psg"],
      missing_data: ["Full polysomnography with AHI scoring", "Daytime sleepiness assessment"],
      not_proven: ["High AHI on PSG is compatible with sleep-disordered breathing; requires clinical sleep evaluation. Not a conclusion."],
      guardrail_hint: ["wearable_sleep_stage_not_PSG"],
    }),
  },
];

/* ------------------------------------------------------------------ */
/* App state                                                           */
/* ------------------------------------------------------------------ */
const state = {
  graph: null,
  nodeById: new Map(),
  outgoing: new Map(),
  incoming: new Map(),
  emPage: 0,
  emPageSize: 25,
  paramPage: 0,
  paramPageSize: 25,
  lastReport: null,
  graphView: { scale: 1, vb: null, base: null },
  selectedGraphId: null,
  traceRows: null,
};

/* ---------------- utilities ---------------- */
function $(sel, root = document) { return root.querySelector(sel); }
function $all(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }
const SVGNS = "http://www.w3.org/2000/svg";
function svgEl(tag, attrs = {}) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, val] of Object.entries(attrs)) el.setAttribute(k, val);
  return el;
}
function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function confClass(conf) { return "c-" + (conf || "unknown"); }
function pipeClass(p) { return "p-" + (p || "needs_review"); }
function uniqueSorted(arr) { return Array.from(new Set(arr.filter(Boolean))).sort(); }
const CONF_RANK = { insufficient: 0, low: 1, moderate: 2, high: 3 };
function minConf(a, b) { return CONF_RANK[a] <= CONF_RANK[b] ? a : b; }

/* ---------------- load + index ---------------- */
async function loadGraph() {
  let resp;
  try {
    resp = await fetch(GRAPH_URL, { cache: "no-store" });
  } catch (err) {
    return showLoadError("Network/fetch error: " + err.message);
  }
  if (!resp.ok) return showLoadError("HTTP " + resp.status + " fetching " + GRAPH_URL);
  let data;
  try {
    data = await resp.json();
  } catch (err) {
    return showLoadError("JSON parse error: " + err.message);
  }
  state.graph = data;
  buildIndices();
  $("#loading").classList.add("hidden");
  $("#tab-workflow").hidden = false;
  initFilters();
  attachTabs();
  buildIntakeForm();
  attachIntakeActions();
  attachGraphControls();
  attachEvidenceMap();
  attachHiddenStates();
  attachParameters();
  attachGuardrails();
  renderCorpus();
  attachTraceability();
  renderGraphLegend();
  const m = data.metadata || {};
  $("#footer-status").textContent =
    `${data.stats.node_count} nodes · ${data.stats.edge_count} edges · graph ${m.version || ""} · built ${(m.build_timestamp || "").slice(0, 19)}`;
  $("#intake-meta").textContent =
    `${INTAKE_SECTIONS.reduce((a, s) => a + s.fields.length, 0)} input fields · ${RULES.length} candidate rules · ${data.stats.node_count}-node graph`;
}

function buildIndices() {
  const { nodes, edges } = state.graph;
  for (const n of nodes) state.nodeById.set(n.id, n);
  for (const n of nodes) { state.outgoing.set(n.id, []); state.incoming.set(n.id, []); }
  for (const e of edges) {
    if (state.outgoing.has(e.source)) state.outgoing.get(e.source).push(e);
    if (state.incoming.has(e.target)) state.incoming.get(e.target).push(e);
  }
}

function showLoadError(detail) {
  $("#loading").classList.add("hidden");
  $("#load-error").classList.remove("hidden");
  $("#error-detail").textContent = detail || "";
}

/* ---------------- tabs ---------------- */
const TAB_PANELS = {
  workflow: "#tab-workflow", "evidence-map": "#tab-evidence-map", "hidden-states": "#tab-hidden-states",
  parameters: "#tab-parameters", guardrails: "#tab-guardrails", corpus: "#tab-corpus", traceability: "#tab-traceability",
};
function attachTabs() {
  $all(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => activateTab(btn.dataset.tab));
  });
}
function activateTab(tab) {
  $all(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
  Object.values(TAB_PANELS).forEach((sel) => { $(sel).hidden = true; });
  $(TAB_PANELS[tab]).hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ---------------- filter population ---------------- */
function initFilters() {
  const nodes = state.graph.nodes;
  fillSelect("#em-filter-type", uniqueSorted(nodes.map((n) => n.type)));
  fillSelect("#em-filter-domain", uniqueSorted(nodes.map((n) => n.domain)));
  fillSelect("#em-filter-confidence", uniqueSorted(nodes.map((n) => n.confidence)));
  fillSelect("#em-filter-evidence", uniqueSorted(nodes.map((n) => n.evidence_strength)));
  fillSelect("#em-filter-pipeline", uniqueSorted(nodes.map((n) => n.pipeline_status)));

  const hs = nodes.filter((n) => n.type === "hidden_state");
  fillSelect("#hs-filter-confidence", uniqueSorted(hs.map((n) => n.confidence)));
  fillSelect("#hs-filter-domain", uniqueSorted(hs.flatMap((n) => (n.metadata.domains || [n.domain]))));

  const params = nodes.filter((n) => n.type === "measured_parameter");
  fillSelect("#param-filter-domain", uniqueSorted(params.map((n) => n.domain)));
  fillSelect("#param-filter-tree", uniqueSorted(params.flatMap((n) => n.source_tree_ids)));
  fillSelect("#param-filter-evidence", uniqueSorted(params.map((n) => n.evidence_strength)));
}
function fillSelect(sel, values) {
  const node = $(sel);
  for (const v of values) {
    if (!v) continue;
    const opt = document.createElement("option");
    opt.value = v; opt.textContent = v;
    node.appendChild(opt);
  }
}

/* ================================================================== */
/* STEP 1 — Data intake form                                           */
/* ================================================================== */
function buildIntakeForm() {
  const form = $("#intake-form");
  form.innerHTML = "";
  for (const sec of INTAKE_SECTIONS) {
    const details = document.createElement("details");
    details.className = "intake-section";
    if (sec.open) details.open = true;
    const grid = sec.fields.map((f) => {
      const opts = f.options.map((o) => `<option value="${esc(o)}">${esc(o)}</option>`).join("");
      return `<div class="field"><label for="f_${f.key}">${esc(f.label)}</label>` +
        `<select id="f_${f.key}" name="${f.key}" data-domain="${sec.domain}">${opts}</select></div>`;
    }).join("");
    details.innerHTML =
      `<summary>${esc(sec.title)}<span class="sec-count">${sec.fields.length} fields</span></summary>` +
      `<div class="form-grid">${grid}</div>`;
    form.appendChild(details);
  }
  $all("#intake-form select").forEach((s) => {
    s.addEventListener("change", () => s.classList.toggle("set", !NONINFORMATIVE.has(s.value)));
  });
}

function attachIntakeActions() {
  $("#btn-generate").addEventListener("click", generateReport);
  $("#btn-clear").addEventListener("click", clearIntake);
  $("#btn-demo-random").addEventListener("click", fillRandomDemo);
}

function readIntake() {
  const v = Object.assign({}, INTAKE_DEFAULTS);
  $all("#intake-form select").forEach((s) => { v[s.name] = s.value; });
  return v;
}

function clearIntake() {
  $all("#intake-form select").forEach((s) => {
    s.value = INTAKE_DEFAULTS[s.name];
    s.classList.remove("set");
  });
  state.lastReport = null;
  $("#report-output").innerHTML = `<p class="placeholder">Fill in observations above and select <strong>Generate report</strong>. Every output below will be a traceable hypothesis with explicit uncertainty &mdash; never a diagnosis.</p>`;
  $("#measurements-output").innerHTML = `<p class="placeholder">Next-best measurements appear here after a report is generated.</p>`;
  $("#report-sources-output").innerHTML = `<p class="placeholder">The sources behind the activated hypotheses appear here after a report is generated.</p>`;
  $("#graph-empty").classList.remove("hidden");
  $("#activated-graph-svg").innerHTML = "";
  $("#graph-side").innerHTML = `<p class="placeholder">Select a node or edge in the activated graph to inspect its full traceable detail.</p>`;
  setRailDone(["intake"]);
}

function fillRandomDemo() {
  const profile = DEMO_PROFILES[Math.floor(Math.random() * DEMO_PROFILES.length)];
  $all("#intake-form select").forEach((s) => {
    const val = profile.set[s.name] !== undefined ? profile.set[s.name] : INTAKE_DEFAULTS[s.name];
    s.value = val;
    s.classList.toggle("set", !NONINFORMATIVE.has(val));
  });
  $("#intake-meta").textContent = `Demo profile: "${profile.name}" — review inputs, then Generate report.`;
}

/* ================================================================== */
/* Inference engine (Part 3)                                           */
/* ================================================================== */
function signalLabel(key, value) { return `${FIELD_LABEL[key]}: ${value}`; }

function paramNodeFor(key, value) {
  const id = SIGNAL_PARAM_NODE[`${key}=${value}`];
  if (id && state.nodeById.has(id)) return id;
  return null;
}

/* Graph-derived guardrails (outgoing CONSTRAINED_BY_GUARDRAIL) for a hidden state. */
function graphGuardrails(hsId) {
  return (state.outgoing.get(hsId) || [])
    .filter((e) => e.type === "CONSTRAINED_BY_GUARDRAIL")
    .map((e) => e.target);
}
/* Supporting inference chains (incoming SUPPORTS_HIDDEN_STATE from inference_chain). */
function supportingChains(hsId) {
  return (state.incoming.get(hsId) || [])
    .filter((e) => e.type === "SUPPORTS_HIDDEN_STATE" && state.nodeById.get(e.source)?.type === "inference_chain")
    .map((e) => e.source);
}
/* Graph-recommended measurements via supporting chains' RECOMMENDS_MEASUREMENT edges. */
function chainMeasurements(hsId) {
  const out = [];
  for (const chainId of supportingChains(hsId)) {
    for (const e of (state.outgoing.get(chainId) || [])) {
      if (e.type === "RECOMMENDS_MEASUREMENT") out.push(e.target);
    }
  }
  return Array.from(new Set(out));
}

function runInference(v) {
  const activeKeys = Object.keys(v).filter((k) => !NONINFORMATIVE.has(v[k]));
  const active_signals = activeKeys.map((k) => ({
    key: k, label: signalLabel(k, v[k]), value: v[k], domain: FIELD_DOMAIN[k], param: paramNodeFor(k, v[k]),
  }));

  const candidates = [];
  if (activeKeys.length === 0) {
    candidates.push(makeUnknownCandidate());
  } else {
    for (const rule of RULES) {
      if (!rule.fire(v)) continue;
      const built = rule.build(v) || {};
      const stateId = rule.stateId || rule.id;
      const cand = resolveCandidate(rule, built, stateId, v, active_signals);
      // Avoid duplicate hidden-state nodes from two rules; merge supporting signals.
      const existing = candidates.find((c) => c.state_id === cand.state_id && !c.pseudo);
      if (existing && !cand.pseudo) mergeCandidate(existing, cand);
      else candidates.push(cand);
    }
    if (candidates.length === 0) candidates.push(makeUnknownCandidate());
  }

  // Confidence governance.
  for (const c of candidates) applyConfidenceGovernance(c, v);
  candidates.sort((a, b) => b.score - a.score);

  // Aggregate guardrails applied across the run.
  const guardrailsApplied = new Set();
  for (const c of candidates) c.guardrails.forEach((g) => guardrailsApplied.add(g));
  if (candidates.some((c) => c.state_id !== "unknown_or_missing_data_state")) {
    CORE_GUARDRAILS.forEach((g) => guardrailsApplied.add(g));
  } else {
    guardrailsApplied.add("unknown_is_not_negative_evidence");
    guardrailsApplied.add("recommend_next_measurement_when_uncertain");
  }

  // Global missing data: relevant fields left unknown/unavailable.
  const missing_data = activeKeys.length
    ? Object.keys(v).filter((k) => v[k] === "unknown" || v[k] === "unavailable").map((k) => FIELD_LABEL[k])
    : ["Any wearable, symptom, context, lab, or functional input to begin a traceable hypothesis"];

  // Ranked next measurements (graph required_measurement nodes preferred).
  const measureCount = new Map();
  const measureNodeOf = new Map();
  for (const c of candidates) {
    for (const mid of c.next_measurement_nodes) {
      measureCount.set(mid, (measureCount.get(mid) || 0) + 1);
      measureNodeOf.set(mid, true);
    }
  }
  const next_measurements = Array.from(measureCount.entries())
    .map(([id, count]) => ({ id, count, label: state.nodeById.get(id)?.label || id, node: true }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  // Fallback label-only measurements from rules (deduped against node labels).
  const haveLabels = new Set(next_measurements.map((m) => m.label.toLowerCase()));
  const labelMeasures = [];
  for (const c of candidates) {
    for (const lbl of c.rule_measurements) {
      if (!haveLabels.has(lbl.toLowerCase())) { haveLabels.add(lbl.toLowerCase()); labelMeasures.push({ id: null, count: 1, label: lbl, node: false }); }
    }
  }

  return {
    inputs: v,
    active_signals,
    candidates,
    guardrails_applied: Array.from(guardrailsApplied),
    missing_data: Array.from(new Set(missing_data)),
    next_measurements: next_measurements.concat(labelMeasures),
  };
}

function makeUnknownCandidate() {
  const node = state.nodeById.get("unknown_or_missing_data_state");
  return {
    state_id: "unknown_or_missing_data_state",
    label: node ? node.label : "Unknown / missing data state",
    node, pseudo: false,
    cap: "insufficient", confidence: "insufficient", score: 12,
    supporting_signals: [{ label: "No informative signals provided", domain: "—" }],
    param_nodes: [], domains: new Set(),
    missing_data: ["Any informative wearable, symptom, context, lab, or functional input"],
    not_proven: ["With no informative input, no hypothesis can be formed. Unknown is not negative evidence."],
    guardrails: ["unknown_is_not_negative_evidence", "recommend_next_measurement_when_uncertain"],
    rule_measurements: [],
    next_measurement_nodes: [],
    activated_paths: [],
    requires_context_met: false, objective_support: false,
  };
}

function resolveCandidate(rule, built, stateId, v, active_signals) {
  const node = rule.pseudo ? null : state.nodeById.get(stateId);
  const sigKeys = Array.from(new Set(built.signals || []));
  const supporting_signals = sigKeys.map((k) => active_signals.find((s) => s.key === k))
    .filter(Boolean);
  const domains = new Set(supporting_signals.map((s) => s.domain));
  const objective_support = supporting_signals.some((s) => s.domain === "labs" || s.domain === "functional");

  // Parameter nodes anchoring this candidate to the graph.
  const paramNodes = new Set();
  for (const s of supporting_signals) if (s.param) paramNodes.add(s.param);
  for (const extra of (built.param_extra || [])) if (state.nodeById.has(extra)) paramNodes.add(extra);

  // Graph guardrails + rule guardrail hints.
  const guardrails = new Set(built.guardrail_hint || []);
  if (node) graphGuardrails(stateId).forEach((g) => guardrails.add(g));

  // Next-measurement nodes from the graph for this hidden state.
  const next_measurement_nodes = node ? chainMeasurements(stateId) : [];

  // requires_context_met: medication context resolved; relevant for high promotion.
  const medResolved = v.med_change !== "unknown" && v.sedative !== "unknown";
  const requires_context_met = built.alwaysContext === true || medResolved;

  return {
    rule_id: rule.id,
    state_id: stateId,
    label: node ? node.label : (rule.pseudoLabel || stateId),
    node, pseudo: !!rule.pseudo,
    cap: built.capOverride || rule.cap,
    confidence: built.capOverride || rule.cap,
    score: 0,
    supporting_signals, domains, objective_support,
    param_nodes: Array.from(paramNodes),
    missing_data: built.missing_data || [],
    not_proven: built.not_proven || [],
    guardrails: Array.from(guardrails),
    rule_measurements: built.missing_data ? [] : [],
    next_measurement_nodes,
    activated_paths: [],
    requires_context_met,
  };
}

function mergeCandidate(target, extra) {
  const seen = new Set(target.supporting_signals.map((s) => s.key));
  for (const s of extra.supporting_signals) if (!seen.has(s.key)) { target.supporting_signals.push(s); seen.add(s.key); }
  extra.domains.forEach((d) => target.domains.add(d));
  target.objective_support = target.objective_support || extra.objective_support;
  target.param_nodes = Array.from(new Set(target.param_nodes.concat(extra.param_nodes)));
  target.guardrails = Array.from(new Set(target.guardrails.concat(extra.guardrails)));
  target.missing_data = Array.from(new Set(target.missing_data.concat(extra.missing_data)));
  target.not_proven = Array.from(new Set(target.not_proven.concat(extra.not_proven)));
  if (CONF_RANK[extra.cap] > CONF_RANK[target.cap]) target.cap = extra.cap;
}

/* Confidence governance (Part 3):
   - default insufficient/low/moderate;
   - high ONLY if >=3 domains support the same hidden state AND required context present
     AND there is objective (labs/functional) support;
   - symptoms-only or a single marker can never exceed low. */
function applyConfidenceGovernance(c, v) {
  const domainCount = c.domains.size;
  const symptomsOnly = domainCount > 0 && Array.from(c.domains).every((d) => d === "symptom");
  let allowed;
  if (domainCount >= 3 && c.requires_context_met && c.objective_support) allowed = "high";
  else if (domainCount >= 2) allowed = "moderate";
  else allowed = "low";
  if (symptomsOnly) allowed = "low";
  if (c.supporting_signals.length <= 1) allowed = minConf(allowed, "low");
  if (c.state_id === "unknown_or_missing_data_state") allowed = "insufficient";

  // Final confidence is the lower of the rule cap and the governance-allowed level,
  // except the unknown state which is fixed at insufficient.
  c.confidence = c.state_id === "unknown_or_missing_data_state" ? "insufficient" : minConf(c.cap, allowed);

  // A single-marker support always invokes the single-marker guardrail.
  if (c.supporting_signals.length <= 1 && c.state_id !== "unknown_or_missing_data_state") {
    if (!c.guardrails.includes("single_marker_never_equals_mechanism")) c.guardrails.push("single_marker_never_equals_mechanism");
  }

  // Score for the confidence bar (visual only).
  const base = { insufficient: 14, low: 42, moderate: 70, high: 90 }[c.confidence];
  c.score = Math.min(98, base + Math.max(0, domainCount - 1) * 4 + (c.objective_support ? 6 : 0));
}

/* ================================================================== */
/* STEP 2 — Report (Part 5)                                            */
/* ================================================================== */
function generateReport() {
  const v = readIntake();
  const report = runInference(v);
  report.activatedGraph = buildActivatedSubgraph(report);
  state.lastReport = report;
  renderReport(report);
  renderMeasurements(report);
  renderReportSources(report);
  renderActivatedGraph();
  setRailDone(["intake", "report", "graph", "measurements", "sources"]);
  $("#step-report").scrollIntoView({ behavior: "smooth", block: "start" });
}

function confidencePhrase(conf) {
  return ({ high: "compatible with (higher support)", moderate: "may support", low: "uncertain / low support", insufficient: "insufficient evidence" })[conf];
}

function renderReport(report) {
  const out = $("#report-output");
  const parts = [];
  parts.push(`<p class="not-diagnosis-line">${esc(NOT_A_DIAGNOSIS_LINE)}</p>`);

  // 1. Plain-language summary
  const top = report.candidates[0];
  const informativeCount = report.active_signals.length;
  let summary;
  if (top && top.state_id === "unknown_or_missing_data_state") {
    summary = `No informative observations were entered, so no hypothesis can be formed. Unknown is not negative evidence — add wearable, symptom, context, lab, or functional inputs to begin a traceable hypothesis.`;
  } else {
    summary = `From ${informativeCount} informative observation(s), the engine produced ${report.candidates.length} traceable hypothes${report.candidates.length === 1 ? "is" : "es"}. ` +
      `The best-supported is <strong>${esc(top.label)}</strong> (${esc(top.confidence)} confidence — ${esc(confidencePhrase(top.confidence))}), drawing on ${top.domains.size} input domain(s). ` +
      `These are hypotheses with uncertainty, constrained by guardrails, and each lists what would reduce uncertainty. This is not a diagnosis.`;
  }
  parts.push(reportSection("Plain-language summary", `<p class="report-summary">${summary}</p>`));

  // 2. Top candidate hidden states
  const cards = report.candidates.slice(0, 8).map((c) => candidateCard(c)).join("");
  parts.push(reportSection("Top candidate hidden states", `<div class="candidate-grid">${cards}</div>`));

  // 3. Evidence cards
  const ev = report.candidates.map((c) => evidenceCard(c)).join("");
  parts.push(reportSection("Evidence cards", ev));

  // 4. Activated graph (interactive version in step 3)
  parts.push(reportSection("Activated graph",
    `<p class="report-summary">The activated subgraph for these hypotheses is rendered in <strong>Step 3 · Activated Evidence Graph</strong> below — ${report.activatedGraph.nodes.length} nodes and ${report.activatedGraph.edges.length} edges drawn from the integrated graph. Click any node or edge there for full traceable detail.</p>`));

  // 5. What this does NOT prove
  const notProven = Array.from(new Set(report.candidates.flatMap((c) => c.not_proven)));
  parts.push(reportSection("What this does NOT prove",
    `<div class="result-block notproven"><ul>` +
    `<li>This is not a diagnosis and does not establish any disease.</li>` +
    notProven.map((x) => `<li>${esc(x)}</li>`).join("") + `</ul></div>`));

  // 6. Missing data
  parts.push(reportSection("Missing data",
    `<div class="chip-list">${report.missing_data.slice(0, 30).map((m) => `<span class="chip">${esc(m)}</span>`).join("") || `<span class="empty-note">None recorded.</span>`}</div>`));

  // 7. Next best measurements (full ranking in step 4)
  parts.push(reportSection("Next best measurements",
    `<p class="report-summary">${report.next_measurements.length} measurement(s) would reduce uncertainty. The ranked list is in <strong>Step 4 · Next Best Measurements</strong> below.</p>`));

  // 8. Guardrails applied
  parts.push(reportSection("Guardrails applied",
    `<div class="chip-list">${report.guardrails_applied.map((g) => `<span class="chip clickable" data-jump="${esc(g)}">${esc(g)}</span>`).join("")}</div>`));

  // 9. Traceable chains
  const chainLines = report.candidates.flatMap((c) => c.activated_paths).slice(0, 12);
  parts.push(reportSection("Traceable chains",
    chainLines.length ? chainLines.map((p) => `<div class="chain-line">${p}</div>`).join("")
      : `<p class="empty-note">No standalone graph chains for these hypotheses; see the activated graph for input-to-hypothesis mappings.</p>`));

  // 10. Source traceability (full view in step 5)
  parts.push(reportSection("Source traceability",
    `<p class="report-summary">The source files and source trees behind these activated hypotheses are listed in <strong>Step 5 · Source Traceability</strong> below, and the corpus-wide view is in the <strong>Source Traceability</strong> tab.</p>`));

  out.innerHTML = parts.join("");
  $all(".chip[data-jump]", out).forEach((c) => c.addEventListener("click", () => jumpToNode(c.getAttribute("data-jump"))));
  $all("[data-open-node]", out).forEach((el) => el.addEventListener("click", () => jumpToNode(el.getAttribute("data-open-node"))));
}

function reportSection(title, bodyHtml) {
  return `<div class="report-section"><h3>${esc(title)}</h3>${bodyHtml}</div>`;
}

function candidateCard(c) {
  const sigs = c.supporting_signals.map((s) => esc(s.label)).join(", ");
  return `<div class="candidate-card conf-${c.confidence}">
    <h4>${esc(c.label)}</h4>
    <div class="cc-meta"><span class="tag c-${c.confidence}">${esc(c.confidence)}</span>
      <span>${esc(confidencePhrase(c.confidence))}</span>
      ${c.node ? `<span class="chip clickable" data-open-node="${esc(c.node.id)}">open in graph</span>` : `<span class="tag c-unknown">hypothesis (not a curated node)</span>`}</div>
    <div class="cc-bars"><div class="score-track"><div class="score-fill" style="width:${c.score}%"></div></div></div>
    <div class="result-block"><div class="rb-title">Supporting signals (${c.domains.size} domain${c.domains.size === 1 ? "" : "s"})</div>
      <ul><li>${sigs || "—"}</li></ul></div>
  </div>`;
}

function evidenceCard(c) {
  const guardrailChips = c.guardrails.map((g) => `<span class="chip clickable" data-open-node="${esc(g)}">${esc(g)}</span>`).join("");
  const measureChips = c.next_measurement_nodes.slice(0, 8).map((m) => `<span class="chip clickable" data-open-node="${esc(m)}">${esc(state.nodeById.get(m)?.label || m)}</span>`).join("")
    || c.missing_data.slice(0, 4).map((m) => `<span class="chip">${esc(m)}</span>`).join("");
  const params = c.param_nodes.map((p) => `<span class="chip clickable" data-open-node="${esc(p)}">${esc(state.nodeById.get(p)?.label || p)}</span>`).join("") || `<span class="empty-note">no direct parameter mapping</span>`;
  return `<div class="evidence-card conf-${c.confidence}">
    <div class="ec-head"><h4>${esc(c.label)}</h4><span class="tag c-${c.confidence}">${esc(c.confidence)}</span></div>
    <div class="ec-row"><span class="ec-key">Supporting signals</span>${c.supporting_signals.map((s) => esc(s.label)).join(" · ") || "—"}</div>
    <div class="ec-row"><span class="ec-key">Graph parameters</span><span class="chip-list">${params}</span></div>
    <div class="ec-row"><span class="ec-key">Guardrails</span><span class="chip-list">${guardrailChips}</span></div>
    <div class="ec-row"><span class="ec-key">Measurements that reduce uncertainty</span><span class="chip-list">${measureChips}</span></div>
    <details class="tech"><summary>Technical detail</summary><div class="tech-body">
      <div class="ec-row"><span class="ec-key">state_id</span><code>${esc(c.state_id)}</code></div>
      <div class="ec-row"><span class="ec-key">rule_id</span><code>${esc(c.rule_id || "—")}</code></div>
      <div class="ec-row"><span class="ec-key">score</span>${c.score}/100</div>
      <div class="ec-row"><span class="ec-key">objective support</span>${c.objective_support ? "yes" : "no"}</div>
      <div class="ec-row"><span class="ec-key">required context met</span>${c.requires_context_met ? "yes" : "no"}</div>
    </div></details>
  </div>`;
}

/* ================================================================== */
/* STEP 4 — Next best measurements                                     */
/* ================================================================== */
function renderMeasurements(report) {
  const out = $("#measurements-output");
  if (!report.next_measurements.length) {
    out.innerHTML = `<p class="empty-note">No specific next-measurement recorded; collect additional within-person baseline data.</p>`;
    return;
  }
  out.innerHTML = report.next_measurements.map((m) => {
    const node = m.id ? state.nodeById.get(m.id) : null;
    return `<div class="measure-row">
      <div class="mr-main">
        <div class="mr-label">${esc(m.label)}</div>
        <div class="mr-sub">${node ? `graph measurement · ${esc(m.id)}` : "recommended (label only)"} · supports ${m.count} hypothes${m.count === 1 ? "is" : "es"}</div>
      </div>
      <div>${node ? `<span class="chip clickable" data-open-node="${esc(m.id)}">open</span>` : `<span class="mr-count">${m.count}</span>`}</div>
    </div>`;
  }).join("");
  $all("[data-open-node]", out).forEach((el) => el.addEventListener("click", () => jumpToNode(el.getAttribute("data-open-node"))));
}

/* ================================================================== */
/* STEP 5 — Report-scoped source traceability                          */
/* ================================================================== */
function renderReportSources(report) {
  const out = $("#report-sources-output");
  const files = new Map(); // filename -> { params:Set, hs:Set, guardrails:Set, trees:Set }
  const add = (fname, role, id) => {
    if (!files.has(fname)) files.set(fname, { params: new Set(), hs: new Set(), guardrails: new Set() });
    if (role) files.get(fname)[role].add(id);
  };
  const collectNode = (nodeId, role) => {
    const n = state.nodeById.get(nodeId);
    if (!n) return;
    for (const f of (n.source_files || [])) add(f, role, nodeId);
    for (const t of (n.source_tree_ids || [])) add(t, role, nodeId);
  };
  for (const c of report.candidates) {
    if (c.node) collectNode(c.state_id, "hs");
    for (const p of c.param_nodes) collectNode(p, "params");
    for (const g of c.guardrails) collectNode(g, "guardrails");
    if (c.node) for (const chainId of supportingChains(c.state_id)) collectNode(chainId, "params");
  }
  if (!files.size) {
    out.innerHTML = `<p class="empty-note">These hypotheses are constrained by universal guardrails that are model-level (no single source file); add lab/functional inputs to surface file-level provenance.</p>`;
    return;
  }
  const rows = Array.from(files.entries())
    .sort((a, b) => (b[1].params.size + b[1].hs.size) - (a[1].params.size + a[1].hs.size));
  out.innerHTML = `<div class="trace-table-wrap"><table class="trace-table">
    <thead><tr><th>Source file / tree</th><th>Parameters</th><th>Hidden states</th><th>Guardrails</th></tr></thead>
    <tbody>${rows.map(([k, r]) => `<tr><td class="fname">${esc(k)}</td><td class="num">${r.params.size}</td><td class="num">${r.hs.size}</td><td class="num">${r.guardrails.size}</td></tr>`).join("")}</tbody>
  </table></div>`;
}

/* ================================================================== */
/* STEP 3 — Activated graph (Part 4)                                   */
/* ================================================================== */
const GRAPH_ROLE = {
  input: 0, measured_parameter: 1, result_variation: 1, inference_chain: 2, context: 2,
  hidden_state: 3, guardrail: 4, required_measurement: 4,
};
/* Literal hex colors (identical to the --node-* CSS variables in styles.css).
   var() does not resolve inside SVG `fill` presentation attributes, so the
   layered node colors must be set with concrete values. */
const NODE_FILL = {
  input: "#4aa8ff", measured_parameter: "#34d3b7", result_variation: "#7bd0c0",
  inference_chain: "#c08bff", context: "#d6a435", hidden_state: "#ff8d6b",
  guardrail: "#6b7d92", required_measurement: "#58c87a",
  source_file: "#50607a", source_tree: "#50607a",
};
const COL_LABELS = ["Inputs", "Parameters / variations", "Chains / context", "Hidden states", "Guardrails / measurements"];

/* Build the curated activated subgraph from the report and current toggles. */
function buildActivatedSubgraph(report) {
  const showGuard = $("#gctl-guardrails").checked;
  const showMeas = $("#gctl-measurements").checked;
  const showSources = $("#gctl-sources").checked;
  const showNeighbors = $("#gctl-neighbors").checked && !$("#gctl-active-only").checked;

  const nodes = new Map(); // id -> {id,label,type,role,synthetic,ref}
  const edges = new Map(); // id -> {id,source,target,type,confidence,synthetic,real}
  const addNode = (id, obj) => { if (!nodes.has(id)) nodes.set(id, obj); return nodes.get(id); };
  const addEdge = (obj) => { if (!edges.has(obj.id)) edges.set(obj.id, obj); };
  const addReal = (nodeId) => {
    const n = state.nodeById.get(nodeId);
    if (!n) return null;
    return addNode(nodeId, { id: nodeId, label: n.label, type: n.type, role: n.type, synthetic: false, ref: n });
  };

  for (const c of report.candidates) {
    // Hidden state node (real or synthetic for pseudo candidates).
    const hsId = c.pseudo ? `hs::${c.state_id}` : c.state_id;
    addNode(hsId, {
      id: hsId, label: c.label, type: "hidden_state", role: "hidden_state",
      synthetic: c.pseudo, ref: c.node || null, candidate: c,
    });

    // Input observation nodes -> parameter -> hidden state.
    for (const s of c.supporting_signals) {
      const inId = `input::${s.key}`;
      addNode(inId, { id: inId, label: s.label, type: "input", role: "input", synthetic: true, ref: null, signal: s });
      if (s.param && state.nodeById.has(s.param)) {
        addReal(s.param);
        addEdge({ id: `${inId}__OBSERVED_AS__${s.param}`, source: inId, target: s.param, type: "OBSERVED_AS", confidence: "n/a", synthetic: true });
        // parameter -> hidden state: use real edge if present, else mapped synthetic.
        const realEdge = (state.outgoing.get(s.param) || []).find((e) => e.type === "SUPPORTS_HIDDEN_STATE" && e.target === c.state_id);
        if (realEdge) addEdge({ id: realEdge.id, source: s.param, target: hsId, type: realEdge.type, confidence: realEdge.confidence, synthetic: false, real: realEdge });
        else addEdge({ id: `${s.param}__SUPPORTS_MAPPED__${hsId}`, source: s.param, target: hsId, type: "SUPPORTS_HIDDEN_STATE (mapped)", confidence: "mapped", synthetic: true });
      } else {
        // No graph parameter: connect the observation directly to the hypothesis as a mapping.
        addEdge({ id: `${inId}__MAPS_TO__${hsId}`, source: inId, target: hsId, type: "INPUT_MAPS_TO", confidence: "mapped", synthetic: true });
      }
    }
    // Extra parameter nodes (e.g. PSG sleep-disordered-breathing anchor).
    for (const p of c.param_nodes) {
      if (addReal(p)) addEdge({ id: `${p}__SUPPORTS_MAPPED__${hsId}`, source: p, target: hsId, type: "SUPPORTS_HIDDEN_STATE (mapped)", confidence: "mapped", synthetic: true });
    }

    if (c.node) {
      // Supporting inference chains (cap 2) -> real edges.
      for (const chainId of supportingChains(c.state_id).slice(0, 2)) {
        addReal(chainId);
        const e = (state.outgoing.get(chainId) || []).find((x) => x.type === "SUPPORTS_HIDDEN_STATE" && x.target === c.state_id);
        if (e) addEdge({ id: e.id, source: chainId, target: hsId, type: e.type, confidence: e.confidence, synthetic: false, real: e });
        // chain -> measurements
        if (showMeas) {
          for (const me of (state.outgoing.get(chainId) || []).filter((x) => x.type === "RECOMMENDS_MEASUREMENT").slice(0, 4)) {
            addReal(me.target);
            addEdge({ id: me.id, source: chainId, target: me.target, type: me.type, confidence: me.confidence, synthetic: false, real: me });
          }
        }
        // chain -> sources
        if (showSources) {
          for (const se of (state.outgoing.get(chainId) || []).filter((x) => ["SUPPORTED_BY_SOURCE", "DERIVED_FROM"].includes(x.type)).slice(0, 2)) {
            addReal(se.target);
            addEdge({ id: se.id, source: chainId, target: se.target, type: se.type, confidence: se.confidence, synthetic: false, real: se });
          }
        }
      }
      // Hidden state -> guardrails (real).
      if (showGuard) {
        for (const e of (state.outgoing.get(c.state_id) || []).filter((x) => x.type === "CONSTRAINED_BY_GUARDRAIL").slice(0, 7)) {
          addReal(e.target);
          addEdge({ id: e.id, source: hsId, target: e.target, type: e.type, confidence: e.confidence, synthetic: false, real: e });
        }
      }
      // Hidden state -> source files (real).
      if (showSources) {
        for (const e of (state.outgoing.get(c.state_id) || []).filter((x) => ["SUPPORTED_BY_SOURCE", "DERIVED_FROM"].includes(x.type)).slice(0, 3)) {
          addReal(e.target);
          addEdge({ id: e.id, source: hsId, target: e.target, type: e.type, confidence: e.confidence, synthetic: false, real: e });
        }
      }
    } else if (showGuard) {
      // Pseudo candidate: still show its hint guardrails as real nodes.
      for (const g of c.guardrails.slice(0, 5)) {
        if (addReal(g)) addEdge({ id: `${hsId}__CONSTRAINED_BY_GUARDRAIL__${g}`, source: hsId, target: g, type: "CONSTRAINED_BY_GUARDRAIL", confidence: "mapped", synthetic: true });
      }
    }

    // Build a readable traceable path string for the report.
    buildPathStrings(c, hsId);
  }

  // Optional first-degree neighbor expansion (bounded).
  if (showNeighbors) {
    const realIds = Array.from(nodes.values()).filter((n) => !n.synthetic).map((n) => n.id);
    let added = 0;
    for (const id of realIds) {
      if (added > 40) break;
      for (const e of (state.outgoing.get(id) || [])) {
        if (added > 40) break;
        if (!nodes.has(e.target)) { if (addReal(e.target)) added++; }
        addEdge({ id: e.id, source: e.source, target: e.target, type: e.type, confidence: e.confidence, synthetic: false, real: e, neighbor: true });
      }
      for (const e of (state.incoming.get(id) || [])) {
        if (added > 40) break;
        if (!nodes.has(e.source)) { if (addReal(e.source)) added++; }
        addEdge({ id: e.id, source: e.source, target: e.target, type: e.type, confidence: e.confidence, synthetic: false, real: e, neighbor: true });
      }
    }
  }

  // Only keep edges whose endpoints are both present.
  const finalEdges = Array.from(edges.values()).filter((e) => nodes.has(e.source) && nodes.has(e.target));
  return { nodes: Array.from(nodes.values()), edges: finalEdges };
}

function buildPathStrings(c, hsId) {
  c.activated_paths = [];
  const nodeName = (id) => state.nodeById.get(id)?.label || id;
  if (!c.node) return;
  const chains = supportingChains(c.state_id).slice(0, 2);
  const guards = graphGuardrails(c.state_id).slice(0, 1);
  const meas = c.next_measurement_nodes.slice(0, 3).map((m) => nodeName(m));
  // input -> param -> hidden state -> guardrail -> measurement
  for (const s of c.supporting_signals) {
    if (!s.param) continue;
    const segs = [`<span class="ch-node">${esc(s.label)}</span>`, `<span class="ch-node">${esc(nodeName(s.param))}</span>`, `<span class="ch-node">${esc(c.label)}</span>`];
    if (guards.length) segs.push(`constrained by <span class="ch-guard">${esc(guards[0])}</span>`);
    if (meas.length) segs.push(`recommends <span class="ch-node">${esc(meas.join(", "))}</span>`);
    c.activated_paths.push(segs.join(' <span class="ch-arrow">&rarr;</span> '));
    break; // one representative path per candidate
  }
  // chain-based path
  if (chains.length) {
    const segs = [`<span class="ch-node">${esc(nodeName(chains[0]))}</span>`, `<span class="ch-node">${esc(c.label)}</span>`];
    if (meas.length) segs.push(`recommends <span class="ch-node">${esc(meas.join(", "))}</span>`);
    c.activated_paths.push(segs.join(' <span class="ch-arrow">&rarr;</span> '));
  }
}

/* ---- SVG layered renderer ---- */
function renderActivatedGraph() {
  const report = state.lastReport;
  const svg = $("#activated-graph-svg");
  svg.innerHTML = "";
  if (!report) { $("#graph-empty").classList.remove("hidden"); return; }
  report.activatedGraph = buildActivatedSubgraph(report);
  const sub = report.activatedGraph;
  if (!sub.nodes.length) { $("#graph-empty").classList.remove("hidden"); return; }
  $("#graph-empty").classList.add("hidden");

  // Layout: columns 0..4 plus a bottom band for source nodes.
  const NODE_W = 168, NODE_H = 30, V_GAP = 12, COL_GAP = 220, MARGIN = 40, TOP = 56;
  const cols = [[], [], [], [], []];
  const sources = [];
  for (const n of sub.nodes) {
    if (n.type === "source_file" || n.type === "source_tree") { sources.push(n); continue; }
    const col = GRAPH_ROLE[n.role] !== undefined ? GRAPH_ROLE[n.role] : 2;
    cols[col].push(n);
  }
  const colHeights = cols.map((c) => c.length ? c.length * NODE_H + (c.length - 1) * V_GAP : 0);
  const contentH = Math.max(...colHeights, 1);
  const pos = new Map();
  cols.forEach((colNodes, ci) => {
    const x = MARGIN + ci * COL_GAP;
    const colH = colHeights[ci];
    let y = TOP + (contentH - colH) / 2;
    for (const n of colNodes) { pos.set(n.id, { x, y, w: NODE_W, h: NODE_H }); y += NODE_H + V_GAP; }
  });
  const bottomY = TOP + contentH + 56;
  sources.forEach((n, i) => {
    const x = MARGIN + (i % 6) * (NODE_W + 16);
    const y = bottomY + Math.floor(i / 6) * (NODE_H + V_GAP);
    pos.set(n.id, { x, y, w: NODE_W, h: NODE_H });
  });
  const totalW = MARGIN * 2 + 4 * COL_GAP + NODE_W;
  const totalH = bottomY + (sources.length ? (Math.floor((sources.length - 1) / 6) + 1) * (NODE_H + V_GAP) : 0) + 40;

  state.graphView.base = { x: 0, y: 0, w: totalW, h: totalH };
  state.graphView.scale = 1;
  setViewBox(0, 0, totalW, totalH);

  // Column labels.
  const gLabels = svgEl("g");
  COL_LABELS.forEach((lbl, ci) => {
    if (!cols[ci].length) return;
    const t = svgEl("text", { x: MARGIN + ci * COL_GAP, y: 28, class: "col-label" });
    t.textContent = lbl;
    gLabels.appendChild(t);
  });
  if (sources.length) {
    const t = svgEl("text", { x: MARGIN, y: bottomY - 14, class: "col-label" });
    t.textContent = "Sources";
    gLabels.appendChild(t);
  }
  svg.appendChild(gLabels);

  // Edges first (under nodes).
  const gEdges = svgEl("g");
  for (const e of sub.edges) {
    const a = pos.get(e.source), b = pos.get(e.target);
    if (!a || !b) continue;
    const x1 = a.x + a.w, y1 = a.y + a.h / 2;
    const x2 = b.x, y2 = b.y + b.h / 2;
    let d;
    if (b.y > a.y + 200 || a.x === b.x) {
      // vertical-ish (e.g. to source band)
      const mx1 = a.x + a.w / 2, my1 = a.y + a.h, mx2 = b.x + b.w / 2, my2 = b.y;
      d = `M ${mx1} ${my1} C ${mx1} ${(my1 + my2) / 2}, ${mx2} ${(my1 + my2) / 2}, ${mx2} ${my2}`;
    } else {
      const dx = Math.max(40, (x2 - x1) / 2);
      d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
    }
    const path = svgEl("path", { d, class: "gedge" + (e.synthetic ? "" : " active"), "data-edge": e.id });
    if (e.synthetic) path.setAttribute("stroke-dasharray", "5 4");
    path.addEventListener("click", (ev) => { ev.stopPropagation(); selectGraphEdge(e); });
    gEdges.appendChild(path);
  }
  svg.appendChild(gEdges);

  // Nodes.
  const gNodes = svgEl("g");
  for (const n of sub.nodes) {
    const p = pos.get(n.id);
    if (!p) continue;
    const g = svgEl("g", { class: "gnode", "data-node": n.id, transform: `translate(${p.x},${p.y})` });
    const rect = svgEl("rect", { x: 0, y: 0, width: p.w, height: p.h, rx: 7, fill: NODE_FILL[n.role] || "var(--node-source)", "fill-opacity": n.synthetic ? 0.32 : 0.85 });
    g.appendChild(rect);
    const label = n.label.length > 26 ? n.label.slice(0, 25) + "…" : n.label;
    const text = svgEl("text", { x: 9, y: p.h / 2 + 4 });
    text.textContent = label;
    const title = svgEl("title"); title.textContent = `${n.label} (${n.type})`;
    g.appendChild(text); g.appendChild(title);
    g.addEventListener("click", (ev) => { ev.stopPropagation(); selectGraphNode(n); });
    gNodes.appendChild(g);
  }
  svg.appendChild(gNodes);

  attachGraphPanZoom();
  if (state.selectedGraphId) highlightGraphSelection();
}

function setViewBox(x, y, w, h) {
  $("#activated-graph-svg").setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
  state.graphView.vb = { x, y, w, h };
}

function attachGraphPanZoom() {
  const svg = $("#activated-graph-svg");
  let dragging = false, sx = 0, sy = 0, start = null;
  svg.onpointerdown = (e) => {
    dragging = true; svg.classList.add("panning"); sx = e.clientX; sy = e.clientY;
    start = Object.assign({}, state.graphView.vb); svg.setPointerCapture(e.pointerId);
  };
  svg.onpointermove = (e) => {
    if (!dragging) return;
    const rect = svg.getBoundingClientRect();
    const dx = (e.clientX - sx) / rect.width * state.graphView.vb.w;
    const dy = (e.clientY - sy) / rect.height * state.graphView.vb.h;
    setViewBox(start.x - dx, start.y - dy, state.graphView.vb.w, state.graphView.vb.h);
  };
  svg.onpointerup = (e) => { dragging = false; svg.classList.remove("panning"); try { svg.releasePointerCapture(e.pointerId); } catch (_) {} };
  svg.onwheel = (e) => { e.preventDefault(); zoomGraph(e.deltaY < 0 ? 0.9 : 1.1); };
}

function zoomGraph(factor) {
  const vb = state.graphView.vb; if (!vb) return;
  const cx = vb.x + vb.w / 2, cy = vb.y + vb.h / 2;
  const nw = vb.w * factor, nh = vb.h * factor;
  setViewBox(cx - nw / 2, cy - nh / 2, nw, nh);
  state.graphView.scale *= factor;
}

function resetGraphView() {
  const b = state.graphView.base; if (!b) return;
  state.graphView.scale = 1;
  setViewBox(b.x, b.y, b.w, b.h);
}

function attachGraphControls() {
  ["gctl-active-only", "gctl-neighbors", "gctl-guardrails", "gctl-measurements", "gctl-sources"].forEach((id) => {
    $("#" + id).addEventListener("change", () => { if (state.lastReport) renderActivatedGraph(); });
  });
  $("#gctl-active-only").addEventListener("change", (e) => {
    if (e.target.checked) $("#gctl-neighbors").checked = false;
  });
  $("#gctl-zoom-in").addEventListener("click", () => zoomGraph(0.85));
  $("#gctl-zoom-out").addEventListener("click", () => zoomGraph(1.18));
  $("#gctl-reset").addEventListener("click", resetGraphView);
}

function renderGraphLegend() {
  const items = [
    ["Input", "var(--node-input)"], ["Parameter / variation", "var(--node-parameter)"],
    ["Chain / context", "var(--node-chain)"], ["Hidden state", "var(--node-hidden)"],
    ["Guardrail", "var(--node-guardrail)"], ["Measurement", "var(--node-measurement)"], ["Source", "var(--node-source)"],
  ];
  $("#graph-legend").innerHTML = items.map(([l, c]) => `<span class="legend-item"><span class="legend-swatch" style="background:${c}"></span>${esc(l)}</span>`).join("")
    + `<span class="legend-item">— solid = graph evidence edge · - - - dashed = input mapping</span>`;
}

function selectGraphNode(n) {
  state.selectedGraphId = n.id;
  highlightGraphSelection();
  const side = $("#graph-side");
  if (n.synthetic && n.type === "input") {
    side.innerHTML = `<div class="detail-head"><div><h3>${esc(n.label)}</h3><div class="detail-id">${esc(n.id)}</div></div><span class="tag type">input</span></div>
      <p class="detail-desc">This is an observation you entered. It maps to graph parameter nodes (dashed edges) and anchors the traceable chain. Inputs are not themselves graph evidence.</p>
      <dl class="kv"><dt>Domain</dt><dd>${esc(n.signal.domain)}</dd><dt>Value</dt><dd>${esc(n.signal.value)}</dd>
      <dt>Mapped parameter</dt><dd>${n.signal.param ? `<span class="chip clickable" data-jump="${esc(n.signal.param)}">${esc(state.nodeById.get(n.signal.param)?.label || n.signal.param)}</span>` : "none"}</dd></dl>`;
  } else if (!n.ref) {
    const c = n.candidate;
    side.innerHTML = `<div class="detail-head"><div><h3>${esc(n.label)}</h3><div class="detail-id">${esc(n.id)}</div></div><span class="tag c-${c ? c.confidence : "unknown"}">hypothesis</span></div>
      <p class="detail-desc">A traceable hypothesis derived from your inputs that is not (yet) a curated hidden-state node in the graph. It is anchored to real graph parameters and guardrails. This is not a diagnosis.</p>`;
  } else {
    renderNodeDetail(n.ref, side, { allowJump: true });
  }
  $all("[data-jump]", side).forEach((el) => el.addEventListener("click", () => jumpToNode(el.getAttribute("data-jump"))));
}

function selectGraphEdge(e) {
  state.selectedGraphId = null;
  $all(".gedge", $("#activated-graph-svg")).forEach((p) => p.classList.toggle("selected", p.getAttribute("data-edge") === e.id));
  $all(".gnode", $("#activated-graph-svg")).forEach((g) => g.classList.remove("selected"));
  const srcName = state.nodeById.get(e.source)?.label || e.source.replace(/^input::/, "input: ").replace(/^hs::/, "");
  const tgtName = state.nodeById.get(e.target)?.label || e.target.replace(/^hs::/, "");
  const real = e.real || {};
  const side = $("#graph-side");
  side.innerHTML = `<div class="detail-head"><div><h3>Edge</h3><div class="detail-id">${esc(e.id)}</div></div>
    <span class="tag ${e.synthetic ? "c-unknown" : "type"}">${e.synthetic ? "input mapping" : "graph evidence"}</span></div>
    <div class="chain-line"><span class="ch-node">${esc(srcName)}</span> <span class="ch-arrow">&mdash;${esc(e.type)}&rarr;</span> <span class="ch-node">${esc(tgtName)}</span></div>
    <dl class="kv">
      <dt>Edge type</dt><dd>${esc(e.type)}</dd>
      <dt>Confidence</dt><dd>${e.confidence ? `<span class="tag ${confClass(e.confidence)}">${esc(e.confidence)}</span>` : "—"}</dd>
      <dt>Chain IDs</dt><dd>${(real.chain_ids || []).map((c) => esc(c)).join(", ") || "—"}</dd>
      <dt>Guardrails</dt><dd>${(real.guardrails || []).map((g) => esc(g)).join(", ") || "—"}</dd>
      <dt>Source files</dt><dd>${(real.source_files || []).map((f) => esc(f)).join(", ") || (e.synthetic ? "(input mapping — not a graph evidence edge)" : "—")}</dd>
    </dl>`;
}

function highlightGraphSelection() {
  const id = state.selectedGraphId;
  $all(".gnode", $("#activated-graph-svg")).forEach((g) => g.classList.toggle("selected", g.getAttribute("data-node") === id));
  $all(".gedge", $("#activated-graph-svg")).forEach((p) => p.classList.remove("selected"));
}

function setRailDone(steps) {
  $all("#workflow-rail li").forEach((li) => {
    const s = li.dataset.step;
    li.classList.toggle("done", steps.includes(s) && s !== "intake");
  });
  // clicking a rail item scrolls to its step
  $all("#workflow-rail li").forEach((li) => {
    li.onclick = () => {
      $all("#workflow-rail li").forEach((x) => x.classList.remove("active"));
      li.classList.add("active");
      const el = $("#step-" + li.dataset.step);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    };
  });
}

/* ================================================================== */
/* Shared node-detail renderer (used by Evidence Map, graph side, etc) */
/* ================================================================== */
function renderNodeDetail(node, container, opts = {}) {
  const out = state.outgoing.get(node.id) || [];
  const inc = state.incoming.get(node.id) || [];
  const md = node.metadata || {};
  const parts = [];
  parts.push(`<div class="detail-head"><div><h3>${esc(node.label)}</h3><div class="detail-id">${esc(node.id)}</div></div>
    <span class="tag type">${esc(node.type)}</span></div>`);
  parts.push(`<dl class="kv">
    <dt>Domain</dt><dd>${esc(node.domain) || "—"}</dd>
    <dt>Evidence strength</dt><dd><span class="tag ${confClass(node.evidence_strength)}">${esc(node.evidence_strength)}</span></dd>
    <dt>Confidence</dt><dd><span class="tag ${confClass(node.confidence)}">${esc(node.confidence)}</span></dd>
    <dt>Readiness</dt><dd><span class="tag ${pipeClass(node.pipeline_status)}">${esc(node.pipeline_status)}</span></dd>
  </dl>`);
  if (node.description) parts.push(`<p class="detail-desc">${esc(node.description)}</p>`);
  parts.push(sectionChips("Source files", node.source_files));
  parts.push(sectionChips("Source tree IDs", node.source_tree_ids));
  parts.push(relSection(`Outgoing edges (${out.length})`, out, "out"));
  parts.push(relSection(`Incoming edges (${inc.length})`, inc, "in"));
  container.innerHTML = parts.join("");
  if (opts.allowJump !== false) {
    $all(".rel-item[data-target]", container).forEach((li) => li.addEventListener("click", () => {
      if (container.id === "graph-side") jumpToNode(li.getAttribute("data-target"));
      else selectInEvidenceMap(li.getAttribute("data-target"));
    }));
  }
}

function sectionChips(title, items) {
  if (!items || !items.length) return `<div class="detail-section"><h4>${esc(title)}</h4><p class="empty-note">None recorded.</p></div>`;
  const chips = items.map((i) => `<span class="chip">${esc(i)}</span>`).join("");
  return `<div class="detail-section"><h4>${esc(title)}</h4><div class="chip-list">${chips}</div></div>`;
}

function relSection(title, edges, direction) {
  if (!edges || !edges.length) return `<div class="detail-section"><h4>${esc(title)}</h4><p class="empty-note">None.</p></div>`;
  const items = edges.slice(0, 60).map((e) => {
    const other = direction === "out" ? e.target : e.source;
    const srcLabel = state.nodeById.get(e.source)?.label || e.source;
    const tgtLabel = state.nodeById.get(e.target)?.label || e.target;
    return `<li class="rel-item" data-target="${esc(other)}">` +
      `<span class="rel-target">${esc(srcLabel)}</span> –<span class="edge-type">${esc(e.type)}</span>→ ` +
      `<span class="rel-target">${esc(tgtLabel)}</span>` +
      (e.confidence ? ` <span class="tag ${confClass(e.confidence)}">${esc(e.confidence)}</span>` : "") + `</li>`;
  }).join("");
  const more = edges.length > 60 ? `<p class="empty-note">+${edges.length - 60} more…</p>` : "";
  return `<div class="detail-section"><h4>${esc(title)}</h4><ul class="rel-list">${items}</ul>${more}</div>`;
}

function jumpToNode(id) {
  const node = state.nodeById.get(id);
  if (!node) return;
  activateTab("evidence-map");
  selectInEvidenceMap(id);
}

/* ================================================================== */
/* Evidence Map (path-centric explorer, Part 7)                        */
/* ================================================================== */
function attachEvidenceMap() {
  ["#em-search", "#em-filter-type", "#em-filter-domain", "#em-filter-confidence", "#em-filter-evidence", "#em-filter-pipeline"]
    .forEach((sel) => $(sel).addEventListener("input", () => { state.emPage = 0; renderEvidenceMap(); }));
  renderEvidenceMap();
}

function evidenceMapFiltered() {
  const q = $("#em-search").value.trim().toLowerCase();
  const ft = $("#em-filter-type").value, fd = $("#em-filter-domain").value;
  const fc = $("#em-filter-confidence").value, fe = $("#em-filter-evidence").value, fp = $("#em-filter-pipeline").value;
  return state.graph.nodes.filter((n) => {
    if (ft && n.type !== ft) return false;
    if (fd && n.domain !== fd) return false;
    if (fc && n.confidence !== fc) return false;
    if (fe && n.evidence_strength !== fe) return false;
    if (fp && n.pipeline_status !== fp) return false;
    if (q) {
      const hay = (n.id + " " + n.label + " " + n.domain + " " + n.type).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

function renderEvidenceMap() {
  const filtered = evidenceMapFiltered();
  $("#em-count").textContent = `${filtered.length} node(s) match`;
  const size = state.emPageSize;
  const pages = Math.max(1, Math.ceil(filtered.length / size));
  if (state.emPage >= pages) state.emPage = 0;
  const slice = filtered.slice(state.emPage * size, state.emPage * size + size);
  const list = $("#em-list");
  list.innerHTML = "";
  for (const n of slice) list.appendChild(nodeListItem(n, () => selectInEvidenceMap(n.id)));
  renderPagination("#em-pagination", state.emPage, pages, (p) => { state.emPage = p; renderEvidenceMap(); });
}

function nodeListItem(n, onClick) {
  const li = document.createElement("li");
  li.className = "node-item";
  li.dataset.id = n.id;
  li.innerHTML =
    `<div class="ni-main"><div class="ni-label">${esc(n.label)}</div><div class="ni-sub">${esc(n.id)}</div></div>` +
    `<div class="ni-tags"><span class="tag type">${esc(n.type)}</span>` +
    `<span class="tag ${pipeClass(n.pipeline_status)}">${esc(n.pipeline_status)}</span></div>`;
  li.addEventListener("click", onClick);
  return li;
}

/* Discover paths through a node: walk upstream to parameters/inputs and downstream
   to hidden states/guardrails/measurements, then format as breadcrumb cards. */
function pathsThroughNode(id) {
  const paths = [];
  const name = (x) => state.nodeById.get(x)?.label || x;
  const node = state.nodeById.get(id);
  if (!node) return paths;
  // Hidden-state centric: param -> variation -> chain -> hidden state -> guardrail -> measurement.
  const hsIds = node.type === "hidden_state" ? [id]
    : (state.outgoing.get(id) || []).filter((e) => e.type === "SUPPORTS_HIDDEN_STATE").map((e) => e.target);
  for (const hsId of Array.from(new Set(hsIds)).slice(0, 6)) {
    const supports = (state.incoming.get(hsId) || []).filter((e) => e.type === "SUPPORTS_HIDDEN_STATE");
    const upstream = supports.slice(0, 4).map((e) => name(e.source));
    const guards = (state.outgoing.get(hsId) || []).filter((e) => e.type === "CONSTRAINED_BY_GUARDRAIL").slice(0, 2).map((e) => e.target);
    const meas = chainMeasurements(hsId).slice(0, 3).map((m) => name(m));
    const segs = [];
    if (upstream.length) segs.push(`<span class="ch-node">${esc(upstream.join(" / "))}</span>`);
    segs.push(`<span class="ch-node">${esc(name(hsId))}</span>`);
    if (guards.length) segs.push(`constrained by <span class="ch-guard">${esc(guards.join(", "))}</span>`);
    if (meas.length) segs.push(`recommends <span class="ch-node">${esc(meas.join(", "))}</span>`);
    paths.push({ hsId, text: segs.join(' <span class="ch-arrow">&rarr;</span> '), plain: `${upstream.join(" / ")} -> ${name(hsId)}${guards.length ? " | guardrails: " + guards.join(", ") : ""}${meas.length ? " | measure: " + meas.join(", ") : ""}` });
  }
  return paths;
}

function selectInEvidenceMap(id) {
  const node = state.nodeById.get(id);
  if (!node) return;
  $all("#em-list .node-item").forEach((li) => li.classList.toggle("selected", li.dataset.id === id));
  const detail = $("#em-detail");
  const paths = pathsThroughNode(id);
  const pathHtml = paths.length
    ? paths.map((p) => `<div class="path-card"><div class="pc-line">${p.text}</div>
        <div class="pc-actions"><button class="copy-btn" data-copy="${esc(p.plain)}">Copy path</button>
        <button class="copy-btn" data-jump="${esc(p.hsId)}">Open hidden state</button></div></div>`).join("")
    : `<p class="empty-note">No hidden-state path runs through this node. Use the edges below to traverse.</p>`;
  const head = `<div class="detail-head"><div><h3>${esc(node.label)}</h3><div class="detail-id">${esc(node.id)}</div></div><span class="tag type">${esc(node.type)}</span></div>`;
  detail.innerHTML = head +
    `<div class="detail-section"><h4>Paths involving this node</h4>${pathHtml}</div>`;
  // append full node detail below
  const more = document.createElement("div");
  renderNodeDetail(node, more, { allowJump: true });
  // strip duplicate head from more
  detail.appendChild(more);
  $all("[data-copy]", detail).forEach((b) => b.addEventListener("click", () => {
    const txt = b.getAttribute("data-copy");
    navigator.clipboard?.writeText(txt).then(() => { b.textContent = "Copied"; setTimeout(() => (b.textContent = "Copy path"), 1200); }).catch(() => {});
  }));
  $all("[data-jump]", detail).forEach((b) => b.addEventListener("click", () => selectInEvidenceMap(b.getAttribute("data-jump"))));
}

function renderPagination(sel, page, pages, onGo) {
  const el = $(sel);
  el.innerHTML = "";
  const prev = document.createElement("button");
  prev.textContent = "‹ Prev"; prev.disabled = page <= 0;
  prev.addEventListener("click", () => onGo(page - 1));
  const next = document.createElement("button");
  next.textContent = "Next ›"; next.disabled = page >= pages - 1;
  next.addEventListener("click", () => onGo(page + 1));
  const info = document.createElement("span");
  info.className = "page-info"; info.textContent = `Page ${page + 1} of ${pages}`;
  el.append(prev, info, next);
}

/* ================================================================== */
/* Hidden States (Part 7)                                              */
/* ================================================================== */
function attachHiddenStates() {
  ["#hs-search", "#hs-filter-pipeline", "#hs-filter-confidence", "#hs-filter-domain"]
    .forEach((sel) => $(sel).addEventListener("input", renderHiddenStates));
  renderHiddenStates();
}

function renderHiddenStates() {
  const q = $("#hs-search").value.trim().toLowerCase();
  const fp = $("#hs-filter-pipeline").value, fc = $("#hs-filter-confidence").value, fd = $("#hs-filter-domain").value;
  const list = $("#hs-list");
  list.innerHTML = "";
  const states = state.graph.nodes.filter((n) => n.type === "hidden_state").filter((n) => {
    if (fp && n.pipeline_status !== fp) return false;
    if (fc && n.confidence !== fc) return false;
    if (fd && !(n.metadata.domains || [n.domain]).includes(fd)) return false;
    if (q && !(n.id + " " + n.label + " " + n.description).toLowerCase().includes(q)) return false;
    return true;
  }).sort((a, b) => a.label.localeCompare(b.label));
  for (const n of states) {
    const card = document.createElement("li");
    card.className = "state-card";
    card.dataset.id = n.id;
    card.innerHTML =
      `<div class="sc-head"><h3>${esc(n.label)}</h3><span class="tag ${pipeClass(n.pipeline_status)}">${esc(n.pipeline_status)}</span></div>` +
      `<p class="sc-desc">${esc(n.description || "")}</p>` +
      `<div class="sc-tags"><span class="tag ${confClass(n.confidence)}">confidence: ${esc(n.confidence)}</span>` +
      (n.domain ? `<span class="tag">${esc(n.domain)}</span>` : "") + `</div>`;
    card.addEventListener("click", () => {
      $all("#hs-list .state-card").forEach((c) => c.classList.toggle("selected", c.dataset.id === n.id));
      renderHiddenStateDetail(n);
    });
    list.appendChild(card);
  }
  if (!states.length) list.innerHTML = `<p class="empty-note">No hidden states match.</p>`;
}

function renderHiddenStateDetail(node) {
  const inc = state.incoming.get(node.id) || [];
  const out = state.outgoing.get(node.id) || [];
  const supportEdges = inc.filter((e) => e.type === "SUPPORTS_HIDDEN_STATE");
  const chainEdges = supportEdges.filter((e) => state.nodeById.get(e.source)?.type === "inference_chain");
  const paramEdges = supportEdges.filter((e) => state.nodeById.get(e.source)?.type === "measured_parameter");
  const variationEdges = supportEdges.filter((e) => state.nodeById.get(e.source)?.type === "result_variation");
  const guardrailEdges = out.filter((e) => e.type === "CONSTRAINED_BY_GUARDRAIL");
  const reduceEdges = inc.filter((e) => e.type === "CONTRADICTS_OR_REDUCES_CONFIDENCE");
  const measures = chainMeasurements(node.id);
  const md = node.metadata || {};
  const parts = [];
  parts.push(`<div class="detail-head"><div><h3>${esc(node.label)}</h3><div class="detail-id">${esc(node.id)}</div></div>
    <span class="tag ${pipeClass(node.pipeline_status)}">readiness: ${esc(node.pipeline_status)}</span></div>`);
  parts.push(`<p class="detail-desc">${esc(node.description || "")}</p>`);
  parts.push(`<dl class="kv"><dt>Confidence</dt><dd><span class="tag ${confClass(node.confidence)}">${esc(node.confidence)}</span></dd>
    <dt>Domains</dt><dd>${esc((md.domains || [node.domain]).join(", ")) || "—"}</dd>
    <dt>Output type</dt><dd>${esc(md.output_type || "traceable_hypothesis_with_uncertainty")}</dd></dl>`);
  parts.push(relSection("Supported by — inference chains", chainEdges, "in"));
  parts.push(relSection("Supporting measured parameters", paramEdges, "in"));
  parts.push(relSection("Supporting result variations", variationEdges, "in"));
  const notProve = (md.do_not_infer || []).map((x) => `<li>${esc(x)}</li>`).join("") || `<li>final_diagnosis</li><li>medical_conclusion</li>`;
  parts.push(`<div class="detail-section"><h4>What this does NOT prove</h4>
    <ul class="rel-list" style="font-family:var(--sans)">
    <li class="empty-note">A hidden state is a hypothesis, never a diagnosis. It cannot be inferred from a single marker or symptom report alone.</li>
    ${notProve}</ul></div>`);
  if (reduceEdges.length) parts.push(relSection("Signals that reduce confidence", reduceEdges, "in"));
  parts.push(relSection("Guardrails applied", guardrailEdges, "out"));
  parts.push(`<div class="detail-section"><h4>Missing data / next measurements</h4>` +
    (measures.length ? `<div class="chip-list">${measures.slice(0, 40).map((m) => `<span class="chip clickable" data-target="${esc(m)}">${esc(state.nodeById.get(m)?.label || m)}</span>`).join("")}</div>`
      : `<p class="empty-note">No specific next-measurement recorded; collect additional within-person baseline data.</p>`) + `</div>`);
  parts.push(`<div class="detail-section"><h4>Traceable chains</h4>` +
    (md.supporting_chains && md.supporting_chains.length
      ? `<div class="chip-list">${md.supporting_chains.map((c) => `<span class="chip clickable" data-target="chain::${esc(c)}">${esc(c)}</span>`).join("")}</div>`
      : (chainEdges.length ? `<div class="chip-list">${chainEdges.map((e) => `<span class="chip clickable" data-target="${esc(e.source)}">${esc(state.nodeById.get(e.source)?.label || e.source)}</span>`).join("")}</div>`
        : `<p class="empty-note">No standalone supporting chains recorded (readiness ${esc(node.pipeline_status)}).</p>`)) + `</div>`);
  parts.push(sectionChips("Source files", node.source_files));
  parts.push(sectionChips("Source tree IDs", node.source_tree_ids));
  const detail = $("#hs-detail");
  detail.innerHTML = parts.join("");
  $all(".rel-item[data-target], .chip[data-target]", detail).forEach((el) => el.addEventListener("click", () => jumpToNode(el.getAttribute("data-target"))));
}

/* ================================================================== */
/* Parameters (Part 7)                                                 */
/* ================================================================== */
function attachParameters() {
  ["#param-search", "#param-filter-domain", "#param-filter-tree", "#param-filter-evidence", "#param-filter-guardrails", "#param-filter-review"]
    .forEach((sel) => $(sel).addEventListener("input", () => { state.paramPage = 0; renderParameters(); }));
  renderParameters();
}
function paramHasGuardrails(n) {
  return (state.outgoing.get(n.id) || []).some((e) => e.type === "CONSTRAINED_BY_GUARDRAIL")
    || (n.metadata.guardrail_texts && n.metadata.guardrail_texts.length);
}
function renderParameters() {
  const q = $("#param-search").value.trim().toLowerCase();
  const fd = $("#param-filter-domain").value, ft = $("#param-filter-tree").value;
  const fe = $("#param-filter-evidence").value, fg = $("#param-filter-guardrails").value, fr = $("#param-filter-review").value;
  let params = state.graph.nodes.filter((n) => n.type === "measured_parameter").filter((n) => {
    if (fd && n.domain !== fd) return false;
    if (ft && !n.source_tree_ids.includes(ft)) return false;
    if (fe && n.evidence_strength !== fe) return false;
    if (fg === "yes" && !paramHasGuardrails(n)) return false;
    if (fg === "no" && paramHasGuardrails(n)) return false;
    if (fr === "yes" && n.pipeline_status === "ready") return false;
    if (fr === "no" && n.pipeline_status !== "ready") return false;
    if (q) {
      const hay = (n.id + " " + n.label + " " + n.domain + " " + (n.metadata.aliases || []).join(" ")).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  }).sort((a, b) => a.label.localeCompare(b.label));
  $("#param-count").textContent = `${params.length} parameter(s) match`;
  const size = state.paramPageSize;
  const pages = Math.max(1, Math.ceil(params.length / size));
  if (state.paramPage >= pages) state.paramPage = 0;
  const slice = params.slice(state.paramPage * size, state.paramPage * size + size);
  const list = $("#param-list");
  list.innerHTML = "";
  for (const n of slice) list.appendChild(nodeListItem(n, () => {
    $all("#param-list .node-item").forEach((li) => li.classList.toggle("selected", li.dataset.id === n.id));
    renderParamDetail(n);
  }));
  renderPagination("#param-pagination", state.paramPage, pages, (p) => { state.paramPage = p; renderParameters(); });
}
function renderParamDetail(node) {
  const out = state.outgoing.get(node.id) || [];
  const variations = out.filter((e) => e.type === "HAS_VARIATION").map((e) => state.nodeById.get(e.target)).filter(Boolean);
  const hiddenStates = out.filter((e) => e.type === "SUPPORTS_HIDDEN_STATE");
  const guardrails = out.filter((e) => e.type === "CONSTRAINED_BY_GUARDRAIL");
  const contexts = out.filter((e) => e.type === "REQUIRES_CONTEXT");
  const md = node.metadata || {};
  const parts = [];
  parts.push(`<div class="detail-head"><div><h3>${esc(node.label)}</h3><div class="detail-id">${esc(node.id)}</div></div>
    <span class="tag ${confClass(node.evidence_strength)}">${esc(node.evidence_strength)}</span></div>`);
  if (node.description) parts.push(`<p class="detail-desc">${esc(node.description)}</p>`);
  parts.push(`<dl class="kv"><dt>Domain</dt><dd>${esc(node.domain) || "—"}</dd>
    <dt>Readiness</dt><dd><span class="tag ${pipeClass(node.pipeline_status)}">${esc(node.pipeline_status)}</span></dd>
    <dt>Measurement types</dt><dd>${esc((md.measurement_types || []).join(", ")) || "—"}</dd>
    <dt>Sample / sensor</dt><dd>${esc((md.sample_or_sensor || []).join(", ")) || "—"}</dd></dl>`);
  // What it can support
  parts.push(`<div class="detail-section"><h4>What it can support</h4>` +
    (hiddenStates.length ? `<div class="chip-list">${hiddenStates.map((e) => `<span class="chip clickable" data-target="${esc(e.target)}">${esc(state.nodeById.get(e.target)?.label || e.target)}</span>`).join("")}</div>`
      : `<p class="empty-note">No direct hidden-state support recorded.</p>`) + `</div>`);
  // What it cannot prove alone
  parts.push(`<div class="detail-section"><h4>What it cannot prove alone</h4>
    <ul class="rel-list" style="font-family:var(--sans)">
    <li class="empty-note">A single parameter never equals a mechanism (single_marker_never_equals_mechanism).</li>
    ${(md.do_not_infer || ["diagnosis", "medical_conclusion"]).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`);
  // Required context
  parts.push(`<div class="detail-section"><h4>Required context</h4>` +
    (contexts.length ? `<div class="chip-list">${contexts.map((e) => `<span class="chip clickable" data-target="${esc(e.target)}">${esc(state.nodeById.get(e.target)?.label || e.target)}</span>`).join("")}</div>`
      : (md.requires_context ? `<p class="empty-note">Requires context for correct interpretation.</p>` : `<p class="empty-note">No specific context edges recorded.</p>`)) + `</div>`);
  // Variations
  if (variations.length) {
    const vitems = variations.map((v) => {
      const dirs = (v.metadata.direction || "").split("|").filter(Boolean).map((d) => `<span class="tag">${esc(d)}</span>`).join(" ");
      return `<li class="rel-item" data-target="${esc(v.id)}"><strong>${esc(v.label)}</strong> ${dirs}</li>`;
    }).join("");
    parts.push(`<div class="detail-section"><h4>Result variations (${variations.length})</h4><ul class="rel-list">${vitems}</ul></div>`);
  }
  parts.push(relSection("Guardrails", guardrails, "out"));
  // Measurements that reduce uncertainty
  const measures = new Set();
  for (const he of hiddenStates) for (const m of chainMeasurements(he.target)) measures.add(m);
  parts.push(`<div class="detail-section"><h4>Measurements that reduce uncertainty</h4>` +
    (measures.size ? `<div class="chip-list">${Array.from(measures).slice(0, 30).map((m) => `<span class="chip clickable" data-target="${esc(m)}">${esc(state.nodeById.get(m)?.label || m)}</span>`).join("")}</div>`
      : `<p class="empty-note">No linked next-measurement.</p>`) + `</div>`);
  parts.push(sectionChips("Source files", node.source_files));
  parts.push(sectionChips("Source tree IDs", node.source_tree_ids));
  const detail = $("#param-detail");
  detail.innerHTML = parts.join("");
  $all(".rel-item[data-target], .chip[data-target]", detail).forEach((el) => el.addEventListener("click", () => jumpToNode(el.getAttribute("data-target"))));
}

/* ================================================================== */
/* Guardrails (Part 7)                                                 */
/* ================================================================== */
function attachGuardrails() {
  $("#guardrail-search").addEventListener("input", renderGuardrails);
  $("#guardrail-filter").addEventListener("change", renderGuardrails);
  renderGuardrails();
}
function renderGuardrails() {
  const q = $("#guardrail-search").value.trim().toLowerCase();
  const filter = $("#guardrail-filter").value;
  const grid = $("#guardrail-list");
  grid.innerHTML = "";
  const guardrails = state.graph.nodes.filter((n) => n.type === "guardrail").filter((n) => {
    if (filter === "required" && !n.metadata.is_required) return false;
    if (filter === "core" && !CORE_GUARDRAILS.includes(n.id)) return false;
    if (q && !(n.id + " " + n.description).toLowerCase().includes(q)) return false;
    return true;
  }).sort((a, b) => {
    const ac = CORE_GUARDRAILS.includes(a.id) ? 0 : 1, bc = CORE_GUARDRAILS.includes(b.id) ? 0 : 1;
    return ac - bc || a.id.localeCompare(b.id);
  });
  for (const n of guardrails) {
    const isCore = CORE_GUARDRAILS.includes(n.id);
    const constrains = (state.incoming.get(n.id) || []).filter((e) => e.type === "CONSTRAINED_BY_GUARDRAIL");
    const states = constrains.map((e) => state.nodeById.get(e.source)).filter((x) => x && x.type === "hidden_state");
    const card = document.createElement("div");
    card.className = "guardrail-card" + (isCore ? " core" : "");
    card.innerHTML =
      `<h3>${esc(n.id)} ${isCore ? '<span class="core-badge">CORE</span>' : ""}</h3>` +
      `<p class="gc-text">${esc(n.description)}</p>` +
      `<div class="gc-why"><span class="gw-key">Prevents the false inference</span>${esc(guardrailPrevents(n))}</div>` +
      `<div class="gc-meta"><span class="tag">${n.metadata.is_required ? "required" : "supporting"}</span>` +
      `<span class="tag">constrains ${constrains.length} path(s)</span>` +
      `<span class="tag">${states.length} hidden state(s)</span></div>` +
      (states.length ? `<div class="gc-meta">${states.slice(0, 8).map((s) => `<span class="chip clickable" data-id="${esc(s.id)}">${esc(s.label)}</span>`).join("")}</div>` : "");
    $all(".chip.clickable", card).forEach((c) => c.addEventListener("click", () => jumpToNode(c.getAttribute("data-id"))));
    grid.appendChild(card);
  }
  if (!guardrails.length) grid.innerHTML = `<p class="empty-note">No guardrails match.</p>`;
}
function guardrailPrevents(n) {
  // Plain-language statement of the false inference each guardrail blocks.
  const id = n.id;
  if (/single_marker/.test(id)) return "that one abnormal marker proves a mechanism.";
  if (/symptom_report/.test(id)) return "that a self-reported symptom alone establishes a mechanism.";
  if (/medication_timing/.test(id)) return "that a signal is physiologic before medication/timing effects are excluded.";
  if (/context_override/.test(id)) return "that a mechanism is concluded before context (medication, environment) is evaluated.";
  if (/unknown_is_not_negative/.test(id)) return "that missing data is the same as a normal/negative result.";
  if (/hydration_intake/.test(id)) return "that fluid intake equals hydration status.";
  if (/wearable_sleep_stage/.test(id)) return "that wearable sleep staging confirms true sleep architecture.";
  if (/immune_marker/.test(id)) return "that an immune/inflammatory marker proves infection without symptoms.";
  if (/environmental_exposure/.test(id)) return "that an environmental exposure is the same as a physiologic effect.";
  if (/pain_limited/.test(id)) return "that pain-limited performance equals muscle weakness.";
  if (/low_activity/.test(id)) return "that low activity equals fatigue.";
  if (/PEM_not_normal_fatigue/.test(id)) return "that normal post-exertional fatigue equals post-exertional malaise.";
  if (/normal_one_source/.test(id)) return "that one normal source rules out a hypothesis.";
  if (/within_person/.test(id)) return "that group reference ranges override within-person baselines.";
  return "an over-interpretation of the underlying signal beyond what is supported.";
}

/* ================================================================== */
/* Corpus / Coverage (Part 6)                                          */
/* ================================================================== */
function renderCorpus() {
  const s = state.graph.stats;
  const m = state.graph.metadata || {};
  $("#corpus-meta").textContent = `${m.scientific_name || ""} — assembled from existing sources. Build ${(m.build_timestamp || "").slice(0, 19)}.`;
  const cards = [
    { label: "Total Nodes", value: s.node_count },
    { label: "Total Edges", value: s.edge_count },
    { label: "Measured Parameters", value: s.measured_parameter_count },
    { label: "Hidden States", value: s.hidden_state_count },
    { label: "Guardrails", value: s.guardrail_count },
    { label: "Source Trees", value: s.source_tree_count },
    { label: "Needs Review", value: s.needs_review_count, cls: "warn" },
    { label: "Low-Confidence Edges", value: s.low_confidence_edge_count, cls: "low" },
  ];
  const grid = $("#corpus-cards");
  grid.innerHTML = "";
  for (const c of cards) {
    const div = document.createElement("div");
    div.className = "summary-card" + (c.cls ? " " + c.cls : "");
    div.innerHTML = `<div class="value">${c.value}</div><div class="label">${esc(c.label)}</div>`;
    grid.appendChild(div);
  }
  renderBarChart("#corpus-nodes-type", Object.entries(s.nodes_by_type).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ label: k, value: v })));
  renderBarChart("#corpus-edges-type", Object.entries(s.edges_by_type).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ label: k, value: v })));
  renderBarChart("#corpus-readiness", ["ready", "partial", "needs_review"].filter((k) => k in (s.pipeline_status_distribution_nodes || {}))
    .map((k) => ({ label: k, value: s.pipeline_status_distribution_nodes[k], fillClass: "p-" + k })));
  renderBarChart("#corpus-confidence", ["high", "moderate", "low", "unknown"].filter((k) => k in (s.confidence_distribution_edges || {}))
    .map((k) => ({ label: k, value: s.confidence_distribution_edges[k], fillClass: "c-" + k })));

  // Hidden-state coverage: supported (ready) vs partial vs needs_review.
  const hs = state.graph.nodes.filter((n) => n.type === "hidden_state");
  const hsCov = { ready: 0, partial: 0, needs_review: 0 };
  for (const n of hs) hsCov[n.pipeline_status] = (hsCov[n.pipeline_status] || 0) + 1;
  renderBarChart("#corpus-hs-coverage", Object.entries(hsCov).map(([k, v]) => ({ label: k === "ready" ? "supported (ready)" : k, value: v, fillClass: "p-" + k })));

  // Guardrail coverage: required vs supporting; constrained vs unused.
  const guards = state.graph.nodes.filter((n) => n.type === "guardrail");
  const required = guards.filter((g) => g.metadata.is_required).length;
  const constrained = guards.filter((g) => (state.incoming.get(g.id) || []).some((e) => e.type === "CONSTRAINED_BY_GUARDRAIL")).length;
  renderBarChart("#corpus-guardrail-coverage", [
    { label: "total guardrails", value: guards.length },
    { label: "required", value: required, fillClass: "p-ready" },
    { label: "actively constraining", value: constrained, fillClass: "c-moderate" },
  ]);

  // Most connected parameters / hidden states (by degree).
  const degree = (id) => (state.outgoing.get(id) || []).length + (state.incoming.get(id) || []).length;
  const topParams = state.graph.nodes.filter((n) => n.type === "measured_parameter")
    .map((n) => ({ label: n.label, value: degree(n.id) })).sort((a, b) => b.value - a.value).slice(0, 12);
  renderBarChart("#corpus-top-params", topParams);
  const topHs = hs.map((n) => ({ label: n.label, value: degree(n.id) })).sort((a, b) => b.value - a.value).slice(0, 12);
  renderBarChart("#corpus-top-hs", topHs);

  // Source tree contribution.
  const treeCounts = new Map();
  for (const n of state.graph.nodes) for (const t of (n.source_tree_ids || [])) treeCounts.set(t, (treeCounts.get(t) || 0) + 1);
  const topTrees = Array.from(treeCounts.entries()).map(([k, v]) => ({ label: k, value: v })).sort((a, b) => b.value - a.value).slice(0, 20);
  renderBarChart("#corpus-source-trees", topTrees);
}

function renderBarChart(container, entries, opts = {}) {
  const el = $(container);
  el.innerHTML = "";
  const max = Math.max(1, ...entries.map((e) => e.value));
  for (const e of entries) {
    const row = document.createElement("div");
    row.className = "bar-row";
    const pct = (e.value / max) * 100;
    const fillClass = e.fillClass ? " " + e.fillClass : "";
    row.innerHTML =
      `<span class="bar-label" title="${esc(e.label)}">${esc(e.label)}</span>` +
      `<span class="bar-track"><span class="bar-fill${fillClass}" style="width:${pct}%"></span></span>` +
      `<span class="bar-value">${e.value}</span>`;
    el.appendChild(row);
  }
}

/* ================================================================== */
/* Source Traceability (Part 8)                                        */
/* ================================================================== */
function attachTraceability() {
  $("#trace-search").addEventListener("input", renderTraceability);
  renderTraceability();
}

function computeTraceRows() {
  const rows = new Map();
  const ensure = (key, kind) => {
    if (!rows.has(key)) rows.set(key, { key, kind, role: "", nodes: 0, edges: 0, hiddenStates: new Set(), params: new Set(), guardrails: new Set() });
    return rows.get(key);
  };
  for (const n of state.graph.nodes) {
    if (n.type === "source_file") { const r = ensure(n.id.replace(/^file::/, ""), "source_file"); r.role = n.domain || (n.description.match(/Role=([\w_]+)/) || [])[1] || ""; }
    if (n.type === "source_tree") { const r = ensure(n.id.replace(/^tree::/, ""), "source_tree"); r.role = n.domain; }
  }
  for (const n of state.graph.nodes) {
    for (const f of n.source_files || []) {
      const r = ensure(f, "source_file"); r.nodes++;
      if (n.type === "hidden_state") r.hiddenStates.add(n.id);
      if (n.type === "measured_parameter") r.params.add(n.id);
      if (n.type === "guardrail") r.guardrails.add(n.id);
    }
    for (const t of n.source_tree_ids || []) {
      const r = ensure(t, "source_tree"); r.nodes++;
      if (n.type === "hidden_state") r.hiddenStates.add(n.id);
      if (n.type === "measured_parameter") r.params.add(n.id);
      if (n.type === "guardrail") r.guardrails.add(n.id);
    }
  }
  for (const e of state.graph.edges) {
    for (const f of e.source_files || []) ensure(f, "source_file").edges++;
    for (const t of e.source_tree_ids || []) ensure(t, "source_tree").edges++;
  }
  return Array.from(rows.values());
}

function renderTraceability() {
  if (!state.traceRows) state.traceRows = computeTraceRows();
  const q = $("#trace-search").value.trim().toLowerCase();
  let rows = state.traceRows;
  if (q) {
    rows = rows.filter((r) => {
      if (r.key.toLowerCase().includes(q)) return true;
      // search by parameter or hidden state label/id within this source
      for (const pid of r.params) { const n = state.nodeById.get(pid); if ((pid + " " + (n?.label || "")).toLowerCase().includes(q)) return true; }
      for (const hid of r.hiddenStates) { const n = state.nodeById.get(hid); if ((hid + " " + (n?.label || "")).toLowerCase().includes(q)) return true; }
      return false;
    });
  }
  rows = rows.slice().sort((a, b) => b.nodes - a.nodes);
  $("#trace-count").textContent = `${rows.length} source file(s) / tree(s)`;
  const body = $("#trace-body");
  body.innerHTML = "";
  for (const r of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td class="fname">${esc(r.key)}</td>` +
      `<td><span class="tag type">${esc(r.kind)}</span></td>` +
      `<td>${esc(r.role || "—")}</td>` +
      `<td class="num">${r.nodes}</td>` +
      `<td class="num">${r.edges}</td>` +
      `<td class="num">${r.params.size}</td>` +
      `<td class="num">${r.hiddenStates.size}</td>` +
      `<td class="num">${r.guardrails.size}</td>`;
    body.appendChild(tr);
  }
  if (!rows.length) body.innerHTML = `<tr><td colspan="8" class="empty-note">No matches.</td></tr>`;
}

/* ---------------- boot ---------------- */
document.addEventListener("DOMContentLoaded", loadGraph);
