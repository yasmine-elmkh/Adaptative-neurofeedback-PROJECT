# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_2L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 14:20


> 🔴 **Deployment Readiness Score : 29.1/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4070 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8060 | Erreur quadratique moyenne |
| R² | -0.0040 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5183 | 0.500 |
| PR-AUC | 0.3744 | 0.366 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 0.9927 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.6326 | — |
| Balanced Accuracy | 0.4964 | 0.500 |
| MCC | -0.0518 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.3864 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.007 | <0.1 = très utile |
| Cohen κ | -0.0092 | 0.000 |
| Brier Score | 0.2602 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5187 | [0.4644, 0.5687]  — |
| F1 macro | 0.3867 | [0.3693, 0.4033]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 0.9925 | [0.9807, 1.0000]  — |
| MCC | -0.0467 | [-0.0855, 0.0000]  — |
| R² | -0.0053 | [-0.0525, 0.0393]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0040 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5183 | p=0.3000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1451 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2602 | < 0.20 |
| Log-Loss | 0.7745 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0798 | proche 0 = pas de biais systématique |
| LoA lower | -5.5838 | limite inférieure d'accord |
| LoA upper | +5.4241 | limite supérieure d'accord |
| LoA width | ±5.5040 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0408 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0040 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5183 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4070 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 9.1 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 36.6 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.8 | 10% |

### **SCORE TOTAL : 29.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 14:20*
