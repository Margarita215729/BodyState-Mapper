# BodyState Mapper — Data Intake Template v0.1

## 1. General Data Intake Logic

Each incoming data unit must be converted not only into a value, but into a structured observation object:

```text
raw input
→ normalized parameter
→ source type
→ timestamp / phase
→ baseline comparison
→ result variation
→ possible interpretations
→ required context
→ candidate hidden states
→ guardrails
→ next measurement recommendation
```

The system does not treat a parameter as a direct truth. It treats it as an **observation with context, limitations, and uncertainty**.

---

## 2. Universal Observation Object

Every measurement should be normalized into this structure:

```json
{
  "observation_id": "obs_000001",
  "user_id": "user_001",
  "timestamp": "2026-06-11T08:30:00-04:00",
  "timezone": "America/New_York",

  "data_source": {
    "source_category": "wearable",
    "source_name": "Apple Watch",
    "source_tree_id": "astro_data_tree_013",
    "device_model": "",
    "collection_method": "automatic",
    "data_quality": "good"
  },

  "parameter": {
    "parameter_id": "resting_heart_rate",
    "display_name": "Resting Heart Rate",
    "domain": "autonomic_cardiovascular",
    "unit": "bpm",
    "value": 82,
    "raw_value": 82,
    "normalized_value": 82,
    "reference_range": {
      "low": null,
      "high": null,
      "source": "device_or_lab_or_population_reference"
    }
  },

  "personal_baseline": {
    "baseline_available": true,
    "baseline_value": 62,
    "baseline_window": "last_30_days",
    "deviation_absolute": 20,
    "deviation_percent": 32.3,
    "deviation_direction": "increased",
    "deviation_severity": "moderate"
  },

  "temporal_context": {
    "mission_phase_or_life_phase": "routine_day",
    "relative_timing": "morning",
    "time_since_event": null,
    "event_context": [],
    "pattern_type": "acute_deviation"
  },

  "result_variation": {
    "variation_id": "elevated_resting_HR_relative_to_baseline",
    "direction": "increased",
    "interpretation_level": "context_required",
    "standalone_meaning": "Possible autonomic load, recovery strain, illness, dehydration, pain, medication effect, or recent exertion.",
    "not_enough_alone": true
  },

  "linked_context": {
    "required_context": [
      "HRV",
      "sleep_fragmentation",
      "temperature",
      "medication_timing",
      "pain",
      "hydration",
      "infection_symptoms",
      "recent_exercise"
    ],
    "available_context": [
      "HRV",
      "sleep_duration",
      "fatigue_report"
    ],
    "missing_context": [
      "temperature",
      "medication_timing",
      "pain",
      "CRP_or_CBC"
    ]
  },

  "candidate_hidden_states": [
    {
      "state_id": "low_recovery_state",
      "support_level": "moderate",
      "reason": "Resting HR is elevated relative to personal baseline and HRV is reduced."
    },
    {
      "state_id": "infectious_or_inflammatory_load",
      "support_level": "low",
      "reason": "Temperature and inflammatory markers are missing."
    }
  ],

  "guardrails_triggered": [
    "single_marker_never_equals_mechanism",
    "within_person_deviation_priority",
    "unknown_is_not_negative_evidence"
  ],

  "next_measurements": [
    {
      "measurement": "temperature",
      "reason": "Helps distinguish low recovery from possible illness/inflammatory load.",
      "priority": "high"
    },
    {
      "measurement": "medication_timing",
      "reason": "Medication or stimulant timing may explain HR/HRV deviation.",
      "priority": "high"
    }
  ],

  "confidence": {
    "data_quality_confidence": "moderate",
    "interpretation_confidence": "low_to_moderate",
    "reason": "Signal is meaningful relative to baseline but missing key context."
  }
}
```

---

## 3. Data Source Categories

The software should accept data from the following categories:

```json
{
  "accepted_source_categories": [
    "wearable",
    "manual_self_report",
    "clinical_lab",
    "urine_test",
    "stool_test",
    "saliva_test",
    "functional_test",
    "cognitive_test",
    "sleep_study",
    "imaging",
    "environment_sensor",
    "medication_log",
    "nutrition_log",
    "event_log",
    "mission_phase_log"
  ]
}
```

