# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-14 10:42


> 🟡 **Deployment Readiness Score : 61.1/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0747 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6807 | Erreur quadratique moyenne |
| R² | 0.2821 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7417 | 0.500 |
| PR-AUC | 0.7249 | 0.521 |
| Sensitivity (TPR) | 0.7788 | 0.500 |
| Specificity (TNR) | 0.6154 | 0.500 |
| PPV (Precision) | 0.6875 | — |
| NPV | 0.7191 | — |
| Balanced Accuracy | 0.6971 | 0.500 |
| MCC | 0.4003 | 0.000 |
| G-Mean | 0.6923 | 0.500 |
| F1 macro | 0.6968 | 0.500 |
| LR+ | 2.025 | >10 = très utile |
| LR− | 0.360 | <0.1 = très utile |
| Cohen κ | 0.3964 | 0.000 |
| Brier Score | 0.2420 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7420 | [0.6757, 0.8054]  ✅ |
| F1 macro | 0.6957 | [0.6331, 0.7616]  ✅ |
| Sensitivity | 0.7793 | [0.7009, 0.8558]  — |
| Specificity | 0.6150 | [0.5150, 0.7087]  — |
| MCC | 0.4005 | [0.2779, 0.5320]  — |
| R² | 0.2770 | [0.1372, 0.4049]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2821 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7417 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1858 | < 0.05 |
| MCE | 0.2524 | < 0.10 |
| Brier Score | 0.2420 | < 0.20 |
| Log-Loss | 0.7862 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1224 | proche 0 = pas de biais systématique |
| LoA lower | -5.1383 | limite inférieure d'accord |
| LoA upper | +5.3832 | limite supérieure d'accord |
| LoA width | ±5.2608 | < ±2 pts : excellent |
| % dans LoA | 93.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.3832 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2821 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7417 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.0747 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 9.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 46.9 | 10% |

### **SCORE TOTAL : 61.1/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:42*
