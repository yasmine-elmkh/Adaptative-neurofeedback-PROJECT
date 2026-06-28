# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN2D`  |  **Exp :** `C`  |  **Date :** 2026-06-12 19:07


> 🟠 **Deployment Readiness Score : 52.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2804 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7634 | Erreur quadratique moyenne |
| R² | 0.2371 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6537 | 0.500 |
| PR-AUC | 0.6378 | 0.521 |
| Sensitivity (TPR) | 0.2743 | 0.500 |
| Specificity (TNR) | 0.8365 | 0.500 |
| PPV (Precision) | 0.6458 | — |
| NPV | 0.5148 | — |
| Balanced Accuracy | 0.5554 | 0.500 |
| MCC | 0.1335 | 0.000 |
| G-Mean | 0.4791 | 0.500 |
| F1 macro | 0.5112 | 0.500 |
| LR+ | 1.678 | >10 = très utile |
| LR− | 0.867 | <0.1 = très utile |
| Cohen κ | 0.1082 | 0.000 |
| Brier Score | 0.2921 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6533 | [0.5769, 0.7232]  ✅ |
| F1 macro | 0.5104 | [0.4421, 0.5737]  — |
| Sensitivity | 0.2745 | [0.1922, 0.3539]  — |
| Specificity | 0.8363 | [0.7659, 0.9079]  — |
| MCC | 0.1332 | [-0.0069, 0.2577]  — |
| R² | 0.2318 | [0.1277, 0.3309]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2371 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6537 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2445 | < 0.05 |
| MCE | 0.5096 | < 0.10 |
| Brier Score | 0.2921 | < 0.20 |
| Log-Loss | 0.8327 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6744 | proche 0 = pas de biais systématique |
| LoA lower | -5.9391 | limite inférieure d'accord |
| LoA upper | +4.5903 | limite supérieure d'accord |
| LoA width | ±5.2647 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0859 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2371 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6537 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2804 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 76.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.8 | 10% |

### **SCORE TOTAL : 52.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 19:07*
