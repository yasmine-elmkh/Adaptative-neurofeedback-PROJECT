# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-13 19:38


> 🟠 **Deployment Readiness Score : 58.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4472 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1745 | Erreur quadratique moyenne |
| R² | -0.0067 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6999 | 0.500 |
| PR-AUC | 0.6677 | 0.521 |
| Sensitivity (TPR) | 0.2920 | 0.500 |
| Specificity (TNR) | 0.8654 | 0.500 |
| PPV (Precision) | 0.7021 | — |
| NPV | 0.5294 | — |
| Balanced Accuracy | 0.5787 | 0.500 |
| MCC | 0.1909 | 0.000 |
| G-Mean | 0.5027 | 0.500 |
| F1 macro | 0.5347 | 0.500 |
| LR+ | 2.169 | >10 = très utile |
| LR− | 0.818 | <0.1 = très utile |
| Cohen κ | 0.1535 | 0.000 |
| Brier Score | 0.3162 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6988 | [0.6242, 0.7683]  ✅ |
| F1 macro | 0.5348 | [0.4700, 0.6059]  — |
| Sensitivity | 0.2934 | [0.2149, 0.3800]  — |
| Specificity | 0.8652 | [0.8016, 0.9290]  — |
| MCC | 0.1919 | [0.0524, 0.3166]  — |
| R² | -0.0121 | [-0.1952, 0.1464]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0067 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6999 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2891 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3162 | < 0.20 |
| Log-Loss | 1.1667 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3423 | proche 0 = pas de biais systématique |
| LoA lower | -6.9937 | limite inférieure d'accord |
| LoA upper | +4.3091 | limite supérieure d'accord |
| LoA width | ±5.6514 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0232 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0067 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6999 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4472 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 99.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.3 | 10% |

### **SCORE TOTAL : 58.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 19:38*
