# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN2D`  |  **Exp :** `FULL`  |  **Date :** 2026-06-12 20:31


> 🟠 **Deployment Readiness Score : 57.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2501 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7258 | Erreur quadratique moyenne |
| R² | 0.2577 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6767 | 0.500 |
| PR-AUC | 0.6358 | 0.521 |
| Sensitivity (TPR) | 0.6460 | 0.500 |
| Specificity (TNR) | 0.5865 | 0.500 |
| PPV (Precision) | 0.6293 | — |
| NPV | 0.6040 | — |
| Balanced Accuracy | 0.6163 | 0.500 |
| MCC | 0.2329 | 0.000 |
| G-Mean | 0.6156 | 0.500 |
| F1 macro | 0.6163 | 0.500 |
| LR+ | 1.562 | >10 = très utile |
| LR− | 0.604 | <0.1 = très utile |
| Cohen κ | 0.2328 | 0.000 |
| Brier Score | 0.2620 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6765 | [0.6074, 0.7420]  ✅ |
| F1 macro | 0.6166 | [0.5564, 0.6822]  ✅ |
| Sensitivity | 0.6497 | [0.5634, 0.7297]  — |
| Specificity | 0.5856 | [0.4975, 0.6766]  — |
| MCC | 0.2358 | [0.1163, 0.3680]  — |
| R² | 0.2517 | [0.1477, 0.3504]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2577 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6767 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1869 | < 0.05 |
| MCE | 0.3511 | < 0.10 |
| Brier Score | 0.2620 | < 0.20 |
| Log-Loss | 0.8007 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0115 | proche 0 = pas de biais systématique |
| LoA lower | -5.3434 | limite inférieure d'accord |
| LoA upper | +5.3665 | limite supérieure d'accord |
| LoA width | ±5.3550 | < ±2 pts : excellent |
| % dans LoA | 98.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.3499 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2577 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6767 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2501 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 88.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 8.7 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.6 | 10% |

### **SCORE TOTAL : 57.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 20:31*
