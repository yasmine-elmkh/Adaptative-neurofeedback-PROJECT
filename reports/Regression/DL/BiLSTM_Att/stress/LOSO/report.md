# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 08:10


> 🔴 **Deployment Readiness Score : 26.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0452 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4126 | Erreur quadratique moyenne |
| R² | -0.0268 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5473 | 0.500 |
| PR-AUC | 0.3148 | 0.282 |
| Sensitivity (TPR) | 0.0193 | 0.500 |
| Specificity (TNR) | 0.9786 | 0.500 |
| PPV (Precision) | 0.2619 | — |
| NPV | 0.7172 | — |
| Balanced Accuracy | 0.4989 | 0.500 |
| MCC | -0.0066 | 0.000 |
| G-Mean | 0.1375 | 0.500 |
| F1 macro | 0.4319 | 0.500 |
| LR+ | 0.902 | >10 = très utile |
| LR− | 1.002 | <0.1 = très utile |
| Cohen κ | -0.0029 | 0.000 |
| Brier Score | 0.2325 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5473 | [0.5213, 0.5786]  ✅ |
| F1 macro | 0.4318 | [0.4192, 0.4456]  — |
| Sensitivity | 0.0196 | [0.0102, 0.0308]  — |
| Specificity | 0.9784 | [0.9706, 0.9853]  — |
| MCC | -0.0062 | [-0.0460, 0.0334]  — |
| R² | -0.0269 | [-0.0497, -0.0008]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1695 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2325 | < 0.20 |
| Log-Loss | 0.7516 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1784 | proche 0 = pas de biais systématique |
| LoA lower | -4.8954 | limite inférieure d'accord |
| LoA upper | +4.5387 | limite supérieure d'accord |
| LoA width | ±4.7170 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0095 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3346 | 0.8089 | 241.7% | 🔴 unstable |
| AUC ROC | 0.5319 | 0.1314 | 24.7% | 🟡 moderate |
| MAE | 2.0452 | 0.5798 | 28.4% | 🟡 moderate |

**Stability Score global : 49.0/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 23.6 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 20.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 95.2 | 10% |

### **SCORE TOTAL : 26.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 08:10*
