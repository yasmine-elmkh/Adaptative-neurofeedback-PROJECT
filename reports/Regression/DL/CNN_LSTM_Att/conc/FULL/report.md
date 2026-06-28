# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 13:39


> 🟠 **Deployment Readiness Score : 59.1/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3812 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1104 | Erreur quadratique moyenne |
| R² | 0.0335 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6987 | 0.500 |
| PR-AUC | 0.6702 | 0.521 |
| Sensitivity (TPR) | 0.3717 | 0.500 |
| Specificity (TNR) | 0.8173 | 0.500 |
| PPV (Precision) | 0.6885 | — |
| NPV | 0.5449 | — |
| Balanced Accuracy | 0.5945 | 0.500 |
| MCC | 0.2100 | 0.000 |
| G-Mean | 0.5512 | 0.500 |
| F1 macro | 0.5683 | 0.500 |
| LR+ | 2.034 | >10 = très utile |
| LR− | 0.769 | <0.1 = très utile |
| Cohen κ | 0.1853 | 0.000 |
| Brier Score | 0.2882 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6978 | [0.6255, 0.7617]  ✅ |
| F1 macro | 0.5670 | [0.4966, 0.6312]  — |
| Sensitivity | 0.3720 | [0.2876, 0.4687]  — |
| Specificity | 0.8160 | [0.7403, 0.8894]  — |
| MCC | 0.2086 | [0.0648, 0.3399]  — |
| R² | 0.0263 | [-0.1564, 0.1924]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0335 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6987 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2351 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2882 | < 0.20 |
| Log-Loss | 1.0746 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.1843 | proche 0 = pas de biais systématique |
| LoA lower | -6.8345 | limite inférieure d'accord |
| LoA upper | +4.4659 | limite supérieure d'accord |
| LoA width | ±5.6502 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0322 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0335 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6987 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3812 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 99.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 42.5 | 10% |

### **SCORE TOTAL : 59.1/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:39*
