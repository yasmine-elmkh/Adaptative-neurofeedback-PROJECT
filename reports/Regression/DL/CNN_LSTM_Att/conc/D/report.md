# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-13 13:26


> 🟠 **Deployment Readiness Score : 56.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3441 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0350 | Erreur quadratique moyenne |
| R² | 0.0798 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6789 | 0.500 |
| PR-AUC | 0.6568 | 0.521 |
| Sensitivity (TPR) | 0.5841 | 0.500 |
| Specificity (TNR) | 0.6250 | 0.500 |
| PPV (Precision) | 0.6286 | — |
| NPV | 0.5804 | — |
| Balanced Accuracy | 0.6045 | 0.500 |
| MCC | 0.2090 | 0.000 |
| G-Mean | 0.6042 | 0.500 |
| F1 macro | 0.6037 | 0.500 |
| LR+ | 1.558 | >10 = très utile |
| LR− | 0.665 | <0.1 = très utile |
| Cohen κ | 0.2084 | 0.000 |
| Brier Score | 0.2958 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6810 | [0.6075, 0.7498]  ✅ |
| F1 macro | 0.6055 | [0.5413, 0.6678]  ✅ |
| Sensitivity | 0.5878 | [0.4917, 0.6765]  — |
| Specificity | 0.6268 | [0.5354, 0.7136]  — |
| MCC | 0.2146 | [0.0862, 0.3389]  — |
| R² | 0.0766 | [-0.1144, 0.2372]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0798 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6789 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2528 | < 0.05 |
| MCE | 0.5398 | < 0.10 |
| Brier Score | 0.2958 | < 0.20 |
| Log-Loss | 1.0397 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3630 | proche 0 = pas de biais systématique |
| LoA lower | -6.2826 | limite inférieure d'accord |
| LoA upper | +5.5567 | limite supérieure d'accord |
| LoA width | ±5.9197 | < ±2 pts : excellent |
| % dans LoA | 93.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1786 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0798 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6789 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3441 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 89.4 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.5 | 10% |

### **SCORE TOTAL : 56.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:26*
