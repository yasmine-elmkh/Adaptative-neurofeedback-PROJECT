# NeuroCap — Tests (`Tests/`)

Evaluation scripts and report generators for all model families: baseline ML, deep learning, DANN, and fine-tuning.

> **Important:** These are standalone **evaluation scripts**, not pytest unit tests.
> Running `pytest Tests/` will **not** work — launch each script directly with `python Tests/<script>.py`.

---

## Files

### Test scripts

| Script | What it evaluates | Output folder |
|---|---|---|
| `test_baselines.py` | SVM / RF / XGBoost / LightGBM on raw + engineered features (holdout) | `reports/Tests/baselines/` |
| `test_deep_learning.py` | All 19 DL architectures — LOSO (honest) + holdout (informational) | `reports/Tests/deep_learning/` |
| `test_dann.py` | All 19 DANN architectures — LOSO + holdout | `reports/Tests/dann/` |
| `test_finetuning.py` | 3 fine-tuning strategies (full / head-only / layer-wise) on DL + DANN | `reports/Tests/finetuning/` |
| `test_final_comparison.py` | Aggregate: Baseline ML vs DL — final recommendation | `reports/Tests/` |
| `test_comparison_dann.py` | Aggregate: Baseline ML + DL + DANN + Fine-tuning — full recommendation | `reports/Tests/comparison_dann/` |

### Rapport scripts

| Script | What it generates |
|---|---|
| `rapport_baseline.py` | `reports/Tests/rapports/RAPPORT_BASELINE.txt` |
| `rapport_deep_learning.py` | `reports/Tests/rapports/RAPPORT_DEEP_LEARNING.txt` |
| `rapport_finetuning.py` | `reports/Tests/rapports/RAPPORT_FINETUNING.txt` |

---

## Prerequisites

The scripts load already-trained models from disk. They will silently skip (`[SKIP]`) any model whose files are not found — **train the models first**.

| Script | Required paths |
|---|---|
| `test_baselines.py` | `models/Baseline/baseline_models/` and `models/baseline_FeatEng/baseline_models/` |
| `test_deep_learning.py` | `models/deep_learning/DL_models/<ModelName>/` + `reports/deep_learning/DL_outputs/<ModelName>/LOSO_exp_A/metrics.json` |
| `test_dann.py` | `models/deep_learning/DANN_models/<ModelName>_DANN/` + corresponding LOSO metrics |
| `test_finetuning.py` | A trained DL or DANN model (chosen automatically by best F1 LOSO) |
| `test_final_comparison.py` | `reports/Tests/baselines/results.json` + `reports/Tests/deep_learning/results.json` |
| `test_comparison_dann.py` | All four `reports/Tests/*/results.json` files |

---

## Recommended execution order

```bash
# Step 1 — evaluate each family
python Tests/test_baselines.py
python Tests/test_deep_learning.py
python Tests/test_dann.py
python Tests/test_finetuning.py

# Step 2 — aggregate comparisons
python Tests/test_final_comparison.py      # Baseline ML vs DL
python Tests/test_comparison_dann.py       # All four approaches

# Step 3 — generate text reports
python Tests/rapport_baseline.py
python Tests/rapport_deep_learning.py
python Tests/rapport_finetuning.py
```

---

## Weighted score formula

All scripts rank models using the same composite score:

```
weighted_score = 0.40 × F1-macro + 0.30 × AUC + 0.20 × Accuracy + 0.10 × (1 − uncertain%)
```

`uncertain%` = fraction of epochs where `max(P(class)) < 0.60` (model not confident enough).

---

## Evaluation methodology

| Script | Metric source | Notes |
|---|---|---|
| `test_baselines.py` | Holdout `X_test.npy` | Random split — may have intra-subject leakage |
| `test_deep_learning.py` | **LOSO first**, holdout fallback | Scores marked `[LEAKED]` if subject leakage detected |
| `test_dann.py` | **LOSO first**, holdout fallback | Same leakage detection |
| `test_finetuning.py` | Val → Test adaptation | Fine-tuned on `X_val.npy`, evaluated on `X_test.npy` |

> **Why LOSO?** A random epoch split lets epochs from the same subject appear in both train and test. The model memorises subject-specific EEG signatures, producing artificially perfect scores (F1≈1.0). LOSO guarantees no subject is shared across splits.

---

## Outputs per script

**`test_baselines.py`** → `reports/Tests/baselines/`
- `results.json` / `results_table.csv`
- `comparison_barplot.png`
- `confusion_matrices/` — one image per model × feature set
- `roc_curves/`
- `decision_report.txt`

**`test_deep_learning.py`** → `reports/Tests/deep_learning/`
- `results_table_LOSO.csv` — honest leaderboard
- `results_table_holdout.csv` — raw scores (informational only)
- `results.json`

**`test_dann.py`** → `reports/Tests/dann/`
- `results_table_LOSO.csv`
- `dann_vs_dl_comparison.csv`
- `results.json`

**`test_finetuning.py`** → `reports/Tests/finetuning/`
- `results.json`
- `sample_efficiency.csv`
- `dann_vs_ft_comparison.csv`

**`test_comparison_dann.py`** → `reports/Tests/comparison_dann/`
- `summary.json` — used by all three rapport scripts

---

## Dependencies

```bash
pip install pytest torch scikit-learn lightgbm joblib numpy pandas matplotlib
```
