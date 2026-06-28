# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 23:12


> 🔴 **Deployment Readiness Score : 29.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5757 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1859 | Erreur quadratique moyenne |
| R² | -0.0580 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6047 | 0.500 |
| PR-AUC | 0.5785 | 0.515 |
| Sensitivity (TPR) | 0.4966 | 0.500 |
| Specificity (TNR) | 0.6362 | 0.500 |
| PPV (Precision) | 0.5919 | — |
| NPV | 0.5433 | — |
| Balanced Accuracy | 0.5664 | 0.500 |
| MCC | 0.1340 | 0.000 |
| G-Mean | 0.5621 | 0.500 |
| F1 macro | 0.5631 | 0.500 |
| LR+ | 1.365 | >10 = très utile |
| LR− | 0.791 | <0.1 = très utile |
| Cohen κ | 0.1322 | 0.000 |
| Brier Score | 0.3112 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6049 | [0.5753, 0.6359]  ✅ |
| F1 macro | 0.5631 | [0.5388, 0.5888]  ✅ |
| Sensitivity | 0.4968 | [0.4615, 0.5358]  — |
| Specificity | 0.6363 | [0.5997, 0.6748]  — |
| MCC | 0.1343 | [0.0847, 0.1851]  — |
| R² | -0.0582 | [-0.1245, 0.0032]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2388 | < 0.05 |
| MCE | 0.3955 | < 0.10 |
| Brier Score | 0.3112 | < 0.20 |
| Log-Loss | 1.1223 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3180 | proche 0 = pas de biais systématique |
| LoA lower | -6.5334 | limite inférieure d'accord |
| LoA upper | +5.8973 | limite supérieure d'accord |
| LoA width | ±6.2153 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0346 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1035 | 0.3639 | 351.7% | 🔴 unstable |
| AUC ROC | 0.6163 | 0.1137 | 18.4% | 🟡 moderate |
| MAE | 2.6107 | 0.5728 | 21.9% | 🟡 moderate |

**Stability Score global : 53.2/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 52.3 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 92.9 | 10% |

### **SCORE TOTAL : 29.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 23:12*
