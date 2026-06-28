# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-14 11:49


> 🔴 **Deployment Readiness Score : 27.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3863 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7751 | Erreur quadratique moyenne |
| R² | 0.0180 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5391 | 0.500 |
| PR-AUC | 0.3786 | 0.366 |
| Sensitivity (TPR) | 0.0063 | 0.500 |
| Specificity (TNR) | 0.9818 | 0.500 |
| PPV (Precision) | 0.1667 | — |
| NPV | 0.6315 | — |
| Balanced Accuracy | 0.4940 | 0.500 |
| MCC | -0.0491 | 0.000 |
| G-Mean | 0.0788 | 0.500 |
| F1 macro | 0.3904 | 0.500 |
| LR+ | 0.347 | >10 = très utile |
| LR− | 1.012 | <0.1 = très utile |
| Cohen κ | -0.0150 | 0.000 |
| Brier Score | 0.2717 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5388 | [0.4839, 0.5897]  — |
| F1 macro | 0.3906 | [0.3671, 0.4133]  — |
| Sensitivity | 0.0061 | [0.0000, 0.0200]  — |
| Specificity | 0.9822 | [0.9644, 0.9964]  — |
| MCC | -0.0474 | [-0.1078, 0.0479]  — |
| R² | 0.0165 | [-0.0252, 0.0566]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0180 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5391 | p=0.0820 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1913 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2717 | < 0.20 |
| Log-Loss | 0.7954 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2311 | proche 0 = pas de biais systématique |
| LoA lower | -5.6576 | limite inférieure d'accord |
| LoA upper | +5.1954 | limite supérieure d'accord |
| LoA width | ±5.4265 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0236 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0180 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5391 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3863 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 19.6 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 5.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 62.8 | 10% |

### **SCORE TOTAL : 27.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 11:49*
