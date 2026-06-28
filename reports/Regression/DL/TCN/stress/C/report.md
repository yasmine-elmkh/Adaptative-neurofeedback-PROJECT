# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `TCN`  |  **Exp :** `C`  |  **Date :** 2026-06-14 03:35


> 🔴 **Deployment Readiness Score : 22.5/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4285 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8669 | Erreur quadratique moyenne |
| R² | -0.0480 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5091 | 0.500 |
| PR-AUC | 0.3553 | 0.366 |
| Sensitivity (TPR) | 0.0127 | 0.500 |
| Specificity (TNR) | 0.9562 | 0.500 |
| PPV (Precision) | 0.1429 | — |
| NPV | 0.6268 | — |
| Balanced Accuracy | 0.4844 | 0.500 |
| MCC | -0.0847 | 0.000 |
| G-Mean | 0.1100 | 0.500 |
| F1 macro | 0.3902 | 0.500 |
| LR+ | 0.289 | >10 = très utile |
| LR− | 1.033 | <0.1 = très utile |
| Cohen κ | -0.0386 | 0.000 |
| Brier Score | 0.2962 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5076 | [0.4501, 0.5541]  — |
| F1 macro | 0.3909 | [0.3671, 0.4190]  — |
| Sensitivity | 0.0131 | [0.0000, 0.0340]  — |
| Specificity | 0.9563 | [0.9328, 0.9775]  — |
| MCC | -0.0828 | [-0.1423, -0.0000]  — |
| R² | -0.0496 | [-0.1088, 0.0040]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0480 | p=0.0240 | ✅ p<0.05 |
| AUC ROC | 0.5091 | p=0.3760 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2377 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2962 | < 0.20 |
| Log-Loss | 0.9145 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4826 | proche 0 = pas de biais systématique |
| LoA lower | -6.0279 | limite inférieure d'accord |
| LoA upper | +5.0627 | limite supérieure d'accord |
| LoA width | ±5.5453 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0061 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0480 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5091 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4285 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 4.5 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 64.0 | 10% |

### **SCORE TOTAL : 22.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 03:35*
