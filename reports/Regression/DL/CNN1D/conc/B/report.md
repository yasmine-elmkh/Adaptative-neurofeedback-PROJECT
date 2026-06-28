# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN1D`  |  **Exp :** `B`  |  **Date :** 2026-06-12 18:10


> 🟠 **Deployment Readiness Score : 55.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5304 | Erreur absolue moyenne (0-10) |
| RMSE | 3.3024 | Erreur quadratique moyenne |
| R² | -0.0895 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6732 | 0.500 |
| PR-AUC | 0.6304 | 0.521 |
| Sensitivity (TPR) | 0.3805 | 0.500 |
| Specificity (TNR) | 0.7788 | 0.500 |
| PPV (Precision) | 0.6515 | — |
| NPV | 0.5364 | — |
| Balanced Accuracy | 0.5797 | 0.500 |
| MCC | 0.1731 | 0.000 |
| G-Mean | 0.5444 | 0.500 |
| F1 macro | 0.5579 | 0.500 |
| LR+ | 1.721 | >10 = très utile |
| LR− | 0.795 | <0.1 = très utile |
| Cohen κ | 0.1566 | 0.000 |
| Brier Score | 0.3319 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6727 | [0.5984, 0.7405]  ✅ |
| F1 macro | 0.5578 | [0.4891, 0.6272]  — |
| Sensitivity | 0.3821 | [0.2896, 0.4759]  — |
| Specificity | 0.7786 | [0.6979, 0.8496]  — |
| MCC | 0.1743 | [0.0522, 0.3002]  — |
| R² | -0.0979 | [-0.2937, 0.0829]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0895 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6732 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2920 | < 0.05 |
| MCE | 0.5396 | < 0.10 |
| Brier Score | 0.3319 | < 0.20 |
| Log-Loss | 1.1970 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.9911 | proche 0 = pas de biais systématique |
| LoA lower | -7.1796 | limite inférieure d'accord |
| LoA upper | +5.1974 | limite supérieure d'accord |
| LoA width | ±6.1885 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0369 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0895 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6732 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5304 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 86.6 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.6 | 10% |

### **SCORE TOTAL : 55.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 18:10*
