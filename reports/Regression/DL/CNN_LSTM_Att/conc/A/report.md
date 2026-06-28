# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-13 12:54


> 🟡 **Deployment Readiness Score : 67.9/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2322 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7104 | Erreur quadratique moyenne |
| R² | 0.2661 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7135 | 0.500 |
| PR-AUC | 0.6868 | 0.521 |
| Sensitivity (TPR) | 0.7522 | 0.500 |
| Specificity (TNR) | 0.5673 | 0.500 |
| PPV (Precision) | 0.6538 | — |
| NPV | 0.6782 | — |
| Balanced Accuracy | 0.6598 | 0.500 |
| MCC | 0.3257 | 0.000 |
| G-Mean | 0.6533 | 0.500 |
| F1 macro | 0.6587 | 0.500 |
| LR+ | 1.738 | >10 = très utile |
| LR− | 0.437 | <0.1 = très utile |
| Cohen κ | 0.3216 | 0.000 |
| Brier Score | 0.2270 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7138 | [0.6409, 0.7774]  ✅ |
| F1 macro | 0.6576 | [0.5931, 0.7159]  ✅ |
| Sensitivity | 0.7531 | [0.6710, 0.8258]  — |
| Specificity | 0.5666 | [0.4663, 0.6505]  — |
| MCC | 0.3259 | [0.2005, 0.4436]  — |
| R² | 0.2629 | [0.1607, 0.3571]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2661 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7135 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1138 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2270 | < 0.20 |
| Log-Loss | 0.6746 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2163 | proche 0 = pas de biais systématique |
| LoA lower | -5.5239 | limite inférieure d'accord |
| LoA upper | +5.0913 | limite supérieure d'accord |
| LoA width | ±5.3076 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2586 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2661 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7135 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2322 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 57.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 42.3 | 10% |

### **SCORE TOTAL : 67.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:54*
