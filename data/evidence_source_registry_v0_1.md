# THSI Evidence Source Registry v0.1

This file contains source cards for the Static Scientific Evidence Graph v0.1.

Core rule: no direct biomarker-to-diagnosis inference is allowed. Biomarkers must pass through physiological, biochemical, or neurobiological mechanism nodes before supporting cautious psychological state hypotheses.

## 1. gu_2022_tsst_salivary_cortisol_meta_analysis

**Title:** A meta-analysis of salivary cortisol responses in the Trier Social Stress Test to evaluate the effects of speech topics, sex, and sample size
**Authors:** Haixia Gu, Xue’er Ma, Jingjing Zhao, Chunyu Liu
**Year:** 2022
**Source type:** meta_analysis
**Domain:** HPA_axis_cortisol
**DOI:** 10.1016/j.cpnec.2022.100125
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9216334/
**PDF:** `A meta-analysis of salivary cortisol responses in the Trier Social Stress Test.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** medium

**Methodology:**
Meta-analysis of TSST studies that measured salivary cortisol before and after task completion. The authors examined cortisol reactivity and tested moderators including speech topic, sex, sample size, and sex-by-topic interactions.

**Main findings:**
- The TSST is a widely used laboratory paradigm for psychosocial stress induction.
- Salivary cortisol reactivity is usable as an objective HPA-axis marker in TSST contexts.
- Cortisol responses vary by sex and protocol features, so context and sampling design must be represented explicitly.
- Baseline and peak salivary cortisol values should be interpreted separately rather than collapsed into a generic stress score.

**Supported nodes:**
- `salivary_cortisol_increase`
- `hpa_axis_activation`
- `acute_psychosocial_stress_response`
- `social_evaluative_threat_context`

**Supported edges:**
- `salivary_cortisol_increase -> hpa_axis_activation`
- `acute_psychosocial_stress_response -> salivary_cortisol_reactivity`
- `TSST_protocol_features -> cortisol_response_moderation`

**Limitations:**
- Specific to TSST and related psychosocial stress protocols.
- Cortisol interpretation depends on timing, baseline sampling, sex, sample size, and task details.
- Does not support cortisol as a standalone detector of chronic stress or psychological diagnosis.

**Use in THSI:** Primary quantitative source for HPA-axis/cortisol edges under acute psychosocial stress conditions.
**Notes:** Use only when stress context and sampling timing are known or explicitly marked as missing.

## 2. mcewen_2000_allostasis_allostatic_load_neuropsychopharmacology

**Title:** Allostasis and allostatic load: implications for neuropsychopharmacology
**Authors:** Bruce S. McEwen
**Year:** 2000
**Source type:** theoretical_review
**Domain:** allostasis
**DOI:** 10.1016/S0893-133X(99)00129-3
**URL:** https://www.nature.com/articles/1395453
**PDF:** `Allostasis and Allostatic Load.pdf`
**Evidence strength:** 3
**Risk of overinterpretation:** high

**Methodology:**
Theoretical review synthesizing neuroendocrine, autonomic, behavioral, and brain-based mechanisms of stress adaptation and cumulative physiological burden.

**Main findings:**
- Allostasis describes adaptation through physiological change rather than fixed homeostasis.
- Stress mediators such as glucocorticoids and catecholamines are protective in the short term but costly when repeatedly or chronically activated.
- Allostatic load links stress biology, brain function, systemic disease risk, and psychiatric vulnerability.
- The brain is both an interpreter of environmental challenge and a target of stress mediators.

**Supported nodes:**
- `allostasis`
- `allostatic_load`
- `stress_adaptation_response`
- `multi_system_dysregulation`

**Supported edges:**
- `repeated_stress_responses -> allostatic_load`
- `stress_adaptation_response -> physiological_state_shift`
- `allostatic_load -> health_risk_state`

**Limitations:**
- Broad theoretical framework, not a quantitative biomarker validation study.
- Does not provide direct individual-level inference rules.
- Psychiatric disorder links require clinical evidence and cannot be inferred from biomarkers alone.

**Use in THSI:** Foundational conceptual source for allostasis/allostatic load nodes and multi-system interpretation.
**Notes:** Use to structure mechanisms, not to assign high-confidence psychological labels.

## 3. shaffer_ginsberg_2017_hrv_metrics_norms

**Title:** An Overview of Heart Rate Variability Metrics and Norms
**Authors:** Fred Shaffer, J. P. Ginsberg
**Year:** 2017
**Source type:** methodological_review
**Domain:** HRV_autonomic_regulation
**DOI:** 10.3389/fpubh.2017.00258
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/
**PDF:** `An Overview of Heart Rate variability.pdf`
**Evidence strength:** 4
**Risk of overinterpretation:** high

**Methodology:**
Review of HRV metrics, recording durations, physiological interpretation, and normative considerations across time-domain, frequency-domain, and nonlinear measures.

**Main findings:**
- HRV metrics differ in physiological meaning and should not be treated as interchangeable.
- HRV is a non-invasive marker of autonomic regulation, especially when interpreted relative to protocol and baseline.
- Recording duration, respiration, age, fitness, health status, medication, and measurement quality affect HRV interpretation.
- Ultra-short and short-term HRV measures require caution and are not equivalent to 24-hour recordings.

**Supported nodes:**
- `reduced_hrv_relative_to_baseline`
- `low_resting_hrv`
- `autonomic_regulation_shift`
- `parasympathetic_withdrawal`

**Supported edges:**
- `reduced_hrv_relative_to_baseline -> autonomic_regulation_shift`
- `hrv_metric_context -> hrv_interpretation_quality`
- `low_resting_hrv -> autonomic_regulation_shift`

**Limitations:**
- Methodological review, not a direct stress/emotion validation study.
- HRV is not specific to anxiety, depression, fatigue, or stress.
- Personal baseline and measurement protocol are mandatory for strong inference.

**Use in THSI:** Primary methodological source for HRV marker nodes and interpretation constraints.
**Notes:** Forbid direct biomarker-to-diagnosis edges from HRV.

## 4. beese_2022_allostatic_load_measurement_review_of_reviews

**Title:** Allostatic Load Measurement: A Systematic Review of Reviews, Database Inventory, and Considerations for Neighborhood Research
**Authors:** Shawna Beese, Julie Postma, Janessa M. Graves
**Year:** 2022
**Source type:** systematic_review_of_reviews
**Domain:** allostatic_load_measurement
**DOI:** 10.3390/ijerph192417006
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9779615/
**PDF:** `Beese_2022_Allostatic_Load_Measurement_Review_of_Reviews.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** medium

