# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 20:08


> 🟠 **Deployment Readiness Score : 58.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3855 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0669 | Erreur quadratique moyenne |
| R² | 0.0604 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6977 | 0.500 |
| PR-AUC | 0.6727 | 0.521 |
| Sensitivity (TPR) | 0.3009 | 0.500 |
| Specificity (TNR) | 0.8269 | 0.500 |
| PPV (Precision) | 0.6538 | — |
| NPV | 0.5212 | — |
| Balanced Accuracy | 0.5639 | 0.500 |
| MCC | 0.1496 | 0.000 |
| G-Mean | 0.4988 | 0.500 |
| F1 macro | 0.5258 | 0.500 |
| LR+ | 1.738 | >10 = très utile |
| LR− | 0.845 | <0.1 = très utile |
| Cohen κ | 0.1249 | 0.000 |
| Brier Score | 0.3103 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6976 | [0.6267, 0.7645]  ✅ |
| F1 macro | 0.5254 | [0.4558, 0.5881]  — |
| Sensitivity | 0.3016 | [0.2196, 0.3897]  — |
| Specificity | 0.8269 | [0.7475, 0.8961]  — |
| MCC | 0.1501 | [0.0181, 0.2685]  — |
| R² | 0.0536 | [-0.1243, 0.2134]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0604 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6977 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2751 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3103 | < 0.20 |
| Log-Loss | 1.0870 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.1797 | proche 0 = pas de biais systématique |
| LoA lower | -6.7411 | limite inférieure d'accord |
| LoA upper | +4.3816 | limite supérieure d'accord |
| LoA width | ±5.5614 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0310 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0604 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6977 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3855 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 98.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 41.5 | 10% |

### **SCORE TOTAL : 58.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:08*
