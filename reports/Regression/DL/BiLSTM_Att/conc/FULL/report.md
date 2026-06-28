# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 21:35


> 🟠 **Deployment Readiness Score : 55.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3966 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1138 | Erreur quadratique moyenne |
| R² | 0.0314 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6762 | 0.500 |
| PR-AUC | 0.6537 | 0.521 |
| Sensitivity (TPR) | 0.5133 | 0.500 |
| Specificity (TNR) | 0.6923 | 0.500 |
| PPV (Precision) | 0.6444 | — |
| NPV | 0.5669 | — |
| Balanced Accuracy | 0.6028 | 0.500 |
| MCC | 0.2085 | 0.000 |
| G-Mean | 0.5961 | 0.500 |
| F1 macro | 0.5974 | 0.500 |
| LR+ | 1.668 | >10 = très utile |
| LR− | 0.703 | <0.1 = très utile |
| Cohen κ | 0.2038 | 0.000 |
| Brier Score | 0.2977 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6746 | [0.5982, 0.7454]  ✅ |
| F1 macro | 0.5956 | [0.5292, 0.6622]  ✅ |
| Sensitivity | 0.5146 | [0.4192, 0.6118]  — |
| Specificity | 0.6890 | [0.6139, 0.7719]  — |
| MCC | 0.2063 | [0.0774, 0.3398]  — |
| R² | 0.0239 | [-0.1616, 0.1876]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0314 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6762 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2410 | < 0.05 |
| MCE | 0.5319 | < 0.10 |
| Brier Score | 0.2977 | < 0.20 |
| Log-Loss | 1.1043 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8403 | proche 0 = pas de biais systématique |
| LoA lower | -6.7304 | limite inférieure d'accord |
| LoA upper | +5.0498 | limite supérieure d'accord |
| LoA width | ±5.8901 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0555 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0314 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6762 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3966 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 88.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.2 | 10% |

### **SCORE TOTAL : 55.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 21:35*
