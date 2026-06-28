# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 15:28


> 🔴 **Deployment Readiness Score : 32.2/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5464 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1530 | Erreur quadratique moyenne |
| R² | -0.0363 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6225 | 0.500 |
| PR-AUC | 0.5933 | 0.515 |
| Sensitivity (TPR) | 0.5580 | 0.500 |
| Specificity (TNR) | 0.5957 | 0.500 |
| PPV (Precision) | 0.5945 | — |
| NPV | 0.5592 | — |
| Balanced Accuracy | 0.5768 | 0.500 |
| MCC | 0.1536 | 0.000 |
| G-Mean | 0.5765 | 0.500 |
| F1 macro | 0.5762 | 0.500 |
| LR+ | 1.380 | >10 = très utile |
| LR− | 0.742 | <0.1 = très utile |
| Cohen κ | 0.1533 | 0.000 |
| Brier Score | 0.3088 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6217 | [0.5925, 0.6513]  ✅ |
| F1 macro | 0.5756 | [0.5496, 0.6024]  ✅ |
| Sensitivity | 0.5579 | [0.5227, 0.5950]  — |
| Specificity | 0.5948 | [0.5584, 0.6314]  — |
| MCC | 0.1527 | [0.1023, 0.2059]  — |
| R² | -0.0395 | [-0.1057, 0.0273]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2378 | < 0.05 |
| MCE | 0.3747 | < 0.10 |
| Brier Score | 0.3088 | < 0.20 |
| Log-Loss | 1.1560 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1637 | proche 0 = pas de biais systématique |
| LoA lower | -6.3374 | limite inférieure d'accord |
| LoA upper | +6.0100 | limite supérieure d'accord |
| LoA width | ±6.1737 | < ±2 pts : excellent |
| % dans LoA | 95.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1097 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0763 | 0.3446 | 451.5% | 🔴 unstable |
| AUC ROC | 0.6224 | 0.0896 | 14.4% | 🟢 stable |
| MAE | 2.5381 | 0.4217 | 16.6% | 🟡 moderate |

**Stability Score global : 56.3/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 61.2 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.2 | 10% |

### **SCORE TOTAL : 32.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:28*
