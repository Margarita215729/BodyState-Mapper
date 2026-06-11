# THSI Static Scientific Edges v0.1

This file defines the first traceable edge layer for the THSI Static Scientific Evidence Graph.

Core rule: no direct diagnostic biomarker-to-disorder edges are allowed. Physiological observations must pass through intermediate mechanisms before reaching cautious psychological state hypotheses.

Generated: 2026-06-08 19:06 UTC

Total edges: 21

## hrv_reduced_to_autonomic_regulation_shift

- **Path:** `reduced_hrv_relative_to_baseline` → `autonomic_regulation_shift`
- **Relationship:** `SUPPORTS`
- **Domain:** `HRV_autonomic_regulation`
- **Evidence strength score:** 4
- **Confidence prior:** 0.78
- **Risk of overinterpretation:** `medium`
- **Source IDs:** shaffer_ginsberg_2017_hrv_metrics_norms
- **Main finding:** HRV is a useful non-invasive marker of autonomic regulation when interpreted relative to protocol, context, and personal baseline.
- **Limitations:** Not emotion-specific; Affected by respiration, age, fitness, illness, medication, and device quality; Requires baseline-sensitive interpretation
- **Context requirements:** Personal baseline; Recording duration; Respiration/activity context; Medication/illness screening
- **Forbidden direct inference:** reduced_hrv_relative_to_baseline_to_anxiety_diagnosis; reduced_hrv_relative_to_baseline_to_depression_diagnosis

## low_resting_hrv_to_mental_health_related_autonomic_dysregulation

- **Path:** `low_resting_hrv` → `mental_health_related_autonomic_dysregulation`
- **Relationship:** `MAY_INDICATE`
- **Domain:** `HRV_autonomic_regulation`
- **Evidence strength score:** 5
- **Confidence prior:** 0.62
- **Risk of overinterpretation:** `high`
- **Source IDs:** wang_2025_hrv_mental_disorders_umbrella_review
- **Main finding:** Lower HRV is associated with several mental-health-related conditions at group level, but the signal is non-specific and cannot identify a diagnosis.
- **Limitations:** High heterogeneity across disorders and HRV metrics; Population-level association; Not usable as a standalone individual diagnosis
- **Context requirements:** Repeated measurements; Functional context; Psychological/subjective data; Exclusion of confounders
- **Forbidden direct inference:** low_resting_hrv_to_any_psychiatric_diagnosis

## persistent_low_hrv_to_depressive_like_pattern_contextual

- **Path:** `persistent_low_hrv` → `depressive_like_pattern_contextual`
- **Relationship:** `WEAKLY_SUPPORTS`
- **Domain:** `HRV_autonomic_regulation`
- **Evidence strength score:** 5
- **Confidence prior:** 0.46
- **Risk of overinterpretation:** `high`
- **Source IDs:** wu_2023_hrv_rest_depression_meta_analysis, wang_2025_hrv_mental_disorders_umbrella_review
- **Main finding:** Persistent low HRV may support a depression-like physiological pattern only when combined with mood, energy, sleep, activity, and longitudinal context.
- **Limitations:** Not diagnostic; Can reflect many physiological states; Confounded by sleep, medication, cardiovascular status, and fitness
- **Context requirements:** Low mood report; Reduced activity; Sleep disruption; Longitudinal persistence; Clinical screening if used in care context
- **Forbidden direct inference:** persistent_low_hrv_to_major_depressive_disorder

## increased_eda_to_sympathetic_arousal

- **Path:** `increased_eda` → `sympathetic_arousal`
- **Relationship:** `SUPPORTS`
- **Domain:** `EDA_sympathetic_arousal`
- **Evidence strength score:** 4
- **Confidence prior:** 0.74
- **Risk of overinterpretation:** `high`
- **Source IDs:** sosa_2026_beyond_eda_multimodal_sns_arousal
- **Main finding:** EDA is a useful anchor signal for sympathetic arousal, but its interpretation improves when combined with other physiological and contextual signals.
- **Limitations:** EDA is not emotion-specific; Sensitive to temperature, movement, skin contact, sweat gland physiology, and cognitive load
- **Context requirements:** Motion/contact quality; Temperature context; Activity context; Co-markers such as HRV/PPG/skin temperature
- **Forbidden direct inference:** increased_eda_to_anxiety_diagnosis; increased_eda_to_stress_diagnosis

