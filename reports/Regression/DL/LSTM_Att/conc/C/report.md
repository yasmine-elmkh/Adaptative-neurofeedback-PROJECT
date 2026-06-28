# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-14 10:26


> 🟠 **Deployment Readiness Score : 58.3/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3040 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9485 | Erreur quadratique moyenne |
| R² | 0.1315 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6854 | 0.500 |
| PR-AUC | 0.6564 | 0.521 |
| Sensitivity (TPR) | 0.7611 | 0.500 |
| Specificity (TNR) | 0.5192 | 0.500 |
| PPV (Precision) | 0.6324 | — |
| NPV | 0.6667 | — |
| Balanced Accuracy | 0.6401 | 0.500 |
| MCC | 0.2895 | 0.000 |
| G-Mean | 0.6286 | 0.500 |
| F1 macro | 0.6373 | 0.500 |
| LR+ | 1.583 | >10 = très utile |
| LR− | 0.460 | <0.1 = très utile |
| Cohen κ | 0.2828 | 0.000 |
| Brier Score | 0.2582 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6842 | [0.6076, 0.7489]  ✅ |
| F1 macro | 0.6346 | [0.5696, 0.7008]  ✅ |
| Sensitivity | 0.7600 | [0.6808, 0.8361]  — |
| Specificity | 0.5173 | [0.4256, 0.6072]  — |
| MCC | 0.2865 | [0.1571, 0.4187]  — |
| R² | 0.1221 | [-0.0308, 0.2589]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1315 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6854 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1883 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2582 | < 0.20 |
| Log-Loss | 0.8598 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2401 | proche 0 = pas de biais systématique |
| LoA lower | -6.0132 | limite inférieure d'accord |
| LoA upper | +5.5330 | limite supérieure d'accord |
| LoA width | ±5.7731 | < ±2 pts : excellent |
| % dans LoA | 92.6% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2173 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1315 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6854 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3040 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 92.7 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 7.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 39.1 | 10% |

### **SCORE TOTAL : 58.3/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:26*
