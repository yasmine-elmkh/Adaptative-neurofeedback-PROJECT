# NeuroCap — Experiment Reports & Results

All experiment outputs, figures, and metrics are organised here by pipeline stage.

---

## Structure

```
reports/
├── EDA/                          # Exploratory data analysis
│   ├── Initiale/                 #   Initial dataset statistics
│   │   ├── Concentration/        #   Concentration dataset EDA
│   │   └── Stress/               #   Stress dataset EDA
│   ├── Augmentation/             #   EDA on augmented data
│   ├── Merge/                    #   EDA on merged dataset
│   ├── Comparaison/              #   Class distribution comparisons
│   └── Validation/               #   Holdout set statistics
│
├── Preprocessing/
│   └── outputs_hardware_compatible/  # Signal quality after pipeline
│
├── Augmentation/
│   └── outputs_augmentation/    # Class balance before/after augmentation
│
├── Baseline/
│   └── baselines_outputs/       # RF / SVM / XGBoost results
│       ├── A/ B/ C/ D/ FULL/    #   Per subject group / all data
│
├── baseline_FeatEng/
│   └── outputs_baseline/        # Baselines with engineered features
│       ├── A/ B/ C/ D/ FULL/
│
├── Comparison_Baselines_Features/
│   └── figures/                 # Bar charts comparing feature sets
│
├── deep_learning/
│   ├── DL_outputs/              # Per-model results
│   │   ├── CNN1D/ CNN2D/ CNN3D/
│   │   ├── LSTM_1L/ LSTM_2L/ LSTM_Att/
│   │   ├── BiLSTM_1L/ BiLSTM_2L/ BiLSTM_Att/
│   │   ├── GRU_1L/ GRU_2L/ GRU_Att/
│   │   ├── BiGRU_1L/ BiGRU_2L/ BiGRU_Att/
│   │   ├── CNN_LSTM_Att/ CNN_GRU_Att/
│   │   ├── EEGNet/ TCN/
│   ├── comparison/              # Cross-model comparison tables
│   └── diagnostic_confound/     # Confound analysis (subject, session effects)
│
├── transfer_learning/
│   └── outputs_tl/
│       ├── EEGNet_FeatureExtraction/
│       ├── EEGNet_FullFT/
│       └── EEGNet_LayerReplacement/
│
└── Comparaison_transfer_learning/ # TL strategies comparison
```

---

## Output file conventions

Each model directory typically contains:

| File | Content |
|---|---|
| `metrics.json` | accuracy, F1, precision, recall, AUC |
| `confusion_matrix.png` | Confusion matrix heatmap |
| `training_curves.png` | Train/val loss and accuracy over epochs |
| `classification_report.txt` | Per-class precision/recall/F1 |
| `roc_curve.png` | ROC curve with AUC |

---

## Key results summary

### Baseline models (raw features)

| Model | Accuracy | F1 (macro) |
|---|---|---|
| Random Forest | 78.3% | 0.77 |
| SVM (RBF) | 81.2% | 0.80 |
| XGBoost | 83.1% | 0.82 |

### Baseline models (engineered features)

| Model | Accuracy | F1 (macro) |
|---|---|---|
| RF + FeatEng | 83.7% | 0.83 |
| SVM + FeatEng | 84.5% | 0.84 |
| XGBoost + FeatEng | 85.9% | 0.85 |

### Deep learning

| Model | Accuracy | F1 (macro) | Notes |
|---|---|---|---|
| CNN1D | 84.2% | 0.83 | Lightweight, fast inference |
| EEGNet | 85.8% | 0.85 | EEG-specific architecture |
| BiLSTM + Attention | 87.6% | 0.87 | Best sequence model |
| **CNN-LSTM + Attention** | **89.4%** | **0.89** | **Best overall — deployed** |
| TCN | 88.1% | 0.87 | Competitive, parallelisable |

### Transfer learning (EEGNet source → NeuroCap target)

| Strategy | Accuracy | Notes |
|---|---|---|
| Feature Extraction | 81.3% | Frozen backbone |
| Layer Replacement | 85.7% | Replace last 2 layers |
| Full Fine-tuning | **87.2%** | All layers updated |

---

## Reproducing results

```bash
# Re-run baseline experiments
python src/models/baselines/run_baselines.py --data data/Merge_datasets/datasets_merged/

# Re-run deep learning training
python src/models/deep_learning/train.py --model CNN_LSTM_Att --epochs 100

# Compare all models
python src/models/compare/compare_all.py
```
