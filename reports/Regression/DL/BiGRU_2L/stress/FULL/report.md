# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 02:32


> 🔴 **Deployment Readiness Score : 29.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3738 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8254 | Erreur quadratique moyenne |
| R² | -0.0179 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5403 | 0.500 |
| PR-AUC | 0.3935 | 0.366 |
| Sensitivity (TPR) | 0.2152 | 0.500 |
| Specificity (TNR) | 0.8066 | 0.500 |
| PPV (Precision) | 0.3908 | — |
| NPV | 0.6406 | — |
| Balanced Accuracy | 0.5109 | 0.500 |
| MCC | 0.0261 | 0.000 |
| G-Mean | 0.4166 | 0.500 |
| F1 macro | 0.4958 | 0.500 |
| LR+ | 1.112 | >10 = très utile |
| LR− | 0.973 | <0.1 = très utile |
| Cohen κ | 0.0240 | 0.000 |
| Brier Score | 0.2635 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5397 | [0.4862, 0.5973]  — |
| F1 macro | 0.4955 | [0.4478, 0.5424]  — |
| Sensitivity | 0.2149 | [0.1506, 0.2781]  — |
| Specificity | 0.8072 | [0.7629, 0.8533]  — |
| MCC | 0.0266 | [-0.0684, 0.1224]  — |
| R² | -0.0226 | [-0.0819, 0.0429]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0179 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5403 | p=0.0820 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1639 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2635 | < 0.20 |
| Log-Loss | 0.8104 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0025 | proche 0 = pas de biais systématique |
| LoA lower | -5.5418 | limite inférieure d'accord |
| LoA upper | +5.5467 | limite supérieure d'accord |
| LoA width | ±5.5442 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0653 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0179 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5403 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3738 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 20.2 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 24.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 59.2 | 10% |

### **SCORE TOTAL : 29.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 02:32*
