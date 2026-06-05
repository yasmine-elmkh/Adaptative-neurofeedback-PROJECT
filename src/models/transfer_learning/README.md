# NeuroCap — Transfer Learning (`src/models/transfer_learning/`)

EEGNet fine-tuning strategies for adapting a pre-trained EEG model to new subjects or sessions.

---

## Scripts

| Script | Strategy | Description |
|---|---|---|
| `EEGNet_feature_extraction.py` | Feature extraction | Backbone frozen — only the classification head is trained |
| `EEGNet_full_finetuning.py` | Full fine-tuning | All layers updated with a low learning rate |
| `EEGNet_layer_replacement.py` | Layer replacement | Last 2 classification layers replaced and retrained from scratch |
| `compare_tl.py` | Comparison | Side-by-side accuracy/F1 across all three strategies |

---

## Strategies overview

```
Pre-trained EEGNet (source domain)
        │
        ├── Feature extraction   → freeze all → train new head only
        ├── Full fine-tuning     → unfreeze all → low lr on everything
        └── Layer replacement    → freeze backbone → reinit + train last 2 layers
```

---

## Usage

```bash
# Feature extraction
python src/models/transfer_learning/EEGNet_feature_extraction.py \
    --weights models/deep_learning/EEGNet.pt \
    --data data/Merge_datasets/datasets_merged/ \
    --output reports/transfer_learning/feature_extraction/

# Full fine-tuning
python src/models/transfer_learning/EEGNet_full_finetuning.py \
    --weights models/deep_learning/EEGNet.pt \
    --data data/Merge_datasets/datasets_merged/ \
    --lr 1e-4 \
    --output reports/transfer_learning/full_finetuning/

# Layer replacement
python src/models/transfer_learning/EEGNet_layer_replacement.py \
    --weights models/deep_learning/EEGNet.pt \
    --data data/Merge_datasets/datasets_merged/ \
    --output reports/transfer_learning/layer_replacement/

# Compare all strategies
python src/models/transfer_learning/compare_tl.py \
    --results-dir reports/transfer_learning/ \
    --output reports/transfer_learning/comparison/
```

---

## Output

Results are saved per strategy under `reports/transfer_learning/`:
- `metrics.json` — accuracy, F1, precision, recall
- `confusion_matrix.png` — heatmap
- `training_curves.png` — loss and accuracy per epoch