---

## 4. Wearable Intake Template

### Data to collect

```json
{
  "wearable_parameters": [
    "heart_rate",
    "resting_heart_rate",
    "HRV_RMSSD",
    "HRV_SDNN",
    "sleep_duration",
    "sleep_efficiency",
    "sleep_fragmentation",
    "WASO_estimate",
    "respiratory_rate",
    "SpO2",
    "skin_temperature",
    "body_temperature_proxy",
    "steps",
    "activity_minutes",
    "sedentary_time",
    "calories_estimate",
    "exercise_sessions",
    "recovery_score_if_available"
  ]
}
```

### Possible result variations

```json
{
  "wearable_result_variations": [
    "normal_relative_to_baseline",
    "increased_relative_to_baseline",
    "decreased_relative_to_baseline",
    "acute_spike",
    "persistent_drift",
    "high_day_to_day_variability",
    "low_signal_quality",
    "missing_or_partial_day",
    "device_changed",
    "not_interpretable_without_baseline"
  ]
}
```

### Example links

```text
elevated_RHR + low_HRV + fragmented_sleep
→ low_recovery_state

elevated_RHR + temperature_increase + fatigue
→ infectious_or_inflammatory_load_hypothesis

low_HRV + high_pain + poor_sleep
→ pain_sleep_fatigue_branch

normal_sleep_duration + high_fragmentation + next_day_fatigue
→ sleep_fragmentation_recovery_failure_branch

low_activity + low_strength + low_VO2
→ deconditioning_branch
```

### Guardrails

```text
Do not infer stress from HRV alone.
Do not infer infection from resting HR alone.
Do not infer sleep recovery from sleep duration alone.
Do not infer fatigue from low activity alone.
Do not compare wearable data across devices without a device-change flag.
```

---

## 5. Manual Self-Report Intake Template

### Data to collect

```json
{
  "self_report_parameters": [
    "fatigue",
    "sleepiness",
    "brain_fog",
    "dizziness",
    "pain_intensity",
    "pain_location",
    "headache",
    "migraine_features",
    "mood",
    "anxiety_like_symptoms",
    "irritability",
    "motivation",
    "GI_symptoms",
    "nausea",
    "shortness_of_breath",
    "palpitations",
    "orthostatic_symptoms",
    "sensory_sensitivity",
    "subjective_sleep_quality"
  ]
}
```

### Standard scale

```json
{
  "scale": {
    "0": "none",
    "1-2": "very_mild",
    "3-4": "mild",
    "5-6": "moderate",
    "7-8": "severe",
    "9-10": "extreme"
  }
}
```

### Possible result variations

```json
{
  "self_report_result_variations": [
    "absent",
    "mild",
    "moderate",
    "severe",
    "acute_onset",
    "persistent",
    "episodic",
    "delayed_after_trigger",
    "worse_after_exertion",
    "worse_after_meal",
    "worse_after_poor_sleep",
    "orthostatic_pattern",
    "circadian_pattern",
    "medication_timing_pattern",
    "unclear_pattern"
  ]
}
```

### Example links

```text
fatigue + sleepiness + short_sleep + PVT_lapses
→ acute_sleep_loss_branch

fatigue + normal_sleep + low_HRV + elevated_RHR
→ low_recovery_state

brain_fog + orthostatic_symptoms + HR_increase_on_standing
→ orthostatic_intolerance_branch

headache + photophobia + phonophobia + nausea + episodic_pattern
→ migraine_phenotype_branch

pain + sleep_fragmentation + next_day_fatigue
→ pain_sleep_fatigue_branch

fatigue + post_exertional_worsening + delayed_peak
→ PEM_hypothesis
```

### Guardrails

```text
Symptom report does not equal mechanism.
Fatigue is not the same as sleepiness.
Brain fog is not the same as objective cognitive impairment.
Dizziness is not automatically vestibular dysfunction.
Anxiety-like physiology is not automatically psychiatric anxiety.
Pain severity does not define pain mechanism.
```

---

## 6. Clinical Lab Intake Template

### Data to collect

