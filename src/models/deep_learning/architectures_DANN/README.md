# NeuroCap — DANN Architectures (`architectures_DANN/`)

Domain Adversarial Neural Network (DANN) variants of all 19 base architectures.
Each file wraps the corresponding base model with a Gradient Reversal Layer (GRL) and a domain classifier head to reduce cross-subject distribution shift.

---

## Structure

Each file follows the naming convention `<BaseName>_DANN.py` and mirrors exactly one architecture from `../architectures/`.

| DANN file | Base architecture |
|---|---|
| `CNN1D_DANN.py` | CNN1D |
| `CNN2D_DANN.py` | CNN2D |
| `CNN3D_DANN.py` | CNN3D |
| `LSTM1L_DANN.py` | LSTM1L |
| `LSTM2L_DANN.py` | LSTM2L |
| `LSTM_ATT_DANN.py` | LSTM_ATT |
| `BILSTM1L_DANN.py` | BILSTM1L |
| `BILSTM2L_DANN.py` | BILSTM2L |
| `BILSTM_ATT_DANN.py` | BILSTM_ATT |
| `GRU1L_DANN.py` | GRU1L |
| `GRU2L_DANN.py` | GRU2L |
| `GRU_ATT_DANN.py` | GRU_ATT |
| `BIGRU1L_DANN.py` | BIGRU1L |
| `BIGRU2L_DANN.py` | BIGRU2L |
| `BIGRU_ATT_DANN.py` | BIGRU_ATT |
| `CNN_LSTM_DANN.py` | CNN_LSTM |
| `CNN_GRU_DANN.py` | CNN_GRU |
| `EEGNet_DANN.py` | EEGNet |
| `TCN_DANN.py` | TCN |

---

## How DANN works

```
Input EEG epoch
      │
  Feature extractor (shared backbone)
      │
      ├── Label classifier  → predicts [rest / concentration / stress]
      │
      └── Domain classifier ← Gradient Reversal Layer (GRL)
                             → predicts [subject / session domain]
```

The GRL negates gradients during backprop, forcing the backbone to learn features that are **invariant to subject identity** while remaining discriminative for mental state.

---

## Common interface

```python
model = CNN_LSTM_DANN(num_classes=3, num_domains=N_subjects, input_len=1000)
label_logits, domain_logits = model(x, alpha=0.5)
# x: (batch, 1, 1000)  alpha: GRL scaling factor (increases during training)
```

---

## Training

See [DANN_utils.py](../DANN_utils.py) for the full training loop and GRL implementation, and [compare_dann.py](../compare_dann.py) to benchmark all DANN variants head-to-head.
