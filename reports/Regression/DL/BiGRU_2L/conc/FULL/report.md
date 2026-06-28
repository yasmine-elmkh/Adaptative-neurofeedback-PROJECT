# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 21:33


> 🟠 **Deployment Readiness Score : 56.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4716 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2754 | Erreur quadratique moyenne |
| R² | -0.0717 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6811 | 0.500 |
| PR-AUC | 0.6543 | 0.521 |
| Sensitivity (TPR) | 0.5310 | 0.500 |
| Specificity (TNR) | 0.6635 | 0.500 |
| PPV (Precision) | 0.6316 | — |
| NPV | 0.5656 | — |
| Balanced Accuracy | 0.5972 | 0.500 |
| MCC | 0.1958 | 0.000 |
| G-Mean | 0.5935 | 0.500 |
| F1 macro | 0.5938 | 0.500 |
| LR+ | 1.578 | >10 = très utile |
| LR− | 0.707 | <0.1 = très utile |
| Cohen κ | 0.1931 | 0.000 |
| Brier Score | 0.3127 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6806 | [0.6059, 0.7523]  ✅ |
| F1 macro | 0.5917 | [0.5224, 0.6633]  ✅ |
| Sensitivity | 0.5290 | [0.4326, 0.6239]  — |
| Specificity | 0.6636 | [0.5719, 0.7500]  — |
| MCC | 0.1939 | [0.0577, 0.3325]  — |
| R² | -0.0799 | [-0.2951, 0.1062]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0717 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6811 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2291 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3127 | < 0.20 |
| Log-Loss | 1.1689 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0978 | proche 0 = pas de biais systématique |
| LoA lower | -7.1602 | limite inférieure d'accord |
| LoA upper | +4.9647 | limite supérieure d'accord |
| LoA width | ±6.0624 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0306 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0717 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6811 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4716 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 90.5 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.8 | 10% |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 21:33*
