# Static Graph Query Result v0.1

**Input nodes:** sleep_loss, increased_eda, reduced_hrv_relative_to_baseline
**Max depth:** 4

## Reachable summary

- Total reachable nodes: 11
- Mechanisms: 4
- Bridge nodes: 2
- Risk states: 0
- State hypotheses: 2
- Paths: 8

### Reachable mechanisms
- `acute_arousal_state`
- `autonomic_regulation_shift`
- `recovery_deficit`
- `sympathetic_arousal`

### Reachable bridge nodes
- `emotion_regulation_impairment`
- `reduced_positive_affect`

### Reachable psychological state hypotheses
- `anxiety_like_arousal_state`
- `fatigue_like_state`

## Sample paths

### Path 1
- **Sequence:** sleep_loss → emotion_regulation_impairment
- **Edges:** sleep_loss_to_emotion_regulation_impairment
- **Sources:** palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, vandekerckhove_wang_2017_emotion_regulation_sleep

### Path 2
- **Sequence:** sleep_loss → reduced_positive_affect
- **Edges:** sleep_loss_to_reduced_positive_affect
- **Sources:** palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses

### Path 3
- **Sequence:** increased_eda → sympathetic_arousal
- **Edges:** increased_eda_to_sympathetic_arousal
- **Sources:** sosa_2026_beyond_eda_multimodal_sns_arousal

### Path 4
- **Sequence:** reduced_hrv_relative_to_baseline → autonomic_regulation_shift
- **Edges:** hrv_reduced_to_autonomic_regulation_shift
- **Sources:** shaffer_ginsberg_2017_hrv_metrics_norms

### Path 5
- **Sequence:** sleep_loss → emotion_regulation_impairment → anxiety_like_arousal_state
- **Edges:** sleep_loss_to_emotion_regulation_impairment, emotion_regulation_impairment_to_anxiety_like_arousal_state_contextual
- **Sources:** palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, vandekerckhove_wang_2017_emotion_regulation_sleep

### Path 6
- **Sequence:** increased_eda → sympathetic_arousal → acute_arousal_state
- **Edges:** increased_eda_to_sympathetic_arousal, sympathetic_arousal_to_acute_arousal_state
- **Sources:** allen_2017_tsst_principles_practice, sosa_2026_beyond_eda_multimodal_sns_arousal

### Path 7
- **Sequence:** reduced_hrv_relative_to_baseline → autonomic_regulation_shift → recovery_deficit
- **Edges:** hrv_reduced_to_autonomic_regulation_shift, autonomic_regulation_shift_to_recovery_deficit
- **Sources:** mcewen_2007_stress_adaptation_brain, shaffer_ginsberg_2017_hrv_metrics_norms

### Path 8
- **Sequence:** reduced_hrv_relative_to_baseline → autonomic_regulation_shift → recovery_deficit → fatigue_like_state
- **Edges:** hrv_reduced_to_autonomic_regulation_shift, autonomic_regulation_shift_to_recovery_deficit, recovery_deficit_to_fatigue_like_state
- **Sources:** mcewen_2007_stress_adaptation_brain, palmer_2024_sleep_loss_emotion_meta_analysis, shaffer_ginsberg_2017_hrv_metrics_norms, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses
