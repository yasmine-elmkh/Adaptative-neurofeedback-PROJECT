# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN1D`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 03:52


> 🔴 **Deployment Readiness Score : 31.1/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0608 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4588 | Erreur quadratique moyenne |
| R² | -0.0665 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5970 | 0.500 |
| PR-AUC | 0.3448 | 0.282 |
| Sensitivity (TPR) | 0.1107 | 0.500 |
| Specificity (TNR) | 0.9260 | 0.500 |
| PPV (Precision) | 0.3706 | — |
| NPV | 0.7257 | — |
| Balanced Accuracy | 0.5184 | 0.500 |
| MCC | 0.0595 | 0.000 |
| G-Mean | 0.3202 | 0.500 |
| F1 macro | 0.4921 | 0.500 |
| LR+ | 1.496 | >10 = très utile |
| LR− | 0.960 | <0.1 = très utile |
| Cohen κ | 0.0466 | 0.000 |
| Brier Score | 0.2358 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5957 | [0.5684, 0.6226]  ✅ |
| F1 macro | 0.4921 | [0.4701, 0.5140]  — |
| Sensitivity | 0.1112 | [0.0841, 0.1375]  — |
| Specificity | 0.9257 | [0.9117, 0.9383]  — |
| MCC | 0.0598 | [0.0123, 0.1092]  — |
| R² | -0.0682 | [-0.1100, -0.0278]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1823 | < 0.05 |
| MCE | 0.5813 | < 0.10 |
| Brier Score | 0.2358 | < 0.20 |
| Log-Loss | 0.7833 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2791 | proche 0 = pas de biais systématique |
| LoA lower | -5.0685 | limite inférieure d'accord |
| LoA upper | +4.5103 | limite supérieure d'accord |
| LoA width | ±4.7894 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0097 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3388 | 0.4782 | 141.1% | 🔴 unstable |
| AUC ROC | 0.5511 | 0.1047 | 19.0% | 🟡 moderate |
| MAE | 2.0608 | 0.5748 | 27.9% | 🟡 moderate |

**Stability Score global : 51.0/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 48.5 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 11.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 97.2 | 10% |

### **SCORE TOTAL : 31.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 03:52*
