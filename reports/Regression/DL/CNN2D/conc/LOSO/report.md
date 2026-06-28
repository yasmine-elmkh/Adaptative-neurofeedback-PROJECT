# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN2D`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-12 21:50


> 🔴 **Deployment Readiness Score : 28.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5878 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1972 | Erreur quadratique moyenne |
| R² | -0.0656 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5960 | 0.500 |
| PR-AUC | 0.5723 | 0.515 |
| Sensitivity (TPR) | 0.4679 | 0.500 |
| Specificity (TNR) | 0.6348 | 0.500 |
| PPV (Precision) | 0.5765 | — |
| NPV | 0.5290 | — |
| Balanced Accuracy | 0.5514 | 0.500 |
| MCC | 0.1041 | 0.000 |
| G-Mean | 0.5450 | 0.500 |
| F1 macro | 0.5468 | 0.500 |
| LR+ | 1.281 | >10 = très utile |
| LR− | 0.838 | <0.1 = très utile |
| Cohen κ | 0.1021 | 0.000 |
| Brier Score | 0.3287 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5955 | [0.5640, 0.6253]  ✅ |
| F1 macro | 0.5470 | [0.5202, 0.5725]  ✅ |
| Sensitivity | 0.4691 | [0.4338, 0.5018]  — |
| Specificity | 0.6343 | [0.5998, 0.6706]  — |
| MCC | 0.1047 | [0.0523, 0.1544]  — |
| R² | -0.0681 | [-0.1345, -0.0024]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2768 | < 0.05 |
| MCE | 0.4287 | < 0.10 |
| Brier Score | 0.3287 | < 0.20 |
| Log-Loss | 1.1180 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0981 | proche 0 = pas de biais systématique |
| LoA lower | -6.3638 | limite inférieure d'accord |
| LoA upper | +6.1677 | limite supérieure d'accord |
| LoA width | ±6.2658 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1261 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1084 | 0.2845 | 262.4% | 🔴 unstable |
| AUC ROC | 0.5972 | 0.1117 | 18.7% | 🟡 moderate |
| MAE | 2.6229 | 0.4717 | 18.0% | 🟡 moderate |

**Stability Score global : 54.4/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 48.0 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 92.5 | 10% |

### **SCORE TOTAL : 28.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 21:50*
