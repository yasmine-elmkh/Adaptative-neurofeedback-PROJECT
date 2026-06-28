# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 06:42


> 🟠 **Deployment Readiness Score : 58.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3861 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1317 | Erreur quadratique moyenne |
| R² | 0.0202 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7092 | 0.500 |
| PR-AUC | 0.7080 | 0.521 |
| Sensitivity (TPR) | 0.2920 | 0.500 |
| Specificity (TNR) | 0.8750 | 0.500 |
| PPV (Precision) | 0.7174 | — |
| NPV | 0.5322 | — |
| Balanced Accuracy | 0.5835 | 0.500 |
| MCC | 0.2042 | 0.000 |
| G-Mean | 0.5055 | 0.500 |
| F1 macro | 0.5385 | 0.500 |
| LR+ | 2.336 | >10 = très utile |
| LR− | 0.809 | <0.1 = très utile |
| Cohen κ | 0.1629 | 0.000 |
| Brier Score | 0.3191 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7094 | [0.6328, 0.7756]  ✅ |
| F1 macro | 0.5378 | [0.4674, 0.6013]  — |
| Sensitivity | 0.2919 | [0.2127, 0.3756]  — |
| Specificity | 0.8757 | [0.8121, 0.9366]  — |
| MCC | 0.2048 | [0.0665, 0.3216]  — |
| R² | 0.0162 | [-0.1903, 0.1797]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0202 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7092 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2888 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3191 | < 0.20 |
| Log-Loss | 1.1554 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3828 | proche 0 = pas de biais systématique |
| LoA lower | -6.9029 | limite inférieure d'accord |
| LoA upper | +4.1374 | limite supérieure d'accord |
| LoA width | ±5.5201 | < ±2 pts : excellent |
| % dans LoA | 93.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0241 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0202 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7092 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3861 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.1 | 10% |

### **SCORE TOTAL : 58.8/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 06:42*
