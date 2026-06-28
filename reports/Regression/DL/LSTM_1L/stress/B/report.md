# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 06:53


> 🔴 **Deployment Readiness Score : 24.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3644 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8205 | Erreur quadratique moyenne |
| R² | -0.0144 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5254 | 0.500 |
| PR-AUC | 0.3949 | 0.366 |
| Sensitivity (TPR) | 0.0253 | 0.500 |
| Specificity (TNR) | 0.9927 | 0.500 |
| PPV (Precision) | 0.6667 | — |
| NPV | 0.6385 | — |
| Balanced Accuracy | 0.5090 | 0.500 |
| MCC | 0.0741 | 0.000 |
| G-Mean | 0.1585 | 0.500 |
| F1 macro | 0.4130 | 0.500 |
| LR+ | 3.468 | >10 = très utile |
| LR− | 0.982 | <0.1 = très utile |
| Cohen κ | 0.0226 | 0.000 |
| Brier Score | 0.2785 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5246 | [0.4710, 0.5790]  — |
| F1 macro | 0.4128 | [0.3864, 0.4439]  — |
| Sensitivity | 0.0250 | [0.0058, 0.0513]  — |
| Specificity | 0.9927 | [0.9813, 1.0000]  — |
| MCC | 0.0715 | [-0.0333, 0.1617]  — |
| R² | -0.0156 | [-0.0658, 0.0376]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0144 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5254 | p=0.1780 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1958 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2785 | < 0.20 |
| Log-Loss | 0.8616 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4221 | proche 0 = pas de biais systématique |
| LoA lower | -5.8943 | limite inférieure d'accord |
| LoA upper | +5.0500 | limite supérieure d'accord |
| LoA width | ±5.4722 | < ±2 pts : excellent |
| % dans LoA | 98.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0142 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0144 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5254 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3644 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 12.7 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 2.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 61.3 | 10% |

### **SCORE TOTAL : 24.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 06:53*