**Methodology:**
Systematic review of reviews and database inventory focused on how allostatic load is measured and operationalized, with attention to neighborhood and environmental stress research.

**Main findings:**
- Allostatic load is commonly operationalized through multi-system biomarker composites rather than a single marker.
- Measurement approaches vary substantially across studies and databases.
- Environmental and neighborhood stressors are relevant contexts for allostatic load research.
- Earlier-life allostatic load can be relevant to later health risk, but operationalization must be explicit.

**Supported nodes:**
- `allostatic_load`
- `multi_system_dysregulation`
- `biomarker_composite`
- `environmental_stressor_context`

**Supported edges:**
- `multi_system_dysregulation -> allostatic_load`
- `biomarker_composite -> allostatic_load_estimate`
- `measurement_protocol_variability -> allostatic_load_uncertainty`

**Limitations:**
- Allostatic load scoring is heterogeneous across studies.
- Biomarker availability strongly affects comparability.
- Not designed to infer momentary psychological states from wearable data.

**Use in THSI:** Primary source for operationalizing allostatic load as a multi-system construct.
**Notes:** Use to define allostatic load measurement metadata and uncertainty fields.

## 5. vandekerckhove_wang_2017_emotion_regulation_sleep

**Title:** Emotion, emotion regulation and sleep: An intimate relationship
**Authors:** Marie Vandekerckhove, Yu-lin Wang
**Year:** 2017
**Source type:** narrative_review
**Domain:** sleep_emotion_regulation
**DOI:** 10.3934/Neuroscience.2018.1.1
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7181893/
**PDF:** `Emotion, emotion regulation and sleep.pdf`
**Evidence strength:** 3
**Risk of overinterpretation:** medium

