# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-13 13:16


> 🟡 **Deployment Readiness Score : 62.2/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1305 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7680 | Erreur quadratique moyenne |
| R² | 0.2346 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7245 | 0.500 |
| PR-AUC | 0.7318 | 0.521 |
| Sensitivity (TPR) | 0.7080 | 0.500 |
| Specificity (TNR) | 0.5673 | 0.500 |
| PPV (Precision) | 0.6400 | — |
| NPV | 0.6413 | — |
| Balanced Accuracy | 0.6376 | 0.500 |
| MCC | 0.2783 | 0.000 |
| G-Mean | 0.6337 | 0.500 |
| F1 macro | 0.6372 | 0.500 |
| LR+ | 1.636 | >10 = très utile |
| LR− | 0.515 | <0.1 = très utile |
| Cohen κ | 0.2765 | 0.000 |
| Brier Score | 0.2425 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7237 | [0.6548, 0.7891]  ✅ |
| F1 macro | 0.6347 | [0.5679, 0.6979]  ✅ |
| Sensitivity | 0.7072 | [0.6227, 0.7867]  — |
| Specificity | 0.5653 | [0.4747, 0.6681]  — |
| MCC | 0.2756 | [0.1411, 0.4007]  — |
| R² | 0.2299 | [0.0746, 0.3626]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2346 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7245 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1721 | < 0.05 |
| MCE | 0.4391 | < 0.10 |
| Brier Score | 0.2425 | < 0.20 |
| Log-Loss | 0.7911 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2023 | proche 0 = pas de biais systématique |
| LoA lower | -5.6256 | limite inférieure d'accord |
| LoA upper | +5.2209 | limite supérieure d'accord |
| LoA width | ±5.4233 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2935 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2346 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7245 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1305 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 18.6 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.8 | 10% |

### **SCORE TOTAL : 62.2/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:16*
