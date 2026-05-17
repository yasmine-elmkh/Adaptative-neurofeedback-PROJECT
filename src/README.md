# NeuroCap — Source Code (`src/`)

All Python source code for data processing, feature engineering, model training, inference, and evaluation.

---

## Structure

```
src/
├── data/                  # Data processing scripts
│   ├── pipeline_fp2.py    # Full preprocessing pipeline (filter → segment → save)
│   ├── augmentation_eeg.py# Data augmentation (noise, shift, scaling, flip)
│   ├── merge_datasets.py  # Merge concentration + stress into 3-class dataset
│   ├── features_extraction.py # Extract spectral/temporal/wavelet features
│   ├── feature_eng.py     # Feature selection and normalisation
│   ├── validate_data/     # Holdout validation scripts
│   └── README.md
│
└── models/                # Model definitions, training, and evaluation
    ├── baselines/         # Classical ML (RF, SVM, XGBoost)
    ├── deep_learning/     # CNN, LSTM, GRU, TCN, EEGNet and hybrids
    ├── inference/         # Production inference API
    ├── transfer_learning/ # EEGNet fine-tuning strategies
    ├── compare/           # Cross-model comparison utilities
    └── README.md
```

---

## Entry points

| Script | Purpose |
|---|---|
| `src/data/pipeline_fp2.py` | Preprocess raw CSVs end-to-end |
| `src/data/augmentation_eeg.py` | Augment training epochs |
| `src/data/merge_datasets.py` | Build unified 3-class dataset |
| `src/models/baselines/baseline_ML.py` | Train and evaluate RF/SVM/XGBoost |
| `src/models/deep_learning/train.py` | Train any DL model by name |
| `src/models/inference/predict.py` | Run live or batch inference |

---

## Quick start

```bash
# 1. Preprocess raw data
python src/data/pipeline_fp2.py --input data/Dataset/ --output data/Merge_datasets/

# 2. Train the best model
python src/models/deep_learning/train.py --model CNN_LSTM_Att --epochs 100

# 3. Evaluate and compare all models
python src/models/deep_learning/compare.py
```

---

## Dependencies

See root `requirements.txt` for the full ML environment.
