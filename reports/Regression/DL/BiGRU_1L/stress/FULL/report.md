# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 18:36


> 🟠 **Deployment Readiness Score : 52.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3735 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7595 | Erreur quadratique moyenne |
| R² | 0.0290 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5838 | 0.500 |
| PR-AUC | 0.4460 | 0.366 |
| Sensitivity (TPR) | 0.0127 | 0.500 |
| Specificity (TNR) | 0.9964 | 0.500 |
| PPV (Precision) | 0.6667 | — |
| NPV | 0.6364 | — |
| Balanced Accuracy | 0.5045 | 0.500 |
| MCC | 0.0522 | 0.000 |
| G-Mean | 0.1123 | 0.500 |
| F1 macro | 0.4008 | 0.500 |
| LR+ | 3.468 | >10 = très utile |
| LR− | 0.991 | <0.1 = très utile |
| Cohen κ | 0.0114 | 0.000 |
| Brier Score | 0.2462 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5806 | [0.5254, 0.6392]  ✅ |
| F1 macro | 0.4014 | [0.3773, 0.4289]  — |
| Sensitivity | 0.0130 | [0.0000, 0.0351]  — |
| Specificity | 0.9963 | [0.9887, 1.0000]  — |
| MCC | 0.0502 | [-0.0504, 0.1319]  — |
| R² | 0.0253 | [-0.0027, 0.0531]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0290 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5838 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1355 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2462 | < 0.20 |
| Log-Loss | 0.7021 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0093 | proche 0 = pas de biais systématique |
| LoA lower | -5.4241 | limite inférieure d'accord |
| LoA upper | +5.4056 | limite supérieure d'accord |
| LoA width | ±5.4149 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0329 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0290 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5838 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3735 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 41.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 43.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 57.4 | 10% |

### **SCORE TOTAL : 52.7/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 18:36*
