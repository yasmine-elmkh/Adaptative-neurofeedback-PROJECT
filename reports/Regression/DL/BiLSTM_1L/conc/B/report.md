# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_1L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 19:49


> 🟡 **Deployment Readiness Score : 60.2/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2139 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8214 | Erreur quadratique moyenne |
| R² | 0.2048 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6958 | 0.500 |
| PR-AUC | 0.6747 | 0.521 |
| Sensitivity (TPR) | 0.5398 | 0.500 |
| Specificity (TNR) | 0.6346 | 0.500 |
| PPV (Precision) | 0.6162 | — |
| NPV | 0.5593 | — |
| Balanced Accuracy | 0.5872 | 0.500 |
| MCC | 0.1750 | 0.000 |
| G-Mean | 0.5853 | 0.500 |
| F1 macro | 0.5850 | 0.500 |
| LR+ | 1.477 | >10 = très utile |
| LR− | 0.725 | <0.1 = très utile |
| Cohen κ | 0.1735 | 0.000 |
| Brier Score | 0.2390 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6957 | [0.6113, 0.7663]  ✅ |
| F1 macro | 0.5831 | [0.5157, 0.6525]  ✅ |
| Sensitivity | 0.5385 | [0.4536, 0.6331]  — |
| Specificity | 0.6343 | [0.5314, 0.7248]  — |
| MCC | 0.1733 | [0.0419, 0.3099]  — |
| R² | 0.2010 | [0.0549, 0.3217]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2048 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6958 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1728 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2390 | < 0.20 |
| Log-Loss | 0.7736 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6750 | proche 0 = pas de biais systématique |
| LoA lower | -6.0567 | limite inférieure d'accord |
| LoA upper | +4.7066 | limite supérieure d'accord |
| LoA width | ±5.3817 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0884 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2048 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6958 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2139 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 97.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 18.2 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 30.0 | 10% |

### **SCORE TOTAL : 60.2/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 19:49*
