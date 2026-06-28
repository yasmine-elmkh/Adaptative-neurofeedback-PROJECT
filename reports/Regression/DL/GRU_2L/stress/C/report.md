# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_2L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 14:58


> 🔴 **Deployment Readiness Score : 26.2/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4104 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8451 | Erreur quadratique moyenne |
| R² | -0.0321 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5229 | 0.500 |
| PR-AUC | 0.3762 | 0.366 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 0.9891 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.6317 | — |
| Balanced Accuracy | 0.4945 | 0.500 |
| MCC | -0.0635 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.3855 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.011 | <0.1 = très utile |
| Cohen κ | -0.0138 | 0.000 |
| Brier Score | 0.2747 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5221 | [0.4675, 0.5751]  — |
| F1 macro | 0.3857 | [0.3675, 0.4025]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 0.9886 | [0.9744, 1.0000]  — |
| MCC | -0.0613 | [-0.0994, 0.0000]  — |
| R² | -0.0344 | [-0.0979, 0.0320]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0321 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5229 | p=0.2080 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1779 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2747 | < 0.20 |
| Log-Loss | 0.8738 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3470 | proche 0 = pas de biais systématique |
| LoA lower | -5.8882 | limite inférieure d'accord |
| LoA upper | +5.1941 | limite supérieure d'accord |
| LoA width | ±5.5411 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0193 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0321 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5229 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4104 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 11.4 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 14.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 61.6 | 10% |

### **SCORE TOTAL : 26.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 14:58*