## wearable_multimodal_features_to_stress_state_prediction

- **Path:** `wearable_multimodal_features` → `stress_state_prediction`
- **Relationship:** `MAY_INDICATE`
- **Domain:** `wearable_stress_detection`
- **Evidence strength score:** 4
- **Confidence prior:** 0.52
- **Risk of overinterpretation:** `high`
- **Source IDs:** vos_2023_wearable_stress_monitoring_systematic_review, sosa_2026_beyond_eda_multimodal_sns_arousal
- **Main finding:** Multimodal wearable features can support stress-state prediction, but generalization across people, protocols, and contexts remains a major limitation.
- **Limitations:** Generalization problem; Small/heterogeneous datasets; Label noise; Context dependence; Risk of overfitting to protocol-specific stressors
- **Context requirements:** Personal baseline; Clear label definition; Activity and environmental context; Model uncertainty reporting
- **Forbidden direct inference:** wearable_multimodal_features_to_clinical_stress_diagnosis

## sleep_loss_to_emotion_regulation_impairment

- **Path:** `sleep_loss` → `emotion_regulation_impairment`
- **Relationship:** `INCREASES_PROBABILITY_OF`
- **Domain:** `sleep_emotion_regulation`
- **Evidence strength score:** 5
- **Confidence prior:** 0.82
- **Risk of overinterpretation:** `medium`
- **Source IDs:** palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, vandekerckhove_wang_2017_emotion_regulation_sleep
- **Main finding:** Sleep loss reliably worsens emotional functioning and should be modeled as a major upstream modulator of emotional regulation capacity.
- **Limitations:** Does not identify a specific emotion or diagnosis; Effects vary by sleep-loss type and individual vulnerability; Bidirectional sleep-emotion effects are possible
- **Context requirements:** Sleep duration/quality metrics; Previous-night and multi-night context; Subjective energy/mood; Illness/pain/medication screening
- **Forbidden direct inference:** sleep_loss_to_depression_diagnosis; sleep_loss_to_anxiety_diagnosis

## sleep_restriction_to_negative_mood_increase

- **Path:** `sleep_restriction` → `negative_mood_increase`
- **Relationship:** `INCREASES_PROBABILITY_OF`
- **Domain:** `sleep_mood`
- **Evidence strength score:** 5
- **Confidence prior:** 0.76
- **Risk of overinterpretation:** `medium`
- **Source IDs:** tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, palmer_2024_sleep_loss_emotion_meta_analysis
- **Main finding:** Sleep restriction/deprivation increases vulnerability to negative mood states and reduces positive mood.
- **Limitations:** Mood effects are not diagnosis-specific; Acute and chronic sleep restriction may differ; Population and experimental setting matter
- **Context requirements:** Sleep history; Baseline mood; Timing of measurement; Stress/activity context
- **Forbidden direct inference:** sleep_restriction_to_mood_disorder

## sleep_loss_to_reduced_positive_affect

- **Path:** `sleep_loss` → `reduced_positive_affect`
- **Relationship:** `INCREASES_PROBABILITY_OF`
- **Domain:** `sleep_mood`
- **Evidence strength score:** 5
- **Confidence prior:** 0.78
- **Risk of overinterpretation:** `medium`
- **Source IDs:** tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, palmer_2024_sleep_loss_emotion_meta_analysis
- **Main finding:** Sleep loss is linked to lower positive affect, making low-energy or low-positive-affect hypotheses more plausible when context agrees.
- **Limitations:** Not specific to depression; Can be mediated by fatigue, illness, pain, or medication; Requires within-person comparison
- **Context requirements:** Subjective energy; Sleep duration and fragmentation; Recent illness/pain; Baseline affect
- **Forbidden direct inference:** sleep_loss_to_depression_diagnosis

