# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN3D`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 12:19


> 🔴 **Deployment Readiness Score : 30.5/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0748 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4226 | Erreur quadratique moyenne |
| R² | -0.0353 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5753 | 0.500 |
| PR-AUC | 0.3335 | 0.282 |
| Sensitivity (TPR) | 0.0246 | 0.500 |
| Specificity (TNR) | 0.9799 | 0.500 |
| PPV (Precision) | 0.3256 | — |
| NPV | 0.7186 | — |
| Balanced Accuracy | 0.5023 | 0.500 |
| MCC | 0.0142 | 0.000 |
| G-Mean | 0.1553 | 0.500 |
| F1 macro | 0.4374 | 0.500 |
| LR+ | 1.227 | >10 = très utile |
| LR− | 0.995 | <0.1 = très utile |
| Cohen κ | 0.0063 | 0.000 |
| Brier Score | 0.2258 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5747 | [0.5481, 0.6017]  ✅ |
| F1 macro | 0.4377 | [0.4229, 0.4520]  — |
| Sensitivity | 0.0251 | [0.0117, 0.0380]  — |
| Specificity | 0.9800 | [0.9725, 0.9869]  — |
| MCC | 0.0158 | [-0.0327, 0.0649]  — |
| R² | -0.0359 | [-0.0612, -0.0133]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1612 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2258 | < 0.20 |
| Log-Loss | 0.7058 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0760 | proche 0 = pas de biais systématique |
| LoA lower | -4.8231 | limite inférieure d'accord |
| LoA upper | +4.6710 | limite supérieure d'accord |
| LoA width | ±4.7470 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0115 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3324 | 0.7243 | 217.9% | 🔴 unstable |
| AUC ROC | 0.5453 | 0.1234 | 22.6% | 🟡 moderate |
| MAE | 2.0747 | 0.5859 | 28.2% | 🟡 moderate |

**Stability Score global : 49.7/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 37.6 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 25.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 97.6 | 10% |

### **SCORE TOTAL : 30.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:19*
