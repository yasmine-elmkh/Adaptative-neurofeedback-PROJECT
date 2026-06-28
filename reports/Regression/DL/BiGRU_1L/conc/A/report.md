# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 15:35


> 🟠 **Deployment Readiness Score : 58.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1859 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7834 | Erreur quadratique moyenne |
| R² | 0.2260 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6921 | 0.500 |
| PR-AUC | 0.6640 | 0.521 |
| Sensitivity (TPR) | 0.5664 | 0.500 |
| Specificity (TNR) | 0.6731 | 0.500 |
| PPV (Precision) | 0.6531 | — |
| NPV | 0.5882 | — |
| Balanced Accuracy | 0.6197 | 0.500 |
| MCC | 0.2404 | 0.000 |
| G-Mean | 0.6174 | 0.500 |
| F1 macro | 0.6172 | 0.500 |
| LR+ | 1.732 | >10 = très utile |
| LR− | 0.644 | <0.1 = très utile |
| Cohen κ | 0.2381 | 0.000 |
| Brier Score | 0.2663 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6910 | [0.6177, 0.7586]  ✅ |
| F1 macro | 0.6159 | [0.5525, 0.6818]  ✅ |
| Sensitivity | 0.5664 | [0.4752, 0.6579]  — |
| Specificity | 0.6723 | [0.5796, 0.7670]  — |
| MCC | 0.2396 | [0.1106, 0.3686]  — |
| R² | 0.2196 | [0.0835, 0.3420]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2260 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6921 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1913 | < 0.05 |
| MCE | 0.5552 | < 0.10 |
| Brier Score | 0.2663 | < 0.20 |
| Log-Loss | 0.8349 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4568 | proche 0 = pas de biais systématique |
| LoA lower | -5.8508 | limite inférieure d'accord |
| LoA upper | +4.9373 | limite supérieure d'accord |
| LoA width | ±5.3940 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1571 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2260 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6921 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1859 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 96.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 5.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 39.4 | 10% |

### **SCORE TOTAL : 58.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:35*
