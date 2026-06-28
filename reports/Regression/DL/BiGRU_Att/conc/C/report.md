# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-13 13:04


> 🟡 **Deployment Readiness Score : 60.1/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1850 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7433 | Erreur quadratique moyenne |
| R² | 0.2482 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7363 | 0.500 |
| PR-AUC | 0.7179 | 0.521 |
| Sensitivity (TPR) | 0.4867 | 0.500 |
| Specificity (TNR) | 0.7788 | 0.500 |
| PPV (Precision) | 0.7051 | — |
| NPV | 0.5827 | — |
| Balanced Accuracy | 0.6328 | 0.500 |
| MCC | 0.2765 | 0.000 |
| G-Mean | 0.6157 | 0.500 |
| F1 macro | 0.6213 | 0.500 |
| LR+ | 2.201 | >10 = très utile |
| LR− | 0.659 | <0.1 = très utile |
| Cohen κ | 0.2621 | 0.000 |
| Brier Score | 0.2571 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7363 | [0.6716, 0.7966]  ✅ |
| F1 macro | 0.6205 | [0.5521, 0.6781]  ✅ |
| Sensitivity | 0.4868 | [0.3952, 0.5835]  — |
| Specificity | 0.7789 | [0.6984, 0.8558]  — |
| MCC | 0.2766 | [0.1402, 0.3840]  — |
| R² | 0.2443 | [0.1235, 0.3545]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2482 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7363 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1987 | < 0.05 |
| MCE | 0.3952 | < 0.10 |
| Brier Score | 0.2571 | < 0.20 |
| Log-Loss | 0.8092 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6750 | proche 0 = pas de biais systématique |
| LoA lower | -5.8986 | limite inférieure d'accord |
| LoA upper | +4.5487 | limite supérieure d'accord |
| LoA width | ±5.2236 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0934 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2482 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7363 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1850 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 50.0 | 10% |

### **SCORE TOTAL : 60.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 13:04*
