# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-13 15:17


> 🔴 **Deployment Readiness Score : 31.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3836 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7746 | Erreur quadratique moyenne |
| R² | 0.0184 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5581 | 0.500 |
| PR-AUC | 0.3804 | 0.366 |
| Sensitivity (TPR) | 0.0443 | 0.500 |
| Specificity (TNR) | 0.9380 | 0.500 |
| PPV (Precision) | 0.2917 | — |
| NPV | 0.6299 | — |
| Balanced Accuracy | 0.4911 | 0.500 |
| MCC | -0.0373 | 0.000 |
| G-Mean | 0.2039 | 0.500 |
| F1 macro | 0.4153 | 0.500 |
| LR+ | 0.714 | >10 = très utile |
| LR− | 1.019 | <0.1 = très utile |
| Cohen κ | -0.0216 | 0.000 |
| Brier Score | 0.2599 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5566 | [0.5013, 0.6065]  ✅ |
| F1 macro | 0.4155 | [0.3840, 0.4526]  — |
| Sensitivity | 0.0443 | [0.0138, 0.0810]  — |
| Specificity | 0.9383 | [0.9097, 0.9640]  — |
| MCC | -0.0366 | [-0.1239, 0.0647]  — |
| R² | 0.0153 | [-0.0307, 0.0560]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0184 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5581 | p=0.0220 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2004 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2599 | < 0.20 |
| Log-Loss | 0.7535 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0701 | proche 0 = pas de biais systématique |
| LoA lower | -5.5129 | limite inférieure d'accord |
| LoA upper | +5.3727 | limite supérieure d'accord |
| LoA width | ±5.4428 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0436 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0184 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5581 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3836 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 29.0 | 25% |
| Significativité (p-value) | 21.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.2 | 10% |

### **SCORE TOTAL : 31.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:17*
