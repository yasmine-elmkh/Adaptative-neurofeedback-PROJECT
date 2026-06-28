# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-14 04:19


> 🔴 **Deployment Readiness Score : 32.9/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4072 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7787 | Erreur quadratique moyenne |
| R² | 0.0154 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5407 | 0.500 |
| PR-AUC | 0.3710 | 0.366 |
| Sensitivity (TPR) | 0.0253 | 0.500 |
| Specificity (TNR) | 0.9380 | 0.500 |
| PPV (Precision) | 0.1905 | — |
| NPV | 0.6253 | — |
| Balanced Accuracy | 0.4816 | 0.500 |
| MCC | -0.0823 | 0.000 |
| G-Mean | 0.1541 | 0.500 |
| F1 macro | 0.3975 | 0.500 |
| LR+ | 0.408 | >10 = très utile |
| LR− | 1.039 | <0.1 = très utile |
| Cohen κ | -0.0450 | 0.000 |
| Brier Score | 0.2478 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5398 | [0.4871, 0.5881]  — |
| F1 macro | 0.3973 | [0.3718, 0.4262]  — |
| Sensitivity | 0.0251 | [0.0060, 0.0525]  — |
| Specificity | 0.9372 | [0.9082, 0.9631]  — |
| MCC | -0.0839 | [-0.1536, -0.0057]  — |
| R² | 0.0123 | [-0.0217, 0.0477]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0154 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5407 | p=0.0740 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1383 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2478 | < 0.20 |
| Log-Loss | 0.6996 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1643 | proche 0 = pas de biais systématique |
| LoA lower | -5.2788 | limite inférieure d'accord |
| LoA upper | +5.6074 | limite supérieure d'accord |
| LoA width | ±5.4431 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0219 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0154 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5407 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4072 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 20.4 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 41.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 66.0 | 10% |

### **SCORE TOTAL : 32.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 04:19*
