# Personal Evidence Graph Demo v0.1

## Raw observations

### raw_demo_001
- **Signal:** `sleep_duration`
- **Value:** 4.5 hours
- **Source:** wearable
- **Quality score:** 0.9
- **Notes:** Short sleep duration relative to baseline.

### raw_demo_002
- **Signal:** `hrv_rmssd`
- **Value:** 28 ms
- **Source:** wearable
- **Quality score:** 0.75
- **Notes:** HRV below personal baseline.

### raw_demo_003
- **Signal:** `eda`
- **Value:** 2.3 microsiemens
- **Source:** wearable
- **Quality score:** 0.7
- **Notes:** EDA above personal baseline.

## Personal baseline used

Baseline period: 2026-05-01 to 2026-05-31 (subject `demo_subject_001`)

- **eda:** median=1.2 microsiemens, std=0.4, sample_count=20
- **hrv_rmssd:** median=48 ms, std=11, sample_count=28
- **sleep_duration:** median=7.4 hours, std=0.9, sample_count=28

## Derived markers

### derived_raw_demo_001
- **Derived node:** `sleep_loss`
- **Rule:** sleep_duration 4.5h is 2.9h below baseline median 7.4h (>= 1.5h threshold) -> sleep_loss
- **Deviation score:** 2.9
- **Confidence:** 0.9
- **Supporting observations:** raw_demo_001

### derived_raw_demo_002
- **Derived node:** `reduced_hrv_relative_to_baseline`
- **Rule:** hrv_rmssd 28.0ms is below baseline median 48.0ms by 20.0ms (>= 1 std or >= 25%) -> reduced_hrv_relative_to_baseline
- **Deviation score:** 1.8182
- **Confidence:** 0.75
- **Supporting observations:** raw_demo_002

### derived_raw_demo_003
- **Derived node:** `increased_eda`
- **Rule:** eda 2.3 is above baseline median 1.2 by 1.10 (>= 1 std or >= 30%) -> increased_eda
- **Deviation score:** 2.75
- **Confidence:** 0.525
- **Supporting observations:** raw_demo_003

Expected demo mappings:
- sleep_duration 4.5h vs baseline 7.4h → `sleep_loss`
- hrv_rmssd 28ms vs baseline 48ms → `reduced_hrv_relative_to_baseline`
- eda 2.3 vs baseline 1.2 → `increased_eda`

## Matched static graph nodes

- `increased_eda` (Increased Eda)
- `reduced_hrv_relative_to_baseline` (Reduced Hrv Relative To Baseline)
- `sleep_loss` (Sleep Loss)

## Inference input

### derived_raw_demo_001
- **Observed node:** `sleep_loss`
- **Quality score (confidence):** 0.9
- **Source:** wearable
- **Notes:** Derived from raw observation(s) raw_demo_001 via sleep_duration 4.5h is 2.9h below baseline median 7.4h (>= 1.5h threshold) -> sleep_loss. Short sleep duration relative to baseline.

### derived_raw_demo_002
- **Observed node:** `reduced_hrv_relative_to_baseline`
- **Quality score (confidence):** 0.75
- **Source:** wearable
- **Notes:** Derived from raw observation(s) raw_demo_002 via hrv_rmssd 28.0ms is below baseline median 48.0ms by 20.0ms (>= 1 std or >= 25%) -> reduced_hrv_relative_to_baseline. HRV below personal baseline.

### derived_raw_demo_003
- **Observed node:** `increased_eda`
- **Quality score (confidence):** 0.525
- **Source:** wearable
- **Notes:** Derived from raw observation(s) raw_demo_003 via eda 2.3 is above baseline median 1.2 by 1.10 (>= 1 std or >= 30%) -> increased_eda. EDA above personal baseline.

## Warnings

- This is not a medical diagnosis.
- Mapping rules are preliminary and rule-based only.
- Baseline quality affects confidence scores.
- Additional context may change interpretation.