```json
{
  "clinical_lab_parameters": [
    "hemoglobin",
    "hematocrit",
    "RBC_count",
    "MCV",
    "MCH",
    "MCHC",
    "RDW",
    "WBC_count",
    "neutrophils",
    "lymphocytes",
    "monocytes",
    "eosinophils",
    "platelets",
    "NLR",
    "PLR",
    "sodium",
    "potassium",
    "chloride",
    "bicarbonate_total_CO2",
    "anion_gap",
    "serum_osmolality",
    "BUN",
    "creatinine",
    "eGFR",
    "cystatin_C",
    "AST",
    "ALT",
    "ALP",
    "GGT",
    "bilirubin",
    "albumin",
    "total_protein",
    "glucose",
    "fasting_insulin",
    "HbA1c",
    "lipids",
    "lactate",
    "ketones",
    "ferritin",
    "TSAT",
    "B12",
    "MMA",
    "folate",
    "vitamin_D_25OH",
    "CRP",
    "ESR",
    "IL6",
    "TNF_alpha",
    "TSH",
    "free_T4",
    "free_T3",
    "cortisol",
    "sex_hormones"
  ]
}
```

### Possible result variations

```json
{
  "lab_result_variations": [
    "within_reference_range",
    "outside_reference_range_low",
    "outside_reference_range_high",
    "within_range_but_abnormal_for_personal_baseline",
    "borderline",
    "acute_change",
    "persistent_abnormality",
    "discordant_with_symptoms",
    "confounded_by_inflammation",
    "confounded_by_hydration",
    "confounded_by_medication",
    "requires_repeat_test",
    "requires_pairing_marker"
  ]
}
```

### Example links

```text
low_Hb + low_MCV/high_RDW + low_ferritin_or_low_TSAT
→ iron_deficiency_anemia_oxygen_delivery_branch

normal_Hb + low_ferritin + fatigue
→ iron_deficiency_without_anemia_branch

high_WBC_neutrophils + fever + high_CRP
→ acute_inflammatory_infection_branch

high_BUN_creatinine_ratio + high_urine_osmolality + orthostatic_tachycardia
→ hypovolemia_dehydration_hypothesis

low_B12 + high_MMA + cognitive_symptoms
→ functional_B12_deficiency_branch

high_TSH + low_free_T4 + fatigue/cold_intolerance
→ hypothyroid_context_branch

high_lactate_at_low_workload + exercise_intolerance
→ metabolic_strain_branch
```

### Guardrails

```text
Do not infer diagnosis from CBC/CMP alone.
Do not infer dehydration from sodium or BUN/creatinine alone.
Do not infer infection from WBC or CRP alone.
Do not infer liver injury from mild AST/ALT elevation without timing/context.
Do not infer nutrient deficiency from intake alone.
Do not infer thyroid dysfunction from fatigue alone.
A normal lab result does not rule out an unmeasured mechanism.
```

---

## 7. Urine / Stool / Saliva Intake Template

### Data to collect

```json
{
  "urine_parameters": [
    "urine_specific_gravity",
    "urine_osmolality",
    "urine_color",
    "urine_output",
    "urinary_sodium",
    "urinary_calcium",
    "urinary_creatinine",
    "ketones",
    "protein",
    "albumin_creatinine_ratio",
    "6_sulfatoxymelatonin",
    "oxidative_stress_markers"
  ],
  "stool_parameters": [
    "stool_frequency",
    "stool_form",
    "occult_blood",
    "calprotectin",
    "lactoferrin",
    "pancreatic_elastase",
    "fecal_fat",
    "microbiome_alpha_diversity",
    "microbiome_beta_diversity",
    "SCFA",
    "bile_acids",
    "pathogen_detection"
  ],
  "saliva_parameters": [
    "salivary_cortisol",
    "cortisol_slope",
    "salivary_alpha_amylase",
    "sIgA",
    "salivary_IL6",
    "oral_microbiome",
    "viral_reactivation_markers"
  ]
}
```

### Possible result variations

```json
{
  "biofluid_result_variations": [
    "normal",
    "elevated",
    "decreased",
    "concentrated",
    "diluted",
    "positive_detection",
    "negative_detection",
    "shifted_rhythm",
    "flattened_slope",
    "high_variability",
    "requires_context",
    "not_interpretable_single_sample"
  ]
}
```

