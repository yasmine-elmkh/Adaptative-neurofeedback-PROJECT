# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 11:18


> 🔴 **Deployment Readiness Score : 32.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5363 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1588 | Erreur quadratique moyenne |
| R² | -0.0401 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6218 | 0.500 |
| PR-AUC | 0.6014 | 0.515 |
| Sensitivity (TPR) | 0.5102 | 0.500 |
| Specificity (TNR) | 0.6391 | 0.500 |
| PPV (Precision) | 0.6003 | — |
| NPV | 0.5513 | — |
| Balanced Accuracy | 0.5747 | 0.500 |
| MCC | 0.1505 | 0.000 |
| G-Mean | 0.5711 | 0.500 |
| F1 macro | 0.5718 | 0.500 |
| LR+ | 1.414 | >10 = très utile |
| LR− | 0.766 | <0.1 = très utile |
| Cohen κ | 0.1487 | 0.000 |
| Brier Score | 0.3064 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6222 | [0.5914, 0.6524]  ✅ |
| F1 macro | 0.5724 | [0.5448, 0.5984]  ✅ |
| Sensitivity | 0.5110 | [0.4746, 0.5470]  — |
| Specificity | 0.6399 | [0.6008, 0.6763]  — |
| MCC | 0.1520 | [0.0970, 0.2050]  — |
| R² | -0.0410 | [-0.1126, 0.0244]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2308 | < 0.05 |
| MCE | 0.3923 | < 0.10 |
| Brier Score | 0.3064 | < 0.20 |
| Log-Loss | 1.1168 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3090 | proche 0 = pas de biais systématique |
| LoA lower | -6.4727 | limite inférieure d'accord |
| LoA upper | +5.8547 | limite supérieure d'accord |
| LoA width | ±6.1637 | < ±2 pts : excellent |
| % dans LoA | 95.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0401 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0813 | 0.3888 | 478.0% | 🔴 unstable |
| AUC ROC | 0.6112 | 0.0931 | 15.2% | 🟡 moderate |
| MAE | 2.5773 | 0.6152 | 23.9% | 🟡 moderate |

**Stability Score global : 53.6/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 60.9 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 92.7 | 10% |

### **SCORE TOTAL : 32.0/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 11:18*
