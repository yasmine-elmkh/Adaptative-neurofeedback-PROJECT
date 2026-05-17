# NeuroCap — Trained Model Artefacts

Serialised model weights and checkpoints produced by the training pipeline.

---

## Structure

```
models/
├── Baseline/              # Scikit-learn models (.pkl)
│   ├── rf_model.pkl       # Random Forest
│   ├── svm_model.pkl      # SVM (RBF kernel)
│   └── xgb_model.pkl      # XGBoost
│
├── baseline_FeatEng/      # Baseline models trained on engineered features
│   ├── rf_feateng.pkl
│   ├── svm_feateng.pkl
│   └── xgb_feateng.pkl
│
├── deep_learning/         # PyTorch model checkpoints (.pt)
│   ├── CNN1D.pt
│   ├── CNN2D.pt
│   ├── CNN3D.pt
│   ├── LSTM_1L.pt / LSTM_2L.pt / LSTM_Att.pt
│   ├── BiLSTM_1L.pt / BiLSTM_2L.pt / BiLSTM_Att.pt
│   ├── GRU_1L.pt / GRU_2L.pt / GRU_Att.pt
│   ├── BiGRU_1L.pt / BiGRU_2L.pt / BiGRU_Att.pt
│   ├── CNN_LSTM_Att.pt    ← best overall (89.4 % accuracy)
│   ├── CNN_GRU_Att.pt
│   ├── EEGNet.pt
│   └── TCN.pt
│
└── transfer_learning/     # Fine-tuned EEGNet variants
    ├── EEGNet_FeatureExtraction.pt
    ├── EEGNet_LayerReplacement.pt
    └── EEGNet_FullFT.pt
```

> **Note:** Large binary files (`.pt`, `.pkl`) are excluded from git via `.gitignore`. Download pre-trained weights from the project release or retrain using the scripts in `src/models/`.

---

## Loading a model

### Deep learning (PyTorch)

```python
import torch
from src.models.deep_learning.architectures.CNN_LSTM import CNN_LSTM_Att

model = CNN_LSTM_Att(num_classes=3)
model.load_state_dict(torch.load("models/deep_learning/CNN_LSTM_Att.pt", map_location="cpu"))
model.eval()
```

### Baseline (scikit-learn)

```python
import joblib

model = joblib.load("models/Baseline/rf_model.pkl")
predictions = model.predict(X_test)
```

---

## Best model

| Model | Accuracy | F1 (macro) | File |
|---|---|---|---|
| CNN-LSTM + Attention | **89.4%** | **0.89** | `deep_learning/CNN_LSTM_Att.pt` |

This model is used in the NeuroCap inference API (`src/models/inference/`).

---

## Retraining

```bash
# Retrain the best model
python src/models/deep_learning/train.py --model CNN_LSTM_Att --epochs 100 --save models/deep_learning/CNN_LSTM_Att.pt

# Retrain all baselines
python src/models/baselines/baseline_ML.py --save-dir models/Baseline/
```
