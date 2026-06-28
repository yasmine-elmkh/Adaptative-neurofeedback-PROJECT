# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_2L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 20:11


> 🟡 **Deployment Readiness Score : 64.0/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2272 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8547 | Erreur quadratique moyenne |
| R² | 0.1859 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7131 | 0.500 |
| PR-AUC | 0.6858 | 0.521 |
| Sensitivity (TPR) | 0.6726 | 0.500 |
| Specificity (TNR) | 0.6058 | 0.500 |
| PPV (Precision) | 0.6496 | — |
| NPV | 0.6300 | — |
| Balanced Accuracy | 0.6392 | 0.500 |
| MCC | 0.2790 | 0.000 |
| G-Mean | 0.6383 | 0.500 |
| F1 macro | 0.6393 | 0.500 |
| LR+ | 1.706 | >10 = très utile |
| LR− | 0.541 | <0.1 = très utile |
| Cohen κ | 0.2788 | 0.000 |
| Brier Score | 0.2439 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7128 | [0.6410, 0.7783]  ✅ |
| F1 macro | 0.6380 | [0.5747, 0.6989]  ✅ |
| Sensitivity | 0.6715 | [0.5890, 0.7596]  — |
| Specificity | 0.6065 | [0.5138, 0.7006]  — |
| MCC | 0.2787 | [0.1542, 0.4047]  — |
| R² | 0.1819 | [0.0401, 0.3052]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1859 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7131 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1523 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2439 | < 0.20 |
| Log-Loss | 0.7885 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4141 | proche 0 = pas de biais systématique |
| LoA lower | -5.9629 | limite inférieure d'accord |
| LoA upper | +5.1347 | limite supérieure d'accord |
| LoA width | ±5.5488 | < ±2 pts : excellent |
| % dans LoA | 93.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1542 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1859 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7131 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2272 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 31.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 41.8 | 10% |

### **SCORE TOTAL : 64.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:11*
