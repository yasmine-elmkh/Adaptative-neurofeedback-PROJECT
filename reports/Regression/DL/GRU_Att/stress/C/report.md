# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-14 12:09


> 🔴 **Deployment Readiness Score : 37.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3964 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7711 | Erreur quadratique moyenne |
| R² | 0.0209 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5587 | 0.500 |
| PR-AUC | 0.4054 | 0.366 |
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
| Brier Score | 0.2490 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5570 | [0.5044, 0.6127]  ✅ |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | 0.0180 | [0.0001, 0.0339]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0209 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5587 | p=0.0200 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1430 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2490 | < 0.20 |
| Log-Loss | 0.7016 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0004 | proche 0 = pas de biais systématique |
| LoA lower | -5.4380 | limite inférieure d'accord |
| LoA upper | +5.4372 | limite supérieure d'accord |
| LoA width | ±5.4376 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0192 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0209 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5587 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3964 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 29.3 | 25% |
| Significativité (p-value) | 23.4 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 38.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 61.1 | 10% |

### **SCORE TOTAL : 37.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 12:09*
