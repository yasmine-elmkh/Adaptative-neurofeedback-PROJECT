# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_1L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 15:08


> 🔴 **Deployment Readiness Score : 20.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0912 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4669 | Erreur quadratique moyenne |
| R² | -0.0735 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5144 | 0.500 |
| PR-AUC | 0.2924 | 0.282 |
| Sensitivity (TPR) | 0.0035 | 0.500 |
| Specificity (TNR) | 0.9903 | 0.500 |
| PPV (Precision) | 0.1250 | — |
| NPV | 0.7164 | — |
| Balanced Accuracy | 0.4969 | 0.500 |
| MCC | -0.0313 | 0.000 |
| G-Mean | 0.0590 | 0.500 |
| F1 macro | 0.4191 | 0.500 |
| LR+ | 0.363 | >10 = très utile |
| LR− | 1.006 | <0.1 = très utile |
| Cohen κ | -0.0087 | 0.000 |
| Brier Score | 0.2379 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5134 | [0.4881, 0.5425]  — |
| F1 macro | 0.4189 | [0.4108, 0.4274]  — |
| Sensitivity | 0.0036 | [0.0000, 0.0090]  — |
| Specificity | 0.9903 | [0.9855, 0.9951]  — |
| MCC | -0.0304 | [-0.0597, 0.0059]  — |
| R² | -0.0746 | [-0.0998, -0.0489]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1806 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2379 | < 0.20 |
| Log-Loss | 0.7756 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2081 | proche 0 = pas de biais systématique |
| LoA lower | -5.0271 | limite inférieure d'accord |
| LoA upper | +4.6110 | limite supérieure d'accord |
| LoA width | ±4.8190 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0003 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3812 | 0.9110 | 239.0% | 🔴 unstable |
| AUC ROC | 0.5178 | 0.0901 | 17.4% | 🟡 moderate |
| MAE | 2.0911 | 0.6182 | 29.6% | 🟡 moderate |

**Stability Score global : 51.0/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 7.2 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 12.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 97.1 | 10% |

### **SCORE TOTAL : 20.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:08*
