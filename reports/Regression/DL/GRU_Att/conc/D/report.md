# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-14 10:24


> 🟠 **Deployment Readiness Score : 54.3/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3793 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9693 | Erreur quadratique moyenne |
| R² | 0.1192 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6641 | 0.500 |
| PR-AUC | 0.6088 | 0.521 |
| Sensitivity (TPR) | 0.2832 | 0.500 |
| Specificity (TNR) | 0.7788 | 0.500 |
| PPV (Precision) | 0.5818 | — |
| NPV | 0.5000 | — |
| Balanced Accuracy | 0.5310 | 0.500 |
| MCC | 0.0712 | 0.000 |
| G-Mean | 0.4696 | 0.500 |
| F1 macro | 0.4950 | 0.500 |
| LR+ | 1.280 | >10 = très utile |
| LR− | 0.920 | <0.1 = très utile |
| Cohen κ | 0.0607 | 0.000 |
| Brier Score | 0.3119 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6610 | [0.5857, 0.7290]  ✅ |
| F1 macro | 0.4920 | [0.4248, 0.5619]  — |
| Sensitivity | 0.2813 | [0.1954, 0.3661]  — |
| Specificity | 0.7768 | [0.7023, 0.8571]  — |
| MCC | 0.0667 | [-0.0661, 0.1987]  — |
| R² | 0.1104 | [-0.0172, 0.2361]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1192 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6641 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2667 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3119 | < 0.20 |
| Log-Loss | 0.9689 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0204 | proche 0 = pas de biais systématique |
| LoA lower | -6.4985 | limite inférieure d'accord |
| LoA upper | +4.4577 | limite supérieure d'accord |
| LoA width | ±5.4781 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0370 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1192 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6641 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3793 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 82.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.8 | 10% |

### **SCORE TOTAL : 54.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:24*
