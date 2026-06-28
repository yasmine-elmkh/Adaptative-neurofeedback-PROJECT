# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 07:44


> 🔴 **Deployment Readiness Score : 20.5/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0817 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4406 | Erreur quadratique moyenne |
| R² | -0.0507 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4540 | 0.500 |
| PR-AUC | 0.2715 | 0.282 |
| Sensitivity (TPR) | 0.0105 | 0.500 |
| Specificity (TNR) | 0.9924 | 0.500 |
| PPV (Precision) | 0.3529 | — |
| NPV | 0.7182 | — |
| Balanced Accuracy | 0.5015 | 0.500 |
| MCC | 0.0145 | 0.000 |
| G-Mean | 0.1023 | 0.500 |
| F1 macro | 0.4269 | 0.500 |
| LR+ | 1.386 | >10 = très utile |
| LR− | 0.997 | <0.1 = très utile |
| Cohen κ | 0.0042 | 0.000 |
| Brier Score | 0.2369 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4532 | [0.4242, 0.4809]  — |
| F1 macro | 0.4268 | [0.4160, 0.4384]  — |
| Sensitivity | 0.0107 | [0.0035, 0.0191]  — |
| Specificity | 0.9923 | [0.9874, 0.9965]  — |
| MCC | 0.0150 | [-0.0283, 0.0613]  — |
| R² | -0.0512 | [-0.0726, -0.0315]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1659 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2369 | < 0.20 |
| Log-Loss | 0.7605 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1174 | proche 0 = pas de biais systématique |
| LoA lower | -4.8966 | limite inférieure d'accord |
| LoA upper | +4.6618 | limite supérieure d'accord |
| LoA width | ±4.7792 | < ±2 pts : excellent |
| % dans LoA | 96.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0016 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3744 | 1.0227 | 273.1% | 🔴 unstable |
| AUC ROC | 0.5242 | 0.1077 | 20.6% | 🟡 moderate |
| MAE | 2.0817 | 0.6312 | 30.3% | 🔴 unstable |

**Stability Score global : 49.7/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 22.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 95.6 | 10% |

### **SCORE TOTAL : 20.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 07:44*
