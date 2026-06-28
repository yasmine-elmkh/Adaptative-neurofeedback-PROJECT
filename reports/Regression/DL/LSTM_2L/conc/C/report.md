# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 05:06


> 🟡 **Deployment Readiness Score : 61.0/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3129 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9280 | Erreur quadratique moyenne |
| R² | 0.1435 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7109 | 0.500 |
| PR-AUC | 0.6658 | 0.521 |
| Sensitivity (TPR) | 0.6018 | 0.500 |
| Specificity (TNR) | 0.6923 | 0.500 |
| PPV (Precision) | 0.6800 | — |
| NPV | 0.6154 | — |
| Balanced Accuracy | 0.6470 | 0.500 |
| MCC | 0.2947 | 0.000 |
| G-Mean | 0.6455 | 0.500 |
| F1 macro | 0.6450 | 0.500 |
| LR+ | 1.956 | >10 = très utile |
| LR− | 0.575 | <0.1 = très utile |
| Cohen κ | 0.2926 | 0.000 |
| Brier Score | 0.2625 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7107 | [0.6353, 0.7838]  ✅ |
| F1 macro | 0.6440 | [0.5750, 0.7095]  ✅ |
| Sensitivity | 0.6035 | [0.5110, 0.6986]  — |
| Specificity | 0.6902 | [0.5903, 0.7794]  — |
| MCC | 0.2943 | [0.1590, 0.4261]  — |
| R² | 0.1399 | [-0.0134, 0.2799]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1435 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7109 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1746 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2625 | < 0.20 |
| Log-Loss | 0.9047 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7962 | proche 0 = pas de biais systématique |
| LoA lower | -6.3317 | limite inférieure d'accord |
| LoA upper | +4.7392 | limite supérieure d'accord |
| LoA width | ±5.5355 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0650 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1435 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7109 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3129 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 16.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 34.3 | 10% |

### **SCORE TOTAL : 61.0/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 05:06*
