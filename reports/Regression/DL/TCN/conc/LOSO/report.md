# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `TCN`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 01:15


> 🔴 **Deployment Readiness Score : 30.3/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6116 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1055 | Erreur quadratique moyenne |
| R² | -0.0053 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6075 | 0.500 |
| PR-AUC | 0.5902 | 0.515 |
| Sensitivity (TPR) | 0.4843 | 0.500 |
| Specificity (TNR) | 0.6377 | 0.500 |
| PPV (Precision) | 0.5868 | — |
| NPV | 0.5379 | — |
| Balanced Accuracy | 0.5610 | 0.500 |
| MCC | 0.1233 | 0.000 |
| G-Mean | 0.5557 | 0.500 |
| F1 macro | 0.5571 | 0.500 |
| LR+ | 1.337 | >10 = très utile |
| LR− | 0.809 | <0.1 = très utile |
| Cohen κ | 0.1213 | 0.000 |
| Brier Score | 0.3098 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6075 | [0.5762, 0.6355]  ✅ |
| F1 macro | 0.5571 | [0.5326, 0.5804]  ✅ |
| Sensitivity | 0.4847 | [0.4489, 0.5186]  — |
| Specificity | 0.6376 | [0.6004, 0.6727]  — |
| MCC | 0.1236 | [0.0728, 0.1697]  — |
| R² | -0.0067 | [-0.0629, 0.0455]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2441 | < 0.05 |
| MCE | 0.3591 | < 0.10 |
| Brier Score | 0.3098 | < 0.20 |
| Log-Loss | 0.9877 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1830 | proche 0 = pas de biais systématique |
| LoA lower | -5.8953 | limite inférieure d'accord |
| LoA upper | +6.2612 | limite supérieure d'accord |
| LoA width | ±6.0783 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0672 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0398 | 0.1555 | 390.3% | 🔴 unstable |
| AUC ROC | 0.6162 | 0.0743 | 12.1% | 🟢 stable |
| MAE | 2.6164 | 0.3334 | 12.7% | 🟢 stable |

**Stability Score global : 58.4/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 53.7 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 93.8 | 10% |

### **SCORE TOTAL : 30.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 01:15*
