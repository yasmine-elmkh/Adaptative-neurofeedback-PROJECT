# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-14 02:28


> 🟠 **Deployment Readiness Score : 55.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4658 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1776 | Erreur quadratique moyenne |
| R² | -0.0087 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6719 | 0.500 |
| PR-AUC | 0.6443 | 0.521 |
| Sensitivity (TPR) | 0.3540 | 0.500 |
| Specificity (TNR) | 0.8077 | 0.500 |
| PPV (Precision) | 0.6667 | — |
| NPV | 0.5350 | — |
| Balanced Accuracy | 0.5808 | 0.500 |
| MCC | 0.1806 | 0.000 |
| G-Mean | 0.5347 | 0.500 |
| F1 macro | 0.5531 | 0.500 |
| LR+ | 1.841 | >10 = très utile |
| LR− | 0.800 | <0.1 = très utile |
| Cohen κ | 0.1585 | 0.000 |
| Brier Score | 0.3275 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6713 | [0.5973, 0.7420]  ✅ |
| F1 macro | 0.5516 | [0.4859, 0.6212]  — |
| Sensitivity | 0.3536 | [0.2653, 0.4454]  — |
| Specificity | 0.8070 | [0.7319, 0.8769]  — |
| MCC | 0.1792 | [0.0563, 0.2955]  — |
| R² | -0.0147 | [-0.1905, 0.1521]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0087 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6719 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2737 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3275 | < 0.20 |
| Log-Loss | 1.2053 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.2869 | proche 0 = pas de biais systématique |
| LoA lower | -6.9946 | limite inférieure d'accord |
| LoA upper | +4.4208 | limite supérieure d'accord |
| LoA width | ±5.7077 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0251 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0087 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6719 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4658 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 85.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.8 | 10% |

### **SCORE TOTAL : 55.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 02:28*
