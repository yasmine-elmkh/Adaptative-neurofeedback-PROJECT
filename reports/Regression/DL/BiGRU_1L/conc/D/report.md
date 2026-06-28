# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 16:12


> 🟡 **Deployment Readiness Score : 61.2/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1188 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7023 | Erreur quadratique moyenne |
| R² | 0.2705 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6892 | 0.500 |
| PR-AUC | 0.6878 | 0.521 |
| Sensitivity (TPR) | 0.7345 | 0.500 |
| Specificity (TNR) | 0.5288 | 0.500 |
| PPV (Precision) | 0.6288 | — |
| NPV | 0.6471 | — |
| Balanced Accuracy | 0.6317 | 0.500 |
| MCC | 0.2695 | 0.000 |
| G-Mean | 0.6233 | 0.500 |
| F1 macro | 0.6298 | 0.500 |
| LR+ | 1.559 | >10 = très utile |
| LR− | 0.502 | <0.1 = très utile |
| Cohen κ | 0.2653 | 0.000 |
| Brier Score | 0.2378 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6882 | [0.6162, 0.7620]  ✅ |
| F1 macro | 0.6280 | [0.5618, 0.6871]  ✅ |
| Sensitivity | 0.7351 | [0.6550, 0.8074]  — |
| Specificity | 0.5273 | [0.4292, 0.6226]  — |
| MCC | 0.2686 | [0.1366, 0.3893]  — |
| R² | 0.2663 | [0.1555, 0.3744]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2705 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6892 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1606 | < 0.05 |
| MCE | 0.4208 | < 0.10 |
| Brier Score | 0.2378 | < 0.20 |
| Log-Loss | 0.7064 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2952 | proche 0 = pas de biais systématique |
| LoA lower | -5.5722 | limite inférieure d'accord |
| LoA upper | +4.9818 | limite supérieure d'accord |
| LoA width | ±5.2770 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2452 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2705 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6892 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1188 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 94.6 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 26.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.1 | 10% |

### **SCORE TOTAL : 61.2/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 16:12*
