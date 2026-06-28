# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 13:58


> 🟡 **Deployment Readiness Score : 65.4/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0866 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7241 | Erreur quadratique moyenne |
| R² | 0.2586 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7451 | 0.500 |
| PR-AUC | 0.7327 | 0.521 |
| Sensitivity (TPR) | 0.7965 | 0.500 |
| Specificity (TNR) | 0.5577 | 0.500 |
| PPV (Precision) | 0.6618 | — |
| NPV | 0.7160 | — |
| Balanced Accuracy | 0.6771 | 0.500 |
| MCC | 0.3658 | 0.000 |
| G-Mean | 0.6665 | 0.500 |
| F1 macro | 0.6750 | 0.500 |
| LR+ | 1.801 | >10 = très utile |
| LR− | 0.365 | <0.1 = très utile |
| Cohen κ | 0.3573 | 0.000 |
| Brier Score | 0.2255 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7442 | [0.6787, 0.8071]  ✅ |
| F1 macro | 0.6731 | [0.6067, 0.7366]  ✅ |
| Sensitivity | 0.7967 | [0.7149, 0.8700]  — |
| Specificity | 0.5560 | [0.4607, 0.6474]  — |
| MCC | 0.3645 | [0.2311, 0.4868]  — |
| R² | 0.2529 | [0.1118, 0.3811]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2586 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7451 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1440 | < 0.05 |
| MCE | 0.2085 | < 0.10 |
| Brier Score | 0.2255 | < 0.20 |
| Log-Loss | 0.7280 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1610 | proche 0 = pas de biais systématique |
| LoA lower | -5.5033 | limite inférieure d'accord |
| LoA upper | +5.1813 | limite supérieure d'accord |
| LoA width | ±5.3423 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.3336 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2586 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7451 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.0866 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 37.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 47.7 | 10% |

### **SCORE TOTAL : 65.4/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:58*
