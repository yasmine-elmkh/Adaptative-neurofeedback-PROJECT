# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN2D`  |  **Exp :** `A`  |  **Date :** 2026-06-12 17:56


> 🟠 **Deployment Readiness Score : 50.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4093 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0476 | Erreur quadratique moyenne |
| R² | 0.0721 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6347 | 0.500 |
| PR-AUC | 0.6026 | 0.521 |
| Sensitivity (TPR) | 0.1504 | 0.500 |
| Specificity (TNR) | 0.8269 | 0.500 |
| PPV (Precision) | 0.4857 | — |
| NPV | 0.4725 | — |
| Balanced Accuracy | 0.4887 | 0.500 |
| MCC | -0.0307 | 0.000 |
| G-Mean | 0.3527 | 0.500 |
| F1 macro | 0.4156 | 0.500 |
| LR+ | 0.869 | >10 = très utile |
| LR− | 1.027 | <0.1 = très utile |
| Cohen κ | -0.0220 | 0.000 |
| Brier Score | 0.3473 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6342 | [0.5596, 0.7090]  ✅ |
| F1 macro | 0.4146 | [0.3599, 0.4736]  — |
| Sensitivity | 0.1505 | [0.0901, 0.2174]  — |
| Specificity | 0.8259 | [0.7582, 0.8934]  — |
| MCC | -0.0320 | [-0.1559, 0.1006]  — |
| R² | 0.0655 | [-0.0868, 0.1959]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0721 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6347 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3374 | < 0.05 |
| MCE | 0.8271 | < 0.10 |
| Brier Score | 0.3473 | < 0.20 |
| Log-Loss | 1.1075 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0770 | proche 0 = pas de biais systématique |
| LoA lower | -6.6779 | limite inférieure d'accord |
| LoA upper | +4.5238 | limite supérieure d'accord |
| LoA width | ±5.6009 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0381 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0721 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6347 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4093 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 67.4 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 33.7 | 10% |

### **SCORE TOTAL : 50.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 17:56*
