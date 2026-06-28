# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 03:49


> 🟠 **Deployment Readiness Score : 59.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2434 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8775 | Erreur quadratique moyenne |
| R² | 0.1729 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6866 | 0.500 |
| PR-AUC | 0.6655 | 0.521 |
| Sensitivity (TPR) | 0.4425 | 0.500 |
| Specificity (TNR) | 0.6923 | 0.500 |
| PPV (Precision) | 0.6098 | — |
| NPV | 0.5333 | — |
| Balanced Accuracy | 0.5674 | 0.500 |
| MCC | 0.1389 | 0.000 |
| G-Mean | 0.5535 | 0.500 |
| F1 macro | 0.5577 | 0.500 |
| LR+ | 1.438 | >10 = très utile |
| LR− | 0.805 | <0.1 = très utile |
| Cohen κ | 0.1332 | 0.000 |
| Brier Score | 0.2577 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6854 | [0.6087, 0.7543]  ✅ |
| F1 macro | 0.5556 | [0.4882, 0.6203]  — |
| Sensitivity | 0.4401 | [0.3456, 0.5361]  — |
| Specificity | 0.6930 | [0.6017, 0.7803]  — |
| MCC | 0.1374 | [-0.0033, 0.2674]  — |
| R² | 0.1688 | [0.0300, 0.2890]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1729 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6866 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1715 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2577 | < 0.20 |
| Log-Loss | 0.8386 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7438 | proche 0 = pas de biais systématique |
| LoA lower | -6.2045 | limite inférieure d'accord |
| LoA upper | +4.7169 | limite supérieure d'accord |
| LoA width | ±5.4607 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0707 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1729 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6866 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2434 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 93.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 19.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.3 | 10% |

### **SCORE TOTAL : 59.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 03:49*
