# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN2D`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 04:31


> 🔴 **Deployment Readiness Score : 27.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0591 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4506 | Erreur quadratique moyenne |
| R² | -0.0594 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5758 | 0.500 |
| PR-AUC | 0.3511 | 0.282 |
| Sensitivity (TPR) | 0.0387 | 0.500 |
| Specificity (TNR) | 0.9848 | 0.500 |
| PPV (Precision) | 0.5000 | — |
| NPV | 0.7225 | — |
| Balanced Accuracy | 0.5117 | 0.500 |
| MCC | 0.0722 | 0.000 |
| G-Mean | 0.1951 | 0.500 |
| F1 macro | 0.4526 | 0.500 |
| LR+ | 2.541 | >10 = très utile |
| LR− | 0.976 | <0.1 = très utile |
| Cohen κ | 0.0326 | 0.000 |
| Brier Score | 0.2371 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5758 | [0.5494, 0.6016]  ✅ |
| F1 macro | 0.4527 | [0.4383, 0.4694]  — |
| Sensitivity | 0.0390 | [0.0249, 0.0559]  — |
| Specificity | 0.9848 | [0.9780, 0.9909]  — |
| MCC | 0.0732 | [0.0230, 0.1222]  — |
| R² | -0.0595 | [-0.0896, -0.0310]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1910 | < 0.05 |
| MCE | 0.4130 | < 0.10 |
| Brier Score | 0.2371 | < 0.20 |
| Log-Loss | 0.7991 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4282 | proche 0 = pas de biais systématique |
| LoA lower | -5.1588 | limite inférieure d'accord |
| LoA upper | +4.3024 | limite supérieure d'accord |
| LoA width | ±4.7306 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0019 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3459 | 0.7480 | 216.2% | 🔴 unstable |
| AUC ROC | 0.5327 | 0.1053 | 19.8% | 🟡 moderate |
| MAE | 2.0591 | 0.6141 | 29.8% | 🟡 moderate |

**Stability Score global : 50.1/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 37.9 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 6.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 98.6 | 10% |

### **SCORE TOTAL : 27.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 04:31*
