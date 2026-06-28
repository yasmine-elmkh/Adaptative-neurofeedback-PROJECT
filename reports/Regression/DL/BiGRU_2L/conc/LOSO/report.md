# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 23:03


> 🔴 **Deployment Readiness Score : 36.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4107 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9737 | Erreur quadratique moyenne |
| R² | 0.0782 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6366 | 0.500 |
| PR-AUC | 0.5988 | 0.515 |
| Sensitivity (TPR) | 0.5853 | 0.500 |
| Specificity (TNR) | 0.5913 | 0.500 |
| PPV (Precision) | 0.6034 | — |
| NPV | 0.5730 | — |
| Balanced Accuracy | 0.5883 | 0.500 |
| MCC | 0.1765 | 0.000 |
| G-Mean | 0.5883 | 0.500 |
| F1 macro | 0.5881 | 0.500 |
| LR+ | 1.432 | >10 = très utile |
| LR− | 0.701 | <0.1 = très utile |
| Cohen κ | 0.1764 | 0.000 |
| Brier Score | 0.2718 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6358 | [0.6091, 0.6658]  ✅ |
| F1 macro | 0.5876 | [0.5638, 0.6148]  ✅ |
| Sensitivity | 0.5853 | [0.5524, 0.6197]  — |
| Specificity | 0.5906 | [0.5552, 0.6246]  — |
| MCC | 0.1758 | [0.1290, 0.2299]  — |
| R² | 0.0757 | [0.0171, 0.1309]  ✅ |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1751 | < 0.05 |
| MCE | 0.4259 | < 0.10 |
| Brier Score | 0.2718 | < 0.20 |
| Log-Loss | 0.9286 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0760 | proche 0 = pas de biais systématique |
| LoA lower | -5.9045 | limite inférieure d'accord |
| LoA upper | +5.7526 | limite supérieure d'accord |
| LoA width | ±5.8286 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1994 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0680 | 0.2087 | 306.8% | 🔴 unstable |
| AUC ROC | 0.6258 | 0.0913 | 14.6% | 🟢 stable |
| MAE | 2.3841 | 0.3275 | 13.7% | 🟢 stable |

**Stability Score global : 57.2/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 68.3 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 16.6 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 95.5 | 10% |

### **SCORE TOTAL : 36.6/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 23:03*
