# EEG Dataset Validation Figures — Fp2 Channel (NeuroCap)

This folder holds the **generated diagnostic figures** produced by the raw-dataset validation scripts. The scripts themselves now live in [`src/data/validate_data/`](../../src/data/validate_data/) — see that folder's README for how to run them and what each check does. This file only documents what ends up here and how to read it.

---

## Overview

The validation pipeline verifies the integrity, signal quality, and hardware compatibility (single active electrode Fp2, reference M2, ground M1) of the two raw EEG datasets used in NeuroCap. It extracts the Fp2 channel, detects artifacts, computes spectral metrics, and generates the figures below.

| Dataset | Reference | Subjects | Channels (incl. Fp2) | Sample rate | Tasks |
|---------|-----------|----------|----------------------|-------------|-------|
| **Concentration** (Cognitive Load) | Nirabi et al., 2024 | 15 | 8 | 250 Hz | Arithmetic / Stroop (4 load levels) |
| **Stress** (SAM40) | Ghosh et al., 2021 | 40 | 32 | 128 Hz | Arithmetic / Stroop / Mirror image (3 trials) |

---

## Structure

```
data/Validate_datasets/
├── outputs_concentration_fp2/   # 12 figures generated for the concentration dataset
├── outputs_stress_fp2/          # 10 figures generated for the stress dataset
├── utils/                       # Shared plotting/loading helpers (eeg_utils.py)
└── README.md                    # This file
```

Scripts that produce these figures: [`src/data/validate_data/validate_concentration.py`](../../src/data/validate_data/validate_concentration.py) and [`validate_stress.py`](../../src/data/validate_data/validate_stress.py).

```bash
# Run from the project root
python src/data/validate_data/validate_concentration.py
python src/data/validate_data/validate_stress.py
```

---

## `outputs_concentration_fp2/` — Interpretation

| File | Content | Utility |
|---|---|---|
| `01_timeseries_arithmetic_fp2_s1.png` | Fp2 time series (Arithmetic, 10 s) | Visual artifact check |
| `02_timeseries_stroop_fp2_s1.png` | Same for Stroop | Cross-task comparison |
| `03_psd_arithmetic_fp2_s1.png` | PSD per load level (Arithmetic) | Spectral discrimination (alpha ↓ with load) |
| `04_psd_stroop_fp2_s1.png` | PSD per load level (Stroop) | Reproducibility |
| `05_histogram_arithmetic_fp2_s1.png` | Amplitude histogram (Arithmetic) | Detects non-stationarity |
| `06_histogram_stroop_fp2_s1.png` | Amplitude histogram (Stroop) | Symmetry, saturation |
| `07_psd_natural_vs_high_fp2_s1.png` | Natural vs. high-load PSD overlay | Alpha biomarker visualisation |
| `08_all_channels_natural_fp2_s1.png` | All 8 channels (Fp2 in red) | Justifies the Fp2 choice |
| `09_band_power_arithmetic_fp2_s1.png` | Band powers δ,θ,α,β,γ (Arithmetic) | Spectral quantification |
| `010_band_power_stroop_fp2_s1.png` | Same for Stroop | Reproducibility |
| `11_cross_subject_psd_fp2_arithmetic.png` | PSD of 5 subjects (natural) | Inter-subject variability → motivates fine-tuning |

## `outputs_stress_fp2/` — Interpretation

| File | Content | Utility |
|---|---|---|
| `01_timeseries_raw_fp2_s1_t1.png` | Raw 128 Hz signal | Ocular artifact detection (large peaks) |
| `02_timeseries_resampled_fp2_s1_t1.png` | After resampling to 250 Hz | Signal preservation check |
| `03_psd_raw_fp2_s1_t1.png` | PSD raw 128 Hz | Mains 50 Hz noise identification |
| `04_psd_resampled_fp2_s1_t1.png` | PSD after resampling | No spectral distortion |
| `05_histogram_fp2_s1_t1.png` | Amplitude histogram (raw) | Asymmetry due to DC offset |
| `06_all_channels_arithmetic_fp2_s1.png` | All 32 channels (Fp2 in red) | Spatial comparison |
| `07_resample_check_fp2_s1_t1.png` | PSD overlay 128 vs 250 Hz | Resampling validation |
| `08_band_power_128Hz_raw_fp2_s1.png` | Band powers (raw) | Baseline before filtering |
| `09_band_power_250Hz_resampled_fp2_s1.png` | Band powers (resampled) | Robustness check |
| `10_cross_subject_psd_fp2.png` | PSD of 5 subjects (Arithmetic) | Inter-subject variability |

---

## Key Conclusions

- Fp2 is usable — it contains the expected EEG rhythms (alpha, beta, theta).
- Ocular artifacts are present on SAM40 → requires DWT soft-thresholding (ICA is not possible on a single channel).
- DC offset on SAM40 → removed by the 0.5 Hz high-pass filter.
- High inter-subject variability → justifies individual fine-tuning after calibration.
- The 500 ms window is compatible with the <500 ms latency requirement (CdC).

These figures directly informed the design of the preprocessing pipeline (`src/data/pipeline_fp2.py`) and the augmentation pipeline (`src/data/augmentation_eeg.py`).

---

## Authors

Scripts & analysis: **Yasmine El Mkhantar**
Projet : NeuroCap sous Easy Medical Device

## License

Code and documentation: MIT License. Datasets are subject to their own licenses (CC BY 4.0 for SAM40, specific terms for the Cognitive Load dataset).
