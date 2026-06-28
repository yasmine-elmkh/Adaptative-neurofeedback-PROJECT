# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_1L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 08:15


> 🟠 **Deployment Readiness Score : 55.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4357 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1716 | Erreur quadratique moyenne |
| R² | -0.0049 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6748 | 0.500 |
| PR-AUC | 0.6307 | 0.521 |
| Sensitivity (TPR) | 0.5752 | 0.500 |
| Specificity (TNR) | 0.6538 | 0.500 |
| PPV (Precision) | 0.6436 | — |
| NPV | 0.5862 | — |
| Balanced Accuracy | 0.6145 | 0.500 |
| MCC | 0.2294 | 0.000 |
| G-Mean | 0.6133 | 0.500 |
| F1 macro | 0.6128 | 0.500 |
| LR+ | 1.662 | >10 = très utile |
| LR− | 0.650 | <0.1 = très utile |
| Cohen κ | 0.2280 | 0.000 |
| Brier Score | 0.2807 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6741 | [0.6015, 0.7439]  ✅ |
| F1 macro | 0.6112 | [0.5439, 0.6726]  ✅ |
| Sensitivity | 0.5743 | [0.4754, 0.6653]  — |
| Specificity | 0.6537 | [0.5612, 0.7415]  — |
| MCC | 0.2284 | [0.0924, 0.3503]  — |
| R² | -0.0116 | [-0.1999, 0.1527]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0049 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6748 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2121 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2807 | < 0.20 |
| Log-Loss | 1.1070 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0085 | proche 0 = pas de biais systématique |
| LoA lower | -6.9158 | limite inférieure d'accord |
| LoA upper | +4.8987 | limite supérieure d'accord |
| LoA width | ±5.9073 | < ±2 pts : excellent |
| % dans LoA | 91.2% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0419 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0049 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6748 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4357 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 87.4 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.5 | 10% |

### **SCORE TOTAL : 55.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 08:15*
