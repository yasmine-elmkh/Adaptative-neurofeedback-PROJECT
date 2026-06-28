# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 03:48


> 🔴 **Deployment Readiness Score : 36.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5470 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1281 | Erreur quadratique moyenne |
| R² | 0.0225 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5919 | 0.500 |
| PR-AUC | 0.5744 | 0.521 |
| Sensitivity (TPR) | 0.3540 | 0.500 |
| Specificity (TNR) | 0.7308 | 0.500 |
| PPV (Precision) | 0.5882 | — |
| NPV | 0.5101 | — |
| Balanced Accuracy | 0.5424 | 0.500 |
| MCC | 0.0913 | 0.000 |
| G-Mean | 0.5086 | 0.500 |
| F1 macro | 0.5214 | 0.500 |
| LR+ | 1.315 | >10 = très utile |
| LR− | 0.884 | <0.1 = très utile |
| Cohen κ | 0.0833 | 0.000 |
| Brier Score | 0.3087 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5902 | [0.5121, 0.6650]  ✅ |
| F1 macro | 0.5194 | [0.4540, 0.5791]  — |
| Sensitivity | 0.3523 | [0.2661, 0.4345]  — |
| Specificity | 0.7308 | [0.6398, 0.8079]  — |
| MCC | 0.0896 | [-0.0425, 0.2154]  — |
| R² | 0.0177 | [-0.1378, 0.1480]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0225 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5919 | p=0.0080 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2147 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3087 | < 0.20 |
| Log-Loss | 1.0586 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8510 | proche 0 = pas de biais systématique |
| LoA lower | -6.7646 | limite inférieure d'accord |
| LoA upper | +5.0626 | limite supérieure d'accord |
| LoA width | ±5.9136 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0391 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0225 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5919 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5470 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 45.9 | 25% |
| Significativité (p-value) | 46.8 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 31.4 | 10% |

### **SCORE TOTAL : 36.7/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 03:48*
