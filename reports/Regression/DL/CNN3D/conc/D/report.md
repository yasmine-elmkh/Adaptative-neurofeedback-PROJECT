# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN3D`  |  **Exp :** `D`  |  **Date :** 2026-06-12 21:59


> 🟠 **Deployment Readiness Score : 55.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2681 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7970 | Erreur quadratique moyenne |
| R² | 0.2185 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6767 | 0.500 |
| PR-AUC | 0.6578 | 0.521 |
| Sensitivity (TPR) | 0.5398 | 0.500 |
| Specificity (TNR) | 0.6731 | 0.500 |
| PPV (Precision) | 0.6421 | — |
| NPV | 0.5738 | — |
| Balanced Accuracy | 0.6064 | 0.500 |
| MCC | 0.2144 | 0.000 |
| G-Mean | 0.6028 | 0.500 |
| F1 macro | 0.6030 | 0.500 |
| LR+ | 1.651 | >10 = très utile |
| LR− | 0.684 | <0.1 = très utile |
| Cohen κ | 0.2114 | 0.000 |
| Brier Score | 0.2938 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6770 | [0.6026, 0.7469]  ✅ |
| F1 macro | 0.6032 | [0.5344, 0.6678]  ✅ |
| Sensitivity | 0.5433 | [0.4443, 0.6376]  — |
| Specificity | 0.6718 | [0.5811, 0.7611]  — |
| MCC | 0.2165 | [0.0785, 0.3488]  — |
| R² | 0.2134 | [0.0761, 0.3491]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2185 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6767 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2517 | < 0.05 |
| MCE | 0.4317 | < 0.10 |
| Brier Score | 0.2938 | < 0.20 |
| Log-Loss | 0.9533 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3089 | proche 0 = pas de biais systématique |
| LoA lower | -5.7701 | limite inférieure d'accord |
| LoA upper | +5.1523 | limite supérieure d'accord |
| LoA width | ±5.4612 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2325 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2185 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6767 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2681 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 88.4 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.1 | 10% |

### **SCORE TOTAL : 55.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 21:59*
