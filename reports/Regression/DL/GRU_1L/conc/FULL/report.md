# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_1L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 12:23


> 🟡 **Deployment Readiness Score : 63.8/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1061 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6616 | Erreur quadratique moyenne |
| R² | 0.2923 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7282 | 0.500 |
| PR-AUC | 0.6997 | 0.521 |
| Sensitivity (TPR) | 0.6372 | 0.500 |
| Specificity (TNR) | 0.6538 | 0.500 |
| PPV (Precision) | 0.6667 | — |
| NPV | 0.6239 | — |
| Balanced Accuracy | 0.6455 | 0.500 |
| MCC | 0.2908 | 0.000 |
| G-Mean | 0.6455 | 0.500 |
| F1 macro | 0.6450 | 0.500 |
| LR+ | 1.841 | >10 = très utile |
| LR− | 0.555 | <0.1 = très utile |
| Cohen κ | 0.2905 | 0.000 |
| Brier Score | 0.2258 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7293 | [0.6568, 0.7905]  ✅ |
| F1 macro | 0.6465 | [0.5800, 0.7062]  ✅ |
| Sensitivity | 0.6406 | [0.5472, 0.7299]  — |
| Specificity | 0.6554 | [0.5648, 0.7535]  — |
| MCC | 0.2958 | [0.1621, 0.4145]  — |
| R² | 0.2881 | [0.1706, 0.3954]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2923 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7282 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1563 | < 0.05 |
| MCE | 0.5233 | < 0.10 |
| Brier Score | 0.2258 | < 0.20 |
| Log-Loss | 0.6840 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4400 | proche 0 = pas de biais systématique |
| LoA lower | -5.5969 | limite inférieure d'accord |
| LoA upper | +4.7170 | limite supérieure d'accord |
| LoA width | ±5.1569 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1784 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2923 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7282 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1061 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 29.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 44.2 | 10% |

### **SCORE TOTAL : 63.8/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:23*