### Example links

```text
high_urine_osmolality + low_fluid_intake + orthostatic_tachycardia
→ hypovolemia_dehydration_hypothesis

low_6_sulfatoxymelatonin + evening_light_exposure + sleep_delay
→ circadian_disruption_branch

high_calprotectin + GI_symptoms + CRP
→ intestinal_inflammation_branch

occult_blood_positive + low_Hb/ferritin
→ GI_blood_loss_iron_deficiency_branch

flattened_cortisol_slope + poor_sleep + fatigue/mood_worsening
→ HPA_circadian_disruption_branch

viral_DNA_detection + stress + immune_shift + fatigue
→ viral_reactivation_context_branch
```

### Guardrails

```text
Urine concentration alone does not equal dehydration.
Microbiome shift does not equal disease.
Firmicutes/Bacteroidetes ratio is not a reliable standalone marker.
Positive viral DNA does not equal symptomatic infection.
A single cortisol value does not define HPA-axis state.
Occult blood requires follow-up; it does not localize the source.
```

---

## 8. Functional / Cognitive / Sleep Study Intake Template

### Data to collect

```json
{
  "functional_parameters": [
    "orthostatic_HR_change",
    "orthostatic_BP_change",
    "grip_strength",
    "chair_stand",
    "TUG",
    "balance_score",
    "gait_speed",
    "VO2peak",
    "anaerobic_threshold",
    "oxygen_pulse",
    "ventilatory_efficiency",
    "lactate_response",
    "day2_CPET_change"
  ],
  "cognitive_parameters": [
    "PVT_lapses",
    "reaction_time",
    "working_memory",
    "attention",
    "executive_function",
    "error_rate",
    "subjective_brain_fog"
  ],
  "PSG_EEG_parameters": [
    "total_sleep_time_PSG",
    "sleep_efficiency_PSG",
    "WASO",
    "arousal_index",
    "N3_slow_wave_sleep",
    "REM_percent",
    "REM_latency",
    "AHI",
    "RDI",
    "ODI",
    "minimum_SpO2_during_sleep",
    "periodic_limb_movement_index",
    "sleep_spindle_density"
  ]
}
```

### Possible result variations

```json
{
  "functional_result_variations": [
    "normal",
    "impaired",
    "reduced_from_baseline",
    "pain_limited",
    "effort_limited",
    "medication_limited",
    "deconditioning_pattern",
    "orthostatic_pattern",
    "respiratory_limitation_pattern",
    "cardiac_output_limitation_pattern",
    "metabolic_limitation_pattern",
    "PEM_pattern",
    "discordant_subjective_objective"
  ]
}
```

### Example links

```text
orthostatic_HR_increase + dizziness + no_BP_drop
→ POTS_like_orthostatic_intolerance_branch

orthostatic_BP_drop + dizziness/syncope
→ orthostatic_hypotension_branch

low_VO2peak + low_oxygen_pulse
→ cardiac_output_limitation_branch

day2_CPET_decline + delayed_symptom_worsening
→ PEM_objective_branch

high_PVT_lapses + short_sleep + subjective_sleepiness
→ acute_sleep_loss_branch

high_WASO/arousal_index + normal_TST + fatigue
→ sleep_fragmentation_recovery_failure_branch

pain_limited_strength_test + injury_report
→ injury_context_override_branch
```

### Guardrails

```text
Low VO2peak is not a mechanism by itself.
Pain-limited performance is not muscle weakness.
Subjective brain fog is not objective cognitive impairment.
Normal one-day cognitive testing does not rule out intermittent brain fog.
Wearable sleep staging does not replace PSG.
PEM is not normal post-exercise tiredness.
Orthostatic symptoms require posture/timing context.
```

---

## 9. Context Intake Template

Context is not secondary. Context can override biological interpretation.

### Data to collect

