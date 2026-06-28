# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN3D`  |  **Exp :** `B`  |  **Date :** 2026-06-13 04:36


> 🔴 **Deployment Readiness Score : 21.3/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4497 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8589 | Erreur quadratique moyenne |
| R² | -0.0422 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4583 | 0.500 |
| PR-AUC | 0.3324 | 0.366 |
| Sensitivity (TPR) | 0.0316 | 0.500 |
| Specificity (TNR) | 0.9197 | 0.500 |
| PPV (Precision) | 0.1852 | — |
| NPV | 0.6222 | — |
| Balanced Accuracy | 0.4757 | 0.500 |
| MCC | -0.0968 | 0.000 |
| G-Mean | 0.1706 | 0.500 |
| F1 macro | 0.3982 | 0.500 |
| LR+ | 0.394 | >10 = très utile |
| LR− | 1.053 | <0.1 = très utile |
| Cohen κ | -0.0590 | 0.000 |
| Brier Score | 0.2880 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4576 | [0.3999, 0.5070]  — |
| F1 macro | 0.3988 | [0.3692, 0.4292]  — |
| Sensitivity | 0.0321 | [0.0066, 0.0621]  — |
| Specificity | 0.9199 | [0.8851, 0.9484]  — |
| MCC | -0.0948 | [-0.1709, -0.0206]  — |
| R² | -0.0444 | [-0.0914, -0.0024]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0422 | p=0.2720 | ❌ ns |
| AUC ROC | 0.4583 | p=0.9180 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1993 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2880 | < 0.20 |
| Log-Loss | 0.8456 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0920 | proche 0 = pas de biais systématique |
| LoA lower | -5.6990 | limite inférieure d'accord |
| LoA upper | +5.5151 | limite supérieure d'accord |
| LoA width | ±5.6071 | < ±2 pts : excellent |
| % dans LoA | 98.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0076 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0422 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.4583 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4497 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 61.9 | 10% |

### **SCORE TOTAL : 21.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 04:36*
