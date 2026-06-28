# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 13:52


> 🔴 **Deployment Readiness Score : 24.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0720 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4219 | Erreur quadratique moyenne |
| R² | -0.0347 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5228 | 0.500 |
| PR-AUC | 0.3125 | 0.282 |
| Sensitivity (TPR) | 0.0246 | 0.500 |
| Specificity (TNR) | 0.9841 | 0.500 |
| PPV (Precision) | 0.3784 | — |
| NPV | 0.7194 | — |
| Balanced Accuracy | 0.5043 | 0.500 |
| MCC | 0.0292 | 0.000 |
| G-Mean | 0.1556 | 0.500 |
| F1 macro | 0.4387 | 0.500 |
| LR+ | 1.547 | >10 = très utile |
| LR− | 0.991 | <0.1 = très utile |
| Cohen κ | 0.0121 | 0.000 |
| Brier Score | 0.2281 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5228 | [0.4955, 0.5539]  — |
| F1 macro | 0.4385 | [0.4257, 0.4530]  — |
| Sensitivity | 0.0247 | [0.0136, 0.0378]  — |
| Specificity | 0.9840 | [0.9776, 0.9897]  — |
| MCC | 0.0290 | [-0.0136, 0.0698]  — |
| R² | -0.0348 | [-0.0580, -0.0125]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1505 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2281 | < 0.20 |
| Log-Loss | 0.7242 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0563 | proche 0 = pas de biais systématique |
| LoA lower | -4.8032 | limite inférieure d'accord |
| LoA upper | +4.6905 | limite supérieure d'accord |
| LoA width | ±4.7468 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0142 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3925 | 1.1310 | 288.1% | 🔴 unstable |
| AUC ROC | 0.5413 | 0.0977 | 18.1% | 🟡 moderate |
| MAE | 2.0719 | 0.5626 | 27.2% | 🟡 moderate |

**Stability Score global : 51.6/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 11.4 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 33.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.4 | 10% |

### **SCORE TOTAL : 24.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 13:52*
