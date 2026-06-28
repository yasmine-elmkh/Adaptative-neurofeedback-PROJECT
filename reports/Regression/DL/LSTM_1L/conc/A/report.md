# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 02:47


> 🟠 **Deployment Readiness Score : 46.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5411 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2533 | Erreur quadratique moyenne |
| R² | -0.0573 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6096 | 0.500 |
| PR-AUC | 0.5771 | 0.521 |
| Sensitivity (TPR) | 0.2389 | 0.500 |
| Specificity (TNR) | 0.7788 | 0.500 |
| PPV (Precision) | 0.5400 | — |
| NPV | 0.4850 | — |
| Balanced Accuracy | 0.5089 | 0.500 |
| MCC | 0.0211 | 0.000 |
| G-Mean | 0.4314 | 0.500 |
| F1 macro | 0.4645 | 0.500 |
| LR+ | 1.080 | >10 = très utile |
| LR− | 0.977 | <0.1 = très utile |
| Cohen κ | 0.0174 | 0.000 |
| Brier Score | 0.3457 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6080 | [0.5296, 0.6811]  ✅ |
| F1 macro | 0.4621 | [0.3969, 0.5307]  — |
| Sensitivity | 0.2381 | [0.1604, 0.3220]  — |
| Specificity | 0.7763 | [0.6986, 0.8539]  — |
| MCC | 0.0168 | [-0.1176, 0.1488]  — |
| R² | -0.0626 | [-0.2388, 0.0994]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0573 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6096 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2969 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3457 | < 0.20 |
| Log-Loss | 1.2162 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.2136 | proche 0 = pas de biais systématique |
| LoA lower | -7.1435 | limite inférieure d'accord |
| LoA upper | +4.7163 | limite supérieure d'accord |
| LoA width | ±5.9299 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0226 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0573 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6096 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5411 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 54.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 32.3 | 10% |

### **SCORE TOTAL : 46.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 02:47*
