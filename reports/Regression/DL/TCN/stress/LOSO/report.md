# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `TCN`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 13:25


> 🔴 **Deployment Readiness Score : 21.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0957 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4622 | Erreur quadratique moyenne |
| R² | -0.0694 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5197 | 0.500 |
| PR-AUC | 0.2995 | 0.282 |
| Sensitivity (TPR) | 0.0439 | 0.500 |
| Specificity (TNR) | 0.9703 | 0.500 |
| PPV (Precision) | 0.3676 | — |
| NPV | 0.7206 | — |
| Balanced Accuracy | 0.5071 | 0.500 |
| MCC | 0.0354 | 0.000 |
| G-Mean | 0.2065 | 0.500 |
| F1 macro | 0.4527 | 0.500 |
| LR+ | 1.478 | >10 = très utile |
| LR− | 0.985 | <0.1 = très utile |
| Cohen κ | 0.0194 | 0.000 |
| Brier Score | 0.2371 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5190 | [0.4903, 0.5479]  — |
| F1 macro | 0.4524 | [0.4351, 0.4702]  — |
| Sensitivity | 0.0439 | [0.0274, 0.0623]  — |
| Specificity | 0.9700 | [0.9613, 0.9784]  — |
| MCC | 0.0346 | [-0.0114, 0.0809]  — |
| R² | -0.0705 | [-0.0991, -0.0412]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1787 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2371 | < 0.20 |
| Log-Loss | 0.7765 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1636 | proche 0 = pas de biais systématique |
| LoA lower | -4.9800 | limite inférieure d'accord |
| LoA upper | +4.6529 | limite supérieure d'accord |
| LoA width | ±4.8164 | < ±2 pts : excellent |
| % dans LoA | 97.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0066 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4464 | 1.1859 | 265.7% | 🔴 unstable |
| AUC ROC | 0.5673 | 0.1116 | 19.7% | 🟡 moderate |
| MAE | 2.0956 | 0.5915 | 28.2% | 🟡 moderate |

**Stability Score global : 50.7/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 9.9 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 14.2 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 94.9 | 10% |

### **SCORE TOTAL : 21.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 13:25*
