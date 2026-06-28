# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `TCN`  |  **Exp :** `B`  |  **Date :** 2026-06-14 02:40


> 🔴 **Deployment Readiness Score : 30.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4419 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8840 | Erreur quadratique moyenne |
| R² | -0.0606 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5559 | 0.500 |
| PR-AUC | 0.3800 | 0.366 |
| Sensitivity (TPR) | 0.0696 | 0.500 |
| Specificity (TNR) | 0.9015 | 0.500 |
| PPV (Precision) | 0.2895 | — |
| NPV | 0.6269 | — |
| Balanced Accuracy | 0.4855 | 0.500 |
| MCC | -0.0492 | 0.000 |
| G-Mean | 0.2505 | 0.500 |
| F1 macro | 0.4259 | 0.500 |
| LR+ | 0.707 | >10 = très utile |
| LR− | 1.032 | <0.1 = très utile |
| Cohen κ | -0.0345 | 0.000 |
| Brier Score | 0.2986 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5537 | [0.4987, 0.6077]  — |
| F1 macro | 0.4254 | [0.3902, 0.4696]  — |
| Sensitivity | 0.0691 | [0.0350, 0.1089]  — |
| Specificity | 0.9011 | [0.8624, 0.9375]  — |
| MCC | -0.0500 | [-0.1323, 0.0414]  — |
| R² | -0.0644 | [-0.1355, 0.0005]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0606 | p=0.0180 | ✅ p<0.05 |
| AUC ROC | 0.5559 | p=0.0260 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2695 | < 0.05 |
| MCE | 0.9469 | < 0.10 |
| Brier Score | 0.2986 | < 0.20 |
| Log-Loss | 0.9173 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4488 | proche 0 = pas de biais systématique |
| LoA lower | -6.0391 | limite inférieure d'accord |
| LoA upper | +5.1415 | limite supérieure d'accord |
| LoA width | ±5.5903 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0105 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0606 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5559 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4419 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 27.9 | 25% |
| Significativité (p-value) | 16.7 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.6 | 10% |

### **SCORE TOTAL : 30.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 02:40*
