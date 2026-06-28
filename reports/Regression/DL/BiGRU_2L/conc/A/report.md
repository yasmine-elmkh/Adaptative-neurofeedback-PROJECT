# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 19:38


> 🟡 **Deployment Readiness Score : 64.2/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3030 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0239 | Erreur quadratique moyenne |
| R² | 0.0865 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6964 | 0.500 |
| PR-AUC | 0.6730 | 0.521 |
| Sensitivity (TPR) | 0.6460 | 0.500 |
| Specificity (TNR) | 0.6058 | 0.500 |
| PPV (Precision) | 0.6404 | — |
| NPV | 0.6117 | — |
| Balanced Accuracy | 0.6259 | 0.500 |
| MCC | 0.2519 | 0.000 |
| G-Mean | 0.6256 | 0.500 |
| F1 macro | 0.6259 | 0.500 |
| LR+ | 1.639 | >10 = très utile |
| LR− | 0.584 | <0.1 = très utile |
| Cohen κ | 0.2519 | 0.000 |
| Brier Score | 0.2559 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6970 | [0.6261, 0.7597]  ✅ |
| F1 macro | 0.6265 | [0.5660, 0.6893]  ✅ |
| Sensitivity | 0.6481 | [0.5654, 0.7360]  — |
| Specificity | 0.6068 | [0.5150, 0.7087]  — |
| MCC | 0.2551 | [0.1337, 0.3821]  — |
| R² | 0.0837 | [-0.1103, 0.2500]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0865 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6964 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1479 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2559 | < 0.20 |
| Log-Loss | 0.9630 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7562 | proche 0 = pas de biais systématique |
| LoA lower | -6.5079 | limite inférieure d'accord |
| LoA upper | +4.9956 | limite supérieure d'accord |
| LoA width | ±5.7517 | < ±2 pts : excellent |
| % dans LoA | 93.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0752 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0865 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6964 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3030 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 98.2 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 34.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 44.3 | 10% |

### **SCORE TOTAL : 64.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 19:38*
