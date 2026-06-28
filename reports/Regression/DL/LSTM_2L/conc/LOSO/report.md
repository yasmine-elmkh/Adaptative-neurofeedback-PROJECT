# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 11:43


> 🔴 **Deployment Readiness Score : 29.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5295 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0804 | Erreur quadratique moyenne |
| R² | 0.0109 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6038 | 0.500 |
| PR-AUC | 0.5695 | 0.515 |
| Sensitivity (TPR) | 0.4175 | 0.500 |
| Specificity (TNR) | 0.6739 | 0.500 |
| PPV (Precision) | 0.5763 | — |
| NPV | 0.5213 | — |
| Balanced Accuracy | 0.5457 | 0.500 |
| MCC | 0.0944 | 0.000 |
| G-Mean | 0.5304 | 0.500 |
| F1 macro | 0.5360 | 0.500 |
| LR+ | 1.280 | >10 = très utile |
| LR− | 0.864 | <0.1 = très utile |
| Cohen κ | 0.0906 | 0.000 |
| Brier Score | 0.2858 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6034 | [0.5737, 0.6322]  ✅ |
| F1 macro | 0.5355 | [0.5109, 0.5588]  ✅ |
| Sensitivity | 0.4174 | [0.3831, 0.4528]  — |
| Specificity | 0.6732 | [0.6397, 0.7056]  — |
| MCC | 0.0936 | [0.0456, 0.1408]  — |
| R² | 0.0079 | [-0.0525, 0.0697]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2014 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2858 | < 0.20 |
| Log-Loss | 1.0090 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2901 | proche 0 = pas de biais systématique |
| LoA lower | -6.3029 | limite inférieure d'accord |
| LoA upper | +5.7226 | limite supérieure d'accord |
| LoA width | ±6.0128 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0446 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0121 | 0.3041 | 2503.9% | 🔴 unstable |
| AUC ROC | 0.6129 | 0.1116 | 18.2% | 🟡 moderate |
| MAE | 2.5158 | 0.3670 | 14.6% | 🟢 stable |

**Stability Score global : 83.6/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 51.9 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.4 | 10% |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 11:43*