**Methodology:**
Narrative review synthesizing bidirectional evidence on sleep, emotion, emotional stress, dream-related processes, and emotion regulation.

**Main findings:**
- Sleep and emotion have a bidirectional relationship.
- Sleep loss can increase emotional arousal and sensitivity to stressful stimuli.
- Sleep quality and amount influence how people react to emotional events.
- Emotion regulation may modulate the effect of emotional stress on sleep.

**Supported nodes:**
- `sleep_disturbance`
- `emotion_regulation_impairment`
- `increased_emotional_reactivity`
- `emotional_stress`

**Supported edges:**
- `sleep_disturbance -> emotion_regulation_impairment`
- `sleep_loss -> increased_emotional_reactivity`
- `emotional_stress -> sleep_disturbance`
- `emotion_regulation_capacity -> sleep_quality_modulation`

**Limitations:**
- Narrative review, not a meta-analysis.
- Bidirectional mechanisms make causal direction context-dependent.
- Does not support direct diagnosis from sleep features.

**Use in THSI:** Mechanistic bridge source for sleep-emotion-emotion regulation paths.
**Notes:** Use alongside Palmer 2024 and Tomaso 2021 for stronger quantitative support.

## 6. vos_2023_wearable_stress_monitoring_systematic_review

**Title:** Generalizable Machine Learning for Stress Monitoring from Wearable Devices: A Systematic Literature Review
**Authors:** Gideon Vos, Kelly Trinh, Zoltan Sarnyai, Mostafa Rahimi Azghadi
**Year:** 2023
**Source type:** machine_learning_systematic_review
**Domain:** wearable_stress_detection
**DOI:** 10.1016/j.ijmedinf.2023.105026
**URL:** https://arxiv.org/abs/2209.15137
**PDF:** `Generalizable Machine Learning for Stress.pdf`
**Evidence strength:** 4
**Risk of overinterpretation:** critical

**Methodology:**
Systematic review of machine-learning approaches for stress monitoring from wearable devices, with emphasis on datasets, generalization, reproducibility, and deployment limitations.

**Main findings:**
- Wearable features can support stress monitoring but generalization remains difficult.
- Models often depend on limited datasets, heterogeneous protocols, and weak external validation.
- Subject-independent performance and reproducibility are central challenges.
- Personal baseline and uncertainty handling are necessary for responsible inference.

**Supported nodes:**
- `wearable_multimodal_features`
- `stress_state_prediction`
- `model_generalizability_limit`
- `personal_baseline_requirement`

**Supported edges:**
- `wearable_multimodal_features -> stress_state_prediction`
- `lack_of_personal_baseline -> reduced_model_generalizability`
- `protocol_heterogeneity -> reduced_evidence_transferability`

**Limitations:**
- ML stress labels vary across datasets and protocols.
- Wearable-only stress detection is not equivalent to psychological diagnosis.
- Generalization across individuals and contexts is a major unresolved problem.

**Use in THSI:** Methodological guardrail for wearable-based inference, baseline logic, and uncertainty design.
**Notes:** Use to justify personalized dynamic graph rather than universal classifier.

## 7. wang_2025_hrv_mental_disorders_umbrella_review

