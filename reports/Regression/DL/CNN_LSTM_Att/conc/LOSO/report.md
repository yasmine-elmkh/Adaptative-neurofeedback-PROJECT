# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 14:16


> 🔴 **Deployment Readiness Score : 30.3/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5316 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1493 | Erreur quadratique moyenne |
| R² | -0.0339 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6080 | 0.500 |
| PR-AUC | 0.5911 | 0.515 |
| Sensitivity (TPR) | 0.4570 | 0.500 |
| Specificity (TNR) | 0.6362 | 0.500 |
| PPV (Precision) | 0.5717 | — |
| NPV | 0.5245 | — |
| Balanced Accuracy | 0.5466 | 0.500 |
| MCC | 0.0947 | 0.000 |
| G-Mean | 0.5392 | 0.500 |
| F1 macro | 0.5415 | 0.500 |
| LR+ | 1.256 | >10 = très utile |
| LR− | 0.853 | <0.1 = très utile |
| Cohen κ | 0.0927 | 0.000 |
| Brier Score | 0.3113 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6077 | [0.5764, 0.6368]  ✅ |
| F1 macro | 0.5412 | [0.5165, 0.5666]  ✅ |
| Sensitivity | 0.4574 | [0.4208, 0.4942]  — |
| Specificity | 0.6356 | [0.6003, 0.6694]  — |
| MCC | 0.0944 | [0.0460, 0.1462]  — |
| R² | -0.0351 | [-0.1061, 0.0355]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2506 | < 0.05 |
| MCE | 0.3835 | < 0.10 |
| Brier Score | 0.3113 | < 0.20 |
| Log-Loss | 1.1201 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3076 | proche 0 = pas de biais systématique |
| LoA lower | -6.4530 | limite inférieure d'accord |
| LoA upper | +5.8378 | limite supérieure d'accord |
| LoA width | ±6.1454 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0423 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0781 | 0.3652 | 467.9% | 🔴 unstable |
| AUC ROC | 0.6028 | 0.1022 | 17.0% | 🟡 moderate |
| MAE | 2.5612 | 0.5715 | 22.3% | 🟡 moderate |

**Stability Score global : 53.6/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 54.0 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 93.0 | 10% |

### **SCORE TOTAL : 30.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 14:16*
