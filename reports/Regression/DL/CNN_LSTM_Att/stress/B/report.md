# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-13 14:38


> 🟠 **Deployment Readiness Score : 42.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3720 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7699 | Erreur quadratique moyenne |
| R² | 0.0217 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5730 | 0.500 |
| PR-AUC | 0.3861 | 0.366 |
| Sensitivity (TPR) | 0.0316 | 0.500 |
| Specificity (TNR) | 0.9489 | 0.500 |
| PPV (Precision) | 0.2632 | — |
| NPV | 0.6295 | — |
| Balanced Accuracy | 0.4903 | 0.500 |
| MCC | -0.0457 | 0.000 |
| G-Mean | 0.1733 | 0.500 |
| F1 macro | 0.4067 | 0.500 |
| LR+ | 0.619 | >10 = très utile |
| LR− | 1.020 | <0.1 = très utile |
| Cohen κ | -0.0239 | 0.000 |
| Brier Score | 0.2655 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5721 | [0.5185, 0.6224]  ✅ |
| F1 macro | 0.4071 | [0.3772, 0.4434]  — |
| Sensitivity | 0.0321 | [0.0066, 0.0618]  — |
| Specificity | 0.9484 | [0.9218, 0.9734]  — |
| MCC | -0.0455 | [-0.1267, 0.0496]  — |
| R² | 0.0197 | [-0.0269, 0.0636]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0217 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5730 | p=0.0020 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2014 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2655 | < 0.20 |
| Log-Loss | 0.7716 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2002 | proche 0 = pas de biais systématique |
| LoA lower | -5.6213 | limite inférieure d'accord |
| LoA upper | +5.2208 | limite supérieure d'accord |
| LoA width | ±5.4210 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0346 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0217 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5730 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3720 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 36.5 | 25% |
| Significativité (p-value) | 82.3 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 64.1 | 10% |

### **SCORE TOTAL : 42.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 14:38*