```json
{
  "context_parameters": [
    "medication_name",
    "medication_dose",
    "medication_start_date",
    "medication_stop_date",
    "time_since_last_dose",
    "caffeine",
    "alcohol",
    "nicotine",
    "THC_or_other_substances",
    "recent_surgery",
    "recent_injury",
    "recent_infection",
    "vaccination",
    "menstrual_cycle_phase",
    "hormonal_contraception",
    "meal_timing",
    "fasting_status",
    "exercise_timing",
    "travel",
    "sleep_schedule_change",
    "light_exposure",
    "noise_exposure",
    "heat_exposure",
    "CO2_exposure",
    "air_quality",
    "mission_phase"
  ]
}
```

### Possible result variations

```json
{
  "context_variations": [
    "present",
    "absent",
    "unknown",
    "recent_change",
    "dose_change",
    "acute_exposure",
    "chronic_exposure",
    "temporally_aligned",
    "not_temporally_aligned",
    "possible_override",
    "confirmed_override"
  ]
}
```

### Example context overrides

```text
sedative_use + next_day_PVT_lapses
→ medication_sleepiness_context_override

beta_blocker_use + low_peak_HR_on_CPET
→ medication_chronotropic_override

opioid_or_tramadol_use + low_RR/sedation
→ medication_respiratory_risk_context_branch

high_CO2 + headache + PVT_lapses
→ environmental_CO2_performance_risk_branch

heat_exposure + elevated_core_temp + cognitive_slowing
→ heat_strain_branch

recent_surgery + pain + fatigue + medication_use
→ procedure_recovery_context_branch
```

### Guardrails

```text
Medication timing first.
Context override before mechanism.
Environmental exposure is not the same as physiological effect.
Recent procedure/injury can explain pain, sleep disruption, activity reduction, HR changes, and fatigue.
Menstrual cycle/hormonal context can shift temperature, HRV, mood, sleep, and symptoms.
```

---

## 10. Result Interpretation Levels

Each result should receive one interpretation level:

```json
{
  "interpretation_levels": [
    {
      "level": "standalone_low_value",
      "meaning": "Parameter is recorded but cannot support inference alone."
    },
    {
      "level": "context_required",
      "meaning": "Parameter may be meaningful only with required context."
    },
    {
      "level": "supportive_signal",
      "meaning": "Parameter supports a candidate state but does not establish it."
    },
    {
      "level": "strong_cross_modal_signal",
      "meaning": "Parameter plus context plus outcome strongly supports a chain."
    },
    {
      "level": "context_override",
      "meaning": "Parameter may override or reframe other interpretations."
    },
    {
      "level": "red_flag_or_safety_flag",
      "meaning": "Parameter may require urgent human review or medical escalation."
    },
    {
      "level": "not_interpretable",
      "meaning": "Data quality, missing units, missing timing, or device uncertainty prevents interpretation."
    }
  ]
}
```

---

## 11. Confidence Template

```json
{
  "confidence_rules": {
    "high": {
      "requires": [
        "measured input marker",
        "measured mediator_or_context",
        "measured outcome",
        "temporal alignment",
        "baseline or valid reference",
        "no unresolved major override"
      ]
    },
    "moderate": {
      "requires": [
        "two or more aligned sources",
        "some context available",
        "missing only non-critical fields"
      ]
    },
    "low": {
      "requires": [
        "single source or symptom-only pattern",
        "limited context",
        "missing timing or baseline"
      ]
    },
    "insufficient": {
      "requires": [
        "missing value",
        "missing unit",
        "missing timestamp",
        "poor data quality",
        "no interpretable context"
      ]
    }
  }
}
```

---

## 12. Standard Software Response Variations

The software should return one of these response types:

```json
{
  "response_variations": [
    {
      "response_type": "state_supported",
      "meaning": "Data supports a candidate hidden state with moderate/high confidence."
    },
    {
      "response_type": "state_possible_but_uncertain",
      "meaning": "Data is compatible with a state but missing key context."
    },
    {
      "response_type": "context_override_detected",
      "meaning": "Medication, environment, injury, procedure, or timing explains/reframes the pattern."
    },
    {
      "response_type": "conflicting_evidence",
      "meaning": "Data sources point in different directions; confidence is reduced."
    },
    {
      "response_type": "missing_data_blocks_inference",
      "meaning": "System cannot infer because required data is missing."
    },
    {
      "response_type": "normal_measured_but_not_ruleout",
      "meaning": "Available measured data is normal, but unmeasured mechanisms remain possible."
    },
    {
      "response_type": "next_measurement_needed",
      "meaning": "The most useful output is a recommendation for what to measure next."
    },
    {
      "response_type": "safety_escalation",
      "meaning": "Potentially dangerous pattern requiring human/clinical review."
    }
  ]
}
```

