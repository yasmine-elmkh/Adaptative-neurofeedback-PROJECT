# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN3D`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 00:23


> 🟠 **Deployment Readiness Score : 59.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3227 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9822 | Erreur quadratique moyenne |
| R² | 0.1116 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7120 | 0.500 |
| PR-AUC | 0.6925 | 0.521 |
| Sensitivity (TPR) | 0.2832 | 0.500 |
| Specificity (TNR) | 0.8846 | 0.500 |
| PPV (Precision) | 0.7273 | — |
| NPV | 0.5318 | — |
| Balanced Accuracy | 0.5839 | 0.500 |
| MCC | 0.2085 | 0.000 |
| G-Mean | 0.5005 | 0.500 |
| F1 macro | 0.5360 | 0.500 |
| LR+ | 2.454 | >10 = très utile |
| LR− | 0.810 | <0.1 = très utile |
| Cohen κ | 0.1635 | 0.000 |
| Brier Score | 0.3412 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7110 | [0.6417, 0.7746]  ✅ |
| F1 macro | 0.5336 | [0.4638, 0.5999]  — |
| Sensitivity | 0.2812 | [0.1991, 0.3606]  — |
| Specificity | 0.8843 | [0.8186, 0.9444]  — |
| MCC | 0.2059 | [0.0676, 0.3254]  — |
| R² | 0.1055 | [-0.0716, 0.2567]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1116 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7120 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3169 | < 0.05 |
| MCE | 0.4882 | < 0.10 |
| Brier Score | 0.3412 | < 0.20 |
| Log-Loss | 1.2181 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3286 | proche 0 = pas de biais systématique |
| LoA lower | -6.5736 | limite inférieure d'accord |
| LoA upper | +3.9164 | limite supérieure d'accord |
| LoA width | ±5.2450 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0316 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1116 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7120 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3227 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 44.8 | 10% |

### **SCORE TOTAL : 59.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 00:23*
