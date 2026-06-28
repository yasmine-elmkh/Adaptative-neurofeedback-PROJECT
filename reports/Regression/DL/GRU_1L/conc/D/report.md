# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_1L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 11:43


> 🟠 **Deployment Readiness Score : 56.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6703 | Erreur absolue moyenne (0-10) |
| RMSE | 3.3860 | Erreur quadratique moyenne |
| R² | -0.1454 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6860 | 0.500 |
| PR-AUC | 0.6710 | 0.521 |
| Sensitivity (TPR) | 0.0619 | 0.500 |
| Specificity (TNR) | 0.9808 | 0.500 |
| PPV (Precision) | 0.7778 | — |
| NPV | 0.4904 | — |
| Balanced Accuracy | 0.5214 | 0.500 |
| MCC | 0.1070 | 0.000 |
| G-Mean | 0.2465 | 0.500 |
| F1 macro | 0.3843 | 0.500 |
| LR+ | 3.221 | >10 = très utile |
| LR− | 0.956 | <0.1 = très utile |
| Cohen κ | 0.0411 | 0.000 |
| Brier Score | 0.3474 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6845 | [0.6094, 0.7552]  ✅ |
| F1 macro | 0.3839 | [0.3366, 0.4399]  — |
| Sensitivity | 0.0617 | [0.0181, 0.1121]  — |
| Specificity | 0.9813 | [0.9500, 1.0000]  — |
| MCC | 0.1064 | [-0.0195, 0.2083]  — |
| R² | -0.1521 | [-0.3815, 0.0311]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1454 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6860 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3316 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3474 | < 0.20 |
| Log-Loss | 1.3221 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.6591 | proche 0 = pas de biais systématique |
| LoA lower | -7.4579 | limite inférieure d'accord |
| LoA upper | +4.1397 | limite supérieure d'accord |
| LoA width | ±5.7988 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0147 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1454 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6860 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.6703 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 93.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.2 | 10% |

### **SCORE TOTAL : 56.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 11:43*
