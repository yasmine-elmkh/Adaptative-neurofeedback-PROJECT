# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_1L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 21:42


> 🔴 **Deployment Readiness Score : 30.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5687 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0757 | Erreur quadratique moyenne |
| R² | 0.0139 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6115 | 0.500 |
| PR-AUC | 0.6090 | 0.515 |
| Sensitivity (TPR) | 0.4557 | 0.500 |
| Specificity (TNR) | 0.6696 | 0.500 |
| PPV (Precision) | 0.5943 | — |
| NPV | 0.5366 | — |
| Balanced Accuracy | 0.5626 | 0.500 |
| MCC | 0.1280 | 0.000 |
| G-Mean | 0.5524 | 0.500 |
| F1 macro | 0.5558 | 0.500 |
| LR+ | 1.379 | >10 = très utile |
| LR− | 0.813 | <0.1 = très utile |
| Cohen κ | 0.1243 | 0.000 |
| Brier Score | 0.2923 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6120 | [0.5808, 0.6416]  ✅ |
| F1 macro | 0.5563 | [0.5293, 0.5821]  ✅ |
| Sensitivity | 0.4559 | [0.4226, 0.4901]  — |
| Specificity | 0.6707 | [0.6329, 0.7056]  — |
| MCC | 0.1294 | [0.0750, 0.1798]  — |
| R² | 0.0134 | [-0.0392, 0.0668]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2081 | < 0.05 |
| MCE | 0.3516 | < 0.10 |
| Brier Score | 0.2923 | < 0.20 |
| Log-Loss | 0.9795 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1148 | proche 0 = pas de biais systématique |
| LoA lower | -6.1410 | limite inférieure d'accord |
| LoA upper | +5.9115 | limite supérieure d'accord |
| LoA width | ±6.0263 | < ±2 pts : excellent |
| % dans LoA | 96.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1097 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0202 | 0.2319 | 1145.2% | 🔴 unstable |
| AUC ROC | 0.6080 | 0.0842 | 13.8% | 🟢 stable |
| MAE | 2.5657 | 0.3565 | 13.9% | 🟢 stable |

**Stability Score global : 86.1/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 55.8 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 92.8 | 10% |

### **SCORE TOTAL : 30.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 21:42*
