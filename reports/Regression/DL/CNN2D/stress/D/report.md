# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN2D`  |  **Exp :** `D`  |  **Date :** 2026-06-13 00:50


> 🔴 **Deployment Readiness Score : 34.4/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4400 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8668 | Erreur quadratique moyenne |
| R² | -0.0480 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5598 | 0.500 |
| PR-AUC | 0.4010 | 0.366 |
| Sensitivity (TPR) | 0.2152 | 0.500 |
| Specificity (TNR) | 0.8102 | 0.500 |
| PPV (Precision) | 0.3953 | — |
| NPV | 0.6416 | — |
| Balanced Accuracy | 0.5127 | 0.500 |
| MCC | 0.0306 | 0.000 |
| G-Mean | 0.4176 | 0.500 |
| F1 macro | 0.4974 | 0.500 |
| LR+ | 1.134 | >10 = très utile |
| LR− | 0.969 | <0.1 = très utile |
| Cohen κ | 0.0281 | 0.000 |
| Brier Score | 0.2722 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5582 | [0.5038, 0.6204]  ✅ |
| F1 macro | 0.4966 | [0.4512, 0.5493]  — |
| Sensitivity | 0.2154 | [0.1560, 0.2802]  — |
| Specificity | 0.8087 | [0.7597, 0.8545]  — |
| MCC | 0.0291 | [-0.0645, 0.1393]  — |
| R² | -0.0520 | [-0.1130, 0.0147]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0480 | p=0.0180 | ✅ p<0.05 |
| AUC ROC | 0.5598 | p=0.0120 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1914 | < 0.05 |
| MCE | 0.9002 | < 0.10 |
| Brier Score | 0.2722 | < 0.20 |
| Log-Loss | 0.8133 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0666 | proche 0 = pas de biais systématique |
| LoA lower | -5.6905 | limite inférieure d'accord |
| LoA upper | +5.5573 | limite supérieure d'accord |
| LoA width | ±5.6239 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0335 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0480 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5598 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4400 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 29.9 | 25% |
| Significativité (p-value) | 36.5 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 5.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 55.6 | 10% |

### **SCORE TOTAL : 34.4/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 00:50*
