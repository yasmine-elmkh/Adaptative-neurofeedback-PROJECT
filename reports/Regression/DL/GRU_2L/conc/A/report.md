# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_2L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 08:47


> 🟠 **Deployment Readiness Score : 58.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4633 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2211 | Erreur quadratique moyenne |
| R² | -0.0365 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7024 | 0.500 |
| PR-AUC | 0.6685 | 0.521 |
| Sensitivity (TPR) | 0.3451 | 0.500 |
| Specificity (TNR) | 0.8077 | 0.500 |
| PPV (Precision) | 0.6610 | — |
| NPV | 0.5316 | — |
| Balanced Accuracy | 0.5764 | 0.500 |
| MCC | 0.1716 | 0.000 |
| G-Mean | 0.5280 | 0.500 |
| F1 macro | 0.5474 | 0.500 |
| LR+ | 1.795 | >10 = très utile |
| LR− | 0.811 | <0.1 = très utile |
| Cohen κ | 0.1497 | 0.000 |
| Brier Score | 0.2894 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7024 | [0.6264, 0.7697]  ✅ |
| F1 macro | 0.5484 | [0.4774, 0.6140]  — |
| Sensitivity | 0.3488 | [0.2546, 0.4450]  — |
| Specificity | 0.8067 | [0.7234, 0.8762]  — |
| MCC | 0.1739 | [0.0349, 0.2974]  — |
| R² | -0.0436 | [-0.2478, 0.1446]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0365 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7024 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2511 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2894 | < 0.20 |
| Log-Loss | 1.1587 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.4217 | proche 0 = pas de biais systématique |
| LoA lower | -7.0998 | limite inférieure d'accord |
| LoA upper | +4.2565 | limite supérieure d'accord |
| LoA width | ±5.6782 | < ±2 pts : excellent |
| % dans LoA | 90.8% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0244 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0365 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7024 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4633 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.8 | 10% |

### **SCORE TOTAL : 58.8/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 08:47*
