# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN1D`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 00:15


> 🔴 **Deployment Readiness Score : 21.1/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5102 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9924 | Erreur quadratique moyenne |
| R² | -0.1418 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5063 | 0.500 |
| PR-AUC | 0.3667 | 0.366 |
| Sensitivity (TPR) | 0.0380 | 0.500 |
| Specificity (TNR) | 0.9380 | 0.500 |
| PPV (Precision) | 0.2609 | — |
| NPV | 0.6284 | — |
| Balanced Accuracy | 0.4880 | 0.500 |
| MCC | -0.0516 | 0.000 |
| G-Mean | 0.1887 | 0.500 |
| F1 macro | 0.4094 | 0.500 |
| LR+ | 0.612 | >10 = très utile |
| LR− | 1.026 | <0.1 = très utile |
| Cohen κ | -0.0294 | 0.000 |
| Brier Score | 0.3083 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5060 | [0.4465, 0.5666]  — |
| F1 macro | 0.4095 | [0.3791, 0.4436]  — |
| Sensitivity | 0.0380 | [0.0125, 0.0719]  — |
| Specificity | 0.9376 | [0.9076, 0.9639]  — |
| MCC | -0.0518 | [-0.1337, 0.0358]  — |
| R² | -0.1422 | [-0.2133, -0.0737]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1418 | p=0.2060 | ❌ ns |
| AUC ROC | 0.5063 | p=0.4120 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2585 | < 0.05 |
| MCE | 0.9379 | < 0.10 |
| Brier Score | 0.3083 | < 0.20 |
| Log-Loss | 1.0175 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6304 | proche 0 = pas de biais systématique |
| LoA lower | -6.3704 | limite inférieure d'accord |
| LoA upper | +5.1097 | limite supérieure d'accord |
| LoA width | ±5.7401 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0019 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1418 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5063 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5102 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 3.1 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 53.2 | 10% |

### **SCORE TOTAL : 21.1/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 00:15*
