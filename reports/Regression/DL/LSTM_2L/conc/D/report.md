# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 05:44


> 🟠 **Deployment Readiness Score : 56.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2414 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8748 | Erreur quadratique moyenne |
| R² | 0.1744 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6746 | 0.500 |
| PR-AUC | 0.6543 | 0.521 |
| Sensitivity (TPR) | 0.7080 | 0.500 |
| Specificity (TNR) | 0.5481 | 0.500 |
| PPV (Precision) | 0.6299 | — |
| NPV | 0.6333 | — |
| Balanced Accuracy | 0.6280 | 0.500 |
| MCC | 0.2596 | 0.000 |
| G-Mean | 0.6229 | 0.500 |
| F1 macro | 0.6271 | 0.500 |
| LR+ | 1.567 | >10 = très utile |
| LR− | 0.533 | <0.1 = très utile |
| Cohen κ | 0.2574 | 0.000 |
| Brier Score | 0.2511 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6751 | [0.5939, 0.7540]  ✅ |
| F1 macro | 0.6265 | [0.5569, 0.6883]  ✅ |
| Sensitivity | 0.7086 | [0.6190, 0.7895]  — |
| Specificity | 0.5485 | [0.4519, 0.6451]  — |
| MCC | 0.2607 | [0.1229, 0.3822]  — |
| R² | 0.1716 | [0.0150, 0.3070]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1744 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6746 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1769 | < 0.05 |
| MCE | 0.3920 | < 0.10 |
| Brier Score | 0.2511 | < 0.20 |
| Log-Loss | 0.8394 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3251 | proche 0 = pas de biais systématique |
| LoA lower | -5.9364 | limite inférieure d'accord |
| LoA upper | +5.2863 | limite supérieure d'accord |
| LoA width | ±5.6114 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2006 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1744 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6746 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2414 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 87.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 15.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 26.7 | 10% |

### **SCORE TOTAL : 56.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 05:44*
