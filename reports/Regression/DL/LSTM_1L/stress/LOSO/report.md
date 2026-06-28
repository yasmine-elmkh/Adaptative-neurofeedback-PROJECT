# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 13:16


> 🔴 **Deployment Readiness Score : 19.1/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1001 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4683 | Erreur quadratique moyenne |
| R² | -0.0747 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4542 | 0.500 |
| PR-AUC | 0.2854 | 0.282 |
| Sensitivity (TPR) | 0.0070 | 0.500 |
| Specificity (TNR) | 0.9924 | 0.500 |
| PPV (Precision) | 0.2667 | — |
| NPV | 0.7175 | — |
| Balanced Accuracy | 0.4997 | 0.500 |
| MCC | -0.0030 | 0.000 |
| G-Mean | 0.0835 | 0.500 |
| F1 macro | 0.4233 | 0.500 |
| LR+ | 0.924 | >10 = très utile |
| LR− | 1.001 | <0.1 = très utile |
| Cohen κ | -0.0008 | 0.000 |
| Brier Score | 0.2371 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4525 | [0.4214, 0.4804]  — |
| F1 macro | 0.4230 | [0.4138, 0.4330]  — |
| Sensitivity | 0.0070 | [0.0017, 0.0143]  — |
| Specificity | 0.9923 | [0.9872, 0.9965]  — |
| MCC | -0.0036 | [-0.0425, 0.0380]  — |
| R² | -0.0768 | [-0.1013, -0.0548]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1784 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2371 | < 0.20 |
| Log-Loss | 0.7718 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2149 | proche 0 = pas de biais systématique |
| LoA lower | -5.0355 | limite inférieure d'accord |
| LoA upper | +4.6058 | limite supérieure d'accord |
| LoA width | ±4.8207 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0017 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4001 | 0.9609 | 240.1% | 🔴 unstable |
| AUC ROC | 0.5201 | 0.0817 | 15.7% | 🟡 moderate |
| MAE | 2.1001 | 0.6039 | 28.8% | 🟡 moderate |

**Stability Score global : 51.8/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 14.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.0 | 10% |

### **SCORE TOTAL : 19.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:16*
