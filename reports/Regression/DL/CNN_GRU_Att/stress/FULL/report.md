# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 05:26


> 🔴 **Deployment Readiness Score : 29.5/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4010 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7784 | Erreur quadratique moyenne |
| R² | 0.0157 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5479 | 0.500 |
| PR-AUC | 0.3700 | 0.366 |
| Sensitivity (TPR) | 0.1076 | 0.500 |
| Specificity (TNR) | 0.8212 | 0.500 |
| PPV (Precision) | 0.2576 | — |
| NPV | 0.6148 | — |
| Balanced Accuracy | 0.4644 | 0.500 |
| MCC | -0.0954 | 0.000 |
| G-Mean | 0.2972 | 0.500 |
| F1 macro | 0.4275 | 0.500 |
| LR+ | 0.602 | >10 = très utile |
| LR− | 1.087 | <0.1 = très utile |
| Cohen κ | -0.0813 | 0.000 |
| Brier Score | 0.2634 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5465 | [0.4932, 0.5983]  — |
| F1 macro | 0.4272 | [0.3903, 0.4703]  — |
| Sensitivity | 0.1074 | [0.0595, 0.1574]  — |
| Specificity | 0.8213 | [0.7762, 0.8690]  — |
| MCC | -0.0952 | [-0.1782, -0.0020]  — |
| R² | 0.0124 | [-0.0348, 0.0585]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0157 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5479 | p=0.0420 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1843 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2634 | < 0.20 |
| Log-Loss | 0.7544 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0586 | proche 0 = pas de biais systématique |
| LoA lower | -5.3922 | limite inférieure d'accord |
| LoA upper | +5.5093 | limite supérieure d'accord |
| LoA width | ±5.4508 | < ±2 pts : excellent |
| % dans LoA | 98.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0551 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0157 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5479 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4010 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 23.9 | 25% |
| Significativité (p-value) | 4.5 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 10.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.3 | 10% |

### **SCORE TOTAL : 29.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 05:26*
