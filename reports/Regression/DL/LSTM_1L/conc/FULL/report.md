# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 05:15


> 🟠 **Deployment Readiness Score : 60.0/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1403 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8092 | Erreur quadratique moyenne |
| R² | 0.2116 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7001 | 0.500 |
| PR-AUC | 0.6710 | 0.521 |
| Sensitivity (TPR) | 0.6814 | 0.500 |
| Specificity (TNR) | 0.5962 | 0.500 |
| PPV (Precision) | 0.6471 | — |
| NPV | 0.6327 | — |
| Balanced Accuracy | 0.6388 | 0.500 |
| MCC | 0.2786 | 0.000 |
| G-Mean | 0.6374 | 0.500 |
| F1 macro | 0.6388 | 0.500 |
| LR+ | 1.687 | >10 = très utile |
| LR− | 0.534 | <0.1 = très utile |
| Cohen κ | 0.2782 | 0.000 |
| Brier Score | 0.2430 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6993 | [0.6230, 0.7692]  ✅ |
| F1 macro | 0.6381 | [0.5754, 0.7006]  ✅ |
| Sensitivity | 0.6829 | [0.6000, 0.7681]  — |
| Specificity | 0.5954 | [0.4951, 0.6888]  — |
| MCC | 0.2794 | [0.1519, 0.4017]  — |
| R² | 0.2079 | [0.0614, 0.3448]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2116 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7001 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1862 | < 0.05 |
| MCE | 0.4696 | < 0.10 |
| Brier Score | 0.2430 | < 0.20 |
| Log-Loss | 0.7987 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3650 | proche 0 = pas de biais systématique |
| LoA lower | -5.8370 | limite inférieure d'accord |
| LoA upper | +5.1071 | limite supérieure d'accord |
| LoA width | ±5.4720 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1985 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2116 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7001 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1403 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 9.2 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.8 | 10% |

### **SCORE TOTAL : 60.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 05:15*
