# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 15:45


> 🟡 **Deployment Readiness Score : 65.7/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1985 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7361 | Erreur quadratique moyenne |
| R² | 0.2521 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7210 | 0.500 |
| PR-AUC | 0.7179 | 0.521 |
| Sensitivity (TPR) | 0.5310 | 0.500 |
| Specificity (TNR) | 0.7019 | 0.500 |
| PPV (Precision) | 0.6593 | — |
| NPV | 0.5794 | — |
| Balanced Accuracy | 0.6164 | 0.500 |
| MCC | 0.2358 | 0.000 |
| G-Mean | 0.6105 | 0.500 |
| F1 macro | 0.6115 | 0.500 |
| LR+ | 1.781 | >10 = très utile |
| LR− | 0.668 | <0.1 = très utile |
| Cohen κ | 0.2310 | 0.000 |
| Brier Score | 0.2370 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7217 | [0.6478, 0.7848]  ✅ |
| F1 macro | 0.6111 | [0.5478, 0.6707]  ✅ |
| Sensitivity | 0.5315 | [0.4450, 0.6119]  — |
| Specificity | 0.7024 | [0.6238, 0.7882]  — |
| MCC | 0.2368 | [0.1033, 0.3548]  — |
| R² | 0.2481 | [0.1374, 0.3467]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2521 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7210 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1351 | < 0.05 |
| MCE | 0.5093 | < 0.10 |
| Brier Score | 0.2370 | < 0.20 |
| Log-Loss | 0.7172 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5147 | proche 0 = pas de biais systématique |
| LoA lower | -5.7939 | limite inférieure d'accord |
| LoA upper | +4.7645 | limite supérieure d'accord |
| LoA width | ±5.2792 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1282 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2521 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7210 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1985 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 43.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 42.0 | 10% |

### **SCORE TOTAL : 65.7/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:45*
