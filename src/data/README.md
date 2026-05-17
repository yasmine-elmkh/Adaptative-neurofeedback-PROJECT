# NeuroCap — Data Processing (`src/data/`)

Scripts for the full EEG data pipeline: preprocessing, augmentation, merging, and feature extraction.

---

## Scripts

| Script | Input | Output | Description |
|---|---|---|---|
| `pipeline_fp2.py` | `data/Dataset/*/raw_data/` | `data/Dataset/*/filtered_data/` | Bandpass + notch filter, artefact rejection, epoch segmentation |
| `augmentation_eeg.py` | Clean epochs | `data/Augmentation/datasets_augmented/` | Gaussian noise, time shift, amplitude scaling, sign flip |
| `merge_datasets.py` | Concentration + Stress epochs | `data/Merge_datasets/datasets_merged/` | Merge into unified 3-class CSV |
| `features_extraction.py` | Merged dataset | `features/features_extraction/` | Extract ~40 spectral/temporal/wavelet features |
| `feature_eng.py` | Raw features | `features/Features_eng/` | Feature selection (RF importance + MI + RFE), normalisation |

---

## Preprocessing pipeline

```
Raw CSV (timestamp, eeg_value, label)
  ↓  Bandpass filter — 1–45 Hz, 4th-order Butterworth
  ↓  Notch filter — 50 Hz (power-line noise)
  ↓  Baseline correction — mean subtraction per epoch
  ↓  Artefact rejection — amplitude threshold ±150 µV
  ↓  Epoch segmentation — 4 s windows, 50% overlap
Clean epochs (shape: N × 1000 @ 250 Hz)
```

---

## Usage

```bash
# Run full preprocessing pipeline
python src/data/pipeline_fp2.py \
    --input data/Dataset/ \
    --output data/Dataset/ \
    --fs 250 --epoch-len 4 --overlap 0.5

# Augment training data
python src/data/augmentation_eeg.py \
    --input data/Merge_datasets/datasets_merged/ \
    --output data/Augmentation/datasets_augmented/

# Merge datasets (3-class)
python src/data/merge_datasets.py \
    --conc data/Dataset/Cognitive_Load_Assessment_Concentration/ \
    --stress data/Dataset/Stress_dataset/ \
    --output data/Merge_datasets/datasets_merged/

# Extract features
python src/data/features_extraction.py \
    --input data/Merge_datasets/datasets_merged/ \
    --output features/features_extraction/ --fs 250
```

---

## Validate data

Scripts in `validate_data/` run quality checks on the holdout sets:
- Signal quality metrics (SNR, peak-to-peak)
- Class balance verification
- Feature distribution sanity checks

Results saved to `reports/EDA/Validation/`.
