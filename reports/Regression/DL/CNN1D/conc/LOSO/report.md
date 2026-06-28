# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN1D`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-12 21:13


> 🔴 **Deployment Readiness Score : 33.5/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5203 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1293 | Erreur quadratique moyenne |
| R² | -0.0208 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6331 | 0.500 |
| PR-AUC | 0.6111 | 0.515 |
| Sensitivity (TPR) | 0.4270 | 0.500 |
| Specificity (TNR) | 0.7145 | 0.500 |
| PPV (Precision) | 0.6137 | — |
| NPV | 0.5400 | — |
| Balanced Accuracy | 0.5708 | 0.500 |
| MCC | 0.1475 | 0.000 |
| G-Mean | 0.5524 | 0.500 |
| F1 macro | 0.5594 | 0.500 |
| LR+ | 1.496 | >10 = très utile |
| LR− | 0.802 | <0.1 = très utile |
| Cohen κ | 0.1402 | 0.000 |
| Brier Score | 0.3228 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6336 | [0.6026, 0.6621]  ✅ |
| F1 macro | 0.5597 | [0.5329, 0.5863]  ✅ |
| Sensitivity | 0.4274 | [0.3920, 0.4619]  — |
| Specificity | 0.7151 | [0.6818, 0.7487]  — |
| MCC | 0.1485 | [0.0949, 0.1997]  — |
| R² | -0.0206 | [-0.0917, 0.0467]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2699 | < 0.05 |
| MCE | 0.3626 | < 0.10 |
| Brier Score | 0.3228 | < 0.20 |
| Log-Loss | 1.1409 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2309 | proche 0 = pas de biais systématique |
| LoA lower | -6.3498 | limite inférieure d'accord |
| LoA upper | +5.8880 | limite supérieure d'accord |
| LoA width | ±6.1189 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0690 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0632 | 0.3359 | 531.7% | 🔴 unstable |
| AUC ROC | 0.6339 | 0.0827 | 13.0% | 🟢 stable |
| MAE | 2.5600 | 0.5953 | 23.3% | 🟡 moderate |

**Stability Score global : 54.6/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 66.5 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 93.7 | 10% |

### **SCORE TOTAL : 33.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 21:13*
