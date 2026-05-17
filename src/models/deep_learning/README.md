# NeuroCap — Deep Learning Models (`src/models/deep_learning/`)

PyTorch implementations of 19 deep learning architectures for EEG mental state classification.

---

## Structure

```
deep_learning/
├── architectures/         # Model class definitions
│   ├── CNN1D.py / CNN2D.py / CNN3D.py
│   ├── LSTM1L.py / LSTM2L.py / LSTM_ATT.py
│   ├── BILSTM1L.py / BILSTM2L.py / BILSTM_ATT.py
│   ├── GRU1L.py / GRU2L.py / GRU_ATT.py
│   ├── BIGRU1L.py / BIGRU2L.py / BIGRU_ATT.py
│   ├── CNN_LSTM.py        ← best model
│   ├── CNN_GRU.py
│   ├── EEGNet.py
│   └── TCN.py
├── DL_utils.py            # Dataset, trainer, metrics, plotting helpers
├── compare.py             # Cross-model leaderboard and comparison charts
└── diagnostic_confound.py # Confound analysis (subject/session effects)
```

---

## Input format

All models accept a single-channel EEG epoch:
```
Input shape:  (batch_size, 1, 1000)   — 1 channel × 1000 samples @ 250 Hz (4 s)
Output shape: (batch_size, 3)          — logits for [rest, concentration, stress]
```

---

## Results

| Model | Accuracy | F1 (macro) | Notes |
|---|---|---|---|
| CNN1D | 84.2% | 0.83 | Lightweight, fast |
| EEGNet | 85.8% | 0.85 | EEG-specific |
| BiLSTM + Attention | 87.6% | 0.87 | Best sequence model |
| TCN | 88.1% | 0.87 | Parallelisable |
| **CNN-LSTM + Attention** | **89.4%** | **0.89** | **Best overall** |

---

## Training a model

```bash
python src/models/deep_learning/train.py \
    --model CNN_LSTM_Att \
    --data data/Merge_datasets/datasets_merged/ \
    --epochs 100 \
    --batch-size 64 \
    --lr 1e-3 \
    --save models/deep_learning/CNN_LSTM_Att.pt
```

Available `--model` values: `CNN1D`, `CNN2D`, `CNN3D`, `LSTM_1L`, `LSTM_2L`, `LSTM_Att`, `BiLSTM_1L`, `BiLSTM_2L`, `BiLSTM_Att`, `GRU_1L`, `GRU_2L`, `GRU_Att`, `BiGRU_1L`, `BiGRU_2L`, `BiGRU_Att`, `CNN_LSTM_Att`, `CNN_GRU_Att`, `EEGNet`, `TCN`

---

## Compare all models

```bash
python src/models/deep_learning/compare.py \
    --results-dir reports/deep_learning/DL_outputs/ \
    --output reports/deep_learning/comparison/
```

Generates a leaderboard table and bar chart across all 19 models.

---

## Confound analysis

```bash
python src/models/deep_learning/diagnostic_confound.py \
    --model CNN_LSTM_Att \
    --weights models/deep_learning/CNN_LSTM_Att.pt \
    --output reports/deep_learning/diagnostic_confound/
```

Tests whether model performance is driven by genuine cognitive state differences or by subject/session identity artefacts.

---

## Training configuration (defaults)

| Parameter | Value |
|---|---|
| Optimizer | Adam |
| Learning rate | 1e-3 with ReduceLROnPlateau |
| Batch size | 64 |
| Epochs | 100 (early stopping patience=10) |
| Loss | CrossEntropyLoss |
| Train/Val/Test split | 70/15/15 stratified |
