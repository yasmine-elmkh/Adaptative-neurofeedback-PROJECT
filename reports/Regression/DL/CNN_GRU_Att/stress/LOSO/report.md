# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 07:22


> 🔴 **Deployment Readiness Score : 26.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0807 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4420 | Erreur quadratique moyenne |
| R² | -0.0520 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5511 | 0.500 |
| PR-AUC | 0.2944 | 0.282 |
| Sensitivity (TPR) | 0.0193 | 0.500 |
| Specificity (TNR) | 0.9716 | 0.500 |
| PPV (Precision) | 0.2115 | — |
| NPV | 0.7157 | — |
| Balanced Accuracy | 0.4955 | 0.500 |
| MCC | -0.0256 | 0.000 |
| G-Mean | 0.1371 | 0.500 |
| F1 macro | 0.4299 | 0.500 |
| LR+ | 0.682 | >10 = très utile |
| LR− | 1.009 | <0.1 = très utile |
| Cohen κ | -0.0125 | 0.000 |
| Brier Score | 0.2355 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5508 | [0.5227, 0.5766]  ✅ |
| F1 macro | 0.4297 | [0.4173, 0.4450]  — |
| Sensitivity | 0.0194 | [0.0092, 0.0325]  — |
| Specificity | 0.9717 | [0.9630, 0.9791]  — |
| MCC | -0.0253 | [-0.0623, 0.0212]  — |
| R² | -0.0524 | [-0.0799, -0.0254]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1765 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2355 | < 0.20 |
| Log-Loss | 0.7357 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1213 | proche 0 = pas de biais systématique |
| LoA lower | -4.9030 | limite inférieure d'accord |
| LoA upper | +4.6604 | limite supérieure d'accord |
| LoA width | ±4.7817 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0128 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3542 | 0.7158 | 202.1% | 🔴 unstable |
| AUC ROC | 0.5633 | 0.1084 | 19.2% | 🟡 moderate |
| MAE | 2.0805 | 0.5847 | 28.1% | 🟡 moderate |

**Stability Score global : 50.9/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 25.6 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 15.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 97.4 | 10% |

### **SCORE TOTAL : 26.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 07:22*
