# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `TCN`  |  **Exp :** `C`  |  **Date :** 2026-06-13 21:14


> 🟠 **Deployment Readiness Score : 52.3/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7065 | Erreur absolue moyenne (0-10) |
| RMSE | 3.3537 | Erreur quadratique moyenne |
| R² | -0.1236 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6476 | 0.500 |
| PR-AUC | 0.6275 | 0.521 |
| Sensitivity (TPR) | 0.0885 | 0.500 |
| Specificity (TNR) | 0.9615 | 0.500 |
| PPV (Precision) | 0.7143 | — |
| NPV | 0.4926 | — |
| Balanced Accuracy | 0.5250 | 0.500 |
| MCC | 0.1017 | 0.000 |
| G-Mean | 0.2917 | 0.500 |
| F1 macro | 0.4045 | 0.500 |
| LR+ | 2.301 | >10 = très utile |
| LR− | 0.948 | <0.1 = très utile |
| Cohen κ | 0.0482 | 0.000 |
| Brier Score | 0.3955 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6455 | [0.5731, 0.7156]  ✅ |
| F1 macro | 0.4038 | [0.3468, 0.4677]  — |
| Sensitivity | 0.0878 | [0.0360, 0.1489]  — |
| Specificity | 0.9629 | [0.9223, 1.0000]  — |
| MCC | 0.1029 | [-0.0324, 0.2349]  — |
| R² | -0.1308 | [-0.3081, 0.0267]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1236 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6476 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.4002 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3955 | < 0.20 |
| Log-Loss | 1.3727 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.5770 | proche 0 = pas de biais systématique |
| LoA lower | -7.3915 | limite inférieure d'accord |
| LoA upper | +4.2376 | limite supérieure d'accord |
| LoA width | ±5.8146 | < ±2 pts : excellent |
| % dans LoA | 98.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0109 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1236 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6476 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.7065 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 73.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.3 | 10% |

### **SCORE TOTAL : 52.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 21:14*
