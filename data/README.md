# NeuroCap — EEG Datasets

This folder contains all raw and processed EEG datasets used to train and evaluate the NeuroCap classifiers.

---

## Structure

```
data/
├── Dataset/
│   ├── Cognitive Load Assessment Concentration/
│   │   └── raw_data/          # Raw CSV files — concentration task (Fp2, 250 Hz)
│   └── Stress_dataset/
│       ├── raw_data/          # Raw CSV files — stress recordings
│       ├── filtered_data/     # Bandpass 1–45 Hz + notch 50 Hz applied
│       └── artifact_removal/  # ICA / threshold-based artefact rejection
├── Augmentation/
│   └── datasets_augmented/    # Time-shift, noise injection, amplitude scaling
├── Merge_datasets/
│   └── datasets_merged/       # Combined concentration + stress → unified CSV
└── Validate_datasets/
    ├── outputs_concentration_fp2/  # Holdout validation — concentration class
    ├── outputs_stress_fp2/         # Holdout validation — stress class
    └── utils/                      # Validation helper scripts
```

---

## Datasets

### Concentration dataset
- **Source:** Cognitive Load Assessment — Fp2 single-channel EEG
- **Sampling rate:** 250 Hz
- **Electrode:** Fp2 (prefrontal)
- **Labels:** `concentration` (1), `rest` (0)
- **Format:** CSV — columns: `timestamp`, `eeg_value`, `label`

### Stress dataset
- **Source:** Emotional stress induction protocol
- **Sampling rate:** 250 Hz
- **Electrode:** Fp2
- **Labels:** `stress` (1), `rest` (0)
- **Format:** CSV

---

## Preprocessing pipeline

```
Raw CSV
  ↓  Bandpass filter (1–45 Hz, 4th-order Butterworth)
  ↓  Notch filter (50 Hz, removes power-line noise)
  ↓  Baseline correction (mean subtraction per epoch)
  ↓  Artefact rejection (amplitude threshold ±150 µV)
  ↓  Epoch segmentation (4 s windows, 50% overlap)
Clean epochs (shape: N × 1000 samples)
```

---

## Data augmentation

Applied to balance classes and increase dataset size:

| Technique | Description |
|---|---|
| Gaussian noise | Add σ = 0.5 µV white noise |
| Time shift | Random circular shift ±50 samples |
| Amplitude scaling | Scale by 0.85–1.15× |
| Sign flip | Invert polarity (valid for Fp2) |

Augmentation scripts: `src/data/` and `data/Augmentation/`.

---

## Merge strategy

The concentration and stress datasets are merged into a 3-class problem:

| Class | Label | Source |
|---|---|---|
| `rest` | 0 | Both datasets (rest periods) |
| `concentration` | 1 | Concentration dataset |
| `stress` | 2 | Stress dataset |

Merged files are in `data/Merge_datasets/datasets_merged/`.

---

## Validation split

Holdout sets (never used during training) are in `data/Validate_datasets/`. Results of validation runs are saved to `reports/EDA/Validation/`.

---

## Notes

- All data is recorded at a single electrode (Fp2) for compatibility with the AD8232 hardware used in NeuroCap.
- No personally identifiable information is present in the datasets.
- Large binary files (`.npy`, `.h5`, processed CSVs) are excluded from git via `.gitignore`.
