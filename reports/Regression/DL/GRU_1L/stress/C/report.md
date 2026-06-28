# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 13:16


> 🔴 **Deployment Readiness Score : 38.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3604 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8044 | Erreur quadratique moyenne |
| R² | -0.0028 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5756 | 0.500 |
| PR-AUC | 0.3927 | 0.366 |
| Sensitivity (TPR) | 0.0063 | 0.500 |
| Specificity (TNR) | 0.9854 | 0.500 |
| PPV (Precision) | 0.2000 | — |
| NPV | 0.6323 | — |
| Balanced Accuracy | 0.4959 | 0.500 |
| MCC | -0.0372 | 0.000 |
| G-Mean | 0.0790 | 0.500 |
| F1 macro | 0.3913 | 0.500 |
| LR+ | 0.434 | >10 = très utile |
| LR− | 1.008 | <0.1 = très utile |
| Cohen κ | -0.0104 | 0.000 |
| Brier Score | 0.2725 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5743 | [0.5180, 0.6278]  ✅ |
| F1 macro | 0.3919 | [0.3703, 0.4143]  — |
| Sensitivity | 0.0066 | [0.0000, 0.0220]  — |
| Specificity | 0.9854 | [0.9705, 0.9965]  — |
| MCC | -0.0354 | [-0.0980, 0.0532]  — |
| R² | -0.0046 | [-0.0667, 0.0537]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0028 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5756 | p=0.0060 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2076 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2725 | < 0.20 |
| Log-Loss | 0.8355 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4400 | proche 0 = pas de biais systématique |
| LoA lower | -5.8749 | limite inférieure d'accord |
| LoA upper | +4.9948 | limite supérieure d'accord |
| LoA width | ±5.4349 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0173 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0028 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5756 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3604 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 37.8 | 25% |
| Significativité (p-value) | 54.2 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.1 | 10% |

### **SCORE TOTAL : 38.6/100**

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
