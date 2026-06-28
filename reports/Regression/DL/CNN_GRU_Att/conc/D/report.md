# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-14 03:07


> 🟠 **Deployment Readiness Score : 53.4/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4573 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2483 | Erreur quadratique moyenne |
| R² | -0.0541 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6642 | 0.500 |
| PR-AUC | 0.6669 | 0.521 |
| Sensitivity (TPR) | 0.4602 | 0.500 |
| Specificity (TNR) | 0.6731 | 0.500 |
| PPV (Precision) | 0.6047 | — |
| NPV | 0.5344 | — |
| Balanced Accuracy | 0.5666 | 0.500 |
| MCC | 0.1361 | 0.000 |
| G-Mean | 0.5565 | 0.500 |
| F1 macro | 0.5592 | 0.500 |
| LR+ | 1.408 | >10 = très utile |
| LR− | 0.802 | <0.1 = très utile |
| Cohen κ | 0.1319 | 0.000 |
| Brier Score | 0.3221 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6647 | [0.5809, 0.7384]  ✅ |
| F1 macro | 0.5589 | [0.4964, 0.6279]  — |
| Sensitivity | 0.4625 | [0.3682, 0.5526]  — |
| Specificity | 0.6718 | [0.5852, 0.7604]  — |
| MCC | 0.1370 | [0.0146, 0.2774]  — |
| R² | -0.0583 | [-0.2583, 0.1349]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0541 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6642 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2805 | < 0.05 |
| MCE | 0.5279 | < 0.10 |
| Brier Score | 0.3221 | < 0.20 |
| Log-Loss | 1.1788 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8910 | proche 0 = pas de biais systématique |
| LoA lower | -7.0276 | limite inférieure d'accord |
| LoA upper | +5.2456 | limite supérieure d'accord |
| LoA width | ±6.1366 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0487 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0541 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6642 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4573 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 82.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 28.3 | 10% |

### **SCORE TOTAL : 53.4/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 03:07*
