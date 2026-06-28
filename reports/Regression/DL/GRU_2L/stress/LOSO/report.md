# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 18:37


> 🔴 **Deployment Readiness Score : 20.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0907 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4626 | Erreur quadratique moyenne |
| R² | -0.0698 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4791 | 0.500 |
| PR-AUC | 0.2861 | 0.282 |
| Sensitivity (TPR) | 0.0018 | 0.500 |
| Specificity (TNR) | 0.9979 | 0.500 |
| PPV (Precision) | 0.2500 | — |
| NPV | 0.7176 | — |
| Balanced Accuracy | 0.4998 | 0.500 |
| MCC | -0.0032 | 0.000 |
| G-Mean | 0.0419 | 0.500 |
| F1 macro | 0.4192 | 0.500 |
| LR+ | 0.847 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | -0.0005 | 0.000 |
| Brier Score | 0.2345 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4780 | [0.4505, 0.5057]  — |
| F1 macro | 0.4188 | [0.4106, 0.4271]  — |
| Sensitivity | 0.0016 | [0.0000, 0.0054]  — |
| Specificity | 0.9979 | [0.9951, 1.0000]  — |
| MCC | -0.0044 | [-0.0348, 0.0475]  — |
| R² | -0.0714 | [-0.0967, -0.0433]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1644 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2345 | < 0.20 |
| Log-Loss | 0.7695 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1869 | proche 0 = pas de biais systématique |
| LoA lower | -5.0010 | limite inférieure d'accord |
| LoA upper | +4.6271 | limite supérieure d'accord |
| LoA width | ±4.8140 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0015 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3916 | 0.9186 | 234.6% | 🔴 unstable |
| AUC ROC | 0.5327 | 0.0715 | 13.4% | 🟢 stable |
| MAE | 2.0906 | 0.6072 | 29.0% | 🟡 moderate |

**Stability Score global : 52.5/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 23.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 96.6 | 10% |

### **SCORE TOTAL : 20.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 18:37*
