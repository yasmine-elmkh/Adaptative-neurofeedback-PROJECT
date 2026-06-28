# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN3D`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 06:20


> 🔴 **Deployment Readiness Score : 22.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4233 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9163 | Erreur quadratique moyenne |
| R² | -0.0845 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5118 | 0.500 |
| PR-AUC | 0.3708 | 0.366 |
| Sensitivity (TPR) | 0.0127 | 0.500 |
| Specificity (TNR) | 0.9818 | 0.500 |
| PPV (Precision) | 0.2857 | — |
| NPV | 0.6329 | — |
| Balanced Accuracy | 0.4972 | 0.500 |
| MCC | -0.0213 | 0.000 |
| G-Mean | 0.1115 | 0.500 |
| F1 macro | 0.3970 | 0.500 |
| LR+ | 0.694 | >10 = très utile |
| LR− | 1.006 | <0.1 = très utile |
| Cohen κ | -0.0070 | 0.000 |
| Brier Score | 0.3093 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5111 | [0.4567, 0.5649]  — |
| F1 macro | 0.3974 | [0.3748, 0.4244]  — |
| Sensitivity | 0.0128 | [0.0000, 0.0318]  — |
| Specificity | 0.9819 | [0.9658, 0.9962]  — |
| MCC | -0.0202 | [-0.0945, 0.0718]  — |
| R² | -0.0848 | [-0.1531, -0.0191]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0845 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.5118 | p=0.3540 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2660 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3093 | < 0.20 |
| Log-Loss | 1.0233 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7715 | proche 0 = pas de biais systématique |
| LoA lower | -6.2903 | limite inférieure d'accord |
| LoA upper | +4.7472 | limite supérieure d'accord |
| LoA width | ±5.5188 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0033 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0845 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5118 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4233 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 5.9 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 61.2 | 10% |

### **SCORE TOTAL : 22.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 06:20*
