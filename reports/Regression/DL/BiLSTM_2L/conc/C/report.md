# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_2L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 20:55


> 🟠 **Deployment Readiness Score : 55.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4757 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1707 | Erreur quadratique moyenne |
| R² | -0.0043 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6751 | 0.500 |
| PR-AUC | 0.6460 | 0.521 |
| Sensitivity (TPR) | 0.4690 | 0.500 |
| Specificity (TNR) | 0.6923 | 0.500 |
| PPV (Precision) | 0.6235 | — |
| NPV | 0.5455 | — |
| Balanced Accuracy | 0.5807 | 0.500 |
| MCC | 0.1651 | 0.000 |
| G-Mean | 0.5698 | 0.500 |
| F1 macro | 0.5728 | 0.500 |
| LR+ | 1.524 | >10 = très utile |
| LR− | 0.767 | <0.1 = très utile |
| Cohen κ | 0.1596 | 0.000 |
| Brier Score | 0.3048 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6759 | [0.6016, 0.7450]  ✅ |
| F1 macro | 0.5734 | [0.5064, 0.6322]  ✅ |
| Sensitivity | 0.4703 | [0.3721, 0.5594]  — |
| Specificity | 0.6946 | [0.6085, 0.7907]  — |
| MCC | 0.1687 | [0.0434, 0.2928]  — |
| R² | -0.0084 | [-0.1881, 0.1596]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0043 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6751 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2596 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3048 | < 0.20 |
| Log-Loss | 1.1042 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0222 | proche 0 = pas de biais systématique |
| LoA lower | -6.9185 | limite inférieure d'accord |
| LoA upper | +4.8742 | limite supérieure d'accord |
| LoA width | ±5.8964 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0346 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0043 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6751 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4757 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 87.6 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.8 | 10% |

### **SCORE TOTAL : 55.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:55*
