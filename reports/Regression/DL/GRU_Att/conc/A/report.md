# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-14 10:00


> 🟠 **Deployment Readiness Score : 53.1/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4968 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1409 | Erreur quadratique moyenne |
| R² | 0.0145 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6567 | 0.500 |
| PR-AUC | 0.6297 | 0.521 |
| Sensitivity (TPR) | 0.1858 | 0.500 |
| Specificity (TNR) | 0.8846 | 0.500 |
| PPV (Precision) | 0.6364 | — |
| NPV | 0.5000 | — |
| Balanced Accuracy | 0.5352 | 0.500 |
| MCC | 0.0980 | 0.000 |
| G-Mean | 0.4055 | 0.500 |
| F1 macro | 0.4633 | 0.500 |
| LR+ | 1.611 | >10 = très utile |
| LR− | 0.920 | <0.1 = très utile |
| Cohen κ | 0.0684 | 0.000 |
| Brier Score | 0.3384 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6543 | [0.5799, 0.7266]  ✅ |
| F1 macro | 0.4607 | [0.3993, 0.5234]  — |
| Sensitivity | 0.1843 | [0.1172, 0.2545]  — |
| Specificity | 0.8828 | [0.8152, 0.9399]  — |
| MCC | 0.0933 | [-0.0379, 0.2080]  — |
| R² | 0.0051 | [-0.1573, 0.1480]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0145 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6567 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3037 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3384 | < 0.20 |
| Log-Loss | 1.1551 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.2821 | proche 0 = pas de biais systématique |
| LoA lower | -6.9149 | limite inférieure d'accord |
| LoA upper | +4.3508 | limite supérieure d'accord |
| LoA width | ±5.6329 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0223 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0145 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6567 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4968 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 78.4 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.6 | 10% |

### **SCORE TOTAL : 53.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:00*
