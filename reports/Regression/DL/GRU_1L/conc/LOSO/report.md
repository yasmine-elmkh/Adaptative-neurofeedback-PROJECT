# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_1L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 12:49


> 🔴 **Deployment Readiness Score : 30.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5230 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1354 | Erreur quadratique moyenne |
| R² | -0.0248 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6088 | 0.500 |
| PR-AUC | 0.5748 | 0.515 |
| Sensitivity (TPR) | 0.4270 | 0.500 |
| Specificity (TNR) | 0.6870 | 0.500 |
| PPV (Precision) | 0.5917 | — |
| NPV | 0.5302 | — |
| Balanced Accuracy | 0.5570 | 0.500 |
| MCC | 0.1179 | 0.000 |
| G-Mean | 0.5416 | 0.500 |
| F1 macro | 0.5473 | 0.500 |
| LR+ | 1.364 | >10 = très utile |
| LR− | 0.834 | <0.1 = très utile |
| Cohen κ | 0.1130 | 0.000 |
| Brier Score | 0.3005 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6094 | [0.5794, 0.6367]  ✅ |
| F1 macro | 0.5484 | [0.5233, 0.5724]  ✅ |
| Sensitivity | 0.4290 | [0.3957, 0.4642]  — |
| Specificity | 0.6872 | [0.6534, 0.7201]  — |
| MCC | 0.1202 | [0.0722, 0.1680]  — |
| R² | -0.0261 | [-0.0882, 0.0371]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2072 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3005 | < 0.20 |
| Log-Loss | 1.0885 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4148 | proche 0 = pas de biais systématique |
| LoA lower | -6.5083 | limite inférieure d'accord |
| LoA upper | +5.6786 | limite supérieure d'accord |
| LoA width | ±6.0935 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0250 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0588 | 0.2386 | 405.9% | 🔴 unstable |
| AUC ROC | 0.6132 | 0.1176 | 19.2% | 🟡 moderate |
| MAE | 2.5189 | 0.3531 | 14.0% | 🟢 stable |

**Stability Score global : 55.6/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 54.4 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 95.1 | 10% |

### **SCORE TOTAL : 30.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:49*
