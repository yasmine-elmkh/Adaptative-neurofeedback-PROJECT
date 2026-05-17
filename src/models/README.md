# NeuroCap — Models (`src/models/`)

Model definitions, training pipelines, and evaluation utilities for all NeuroCap classifiers.

---

## Structure

```
src/models/
├── baselines/             # Classical ML models
│   ├── baseline_ML.py           # RF / SVM / XGBoost on raw features
│   ├── baseline_ML_feature_eng.py # Same models on engineered features
│   └── compare_baselines_features.py # Cross-feature-set comparison
│
├── deep_learning/         # Deep learning models
│   ├── architectures/     # Model class definitions (19 architectures)
│   ├── DL_utils.py        # Shared: dataset loader, trainer loop, metrics
│   ├── compare.py         # Cross-model comparison and leaderboard
│   └── diagnostic_confound.py   # Subject/session confound analysis
│
├── inference/             # Production inference
│   └── predict.py         # Load model + run prediction on raw epoch
│
├── transfer_learning/     # EEGNet fine-tuning
│   ├── EEGNet_feature_extraction.py  # Frozen backbone
│   ├── EEGNet_full_finetuning.py     # All layers updated
│   └── EEGNet_layer_replacement.py   # Replace last 2 classification layers
│
└── compare/               # Aggregate comparison utilities
    └── compare_tl.py      # Transfer learning strategy comparison
```

---

## Deep learning architectures

All architectures in `deep_learning/architectures/` share a common interface:

```python
model = ArchitectureName(num_classes=3, input_len=1000)
output = model(x)  # x: (batch, 1, 1000) → output: (batch, 3)
```

| File | Architecture | Notes |
|---|---|---|
| `CNN1D.py` | 1D-CNN | Lightweight, fast inference |
| `CNN2D.py` | 2D-CNN | Treats epoch as 2D image |
| `CNN3D.py` | 3D-CNN | Multi-scale temporal convolutions |
| `LSTM_1L/2L/ATT.py` | LSTM variants | 1-layer, 2-layer, with attention |
| `BILSTM_1L/2L/ATT.py` | BiLSTM variants | Bidirectional |
| `GRU_1L/2L/ATT.py` | GRU variants | Gated Recurrent Unit |
| `BIGRU_1L/2L/ATT.py` | BiGRU variants | Bidirectional GRU |
| `CNN_LSTM.py` | CNN-LSTM + Attention | **Best model — 89.4% accuracy** |
| `CNN_GRU.py` | CNN-GRU + Attention | Competitive alternative |
| `EEGNet.py` | EEGNet | EEG-specific compact architecture |
| `TCN.py` | Temporal CNN | Parallelisable, competitive |

---

## Training

```bash
# Train a specific model
python src/models/deep_learning/train.py \
    --model CNN_LSTM_Att \
    --data data/Merge_datasets/datasets_merged/ \
    --epochs 100 \
    --batch-size 64 \
    --save models/deep_learning/CNN_LSTM_Att.pt

# Run all baselines
python src/models/baselines/baseline_ML.py \
    --data data/Merge_datasets/datasets_merged/ \
    --save-dir models/Baseline/

# Compare all deep learning models
python src/models/deep_learning/compare.py \
    --results-dir reports/deep_learning/DL_outputs/
```

---

## Inference

```python
from src.models.inference.predict import predict_epoch

epoch = np.load("epoch.npy")  # shape: (1000,) @ 250 Hz
result = predict_epoch(epoch, model_path="models/deep_learning/CNN_LSTM_Att.pt")
# Returns: {"class": "concentration", "confidence": 0.92, "probabilities": [...]}
```
