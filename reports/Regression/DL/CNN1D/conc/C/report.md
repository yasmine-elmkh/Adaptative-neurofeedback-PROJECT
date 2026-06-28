# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN1D`  |  **Exp :** `C`  |  **Date :** 2026-06-12 18:49


> 🟠 **Deployment Readiness Score : 57.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3641 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0233 | Erreur quadratique moyenne |
| R² | 0.0869 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6884 | 0.500 |
| PR-AUC | 0.6533 | 0.521 |
| Sensitivity (TPR) | 0.3717 | 0.500 |
| Specificity (TNR) | 0.7788 | 0.500 |
| PPV (Precision) | 0.6462 | — |
| NPV | 0.5329 | — |
| Balanced Accuracy | 0.5753 | 0.500 |
| MCC | 0.1642 | 0.000 |
| G-Mean | 0.5380 | 0.500 |
| F1 macro | 0.5524 | 0.500 |
| LR+ | 1.681 | >10 = très utile |
| LR− | 0.807 | <0.1 = très utile |
| Cohen κ | 0.1478 | 0.000 |
| Brier Score | 0.3276 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6869 | [0.6164, 0.7510]  ✅ |
| F1 macro | 0.5503 | [0.4839, 0.6189]  — |
| Sensitivity | 0.3715 | [0.2843, 0.4724]  — |
| Specificity | 0.7766 | [0.7026, 0.8534]  — |
| MCC | 0.1613 | [0.0343, 0.2879]  — |
| R² | 0.0813 | [-0.0688, 0.2224]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0869 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6884 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3193 | < 0.05 |
| MCE | 0.4585 | < 0.10 |
| Brier Score | 0.3276 | < 0.20 |
| Log-Loss | 1.0725 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8883 | proche 0 = pas de biais systématique |
| LoA lower | -6.5656 | limite inférieure d'accord |
| LoA upper | +4.7890 | limite supérieure d'accord |
| LoA width | ±5.6773 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0540 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0869 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6884 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3641 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 94.2 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.6 | 10% |

### **SCORE TOTAL : 57.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 18:49*
