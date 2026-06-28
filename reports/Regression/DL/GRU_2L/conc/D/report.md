# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_2L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 12:28


> 🟡 **Deployment Readiness Score : 67.2/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2102 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7926 | Erreur quadratique moyenne |
| R² | 0.2209 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7131 | 0.500 |
| PR-AUC | 0.7076 | 0.521 |
| Sensitivity (TPR) | 0.5929 | 0.500 |
| Specificity (TNR) | 0.6731 | 0.500 |
| PPV (Precision) | 0.6634 | — |
| NPV | 0.6034 | — |
| Balanced Accuracy | 0.6330 | 0.500 |
| MCC | 0.2664 | 0.000 |
| G-Mean | 0.6317 | 0.500 |
| F1 macro | 0.6313 | 0.500 |
| LR+ | 1.814 | >10 = très utile |
| LR− | 0.605 | <0.1 = très utile |
| Cohen κ | 0.2648 | 0.000 |
| Brier Score | 0.2412 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7133 | [0.6410, 0.7807]  ✅ |
| F1 macro | 0.6303 | [0.5569, 0.6997]  ✅ |
| Sensitivity | 0.5933 | [0.5000, 0.6870]  — |
| Specificity | 0.6729 | [0.5713, 0.7596]  — |
| MCC | 0.2666 | [0.1225, 0.4030]  — |
| R² | 0.2160 | [0.0910, 0.3321]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2209 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7131 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1178 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2412 | < 0.20 |
| Log-Loss | 0.7652 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5577 | proche 0 = pas de biais systématique |
| LoA lower | -5.9335 | limite inférieure d'accord |
| LoA upper | +4.8180 | limite supérieure d'accord |
| LoA width | ±5.3757 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1145 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2209 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7131 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2102 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 54.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 40.2 | 10% |

### **SCORE TOTAL : 67.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:28*
