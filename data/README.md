# NeuroCap — EEG Datasets (`data/`)

Raw and processed EEG data for the NeuroCap regression pipeline (continuous 0–10 concentration/stress scores). This file documents **what lives where** — for the processing logic itself (scoring, preprocessing, augmentation, feature extraction), see [`src/data/README.md`](../src/data/README.md) and [`src/data/scoring/README.md`](../src/data/scoring/README.md).

---

## Structure

```
data/
├── Dataset/                                          # Raw recordings (source of truth, never modified)
│   ├── Cognitive Load Assessment Concentration/
│   │   └── raw_data/                                 # .txt files, OpenBCI Cyton, 200 Hz, 15 subjects
│   └── Stress_dataset/
│       ├── raw_data/                                 # .mat files, Emotiv Epoc Flex, 128 Hz, 40 subjects
│       └── scales.xls                                # Self-reported stress scores (1–10) — ground truth
│
├── Scoring/                                           # Output of src/data/scoring/*.py
│   ├── scored_concentration.csv                       # ~1,859 epochs — conc_score 0–10
│   ├── scored_stress.csv                               # ~2,879 epochs — stress_score 0–10
│   └── merged/                                        # Signals + scores reassembled → .npy
│       ├── X_concentration.npy · y_conc_score.npy · subjects_concentration.npy · levels_concentration.npy
│       └── X_stress.npy · y_stress_score.npy · subjects_stress.npy
│
├── Regression/                                         # Output of src/data/pipeline_regression.py
│   ├── preprocessed/                                   # Filtered + resampled signals, pre-split
│   │   └── X_conc.npy · y_conc.npy · subjects_conc.npy · levels_conc.npy · X_stress.npy · y_stress.npy · subjects_stress.npy
│   └── augmented/                                      # Subject-wise 70/15/15 split, then augmented
│       ├── conc/       X_train_{A,B,C,D,FULL}.npy · y_train_{A,B,C,D,FULL}.npy · X_val.npy · X_test.npy · y_val.npy · y_test.npy
│       └── stress/     (same layout)
│
└── Validate_datasets/                                  # Output of src/data/validate_data/*.py
    ├── outputs_concentration_fp2/                       # 12 diagnostic figures (see its own README)
    ├── outputs_stress_fp2/                               # 10 diagnostic figures
    └── utils/                                           # Shared plotting/loading helpers (eeg_utils.py)
```

Feature matrices extracted from `Regression/augmented/` (feat15 / feat78) are written to `Features/conc/` and `Features/stress/` at the project root, not under `data/`.

---

## Datasets

| Dataset | Source | Subjects | Native rate | Task | Ground truth |
|---|---|---|---|---|---|
| **CLA** (Cognitive Load Assessment) | OpenBCI Cyton, single channel Fp2 | 15 | 200 Hz | Arithmetic / Stroop, 4 load levels | Task level (natural/low/mid/high) + EEG biomarkers |
| **SAM40** | Emotiv Epoc Flex, 32 channels (AF3 used) | 40 | 128 Hz | Relax / Arithmetic / Social stress / Stroop | Self-reported score 1–10 (`scales.xls`) |

Both datasets are resampled to **250 Hz** to match the AD8232/ESP32 hardware sampling rate, and are processed by **two fully independent pipelines** — they are never merged (different hardware, different electrodes).

---

## Pipeline stages (summary)

```
Dataset/ (raw)
   │  src/data/validate_data/  — integrity checks
   ▼
Scoring/ (scored_*.csv, merged/*.npy)
   │  src/data/scoring/  — 0–10 score attribution
   ▼
Regression/ (preprocessed/, augmented/)
   │  src/data/pipeline_regression.py  — filter → subject split → augment
   ▼
Features/ (feat15, feat78)             → src/models/  — ML / DL / TL training
```

Full detail, execution order, and script-level documentation: [`src/README.md`](../src/README.md).

---

## Notes

- All data is recorded/processed at a single active electrode compatible with the AD8232 + Fp2 hardware used in NeuroCap.
- No personally identifiable information is present in the datasets.
- `.npy`, processed CSVs, and other large binary outputs under `data/` are excluded from git via `.gitignore` — only raw source data and code are versioned.
- CLA dataset reference: Nirabi et al., 2024. SAM40 dataset reference: Ghosh et al., 2021.