**Title:** Heart rate variability in mental disorders: an umbrella review of meta-analyses
**Authors:** Zuxing Wang, Yazhu Zou, Jingwen Liu, Wei Peng, Mingmei Li, Zhili Zou
**Year:** 2025
**Source type:** umbrella_review
**Domain:** HRV_autonomic_regulation
**DOI:** 10.1038/s41398-025-03339-x
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11953273/
**PDF:** `Heart rate variability in mental disorders.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** critical

**Methodology:**
Umbrella review summarizing meta-analytic evidence on HRV differences and treatment responses across mental disorders.

**Main findings:**
- HRV is widely studied in mental disorders but remains controversial and heterogeneous.
- Mental disorders can be associated with altered autonomic regulation as reflected in HRV.
- HRV findings are not disorder-specific enough for direct diagnosis.
- Treatment-related HRV changes require cautious interpretation due to differences across metrics and populations.

**Supported nodes:**
- `low_resting_hrv`
- `mental_health_related_autonomic_dysregulation`
- `autonomic_regulation_shift`

**Supported edges:**
- `low_resting_hrv -> mental_health_related_autonomic_dysregulation`
- `mental_disorder_context -> hrv_variability_across_populations`
- `hrv_metric_heterogeneity -> inference_uncertainty`

**Limitations:**
- Umbrella-level heterogeneity across disorders, metrics, and study designs.
- Does not justify individual diagnosis from HRV.
- Clinical context and symptom data are mandatory for psychological interpretation.

**Use in THSI:** Boundary-setting source: HRV may support autonomic dysregulation, not direct disorder detection.
**Notes:** Use to enforce intermediate mechanism nodes between HRV and psychological hypotheses.

## 8. wu_2023_hrv_rest_depression_meta_analysis

**Title:** Heart rate variability status at rest in adult depressed patients: a systematic review and meta-analysis
**Authors:** Q. Wu, et al.
**Year:** 2023
**Source type:** meta_analysis
**Domain:** HRV_autonomic_regulation
**DOI:** 10.3389/fpubh.2023.1243213
**URL:** https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2023.1243213/full
**PDF:** `Heart rate variability status.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** critical

**Methodology:**
Systematic review and meta-analysis comparing resting HRV indices in adult depressed patients and healthy controls.

**Main findings:**
- Resting HRV can differ between depressed patients and healthy controls at the group level.
- The finding supports a link between depression and autonomic regulation abnormalities.
- HRV remains non-specific and cannot be used as an individual depression detector.
- Medication, comorbidity, HRV metric type, and population characteristics can affect interpretation.

**Supported nodes:**
- `persistent_low_hrv`
- `autonomic_regulation_shift`
- `depressive_like_pattern_contextual`

**Supported edges:**
- `persistent_low_hrv -> autonomic_regulation_shift`
- `autonomic_regulation_shift -> depressive_like_pattern_CONTEXT_REQUIRED`

**Limitations:**
- Population-level clinical comparison, not individual diagnosis tool.
- Depression-specific inference requires subjective/clinical data.
- Confounding by medication, comorbidity, and HRV protocol is possible.

**Use in THSI:** Secondary HRV source for clinical-context edges, never direct diagnosis.
**Notes:** Mark depression-related edges as contextual and high-risk.

## 9. palmer_2024_sleep_loss_emotion_meta_analysis

