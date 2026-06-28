# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 04:47


> 🟠 **Deployment Readiness Score : 56.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4751 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2792 | Erreur quadratique moyenne |
| R² | -0.0742 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6864 | 0.500 |
| PR-AUC | 0.6772 | 0.521 |
| Sensitivity (TPR) | 0.4779 | 0.500 |
| Specificity (TNR) | 0.7596 | 0.500 |
| PPV (Precision) | 0.6835 | — |
| NPV | 0.5725 | — |
| Balanced Accuracy | 0.6187 | 0.500 |
| MCC | 0.2466 | 0.000 |
| G-Mean | 0.6025 | 0.500 |
| F1 macro | 0.6077 | 0.500 |
| LR+ | 1.988 | >10 = très utile |
| LR− | 0.687 | <0.1 = très utile |
| Cohen κ | 0.2344 | 0.000 |
| Brier Score | 0.3161 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6853 | [0.6091, 0.7583]  ✅ |
| F1 macro | 0.6057 | [0.5316, 0.6713]  ✅ |
| Sensitivity | 0.4770 | [0.3817, 0.5765]  — |
| Specificity | 0.7586 | [0.6744, 0.8432]  — |
| MCC | 0.2447 | [0.1184, 0.3775]  — |
| R² | -0.0786 | [-0.2782, 0.1014]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0742 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6864 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2761 | < 0.05 |
| MCE | 0.5516 | < 0.10 |
| Brier Score | 0.3161 | < 0.20 |
| Log-Loss | 1.2329 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0885 | proche 0 = pas de biais systématique |
| LoA lower | -7.1653 | limite inférieure d'accord |
| LoA upper | +4.9883 | limite supérieure d'accord |
| LoA width | ±6.0768 | < ±2 pts : excellent |
| % dans LoA | 91.7% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0361 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0742 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6864 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4751 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 93.2 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 33.8 | 10% |

### **SCORE TOTAL : 56.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 04:47*