## sleep_disturbance_to_increased_emotional_reactivity

- **Path:** `sleep_disturbance` → `increased_emotional_reactivity`
- **Relationship:** `SUPPORTS`
- **Domain:** `sleep_emotion_regulation`
- **Evidence strength score:** 3
- **Confidence prior:** 0.64
- **Risk of overinterpretation:** `medium`
- **Source IDs:** vandekerckhove_wang_2017_emotion_regulation_sleep, palmer_2024_sleep_loss_emotion_meta_analysis
- **Main finding:** Sleep disturbance can increase emotional reactivity and weaken regulation, but causality may be bidirectional.
- **Limitations:** Narrative mechanism source; Bidirectional stress-sleep effects; Needs temporal sequencing
- **Context requirements:** Temporal order; Stress context; Baseline sleep quality; Subjective report
- **Forbidden direct inference:** sleep_disturbance_to_any_psychiatric_diagnosis

## acute_sleep_deprivation_to_cortisol_elevation_contextual

- **Path:** `acute_sleep_deprivation` → `cortisol_elevation`
- **Relationship:** `MAY_INDICATE`
- **Domain:** `sleep_cortisol`
- **Evidence strength score:** 5
- **Confidence prior:** 0.38
- **Risk of overinterpretation:** `high`
- **Source IDs:** chen_2024_acute_sleep_deprivation_cortisol_meta_analysis
- **Main finding:** The relationship between acute sleep deprivation and cortisol is mixed/contextual; this edge should remain weak and explicitly uncertain.
- **Limitations:** Total cortisol effects may be non-significant; Sampling medium and timing matter; Acute deprivation differs from chronic sleep disruption
- **Context requirements:** Sampling medium; Time of day; Baseline cortisol; Sleep deprivation protocol
- **Forbidden direct inference:** acute_sleep_deprivation_to_chronic_stress

## salivary_cortisol_increase_to_hpa_axis_activation

- **Path:** `salivary_cortisol_increase` → `hpa_axis_activation`
- **Relationship:** `SUPPORTS`
- **Domain:** `HPA_axis_cortisol`
- **Evidence strength score:** 5
- **Confidence prior:** 0.81
- **Risk of overinterpretation:** `medium`
- **Source IDs:** gu_2022_tsst_salivary_cortisol_meta_analysis
- **Main finding:** Salivary cortisol increases support HPA-axis activation, especially in structured acute psychosocial stress paradigms.
- **Limitations:** Time of day, sex, sample timing, and protocol features influence response; Cortisol is not a direct psychological-state marker
- **Context requirements:** Sampling timing; Baseline sample; Time of day; Sex/hormonal context; Acute stressor context
- **Forbidden direct inference:** salivary_cortisol_increase_to_anxiety_diagnosis; salivary_cortisol_increase_to_chronic_stress_diagnosis

## social_evaluative_threat_to_acute_psychosocial_stress_response

- **Path:** `social_evaluative_threat_context` → `acute_psychosocial_stress_response`
- **Relationship:** `SUPPORTS`
- **Domain:** `acute_psychosocial_stress`
- **Evidence strength score:** 4
- **Confidence prior:** 0.78
- **Risk of overinterpretation:** `medium`
- **Source IDs:** allen_2017_tsst_principles_practice, frisch_2015_tsst_social_threat_paradigm
- **Main finding:** Social-evaluative threat and uncontrollability are central contextual features that support acute psychosocial stress-response inference.
- **Limitations:** Laboratory paradigm may not map directly to everyday contexts; Requires context evidence, not physiology alone
- **Context requirements:** Evaluation threat; Task demand; Uncontrollability/novelty; Temporal proximity
- **Forbidden direct inference:** social_evaluative_threat_context_to_anxiety_disorder

## acute_psychosocial_stress_response_to_hpa_axis_activation