**Title:** Sleep loss and emotion: A systematic review and meta-analysis
**Authors:** C. A. Palmer, et al.
**Year:** 2024
**Source type:** meta_analysis
**Domain:** sleep_emotion_regulation
**DOI:** 10.1037/bul0000410
**URL:** https://www.apa.org/pubs/journals/releases/bul-bul0000410.pdf
**PDF:** `Palmer_2024_Sleep_Loss_and_Emotion_Meta_Analysis.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** medium

**Methodology:**
Preregistered systematic review and meta-analysis evaluating effects of multiple forms of sleep loss on emotional experience and related affective outcomes.

**Main findings:**
- Sleep loss affects emotional functioning across multiple outcome types.
- Sleep loss can reduce positive affect and alter negative emotional responses.
- Effects vary by type of sleep loss and emotional outcome.
- The evidence supports sleep loss as a modifier of psychological-state vulnerability, not a diagnostic signal.

**Supported nodes:**
- `sleep_loss`
- `emotion_regulation_impairment`
- `reduced_positive_affect`
- `negative_affect_vulnerability`

**Supported edges:**
- `sleep_loss -> emotion_regulation_impairment`
- `sleep_loss -> reduced_positive_affect`
- `sleep_loss -> negative_affect_vulnerability`

**Limitations:**
- Effects vary across sleep manipulation types and measured emotional constructs.
- Does not infer a specific mental disorder.
- Individual baseline, context, and subjective reports remain important.

**Use in THSI:** Primary quantitative source for sleep-loss-to-emotional-functioning edges.
**Notes:** Use as strong evidence for intermediate affective vulnerability nodes.

## 10. mcewen_2007_stress_adaptation_brain

**Title:** Physiology and Neurobiology of Stress and Adaptation: Central Role of the Brain
**Authors:** Bruce S. McEwen
**Year:** 2007
**Source type:** theoretical_review
**Domain:** allostasis
**DOI:** 10.1152/physrev.00041.2006
**URL:** https://journals.physiology.org/doi/full/10.1152/physrev.00041.2006
**PDF:** `Physiology and Neurobiology of Stress and Adaptation.pdf`
**Evidence strength:** 3
**Risk of overinterpretation:** high

**Methodology:**
Major theoretical review integrating physiology, neurobiology, stress adaptation, brain regulation, HPA-axis, autonomic, immune, and metabolic systems.

**Main findings:**
- The brain is central in perceiving stressors, coordinating responses, and being changed by stress exposure.
- Stress adaptation involves multiple interacting systems rather than one biomarker.
- Repeated or dysregulated stress responses can contribute to allostatic load.
- Stress effects are context-dependent and can be adaptive or damaging depending on timing and duration.

**Supported nodes:**
- `stress_adaptation_response`
- `hpa_axis_activation`
- `autonomic_regulation_shift`
- `allostatic_load`
- `multi_system_dysregulation`

**Supported edges:**
- `stress_adaptation_response -> physiological_state_shift`
- `repeated_stress_responses -> allostatic_load`
- `brain_stress_processing -> multi_system_regulation`

**Limitations:**
- Theoretical/mechanistic review rather than a quantitative inference model.
- Broad framework requires operationalization through specific biomarkers and contexts.
- Does not support direct psychological diagnosis from physiological data.

**Use in THSI:** Foundational source for stress adaptation and multi-system mechanism layer.
**Notes:** Use for graph architecture and mechanism labels.

## 11. sosa_2026_beyond_eda_multimodal_sns_arousal

**Title:** Beyond EDA: A Systematic Review of Multimodal Sympathetic Nervous System Arousal Classification for Stress Detection
**Authors:** S. Sosa, et al.
**Year:** 2026
**Source type:** systematic_review
**Domain:** EDA_sympathetic_arousal
**DOI:** 10.3390/s26051584
**URL:** https://www.mdpi.com/1424-8220/26/5/1584
**PDF:** `Sosa_2026_Beyond_EDA_Multimodal_SNS_Arousal.pdf`
**Evidence strength:** 4
**Risk of overinterpretation:** high

**Methodology:**
Systematic review of multimodal approaches to sympathetic nervous system arousal classification for stress detection, emphasizing EDA and complementary wearable signals.

**Main findings:**
- EDA is a central signal for sympathetic arousal but is insufficient alone for reliable stress interpretation.
- Multimodal signals such as HRV, PPG, skin temperature, movement, and context improve interpretability.
- Stress detection must distinguish arousal from cognitive load, movement, thermoregulation, excitement, and other confounds.
- Signal quality and context are necessary for wearable-based SNS inference.

**Supported nodes:**
- `increased_eda`
- `sympathetic_arousal`
- `wearable_multimodal_features`
- `sympathetic_nervous_system_activation`

**Supported edges:**
- `increased_eda -> sympathetic_arousal`
- `wearable_multimodal_features -> sympathetic_arousal_inference`
- `increased_eda_PLUS_context -> stress_like_arousal`

**Limitations:**
- EDA is not emotion-specific.
- Movement, temperature, skin contact, and task context can confound interpretation.
- Stress detection labels differ across studies.

**Use in THSI:** Primary EDA/SNS source and guardrail against unimodal EDA emotion detection.
**Notes:** Do not create increased_eda -> anxiety direct edges.

## 12. chen_2024_acute_sleep_deprivation_cortisol_meta_analysis

**Title:** The effect of acute sleep deprivation on cortisol level: a systematic review and meta-analysis
**Authors:** Yifei Chen, Wenhui Xu, Yiru Chen, Jiayu Gong, Yanyan Wu, Shutong Chen, Yuan He, Haitao Yu, Lin Xie
**Year:** 2024
**Source type:** meta_analysis
**Domain:** sleep_cortisol
**DOI:** 10.1507/endocrj.EJ23-0714
**URL:** https://pubmed.ncbi.nlm.nih.gov/38777757/
**PDF:** `The effect of acute sleep deprivation on cortisol level.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** high

