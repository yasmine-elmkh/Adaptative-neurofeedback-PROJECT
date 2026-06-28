# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN1D`  |  **Exp :** `A`  |  **Date :** 2026-06-12 21:37


> 🔴 **Deployment Readiness Score : 39.5/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4302 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8766 | Erreur quadratique moyenne |
| R² | -0.0552 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5690 | 0.500 |
| PR-AUC | 0.3958 | 0.366 |
| Sensitivity (TPR) | 0.1962 | 0.500 |
| Specificity (TNR) | 0.8102 | 0.500 |
| PPV (Precision) | 0.3735 | — |
| NPV | 0.6361 | — |
| Balanced Accuracy | 0.5032 | 0.500 |
| MCC | 0.0079 | 0.000 |
| G-Mean | 0.3987 | 0.500 |
| F1 macro | 0.4850 | 0.500 |
| LR+ | 1.034 | >10 = très utile |
| LR− | 0.992 | <0.1 = très utile |
| Cohen κ | 0.0071 | 0.000 |
| Brier Score | 0.2943 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5669 | [0.5141, 0.6209]  ✅ |
| F1 macro | 0.4834 | [0.4356, 0.5284]  — |
| Sensitivity | 0.1955 | [0.1353, 0.2508]  — |
| Specificity | 0.8084 | [0.7629, 0.8511]  — |
| MCC | 0.0048 | [-0.0928, 0.0991]  — |
| R² | -0.0602 | [-0.1360, 0.0160]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0552 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5690 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2379 | < 0.05 |
| MCE | 0.6426 | < 0.10 |
| Brier Score | 0.2943 | < 0.20 |
| Log-Loss | 0.9122 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1822 | proche 0 = pas de biais systématique |
| LoA lower | -5.8156 | limite inférieure d'accord |
| LoA upper | +5.4512 | limite supérieure d'accord |
| LoA width | ±5.6334 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0548 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0552 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5690 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4302 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 34.5 | 25% |
| Significativité (p-value) | 64.6 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 62.1 | 10% |

### **SCORE TOTAL : 39.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 21:37*
