# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 17:45


> 🔴 **Deployment Readiness Score : 36.3/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3811 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8083 | Erreur quadratique moyenne |
| R² | -0.0056 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5678 | 0.500 |
| PR-AUC | 0.4005 | 0.366 |
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
| Brier Score | 0.2759 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5659 | [0.5160, 0.6164]  ✅ |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.0071 | [-0.0522, 0.0349]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0056 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5678 | p=0.0100 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2134 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2759 | < 0.20 |
| Log-Loss | 0.8258 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4275 | proche 0 = pas de biais systématique |
| LoA lower | -5.8739 | limite inférieure d'accord |
| LoA upper | +5.0190 | limite supérieure d'accord |
| LoA width | ±5.4464 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0092 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0056 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5678 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3811 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 33.9 | 25% |
| Significativité (p-value) | 41.1 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 66.4 | 10% |

### **SCORE TOTAL : 36.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 17:45*