**Methodology:**
Systematic review and meta-analysis of studies comparing cortisol levels after acute sleep deprivation versus normal sleep, including crossover studies and RCTs with subgroup analyses by sample type and measurement strategy.

**Main findings:**
- Overall cortisol differences after acute sleep deprivation were not significant in pooled crossover studies or RCTs.
- Serum cortisol subgroup analysis showed higher cortisol after acute sleep deprivation.
- Multiple cortisol measurements showed significant pooled effects, while single assessments did not.
- The sleep deprivation-cortisol relationship is mixed and method-dependent.

**Supported nodes:**
- `acute_sleep_deprivation`
- `cortisol_level`
- `salivary_or_serum_cortisol`
- `sleep_cortisol_uncertainty`

**Supported edges:**
- `acute_sleep_deprivation -> cortisol_elevation_MAY_INDICATE`
- `sample_type -> cortisol_effect_moderation`
- `measurement_frequency -> cortisol_effect_moderation`

**Limitations:**
- Cortisol effects depend on sample type, timing, and measurement frequency.
- Overall effect may be non-significant depending on analysis design.
- Does not support a simple poor_sleep -> high_cortisol rule.

**Use in THSI:** Corrective source preventing overconfident sleep-to-cortisol edges.
**Notes:** Represent this edge as mixed/contextual, not strong direct support.

## 13. frisch_2015_tsst_social_threat_paradigm

**Title:** The Trier Social Stress Test as a paradigm to study how people respond to threat in social interactions
**Authors:** Johanna U. Frisch, Jan A. Häusser, Andreas Mojzisch
**Year:** 2015
**Source type:** narrative_review
**Domain:** acute_psychosocial_stress
**DOI:** 10.3389/fpsyg.2015.00014
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4313597/
**PDF:** `The Trier Social Stress Test as a paradigm.pdf`
**Evidence strength:** 3
**Risk of overinterpretation:** medium

**Methodology:**
Review discussing TSST as a paradigm for studying social-evaluative threat, social processes, and neurophysiological stress responses.

**Main findings:**
- Social-evaluative threat reliably elicits neurophysiological stress reactions in TSST contexts.
- The TSST is adaptable for studying social interaction, social support, cognition, and behavior under threat.
- Social variables can amplify, buffer, or be affected by stress responses.
- Cortisol is a major but not exclusive marker of TSST-related stress response.

**Supported nodes:**
- `social_evaluative_threat_context`
- `acute_psychosocial_stress_response`
- `cortisol_response`
- `social_support_context`

**Supported edges:**
- `social_evaluative_threat_context -> acute_psychosocial_stress_response`
- `social_support_context -> stress_response_modulation`
- `acute_psychosocial_stress_response -> neurophysiological_stress_reaction`

