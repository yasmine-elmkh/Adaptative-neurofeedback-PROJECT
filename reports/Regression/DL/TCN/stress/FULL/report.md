# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `TCN`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 06:19


> 🔴 **Deployment Readiness Score : 21.3/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5224 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9516 | Erreur quadratique moyenne |
| R² | -0.1109 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4747 | 0.500 |
| PR-AUC | 0.3368 | 0.366 |
| Sensitivity (TPR) | 0.0633 | 0.500 |
| Specificity (TNR) | 0.8978 | 0.500 |
| PPV (Precision) | 0.2632 | — |
| NPV | 0.6244 | — |
| Balanced Accuracy | 0.4806 | 0.500 |
| MCC | -0.0661 | 0.000 |
| G-Mean | 0.2384 | 0.500 |
| F1 macro | 0.4193 | 0.500 |
| LR+ | 0.619 | >10 = très utile |
| LR− | 1.043 | <0.1 = très utile |
| Cohen κ | -0.0464 | 0.000 |
| Brier Score | 0.3202 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4727 | [0.4179, 0.5238]  — |
| F1 macro | 0.4176 | [0.3837, 0.4581]  — |
| Sensitivity | 0.0615 | [0.0301, 0.1035]  — |
| Specificity | 0.8974 | [0.8635, 0.9299]  — |
| MCC | -0.0700 | [-0.1508, 0.0204]  — |
| R² | -0.1140 | [-0.1867, -0.0485]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1109 | p=0.1860 | ❌ ns |
| AUC ROC | 0.4747 | p=0.8000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2882 | < 0.05 |
| MCE | 0.9114 | < 0.10 |
| Brier Score | 0.3202 | < 0.20 |
| Log-Loss | 1.0245 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4946 | proche 0 = pas de biais systématique |
| LoA lower | -6.2045 | limite inférieure d'accord |
| LoA upper | +5.2153 | limite supérieure d'accord |
| LoA width | ±5.7099 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0038 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1109 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.4747 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5224 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 62.7 | 10% |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 06:19*
