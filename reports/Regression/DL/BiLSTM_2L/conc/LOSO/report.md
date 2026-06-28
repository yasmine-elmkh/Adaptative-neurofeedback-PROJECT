# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 00:00


> 🔴 **Deployment Readiness Score : 25.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6423 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1497 | Erreur quadratique moyenne |
| R² | -0.0342 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5714 | 0.500 |
| PR-AUC | 0.5654 | 0.515 |
| Sensitivity (TPR) | 0.3492 | 0.500 |
| Specificity (TNR) | 0.6957 | 0.500 |
| PPV (Precision) | 0.5494 | — |
| NPV | 0.5016 | — |
| Balanced Accuracy | 0.5225 | 0.500 |
| MCC | 0.0478 | 0.000 |
| G-Mean | 0.4929 | 0.500 |
| F1 macro | 0.5050 | 0.500 |
| LR+ | 1.148 | >10 = très utile |
| LR− | 0.935 | <0.1 = très utile |
| Cohen κ | 0.0444 | 0.000 |
| Brier Score | 0.3203 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5714 | [0.5427, 0.6012]  ✅ |
| F1 macro | 0.5048 | [0.4770, 0.5322]  — |
| Sensitivity | 0.3488 | [0.3133, 0.3856]  — |
| Specificity | 0.6963 | [0.6616, 0.7312]  — |
| MCC | 0.0481 | [-0.0073, 0.1004]  — |
| R² | -0.0344 | [-0.0829, 0.0213]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2467 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3203 | < 0.20 |
| Log-Loss | 1.0430 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2452 | proche 0 = pas de biais systématique |
| LoA lower | -6.4021 | limite inférieure d'accord |
| LoA upper | +5.9117 | limite supérieure d'accord |
| LoA width | ±6.1569 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0357 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0763 | 0.2380 | 312.0% | 🔴 unstable |
| AUC ROC | 0.5730 | 0.1016 | 17.7% | 🟡 moderate |
| MAE | 2.6358 | 0.4153 | 15.8% | 🟡 moderate |

**Stability Score global : 55.5/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 35.7 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.3 | 10% |

### **SCORE TOTAL : 25.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 00:00*
