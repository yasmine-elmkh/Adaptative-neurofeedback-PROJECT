# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN1D`  |  **Exp :** `D`  |  **Date :** 2026-06-12 23:21


> 🔴 **Deployment Readiness Score : 22.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4743 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8765 | Erreur quadratique moyenne |
| R² | -0.0551 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5151 | 0.500 |
| PR-AUC | 0.3884 | 0.366 |
| Sensitivity (TPR) | 0.2089 | 0.500 |
| Specificity (TNR) | 0.8431 | 0.500 |
| PPV (Precision) | 0.4342 | — |
| NPV | 0.6489 | — |
| Balanced Accuracy | 0.5260 | 0.500 |
| MCC | 0.0657 | 0.000 |
| G-Mean | 0.4196 | 0.500 |
| F1 macro | 0.5077 | 0.500 |
| LR+ | 1.331 | >10 = très utile |
| LR− | 0.938 | <0.1 = très utile |
| Cohen κ | 0.0583 | 0.000 |
| Brier Score | 0.2861 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5163 | [0.4569, 0.5710]  — |
| F1 macro | 0.5081 | [0.4592, 0.5593]  — |
| Sensitivity | 0.2110 | [0.1487, 0.2790]  — |
| Specificity | 0.8416 | [0.7972, 0.8821]  — |
| MCC | 0.0662 | [-0.0304, 0.1632]  — |
| R² | -0.0558 | [-0.1227, 0.0088]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0551 | p=0.0120 | ✅ p<0.05 |
| AUC ROC | 0.5151 | p=0.3220 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2164 | < 0.05 |
| MCE | 0.9094 | < 0.10 |
| Brier Score | 0.2861 | < 0.20 |
| Log-Loss | 0.8757 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1166 | proche 0 = pas de biais systématique |
| LoA lower | -5.7565 | limite inférieure d'accord |
| LoA upper | +5.5232 | limite supérieure d'accord |
| LoA width | ±5.6398 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0356 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0551 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5151 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4743 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 7.6 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 57.3 | 10% |

### **SCORE TOTAL : 22.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 23:21*
