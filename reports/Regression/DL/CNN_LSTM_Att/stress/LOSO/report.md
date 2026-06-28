# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 17:32


> 🔴 **Deployment Readiness Score : 25.2/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0903 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4516 | Erreur quadratique moyenne |
| R² | -0.0603 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5285 | 0.500 |
| PR-AUC | 0.3106 | 0.282 |
| Sensitivity (TPR) | 0.0281 | 0.500 |
| Specificity (TNR) | 0.9813 | 0.500 |
| PPV (Precision) | 0.3721 | — |
| NPV | 0.7196 | — |
| Balanced Accuracy | 0.5047 | 0.500 |
| MCC | 0.0294 | 0.000 |
| G-Mean | 0.1661 | 0.500 |
| F1 macro | 0.4413 | 0.500 |
| LR+ | 1.506 | >10 = très utile |
| LR− | 0.990 | <0.1 = très utile |
| Cohen κ | 0.0131 | 0.000 |
| Brier Score | 0.2303 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5279 | [0.4974, 0.5550]  — |
| F1 macro | 0.4415 | [0.4269, 0.4573]  — |
| Sensitivity | 0.0286 | [0.0155, 0.0430]  — |
| Specificity | 0.9813 | [0.9737, 0.9877]  — |
| MCC | 0.0308 | [-0.0195, 0.0762]  — |
| R² | -0.0609 | [-0.0912, -0.0328]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1538 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2303 | < 0.20 |
| Log-Loss | 0.7507 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1365 | proche 0 = pas de biais systématique |
| LoA lower | -4.9354 | limite inférieure d'accord |
| LoA upper | +4.6625 | limite supérieure d'accord |
| LoA width | ±4.7990 | < ±2 pts : excellent |
| % dans LoA | 97.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0089 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3855 | 0.8275 | 214.7% | 🔴 unstable |
| AUC ROC | 0.5543 | 0.0912 | 16.4% | 🟡 moderate |
| MAE | 2.0903 | 0.5584 | 26.7% | 🟡 moderate |

**Stability Score global : 52.3/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 14.3 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 30.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.9 | 10% |

### **SCORE TOTAL : 25.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 17:32*
