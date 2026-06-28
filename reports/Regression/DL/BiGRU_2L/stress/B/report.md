# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `B`  |  **Date :** 2026-06-14 00:01


> 🔴 **Deployment Readiness Score : 27.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3773 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8103 | Erreur quadratique moyenne |
| R² | -0.0071 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5471 | 0.500 |
| PR-AUC | 0.3984 | 0.366 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 1.0000 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.6343 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0000 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.3881 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | 0.0000 | 0.000 |
| Brier Score | 0.2899 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5451 | [0.4896, 0.5932]  — |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.0084 | [-0.0620, 0.0405]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0071 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5471 | p=0.0460 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2372 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2899 | < 0.20 |
| Log-Loss | 0.8881 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5877 | proche 0 = pas de biais systématique |
| LoA lower | -5.9803 | limite inférieure d'accord |
| LoA upper | +4.8050 | limite supérieure d'accord |
| LoA width | ±5.3927 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0074 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0071 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5471 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3773 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 23.5 | 25% |
| Significativité (p-value) | 2.1 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 64.3 | 10% |

### **SCORE TOTAL : 27.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 00:01*
