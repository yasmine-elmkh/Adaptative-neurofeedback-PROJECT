# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 20:03


> 🔴 **Deployment Readiness Score : 34.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7349 | Erreur absolue moyenne (0-10) |
| RMSE | 3.4134 | Erreur quadratique moyenne |
| R² | -0.1640 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5819 | 0.500 |
| PR-AUC | 0.5897 | 0.521 |
| Sensitivity (TPR) | 0.4159 | 0.500 |
| Specificity (TNR) | 0.6635 | 0.500 |
| PPV (Precision) | 0.5732 | — |
| NPV | 0.5111 | — |
| Balanced Accuracy | 0.5397 | 0.500 |
| MCC | 0.0818 | 0.000 |
| G-Mean | 0.5253 | 0.500 |
| F1 macro | 0.5297 | 0.500 |
| LR+ | 1.236 | >10 = très utile |
| LR− | 0.880 | <0.1 = très utile |
| Cohen κ | 0.0785 | 0.000 |
| Brier Score | 0.3504 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5799 | [0.5012, 0.6527]  ✅ |
| F1 macro | 0.5284 | [0.4596, 0.5968]  — |
| Sensitivity | 0.4156 | [0.3282, 0.5022]  — |
| Specificity | 0.6630 | [0.5776, 0.7501]  — |
| MCC | 0.0809 | [-0.0485, 0.2118]  — |
| R² | -0.1735 | [-0.3918, 0.0137]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1640 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5819 | p=0.0100 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3064 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3504 | < 0.20 |
| Log-Loss | 1.3746 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0250 | proche 0 = pas de biais systématique |
| LoA lower | -7.4213 | limite inférieure d'accord |
| LoA upper | +5.3712 | limite supérieure d'accord |
| LoA width | ±6.3962 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0262 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1640 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5819 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.7349 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 40.9 | 25% |
| Significativité (p-value) | 41.1 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 32.4 | 10% |

### **SCORE TOTAL : 34.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:03*
