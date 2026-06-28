# NeuroCap — Tests (`Tests/`)

Evaluation scripts for all model families: baseline ML, deep learning, and transfer learning.  
**Pipeline de régression continue 0–10 (concentration + stress).**

> **Important:** These are standalone **evaluation scripts**, not pytest unit tests.  
> Launch each script directly with `python Tests/<script>.py`.

---

## Files

| Script | What it evaluates | Output folder |
|---|---|---|
| `test_baselines.py` | SVR / RF / XGBoost / LightGBM — feat15 et feat78 × sans/avec SMOTE (holdout) | `reports/Tests/baselines/` |
| `test_deep_learning.py` | 19 architectures DL — LOSO (évaluation honnête) + holdout | `reports/Tests/deep_learning/` |
| `test_finetuning.py` | 3 stratégies TL EEGNet (full FT / feature extraction / layer replacement) | `reports/Tests/finetuning/` |
| `test_final_comparaison.py` | Comparaison globale : ML vs DL vs TL — recommandation finale | `reports/Tests/` |

---

## Prerequisites

The scripts load already-trained models from disk. They will silently skip (`[SKIP]`) any model whose files are not found — **train the models first** using scripts in `src/`.

| Script | Required paths |
|---|---|
| `test_baselines.py` | `models/Baseline/` et `models/baseline_FeatEng/` |
| `test_deep_learning.py` | `models/Regression/DL/<ModelName>/` + LOSO metrics JSON |
| `test_finetuning.py` | `models/Regression/TL/<StrategyName>/` |
| `test_final_comparaison.py` | `reports/Tests/baselines/results.json` + `reports/Tests/deep_learning/results.json` + `reports/Tests/finetuning/results.json` |

---

## Recommended execution order

```bash
# Step 1 — evaluate each family
python Tests/test_baselines.py
python Tests/test_deep_learning.py
python Tests/test_finetuning.py

# Step 2 — global comparison
python Tests/test_final_comparaison.py
```

---

## Weighted score formula

All scripts rank models using the same composite score:

```
S = 0.40 × AUC + 0.30 × Sensitivity + 0.20 × MCC + 0.10 × Specificity
```

---

## Evaluation methodology

| Script | Metric source | Notes |
|---|---|---|
| `test_baselines.py` | Holdout `feat*_test.npy` | Random split — informational |
| `test_deep_learning.py` | **LOSO first**, holdout fallback | Scores `[LEAKED]` si leakage sujet détecté |
| `test_finetuning.py` | Val → Test adaptation | Fine-tuné sur `X_val.npy`, évalué sur `X_test.npy` |
| `test_final_comparaison.py` | JSON agrégés | Décision finale basée sur score composite S |

> **Why LOSO?** A random epoch split lets epochs from the same subject appear in both train and test — model memorises subject-specific EEG signatures → artificially perfect scores. LOSO guarantees no subject leakage.

---

## Résultats obtenus (LOSO strict)

| Famille | Modèle | Cible | AUC | Statut |
|---------|--------|-------|-----|--------|
| Deep Learning | EEGNet FULL | Concentration | **0.751** | ✓ PRODUCTION |
| Transfer Learning | TL-LayerReplacement FULL | Stress | **0.607** | ⚠ CONDITIONNEL |
| Machine Learning | LightGBM feat78_smote | Concentration | 0.676 | (référence ML) |
| Machine Learning | RF feat78_smote | Stress | 0.668 | (référence ML) |

---

## Dependencies

```bash
pip install torch scikit-learn lightgbm joblib numpy pandas matplotlib scipy pywavelets
```
