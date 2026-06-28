# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-13 14:25


> 🟠 **Deployment Readiness Score : 49.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3578 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7627 | Erreur quadratique moyenne |
| R² | 0.0268 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5873 | 0.500 |
| PR-AUC | 0.4148 | 0.366 |
| Sensitivity (TPR) | 0.0380 | 0.500 |
| Specificity (TNR) | 0.9380 | 0.500 |
| PPV (Precision) | 0.2609 | — |
| NPV | 0.6284 | — |
| Balanced Accuracy | 0.4880 | 0.500 |
| MCC | -0.0516 | 0.000 |
| G-Mean | 0.1887 | 0.500 |
| F1 macro | 0.4094 | 0.500 |
| LR+ | 0.612 | >10 = très utile |
| LR− | 1.026 | <0.1 = très utile |
| Cohen κ | -0.0294 | 0.000 |
| Brier Score | 0.2573 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5859 | [0.5317, 0.6403]  ✅ |
| F1 macro | 0.4089 | [0.3796, 0.4422]  — |
| Sensitivity | 0.0374 | [0.0128, 0.0669]  — |
| Specificity | 0.9375 | [0.9084, 0.9630]  — |
| MCC | -0.0534 | [-0.1295, 0.0333]  — |
| R² | 0.0242 | [-0.0177, 0.0682]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0268 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5873 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1737 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2573 | < 0.20 |
| Log-Loss | 0.7469 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1501 | proche 0 = pas de biais systématique |
| LoA lower | -5.5632 | limite inférieure d'accord |
| LoA upper | +5.2630 | limite supérieure d'accord |
| LoA width | ±5.4131 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0403 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0268 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5873 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3578 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 43.6 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 17.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.9 | 10% |

### **SCORE TOTAL : 49.6/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 14:25*