- **Path:** `acute_psychosocial_stress_response` → `hpa_axis_activation`
- **Relationship:** `INCREASES_PROBABILITY_OF`
- **Domain:** `HPA_axis_cortisol`
- **Evidence strength score:** 5
- **Confidence prior:** 0.73
- **Risk of overinterpretation:** `medium`
- **Source IDs:** gu_2022_tsst_salivary_cortisol_meta_analysis, allen_2017_tsst_principles_practice
- **Main finding:** Acute psychosocial stress responses can involve HPA-axis activation, measurable through salivary cortisol under appropriate sampling conditions.
- **Limitations:** Not all stressors produce the same cortisol response; Habituation and individual differences matter
- **Context requirements:** Stressor type; Sampling schedule; Baseline comparison; Repeated exposure/habituation
- **Forbidden direct inference:** hpa_axis_activation_to_psychiatric_diagnosis

## repeated_stress_responses_to_stress_adaptation_response

- **Path:** `repeated_stress_responses` → `stress_adaptation_response`
- **Relationship:** `SUPPORTS`
- **Domain:** `allostasis`
- **Evidence strength score:** 3
- **Confidence prior:** 0.7
- **Risk of overinterpretation:** `medium`
- **Source IDs:** mcewen_2007_stress_adaptation_brain, mcewen_2000_allostasis_allostatic_load_neuropsychopharmacology
- **Main finding:** Stress responses are adaptive regulatory processes involving brain, autonomic, neuroendocrine, immune, cardiovascular, and metabolic systems.
- **Limitations:** Theoretical framework; Requires operational biomarkers for individual measurement
- **Context requirements:** Repeated or prolonged exposure; Multi-system markers; Time course
- **Forbidden direct inference:** repeated_stress_responses_to_disease_diagnosis

## multi_system_dysregulation_to_allostatic_load

- **Path:** `multi_system_dysregulation` → `allostatic_load`
- **Relationship:** `SUPPORTS`
- **Domain:** `allostatic_load_measurement`
- **Evidence strength score:** 5
- **Confidence prior:** 0.76
- **Risk of overinterpretation:** `medium`
- **Source IDs:** beese_2022_allostatic_load_measurement_review_of_reviews, mcewen_2000_allostasis_allostatic_load_neuropsychopharmacology, mcewen_2007_stress_adaptation_brain
- **Main finding:** Allostatic load is best represented as multi-system dysregulation, operationalized through composite biomarkers rather than one signal.
- **Limitations:** No single universal allostatic load formula; Biomarker panels vary; Cross-sectional scores may miss temporal dynamics
- **Context requirements:** Multi-system biomarker panel; Personal or population reference ranges; Longitudinal trend if available
- **Forbidden direct inference:** single_biomarker_to_allostatic_load

## allostatic_load_to_health_risk_state

- **Path:** `allostatic_load` → `health_risk_state`
- **Relationship:** `INCREASES_PROBABILITY_OF`
- **Domain:** `allostatic_load_measurement`
- **Evidence strength score:** 5
- **Confidence prior:** 0.68
- **Risk of overinterpretation:** `medium`
- **Source IDs:** beese_2022_allostatic_load_measurement_review_of_reviews, mcewen_2000_allostasis_allostatic_load_neuropsychopharmacology
- **Main finding:** Higher allostatic load can represent increased physiological risk burden, but it should be treated as a risk state rather than a diagnosis.
- **Limitations:** Measurement heterogeneity; Different biomarker panels produce different scores; Health-risk inference needs clinical validation
- **Context requirements:** Validated biomarker set; Age/sex/reference context; Longitudinal comparison
- **Forbidden direct inference:** allostatic_load_to_specific_disease_diagnosis

## autonomic_regulation_shift_to_recovery_deficit

- **Path:** `autonomic_regulation_shift` → `recovery_deficit`
- **Relationship:** `MAY_INDICATE`
- **Domain:** `HRV_autonomic_regulation`
- **Evidence strength score:** 4
- **Confidence prior:** 0.58
- **Risk of overinterpretation:** `medium`
- **Source IDs:** shaffer_ginsberg_2017_hrv_metrics_norms, mcewen_2007_stress_adaptation_brain
- **Main finding:** Autonomic shifts may support a recovery-deficit interpretation when paired with poor sleep, low energy, or repeated stress context.
- **Limitations:** Mechanistic bridge edge; Needs co-markers; Not specific to psychological fatigue
- **Context requirements:** Sleep metrics; Activity load; Subjective fatigue/energy; Illness screening
- **Forbidden direct inference:** autonomic_regulation_shift_to_burnout_diagnosis

