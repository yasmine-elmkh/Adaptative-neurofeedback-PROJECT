# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN2D`  |  **Exp :** `C`  |  **Date :** 2026-06-12 23:53


> 🔴 **Deployment Readiness Score : 31.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4383 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8514 | Erreur quadratique moyenne |
| R² | -0.0367 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5544 | 0.500 |
| PR-AUC | 0.4137 | 0.366 |
| Sensitivity (TPR) | 0.2405 | 0.500 |
| Specificity (TNR) | 0.8212 | 0.500 |
| PPV (Precision) | 0.4368 | — |
| NPV | 0.6522 | — |
| Balanced Accuracy | 0.5308 | 0.500 |
| MCC | 0.0741 | 0.000 |
| G-Mean | 0.4444 | 0.500 |
| F1 macro | 0.5186 | 0.500 |
| LR+ | 1.345 | >10 = très utile |
| LR− | 0.925 | <0.1 = très utile |
| Cohen κ | 0.0682 | 0.000 |
| Brier Score | 0.2704 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5530 | [0.4993, 0.6146]  — |
| F1 macro | 0.5177 | [0.4701, 0.5657]  — |
| Sensitivity | 0.2409 | [0.1749, 0.3084]  — |
| Specificity | 0.8195 | [0.7705, 0.8626]  — |
| MCC | 0.0723 | [-0.0245, 0.1690]  — |
| R² | -0.0415 | [-0.1056, 0.0244]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0367 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.5544 | p=0.0260 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1807 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2704 | < 0.20 |
| Log-Loss | 0.8098 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0208 | proche 0 = pas de biais systématique |
| LoA lower | -5.6160 | limite inférieure d'accord |
| LoA upper | +5.5743 | limite supérieure d'accord |
| LoA width | ±5.5951 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0484 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0367 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5544 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4383 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 27.2 | 25% |
| Significativité (p-value) | 16.7 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 12.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 56.5 | 10% |

### **SCORE TOTAL : 31.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 23:53*
