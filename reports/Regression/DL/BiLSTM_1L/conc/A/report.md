# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_1L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 19:35


> 🟡 **Deployment Readiness Score : 64.3/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2744 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8728 | Erreur quadratique moyenne |
| R² | 0.1755 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7021 | 0.500 |
| PR-AUC | 0.6772 | 0.521 |
| Sensitivity (TPR) | 0.6814 | 0.500 |
| Specificity (TNR) | 0.6058 | 0.500 |
| PPV (Precision) | 0.6525 | — |
| NPV | 0.6364 | — |
| Balanced Accuracy | 0.6436 | 0.500 |
| MCC | 0.2880 | 0.000 |
| G-Mean | 0.6425 | 0.500 |
| F1 macro | 0.6437 | 0.500 |
| LR+ | 1.728 | >10 = très utile |
| LR− | 0.526 | <0.1 = très utile |
| Cohen κ | 0.2877 | 0.000 |
| Brier Score | 0.2452 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7009 | [0.6254, 0.7693]  ✅ |
| F1 macro | 0.6424 | [0.5755, 0.7004]  ✅ |
| Sensitivity | 0.6799 | [0.5973, 0.7732]  — |
| Specificity | 0.6070 | [0.5021, 0.7005]  — |
| MCC | 0.2878 | [0.1520, 0.4025]  — |
| R² | 0.1692 | [0.0295, 0.2927]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1755 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7021 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1440 | < 0.05 |
| MCE | 0.3619 | < 0.10 |
| Brier Score | 0.2452 | < 0.20 |
| Log-Loss | 0.7730 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3021 | proche 0 = pas de biais systématique |
| LoA lower | -5.9145 | limite inférieure d'accord |
| LoA upper | +5.3103 | limite supérieure d'accord |
| LoA width | ±5.6124 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1996 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1755 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7021 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2744 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 37.4 | 10% |

### **SCORE TOTAL : 64.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 19:35*