---

## 13. Output Report Template

```json
{
  "report_id": "report_000001",
  "generated_at": "2026-06-11T10:00:00-04:00",
  "summary": {
    "primary_response_type": "state_possible_but_uncertain",
    "main_candidate_state": "low_recovery_state",
    "confidence": "moderate",
    "plain_language_summary": "Your data pattern is most consistent with a low recovery state, but the mechanism is uncertain because temperature, medication timing, and inflammation markers are missing."
  },
  "supported_by": [
    {
      "parameter": "resting_heart_rate",
      "finding": "elevated relative to baseline",
      "role": "supportive_signal"
    },
    {
      "parameter": "HRV_RMSSD",
      "finding": "decreased relative to baseline",
      "role": "supportive_signal"
    },
    {
      "parameter": "sleep_fragmentation",
      "finding": "increased",
      "role": "possible_mediator"
    }
  ],
  "not_supported_or_not_proven": [
    "Does not prove infection.",
    "Does not prove dehydration.",
    "Does not prove psychiatric anxiety.",
    "Does not identify a diagnosis."
  ],
  "missing_data": [
    "temperature",
    "medication timing",
    "pain/headache status",
    "CBC/CRP if illness suspected"
  ],
  "next_best_measurements": [
    {
      "measurement": "temperature",
      "priority": "high",
      "reason": "Helps distinguish low recovery from possible illness/inflammatory load."
    },
    {
      "measurement": "medication/caffeine timing",
      "priority": "high",
      "reason": "Can explain HR/HRV and sleep changes."
    }
  ],
  "guardrails_applied": [
    "single_marker_never_equals_mechanism",
    "unknown_is_not_negative_evidence",
    "context_override_before_mechanism"
  ],
  "traceable_chains": [
    {
      "chain_id": "low_recovery_state_branch",
      "chain": "elevated_RHR + low_HRV + poor_sleep/fatigue -> low_recovery_state",
      "confidence": "moderate"
    }
  ]
}
```

---

## 14. Minimal MVP Intake Form

For the MVP, the minimum daily intake can be:

```json
{
  "date": "YYYY-MM-DD",
  "wearable": {
    "resting_heart_rate": null,
    "HRV_RMSSD": null,
    "sleep_duration": null,
    "sleep_fragmentation_or_WASO": null,
    "steps": null,
    "skin_temperature": null,
    "SpO2": null
  },
  "symptoms_0_10": {
    "fatigue": null,
    "sleepiness": null,
    "brain_fog": null,
    "dizziness": null,
    "pain": null,
    "headache": null,
    "mood_worse": null,
    "anxiety_like": null,
    "GI_symptoms": null
  },
  "context": {
    "medication_change": null,
    "caffeine_alcohol_or_substance": null,
    "recent_exercise": null,
    "recent_illness": null,
    "injury_or_procedure": null,
    "menstrual_cycle_phase": null,
    "unusual_light_noise_heat_CO2": null,
    "poor_food_or_fluid_intake": null
  },
  "optional_tests": {
    "temperature": null,
    "orthostatic_HR_BP": null,
    "PVT_or_reaction_time": null,
    "lab_results_available": false
  }
}
```

---

## 15. Minimal MVP Output

```json
{
  "primary_state_hypotheses": [],
  "confidence": "low|moderate|high|insufficient",
  "main_supporting_signals": [],
  "major_missing_data": [],
  "context_overrides": [],
  "guardrails": [],
  "next_best_measurements": [],
  "traceable_explanation": ""
}
```

---

## 16. Core Rule

The system must always preserve this logic:

```text
Data does not directly become a conclusion.

Data becomes:
observation
→ variation
→ possible chain
→ uncertainty-aware hypothesis
→ next measurement
→ traceable explanation
```
