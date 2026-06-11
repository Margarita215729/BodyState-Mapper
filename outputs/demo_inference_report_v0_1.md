# THSI Inference Report v0.1

**Inference ID:** demo_inference_v0_1
**Subject:** demo_subject_001
**Created:** 2026-06-08T19:42:29.257446+00:00

## Input observations

### obs_demo_001
- **Node:** `sleep_loss` (Sleep Loss)
- **Value:** true
- **Source:** manual_input
- **Quality score:** 0.9
- **Notes:** Demo observation for testing sleep-loss pathway.

### obs_demo_002
- **Node:** `increased_eda` (Increased Eda)
- **Value:** true
- **Source:** wearable
- **Quality score:** 0.7
- **Notes:** Demo observation for testing sympathetic arousal pathway.

### obs_demo_003
- **Node:** `reduced_hrv_relative_to_baseline` (Reduced Hrv Relative To Baseline)
- **Value:** true
- **Source:** wearable
- **Quality score:** 0.75
- **Notes:** Demo observation for testing autonomic regulation pathway.

## Supported mechanisms

- **Sleep Loss:** Observed sleep loss may support pathways involving emotion regulation impairment and reduced positive affect, and may be compatible with recovery-related mechanism chains when combined with other signals.
- **Increased Eda:** Observed increased EDA may support sympathetic arousal and acute arousal mechanism pathways; EDA is not emotion-specific and requires context.
- **Reduced Hrv Relative To Baseline:** Observed reduced HRV relative to baseline may support autonomic regulation shift and downstream recovery-deficit mechanism pathways; interpretation requires baseline-sensitive context.
- **Acute Arousal State:** Reachable via evidence paths from observed inputs.
- **Autonomic Regulation Shift:** Reachable via evidence paths from observed inputs.
- **Recovery Deficit:** Reachable via evidence paths from observed inputs.
- **Sympathetic Arousal:** Reachable via evidence paths from observed inputs.

## Cautious state hypotheses

### Fatigue Like State
- **Preliminary score:** 0.451
- **Interpretation:** Observed `reduced_hrv_relative_to_baseline` (among other inputs) supports literature-backed pathways that may be compatible with a cautious 'Fatigue Like State' hypothesis (preliminary score 0.45). Primary supporting path: reduced_hrv_relative_to_baseline → autonomic_regulation_shift → recovery_deficit → fatigue_like_state. This reflects evidence-linked mechanism traversal, not a clinical conclusion; context is required and alternative explanations remain possible.
- **Supporting paths:** 1
  - Path (score 0.451): reduced_hrv_relative_to_baseline → autonomic_regulation_shift → recovery_deficit → fatigue_like_state
    Sources: mcewen_2007_stress_adaptation_brain, palmer_2024_sleep_loss_emotion_meta_analysis, shaffer_ginsberg_2017_hrv_metrics_norms, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses
- **Limitations:**
  - Not emotion-specific
  - Affected by respiration, age, fitness, illness, medication, and device quality
  - Requires baseline-sensitive interpretation
  - Mechanistic bridge edge
  - Needs co-markers
  - Not specific to psychological fatigue
- **Warning:** This is a cautious state hypothesis, not a clinical conclusion.

### Anxiety Like Arousal State
- **Preliminary score:** 0.447
- **Interpretation:** Observed `sleep_loss` (among other inputs) supports literature-backed pathways that may be compatible with a cautious 'Anxiety Like Arousal State' hypothesis (preliminary score 0.45). Primary supporting path: sleep_loss → emotion_regulation_impairment → anxiety_like_arousal_state. This reflects evidence-linked mechanism traversal, not a clinical conclusion; context is required and alternative explanations remain possible.
- **Supporting paths:** 1
  - Path (score 0.447): sleep_loss → emotion_regulation_impairment → anxiety_like_arousal_state
    Sources: palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, vandekerckhove_wang_2017_emotion_regulation_sleep
- **Limitations:**
  - Does not identify a specific emotion or diagnosis
  - Effects vary by sleep-loss type and individual vulnerability
  - Bidirectional sleep-emotion effects are possible
  - Bridge to psychological hypothesis
  - Not diagnostic
  - Many alternative explanations
- **Warning:** This is a cautious state hypothesis, not a clinical conclusion.

## Evidence paths

### Path 1 (score 0.627)
sleep_loss
→ emotion_regulation_impairment
- Sources: palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, vandekerckhove_wang_2017_emotion_regulation_sleep

### Path 2 (score 0.597)
sleep_loss
→ reduced_positive_affect
- Sources: palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses

### Path 3 (score 0.451)
reduced_hrv_relative_to_baseline
→ autonomic_regulation_shift
→ recovery_deficit
→ fatigue_like_state
- Sources: mcewen_2007_stress_adaptation_brain, palmer_2024_sleep_loss_emotion_meta_analysis, shaffer_ginsberg_2017_hrv_metrics_norms, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses

### Path 4 (score 0.447)
sleep_loss
→ emotion_regulation_impairment
→ anxiety_like_arousal_state
- Sources: palmer_2024_sleep_loss_emotion_meta_analysis, tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses, vandekerckhove_wang_2017_emotion_regulation_sleep

### Path 5 (score 0.423)
reduced_hrv_relative_to_baseline
→ autonomic_regulation_shift
- Sources: shaffer_ginsberg_2017_hrv_metrics_norms

### Path 6 (score 0.421)
reduced_hrv_relative_to_baseline
→ autonomic_regulation_shift
→ recovery_deficit
- Sources: mcewen_2007_stress_adaptation_brain, shaffer_ginsberg_2017_hrv_metrics_norms

### Path 7 (score 0.323)
increased_eda
→ sympathetic_arousal
→ acute_arousal_state
- Sources: allen_2017_tsst_principles_practice, sosa_2026_beyond_eda_multimodal_sns_arousal

### Path 8 (score 0.286)
increased_eda
→ sympathetic_arousal
- Sources: sosa_2026_beyond_eda_multimodal_sns_arousal

## Limitations

- EDA is not emotion-specific
- HRV is not diagnosis-specific
- sleep loss does not identify a specific disorder
- fatigue has many causes
- context is required
- Does not identify a specific emotion or diagnosis
- Effects vary by sleep-loss type and individual vulnerability
- Bidirectional sleep-emotion effects are possible
- Not specific to depression
- Can be mediated by fatigue, illness, pain, or medication
- Requires within-person comparison
- Not emotion-specific
- Affected by respiration, age, fitness, illness, medication, and device quality
- Requires baseline-sensitive interpretation
- Mechanistic bridge edge

## Warning

This is not a medical diagnosis. All psychological outputs are cautious state hypotheses that require context, may change with additional observations, and must not be read as proof of any disorder or clinical condition.
