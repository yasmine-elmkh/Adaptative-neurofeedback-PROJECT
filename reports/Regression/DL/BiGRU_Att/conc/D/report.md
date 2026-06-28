# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-13 13:23


> 🟠 **Deployment Readiness Score : 59.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2663 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9284 | Erreur quadratique moyenne |
| R² | 0.1433 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6990 | 0.500 |
| PR-AUC | 0.7183 | 0.521 |
| Sensitivity (TPR) | 0.6018 | 0.500 |
| Specificity (TNR) | 0.6058 | 0.500 |
| PPV (Precision) | 0.6239 | — |
| NPV | 0.5833 | — |
| Balanced Accuracy | 0.6038 | 0.500 |
| MCC | 0.2074 | 0.000 |
| G-Mean | 0.6038 | 0.500 |
| F1 macro | 0.6035 | 0.500 |
| LR+ | 1.526 | >10 = très utile |
| LR− | 0.657 | <0.1 = très utile |
| Cohen κ | 0.2072 | 0.000 |
| Brier Score | 0.2636 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6977 | [0.6205, 0.7626]  ✅ |
| F1 macro | 0.6003 | [0.5333, 0.6632]  ✅ |
| Sensitivity | 0.6017 | [0.5112, 0.6980]  — |
| Specificity | 0.6017 | [0.5071, 0.6943]  — |
| MCC | 0.2033 | [0.0677, 0.3288]  — |
| R² | 0.1385 | [-0.0157, 0.2792]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1433 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6990 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1905 | < 0.05 |
| MCE | 0.5988 | < 0.10 |
| Brier Score | 0.2636 | < 0.20 |
| Log-Loss | 0.8969 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5573 | proche 0 = pas de biais systématique |
| LoA lower | -6.2051 | limite inférieure d'accord |
| LoA upper | +5.0905 | limite supérieure d'accord |
| LoA width | ±5.6478 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1096 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1433 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6990 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2663 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 99.5 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 6.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.6 | 10% |

### **SCORE TOTAL : 59.7/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:23*
