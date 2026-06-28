# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 04:37


> 🟠 **Deployment Readiness Score : 56.1/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2740 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8438 | Erreur quadratique moyenne |
| R² | 0.1921 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6740 | 0.500 |
| PR-AUC | 0.6260 | 0.521 |
| Sensitivity (TPR) | 0.5310 | 0.500 |
| Specificity (TNR) | 0.6827 | 0.500 |
| PPV (Precision) | 0.6452 | — |
| NPV | 0.5726 | — |
| Balanced Accuracy | 0.6068 | 0.500 |
| MCC | 0.2157 | 0.000 |
| G-Mean | 0.6021 | 0.500 |
| F1 macro | 0.6027 | 0.500 |
| LR+ | 1.673 | >10 = très utile |
| LR− | 0.687 | <0.1 = très utile |
| Cohen κ | 0.2120 | 0.000 |
| Brier Score | 0.2659 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6740 | [0.5908, 0.7406]  ✅ |
| F1 macro | 0.6012 | [0.5320, 0.6587]  ✅ |
| Sensitivity | 0.5299 | [0.4325, 0.6235]  — |
| Specificity | 0.6831 | [0.5932, 0.7656]  — |
| MCC | 0.2150 | [0.0767, 0.3369]  — |
| R² | 0.1872 | [0.0662, 0.2933]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1921 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6740 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1900 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2659 | < 0.20 |
| Log-Loss | 0.8146 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7428 | proche 0 = pas de biais systématique |
| LoA lower | -6.1356 | limite inférieure d'accord |
| LoA upper | +4.6500 | limite supérieure d'accord |
| LoA width | ±5.3928 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0680 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1921 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6740 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2740 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 87.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 6.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 33.4 | 10% |

### **SCORE TOTAL : 56.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 04:37*
