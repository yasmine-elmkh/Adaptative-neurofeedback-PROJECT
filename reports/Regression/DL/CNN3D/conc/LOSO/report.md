# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN3D`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 03:52


> 🔴 **Deployment Readiness Score : 33.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4948 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0047 | Erreur quadratique moyenne |
| R² | 0.0589 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6326 | 0.500 |
| PR-AUC | 0.5840 | 0.515 |
| Sensitivity (TPR) | 0.4188 | 0.500 |
| Specificity (TNR) | 0.7159 | 0.500 |
| PPV (Precision) | 0.6103 | — |
| NPV | 0.5370 | — |
| Balanced Accuracy | 0.5674 | 0.500 |
| MCC | 0.1409 | 0.000 |
| G-Mean | 0.5476 | 0.500 |
| F1 macro | 0.5552 | 0.500 |
| LR+ | 1.474 | >10 = très utile |
| LR− | 0.812 | <0.1 = très utile |
| Cohen κ | 0.1335 | 0.000 |
| Brier Score | 0.3247 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6324 | [0.6027, 0.6598]  ✅ |
| F1 macro | 0.5557 | [0.5298, 0.5821]  ✅ |
| Sensitivity | 0.4195 | [0.3835, 0.4574]  — |
| Specificity | 0.7165 | [0.6826, 0.7482]  — |
| MCC | 0.1421 | [0.0887, 0.1934]  — |
| R² | 0.0573 | [0.0026, 0.1166]  ✅ |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2807 | < 0.05 |
| MCE | 0.4145 | < 0.10 |
| Brier Score | 0.3247 | < 0.20 |
| Log-Loss | 1.0979 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2330 | proche 0 = pas de biais systématique |
| LoA lower | -6.1066 | limite inférieure d'accord |
| LoA upper | +5.6406 | limite supérieure d'accord |
| LoA width | ±5.8736 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0723 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0084 | 0.2624 | 3129.9% | 🔴 unstable |
| AUC ROC | 0.6199 | 0.1154 | 18.6% | 🟡 moderate |
| MAE | 2.5215 | 0.2966 | 11.8% | 🟢 stable |

**Stability Score global : 84.8/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 66.3 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 95.3 | 10% |

### **SCORE TOTAL : 33.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 03:52*