**Limitations:**
- Focused on laboratory social-evaluative threat paradigm.
- Generalization to everyday stress requires caution.
- Not a wearable biomarker validation study.

**Use in THSI:** Context source for social-evaluative threat and TSST-related stress edges.
**Notes:** Use to require context nodes for acute stress inference.

## 14. allen_2017_tsst_principles_practice

**Title:** The Trier Social Stress Test: Principles and practice
**Authors:** Andrew P. Allen, Paul J. Kennedy, Samantha Dockray, John F. Cryan, Timothy G. Dinan, Gerard Clarke
**Year:** 2017
**Source type:** methodological_review
**Domain:** TSST
**DOI:** 10.1016/j.ynstr.2016.11.001
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC5314443/
**PDF:** `The Trier Social Stress Test.pdf`
**Evidence strength:** 4
**Risk of overinterpretation:** medium

**Methodology:**
Protocol-oriented review of TSST methodology, use cases, biological outcomes, and methodological considerations for acute laboratory stress research.

**Main findings:**
- The TSST is a valid and reliable acute stressor for experimental human research.
- The protocol combines interview-style presentation and surprise mental arithmetic in front of a non-reinforcing panel.
- TSST responses vary by sex, age, genotype, disorder status, and protocol features.
- The paradigm helps study neurobiology of acute stress under controlled conditions.

**Supported nodes:**
- `TSST_protocol`
- `acute_psychosocial_stress_response`
- `social_evaluative_threat_context`
- `hpa_axis_activation`

**Supported edges:**
- `TSST_protocol -> acute_psychosocial_stress_response`
- `social_evaluative_threat_context -> acute_stress_response`
- `protocol_moderators -> stress_response_variability`

**Limitations:**
- Laboratory paradigm, not direct everyday-life stress detection.
- Protocol deviations and participant characteristics affect response.
- Does not imply that any elevated biomarker equals stress.

**Use in THSI:** Primary methodological source for acute psychosocial stress context nodes.
**Notes:** Use TSST as reference model for what counts as validated stress induction.

## 15. tomaso_2021_sleep_deprivation_restriction_mood_meta_analyses

**Title:** The effect of sleep deprivation and restriction on mood, emotion, and emotion regulation: three meta-analyses in one
**Authors:** Cara C. Tomaso, Anna B. Johnson, Timothy D. Nelson
**Year:** 2021
**Source type:** meta_analysis
**Domain:** sleep_mood
**DOI:** 10.1093/sleep/zsaa289
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC8193556/
**PDF:** `Tomaso_2021_Sleep_Deprivation_Restriction_Mood_Meta_Analyses.pdf`
**Evidence strength:** 5
**Risk of overinterpretation:** medium

**Methodology:**
Three related meta-analyses using multilevel meta-analytic techniques to estimate effects of sleep deprivation and restriction on mood, emotion, and emotion regulation.

**Main findings:**
- Sleep loss moderately increases negative mood states.
- Sleep loss has a large diminishing effect on positive mood states.
- Sleep loss has a modest blunting effect on emotional arousal.
- Sleep restriction shows a small negative effect on adaptive emotion regulation in available youth studies.

**Supported nodes:**
- `sleep_loss`
- `sleep_restriction`
- `negative_mood_increase`
- `reduced_positive_affect`
- `adaptive_emotion_regulation_reduction`

**Supported edges:**
- `sleep_loss -> negative_mood_increase`
- `sleep_loss -> reduced_positive_affect`
- `sleep_restriction -> adaptive_emotion_regulation_reduction`
- `sleep_loss -> affective_functioning_impairment`

**Limitations:**
- Effect sizes differ by mood/emotion construct and sleep manipulation type.
- Adaptive emotion regulation evidence is more limited and youth-skewed.
- Does not support direct diagnosis of depression/anxiety from sleep loss.

**Use in THSI:** Primary quantitative source for sleep-loss-to-mood and affective functioning edges.
**Notes:** Use with Palmer 2024 to create strong sleep-affect pathways.
