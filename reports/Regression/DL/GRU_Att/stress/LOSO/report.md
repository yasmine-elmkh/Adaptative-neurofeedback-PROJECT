# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 14:03


> 🔴 **Deployment Readiness Score : 25.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0746 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4442 | Erreur quadratique moyenne |
| R² | -0.0539 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5376 | 0.500 |
| PR-AUC | 0.3208 | 0.282 |
| Sensitivity (TPR) | 0.0105 | 0.500 |
| Specificity (TNR) | 0.9959 | 0.500 |
| PPV (Precision) | 0.5000 | — |
| NPV | 0.7189 | — |
| Balanced Accuracy | 0.5032 | 0.500 |
| MCC | 0.0374 | 0.000 |
| G-Mean | 0.1025 | 0.500 |
| F1 macro | 0.4278 | 0.500 |
| LR+ | 2.541 | >10 = très utile |
| LR− | 0.994 | <0.1 = très utile |
| Cohen κ | 0.0091 | 0.000 |
| Brier Score | 0.2323 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5360 | [0.5097, 0.5651]  ✅ |
| F1 macro | 0.4274 | [0.4158, 0.4387]  — |
| Sensitivity | 0.0104 | [0.0033, 0.0188]  — |
| Specificity | 0.9958 | [0.9923, 0.9986]  — |
| MCC | 0.0358 | [-0.0109, 0.0838]  — |
| R² | -0.0551 | [-0.0790, -0.0313]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1681 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2323 | < 0.20 |
| Log-Loss | 0.7547 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2383 | proche 0 = pas de biais systématique |
| LoA lower | -5.0074 | limite inférieure d'accord |
| LoA upper | +4.5308 | limite supérieure d'accord |
| LoA width | ±4.7691 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0020 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3444 | 0.7441 | 216.0% | 🔴 unstable |
| AUC ROC | 0.5340 | 0.0862 | 16.1% | 🟡 moderate |
| MAE | 2.0745 | 0.6072 | 29.3% | 🟡 moderate |

**Stability Score global : 51.5/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 18.8 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 21.2 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 96.4 | 10% |

### **SCORE TOTAL : 25.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 14:03*
