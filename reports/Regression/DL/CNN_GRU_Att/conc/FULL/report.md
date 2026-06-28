# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 03:24


> 🟠 **Deployment Readiness Score : 57.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4150 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2020 | Erreur quadratique moyenne |
| R² | -0.0243 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6918 | 0.500 |
| PR-AUC | 0.6809 | 0.521 |
| Sensitivity (TPR) | 0.3274 | 0.500 |
| Specificity (TNR) | 0.8750 | 0.500 |
| PPV (Precision) | 0.7400 | — |
| NPV | 0.5449 | — |
| Balanced Accuracy | 0.6012 | 0.500 |
| MCC | 0.2402 | 0.000 |
| G-Mean | 0.5353 | 0.500 |
| F1 macro | 0.5628 | 0.500 |
| LR+ | 2.619 | >10 = très utile |
| LR− | 0.769 | <0.1 = très utile |
| Cohen κ | 0.1977 | 0.000 |
| Brier Score | 0.3230 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6918 | [0.6153, 0.7606]  ✅ |
| F1 macro | 0.5638 | [0.4940, 0.6332]  — |
| Sensitivity | 0.3294 | [0.2478, 0.4178]  — |
| Specificity | 0.8761 | [0.8018, 0.9375]  — |
| MCC | 0.2434 | [0.1168, 0.3619]  — |
| R² | -0.0299 | [-0.2496, 0.1566]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0243 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6918 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2760 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3230 | < 0.20 |
| Log-Loss | 1.2511 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3924 | proche 0 = pas de biais systématique |
| LoA lower | -7.0570 | limite inférieure d'accord |
| LoA upper | +4.2722 | limite supérieure d'accord |
| LoA width | ±5.6646 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0240 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0243 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6918 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4150 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 95.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.5 | 10% |

### **SCORE TOTAL : 57.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 03:24*
