# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-13 13:03


> 🟠 **Deployment Readiness Score : 58.4/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2439 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8987 | Erreur quadratique moyenne |
| R² | 0.1606 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6822 | 0.500 |
| PR-AUC | 0.6591 | 0.521 |
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
| Brier Score | 0.2611 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6807 | [0.6079, 0.7512]  ✅ |
| F1 macro | 0.6251 | [0.5576, 0.6894]  ✅ |
| Sensitivity | 0.7076 | [0.6168, 0.7887]  — |
| Specificity | 0.5466 | [0.4559, 0.6476]  — |
| MCC | 0.2578 | [0.1223, 0.3859]  — |
| R² | 0.1540 | [-0.0084, 0.2962]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1606 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6822 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1812 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2611 | < 0.20 |
| Log-Loss | 0.8713 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4169 | proche 0 = pas de biais systématique |
| LoA lower | -6.0523 | limite inférieure d'accord |
| LoA upper | +5.2185 | limite supérieure d'accord |
| LoA width | ±5.6354 | < ±2 pts : excellent |
| % dans LoA | 92.6% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1555 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1606 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6822 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2439 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 91.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 12.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.8 | 10% |

### **SCORE TOTAL : 58.4/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:03*
