# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 13:41


> 🔴 **Deployment Readiness Score : 30.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5228 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1011 | Erreur quadratique moyenne |
| R² | -0.0025 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6015 | 0.500 |
| PR-AUC | 0.5590 | 0.515 |
| Sensitivity (TPR) | 0.5157 | 0.500 |
| Specificity (TNR) | 0.6304 | 0.500 |
| PPV (Precision) | 0.5972 | — |
| NPV | 0.5506 | — |
| Balanced Accuracy | 0.5731 | 0.500 |
| MCC | 0.1470 | 0.000 |
| G-Mean | 0.5702 | 0.500 |
| F1 macro | 0.5706 | 0.500 |
| LR+ | 1.395 | >10 = très utile |
| LR− | 0.768 | <0.1 = très utile |
| Cohen κ | 0.1455 | 0.000 |
| Brier Score | 0.2893 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6019 | [0.5743, 0.6328]  ✅ |
| F1 macro | 0.5716 | [0.5472, 0.5982]  ✅ |
| Sensitivity | 0.5171 | [0.4850, 0.5540]  — |
| Specificity | 0.6313 | [0.5977, 0.6667]  — |
| MCC | 0.1493 | [0.1020, 0.2002]  — |
| R² | -0.0044 | [-0.0685, 0.0567]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1963 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2893 | < 0.20 |
| Log-Loss | 1.0498 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2989 | proche 0 = pas de biais systématique |
| LoA lower | -6.3510 | limite inférieure d'accord |
| LoA upper | +5.7531 | limite supérieure d'accord |
| LoA width | ±6.0521 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0440 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0338 | 0.3377 | 999.9% | 🔴 unstable |
| AUC ROC | 0.6134 | 0.1111 | 18.1% | 🟡 moderate |
| MAE | 2.5110 | 0.3932 | 15.7% | 🟡 moderate |

**Stability Score global : 55.4/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 50.8 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 2.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.3 | 10% |

### **SCORE TOTAL : 30.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:41*
