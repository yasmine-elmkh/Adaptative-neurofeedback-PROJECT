# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 02:36


> 🔴 **Deployment Readiness Score : 22.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4526 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8550 | Erreur quadratique moyenne |
| R² | -0.0394 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5116 | 0.500 |
| PR-AUC | 0.3598 | 0.366 |
| Sensitivity (TPR) | 0.1266 | 0.500 |
| Specificity (TNR) | 0.8212 | 0.500 |
| PPV (Precision) | 0.2899 | — |
| NPV | 0.6198 | — |
| Balanced Accuracy | 0.4739 | 0.500 |
| MCC | -0.0687 | 0.000 |
| G-Mean | 0.3224 | 0.500 |
| F1 macro | 0.4413 | 0.500 |
| LR+ | 0.708 | >10 = très utile |
| LR− | 1.064 | <0.1 = très utile |
| Cohen κ | -0.0593 | 0.000 |
| Brier Score | 0.2984 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5102 | [0.4561, 0.5623]  — |
| F1 macro | 0.4405 | [0.3963, 0.4786]  — |
| Sensitivity | 0.1264 | [0.0752, 0.1807]  — |
| Specificity | 0.8198 | [0.7752, 0.8624]  — |
| MCC | -0.0705 | [-0.1653, 0.0188]  — |
| R² | -0.0426 | [-0.1077, 0.0211]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0394 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5116 | p=0.3560 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2477 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2984 | < 0.20 |
| Log-Loss | 0.8938 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1629 | proche 0 = pas de biais systématique |
| LoA lower | -5.7560 | limite inférieure d'accord |
| LoA upper | +5.4303 | limite supérieure d'accord |
| LoA width | ±5.5932 | < ±2 pts : excellent |
| % dans LoA | 98.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0369 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0394 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5116 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4526 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 5.8 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 62.5 | 10% |

### **SCORE TOTAL : 22.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 02:36*