## sympathetic_arousal_to_acute_arousal_state

- **Path:** `sympathetic_arousal` → `acute_arousal_state`
- **Relationship:** `SUPPORTS`
- **Domain:** `EDA_sympathetic_arousal`
- **Evidence strength score:** 4
- **Confidence prior:** 0.66
- **Risk of overinterpretation:** `high`
- **Source IDs:** sosa_2026_beyond_eda_multimodal_sns_arousal, allen_2017_tsst_principles_practice
- **Main finding:** Sympathetic arousal supports an acute physiological arousal state, not a specific emotion.
- **Limitations:** Arousal can reflect stress, cognitive load, excitement, pain, heat, or movement; Needs context disambiguation
- **Context requirements:** Activity/temperature context; Task context; Co-markers; Subjective label if available
- **Forbidden direct inference:** sympathetic_arousal_to_anxiety_diagnosis

## emotion_regulation_impairment_to_anxiety_like_arousal_state_contextual

- **Path:** `emotion_regulation_impairment` → `anxiety_like_arousal_state`
- **Relationship:** `WEAKLY_SUPPORTS`
- **Domain:** `sleep_emotion_regulation`
- **Evidence strength score:** 5
- **Confidence prior:** 0.49
- **Risk of overinterpretation:** `high`
- **Source IDs:** palmer_2024_sleep_loss_emotion_meta_analysis, vandekerckhove_wang_2017_emotion_regulation_sleep
- **Main finding:** Impaired emotion regulation can support anxiety-like arousal as a hypothesis only when physiological arousal and subjective/contextual evidence agree.
- **Limitations:** Bridge to psychological hypothesis; Not diagnostic; Many alternative explanations
- **Context requirements:** Physiological arousal; Subjective anxiety/stress or threat context; Sleep history; Alternative-explanation screening
- **Forbidden direct inference:** emotion_regulation_impairment_to_anxiety_disorder

## recovery_deficit_to_fatigue_like_state

- **Path:** `recovery_deficit` → `fatigue_like_state`
- **Relationship:** `SUPPORTS`
- **Domain:** `sleep_mood`
- **Evidence strength score:** 5
- **Confidence prior:** 0.61
- **Risk of overinterpretation:** `medium`
- **Source IDs:** palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, shaffer_ginsberg_2017_hrv_metrics_norms
- **Main finding:** Recovery deficit can support a fatigue-like state hypothesis when sleep, autonomic, activity, and subjective-energy evidence align.
- **Limitations:** Fatigue has many causes; Needs medical/medication/illness context; Not equivalent to chronic fatigue diagnosis
- **Context requirements:** Low energy report; Sleep loss or fragmentation; Reduced activity or autonomic recovery markers; Illness and medication context
- **Forbidden direct inference:** recovery_deficit_to_chronic_fatigue_syndrome

## negative_mood_increase_to_irritability_vulnerability

- **Path:** `negative_mood_increase` → `irritability_vulnerability`
- **Relationship:** `MAY_INDICATE`
- **Domain:** `sleep_mood`
- **Evidence strength score:** 5
- **Confidence prior:** 0.52
- **Risk of overinterpretation:** `medium`
- **Source IDs:** tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, palmer_2024_sleep_loss_emotion_meta_analysis
- **Main finding:** Increased negative mood after poor sleep may support irritability vulnerability as a state hypothesis, not as a trait or diagnosis.
- **Limitations:** Not specific to irritability; Needs subjective/behavioral confirmation; May reflect pain, stressor exposure, or illness
- **Context requirements:** Subjective mood; Recent sleep loss; Behavioral context; Pain/illness/stressor screening
- **Forbidden direct inference:** negative_mood_increase_to_personality_trait
