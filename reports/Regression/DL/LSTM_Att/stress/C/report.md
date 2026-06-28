# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-14 12:05


> 🔴 **Deployment Readiness Score : 25.6/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4202 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7919 | Erreur quadratique moyenne |
| R² | 0.0061 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5160 | 0.500 |
| PR-AUC | 0.3713 | 0.366 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 0.9964 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.6334 | — |
| Balanced Accuracy | 0.4982 | 0.500 |
| MCC | -0.0366 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.3872 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.004 | <0.1 = très utile |
| Cohen κ | -0.0046 | 0.000 |
| Brier Score | 0.2646 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5165 | [0.4611, 0.5685]  — |
| F1 macro | 0.3876 | [0.3698, 0.4041]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 0.9963 | [0.9890, 1.0000]  — |
| MCC | -0.0287 | [-0.0638, 0.0000]  — |
| R² | 0.0045 | [-0.0182, 0.0262]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0061 | p=0.0260 | ✅ p<0.05 |
| AUC ROC | 0.5160 | p=0.3120 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1757 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2646 | < 0.20 |
| Log-Loss | 0.7544 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1107 | proche 0 = pas de biais systématique |
| LoA lower | -5.5848 | limite inférieure d'accord |
| LoA upper | +5.3633 | limite supérieure d'accord |
| LoA width | ±5.4741 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0112 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0061 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5160 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4202 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 8.0 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 16.2 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 61.8 | 10% |

### **SCORE TOTAL : 25.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 12:05*
