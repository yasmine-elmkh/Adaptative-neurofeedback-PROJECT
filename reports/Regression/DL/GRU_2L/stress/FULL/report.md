# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_2L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 15:52


> 🔴 **Deployment Readiness Score : 28.3/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4096 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8308 | Erreur quadratique moyenne |
| R² | -0.0218 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5398 | 0.500 |
| PR-AUC | 0.3814 | 0.366 |
| Sensitivity (TPR) | 0.0886 | 0.500 |
| Specificity (TNR) | 0.8905 | 0.500 |
| PPV (Precision) | 0.3182 | — |
| NPV | 0.6289 | — |
| Balanced Accuracy | 0.4896 | 0.500 |
| MCC | -0.0333 | 0.000 |
| G-Mean | 0.2809 | 0.500 |
| F1 macro | 0.4379 | 0.500 |
| LR+ | 0.809 | >10 = très utile |
| LR− | 1.023 | <0.1 = très utile |
| Cohen κ | -0.0246 | 0.000 |
| Brier Score | 0.2681 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5393 | [0.4872, 0.5915]  — |
| F1 macro | 0.4366 | [0.3969, 0.4741]  — |
| Sensitivity | 0.0870 | [0.0433, 0.1293]  — |
| Specificity | 0.8909 | [0.8514, 0.9263]  — |
| MCC | -0.0351 | [-0.1194, 0.0508]  — |
| R² | -0.0249 | [-0.0847, 0.0342]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0218 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5398 | p=0.0780 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1805 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2681 | < 0.20 |
| Log-Loss | 0.8092 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1209 | proche 0 = pas de biais systématique |
| LoA lower | -5.6706 | limite inférieure d'accord |
| LoA upper | +5.4288 | limite supérieure d'accord |
| LoA width | ±5.5497 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0431 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0218 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5398 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4096 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 19.9 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 13.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.8 | 10% |

### **SCORE TOTAL : 28.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:52*
