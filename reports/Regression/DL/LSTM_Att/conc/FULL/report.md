# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 10:48


> 🟠 **Deployment Readiness Score : 59.4/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3009 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9538 | Erreur quadratique moyenne |
| R² | 0.1284 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7232 | 0.500 |
| PR-AUC | 0.6862 | 0.521 |
| Sensitivity (TPR) | 0.3451 | 0.500 |
| Specificity (TNR) | 0.8558 | 0.500 |
| PPV (Precision) | 0.7222 | — |
| NPV | 0.5460 | — |
| Balanced Accuracy | 0.6005 | 0.500 |
| MCC | 0.2321 | 0.000 |
| G-Mean | 0.5435 | 0.500 |
| F1 macro | 0.5669 | 0.500 |
| LR+ | 2.393 | >10 = très utile |
| LR− | 0.765 | <0.1 = très utile |
| Cohen κ | 0.1965 | 0.000 |
| Brier Score | 0.2847 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7218 | [0.6486, 0.7829]  ✅ |
| F1 macro | 0.5670 | [0.4980, 0.6301]  — |
| Sensitivity | 0.3466 | [0.2648, 0.4344]  — |
| Specificity | 0.8558 | [0.7935, 0.9223]  — |
| MCC | 0.2336 | [0.1066, 0.3515]  — |
| R² | 0.1226 | [-0.0268, 0.2607]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1284 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7232 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2458 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2847 | < 0.20 |
| Log-Loss | 0.9442 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0330 | proche 0 = pas de biais systématique |
| LoA lower | -6.4694 | limite inférieure d'accord |
| LoA upper | +4.4034 | limite supérieure d'accord |
| LoA width | ±5.4364 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0394 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1284 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7232 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3009 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.8 | 10% |

### **SCORE TOTAL : 59.4/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:48*
