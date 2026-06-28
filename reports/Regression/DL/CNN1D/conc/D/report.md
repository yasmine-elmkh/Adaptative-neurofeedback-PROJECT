# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN1D`  |  **Exp :** `D`  |  **Date :** 2026-06-12 19:12


> 🟠 **Deployment Readiness Score : 58.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2547 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8469 | Erreur quadratique moyenne |
| R² | 0.1903 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6957 | 0.500 |
| PR-AUC | 0.6590 | 0.521 |
| Sensitivity (TPR) | 0.4425 | 0.500 |
| Specificity (TNR) | 0.7308 | 0.500 |
| PPV (Precision) | 0.6410 | — |
| NPV | 0.5468 | — |
| Balanced Accuracy | 0.5866 | 0.500 |
| MCC | 0.1804 | 0.000 |
| G-Mean | 0.5686 | 0.500 |
| F1 macro | 0.5745 | 0.500 |
| LR+ | 1.643 | >10 = très utile |
| LR− | 0.763 | <0.1 = très utile |
| Cohen κ | 0.1710 | 0.000 |
| Brier Score | 0.2894 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6968 | [0.6271, 0.7616]  ✅ |
| F1 macro | 0.5744 | [0.5050, 0.6408]  ✅ |
| Sensitivity | 0.4431 | [0.3486, 0.5403]  — |
| Specificity | 0.7321 | [0.6600, 0.8095]  — |
| MCC | 0.1823 | [0.0554, 0.3062]  — |
| R² | 0.1874 | [0.0544, 0.3117]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1903 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6957 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2628 | < 0.05 |
| MCE | 0.4068 | < 0.10 |
| Brier Score | 0.2894 | < 0.20 |
| Log-Loss | 0.9125 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6675 | proche 0 = pas de biais systématique |
| LoA lower | -6.1045 | limite inférieure d'accord |
| LoA upper | +4.7695 | limite supérieure d'accord |
| LoA width | ±5.4370 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0943 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1903 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6957 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2547 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 97.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.7 | 10% |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 19:12*
