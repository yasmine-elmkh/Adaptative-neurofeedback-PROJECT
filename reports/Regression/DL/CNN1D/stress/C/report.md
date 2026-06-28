# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN1D`  |  **Exp :** `C`  |  **Date :** 2026-06-12 23:07


> 🔴 **Deployment Readiness Score : 23.1/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4607 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9506 | Erreur quadratique moyenne |
| R² | -0.1101 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5169 | 0.500 |
| PR-AUC | 0.3778 | 0.366 |
| Sensitivity (TPR) | 0.0570 | 0.500 |
| Specificity (TNR) | 0.9489 | 0.500 |
| PPV (Precision) | 0.3913 | — |
| NPV | 0.6357 | — |
| Balanced Accuracy | 0.5029 | 0.500 |
| MCC | 0.0126 | 0.000 |
| G-Mean | 0.2325 | 0.500 |
| F1 macro | 0.4304 | 0.500 |
| LR+ | 1.115 | >10 = très utile |
| LR− | 0.994 | <0.1 = très utile |
| Cohen κ | 0.0072 | 0.000 |
| Brier Score | 0.3024 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5169 | [0.4598, 0.5705]  — |
| F1 macro | 0.4300 | [0.3923, 0.4701]  — |
| Sensitivity | 0.0567 | [0.0229, 0.0978]  — |
| Specificity | 0.9482 | [0.9214, 0.9718]  — |
| MCC | 0.0102 | [-0.0800, 0.1031]  — |
| R² | -0.1103 | [-0.1870, -0.0381]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1101 | p=0.0320 | ✅ p<0.05 |
| AUC ROC | 0.5169 | p=0.2860 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2496 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3024 | < 0.20 |
| Log-Loss | 0.9969 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6651 | proche 0 = pas de biais systématique |
| LoA lower | -6.3059 | limite inférieure d'accord |
| LoA upper | +4.9757 | limite supérieure d'accord |
| LoA width | ±5.6408 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0047 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1101 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5169 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4607 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 8.4 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 59.5 | 10% |

### **SCORE TOTAL : 23.1/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 23:07*
