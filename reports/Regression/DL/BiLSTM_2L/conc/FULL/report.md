# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_2L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 22:18


> 🟠 **Deployment Readiness Score : 59.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2829 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9944 | Erreur quadratique moyenne |
| R² | 0.1043 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7090 | 0.500 |
| PR-AUC | 0.6947 | 0.521 |
| Sensitivity (TPR) | 0.6991 | 0.500 |
| Specificity (TNR) | 0.6250 | 0.500 |
| PPV (Precision) | 0.6695 | — |
| NPV | 0.6566 | — |
| Balanced Accuracy | 0.6621 | 0.500 |
| MCC | 0.3251 | 0.000 |
| G-Mean | 0.6610 | 0.500 |
| F1 macro | 0.6622 | 0.500 |
| LR+ | 1.864 | >10 = très utile |
| LR− | 0.481 | <0.1 = très utile |
| Cohen κ | 0.3247 | 0.000 |
| Brier Score | 0.2602 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7088 | [0.6371, 0.7766]  ✅ |
| F1 macro | 0.6603 | [0.5970, 0.7217]  ✅ |
| Sensitivity | 0.6987 | [0.6085, 0.7887]  — |
| Specificity | 0.6237 | [0.5324, 0.7182]  — |
| MCC | 0.3236 | [0.1946, 0.4460]  — |
| R² | 0.1009 | [-0.0735, 0.2552]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1043 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7090 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1979 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2602 | < 0.20 |
| Log-Loss | 0.9779 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6771 | proche 0 = pas de biais systématique |
| LoA lower | -6.4073 | limite inférieure d'accord |
| LoA upper | +5.0532 | limite supérieure d'accord |
| LoA width | ±5.7302 | < ±2 pts : excellent |
| % dans LoA | 90.8% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0844 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1043 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7090 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2829 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 1.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 40.3 | 10% |

### **SCORE TOTAL : 59.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 22:18*
