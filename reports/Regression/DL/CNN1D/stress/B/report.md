# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN1D`  |  **Exp :** `B`  |  **Date :** 2026-06-12 22:21


> 🔴 **Deployment Readiness Score : 24.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4645 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9575 | Erreur quadratique moyenne |
| R² | -0.1153 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5319 | 0.500 |
| PR-AUC | 0.3759 | 0.366 |
| Sensitivity (TPR) | 0.1835 | 0.500 |
| Specificity (TNR) | 0.8248 | 0.500 |
| PPV (Precision) | 0.3766 | — |
| NPV | 0.6366 | — |
| Balanced Accuracy | 0.5042 | 0.500 |
| MCC | 0.0105 | 0.000 |
| G-Mean | 0.3891 | 0.500 |
| F1 macro | 0.4827 | 0.500 |
| LR+ | 1.048 | >10 = très utile |
| LR− | 0.990 | <0.1 = très utile |
| Cohen κ | 0.0094 | 0.000 |
| Brier Score | 0.3086 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5307 | [0.4738, 0.5848]  — |
| F1 macro | 0.4816 | [0.4386, 0.5281]  — |
| Sensitivity | 0.1832 | [0.1254, 0.2442]  — |
| Specificity | 0.8235 | [0.7759, 0.8686]  — |
| MCC | 0.0084 | [-0.0876, 0.1079]  — |
| R² | -0.1177 | [-0.2040, -0.0376]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1153 | p=0.0200 | ✅ p<0.05 |
| AUC ROC | 0.5319 | p=0.1320 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2539 | < 0.05 |
| MCE | 0.8420 | < 0.10 |
| Brier Score | 0.3086 | < 0.20 |
| Log-Loss | 0.9761 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3168 | proche 0 = pas de biais systématique |
| LoA lower | -6.0868 | limite inférieure d'accord |
| LoA upper | +5.4532 | limite supérieure d'accord |
| LoA width | ±5.7700 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0181 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1153 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5319 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4645 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 16.0 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 59.3 | 10% |

### **SCORE TOTAL : 24.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 22:21*
