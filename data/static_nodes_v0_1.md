# Static Nodes v0.1

Typed node registry inferred from `static_scientific_edges_v0_1.json`.
All nodes have `clinical_diagnosis: false`. Psychological outputs are state hypotheses only.

**Total nodes:** 33

| node_id | node_type | label | domain | allowed_as_input | allowed_as_output | edges |
| --- | --- | --- | --- | --- | --- | --- |
| acute_arousal_state | physiological_mechanism | Acute Arousal State | EDA_sympathetic_arousal | False | True | 1 |
| acute_psychosocial_stress_response | physiological_mechanism | Acute Psychosocial Stress Response | HPA_axis_cortisol | False | True | 2 |
| acute_sleep_deprivation | observable_marker | Acute Sleep Deprivation | sleep_cortisol | True | False | 1 |
| allostatic_load | physiological_mechanism | Allostatic Load | allostasis | False | True | 2 |
| anxiety_like_arousal_state | psychological_state_hypothesis | Anxiety Like Arousal State | sleep_emotion_regulation | False | True | 1 |
| autonomic_regulation_shift | physiological_mechanism | Autonomic Regulation Shift | HRV_autonomic_regulation | False | True | 2 |
| cortisol_elevation | biochemical_marker | Cortisol Elevation | sleep_cortisol | False | False | 1 |
| depressive_like_pattern_contextual | neurobiological_affective_bridge | Depressive Like Pattern Contextual | HRV_autonomic_regulation | False | True | 1 |
| emotion_regulation_impairment | neurobiological_affective_bridge | Emotion Regulation Impairment | sleep_emotion_regulation | False | True | 2 |
| fatigue_like_state | psychological_state_hypothesis | Fatigue Like State | sleep_mood | False | True | 1 |
| health_risk_state | risk_state | Health Risk State | allostatic_load_measurement | False | True | 1 |
| hpa_axis_activation | physiological_mechanism | Hpa Axis Activation | HPA_axis_cortisol | False | True | 2 |
| increased_eda | observable_marker | Increased Eda | EDA_sympathetic_arousal | True | False | 1 |
| increased_emotional_reactivity | neurobiological_affective_bridge | Increased Emotional Reactivity | sleep_emotion_regulation | False | True | 1 |
| irritability_vulnerability | psychological_state_hypothesis | Irritability Vulnerability | sleep_mood | False | True | 1 |
| low_resting_hrv | observable_marker | Low Resting Hrv | HRV_autonomic_regulation | True | False | 1 |
| mental_health_related_autonomic_dysregulation | physiological_mechanism | Mental Health Related Autonomic Dysregulation | HRV_autonomic_regulation | False | True | 1 |
| multi_system_dysregulation | physiological_mechanism | Multi System Dysregulation | allostasis | False | True | 1 |
| negative_mood_increase | neurobiological_affective_bridge | Negative Mood Increase | sleep_mood | False | True | 2 |
| persistent_low_hrv | observable_marker | Persistent Low Hrv | HRV_autonomic_regulation | True | False | 1 |
| recovery_deficit | physiological_mechanism | Recovery Deficit | HRV_autonomic_regulation | False | True | 2 |
| reduced_hrv_relative_to_baseline | observable_marker | Reduced Hrv Relative To Baseline | HRV_autonomic_regulation | True | False | 1 |
| reduced_positive_affect | neurobiological_affective_bridge | Reduced Positive Affect | sleep_emotion_regulation | False | True | 1 |
| repeated_stress_responses | physiological_mechanism | Repeated Stress Responses | allostasis | False | True | 1 |
| salivary_cortisol_increase | observable_marker | Salivary Cortisol Increase | HPA_axis_cortisol | True | False | 1 |
| sleep_disturbance | observable_marker | Sleep Disturbance | sleep_emotion_regulation | True | False | 1 |
| sleep_loss | observable_marker | Sleep Loss | sleep_emotion_regulation | True | False | 2 |
| sleep_restriction | observable_marker | Sleep Restriction | sleep_mood | True | False | 1 |
| social_evaluative_threat_context | context_node | Social Evaluative Threat Context | HPA_axis_cortisol | True | False | 1 |
| stress_adaptation_response | physiological_mechanism | Stress Adaptation Response | allostasis | False | True | 1 |
| stress_state_prediction | risk_state | Stress State Prediction | wearable_stress_detection | False | True | 1 |
| sympathetic_arousal | physiological_mechanism | Sympathetic Arousal | EDA_sympathetic_arousal | False | True | 2 |
| wearable_multimodal_features | model_feature_node | Wearable Multimodal Features | EDA_sympathetic_arousal | True | False | 1 |
