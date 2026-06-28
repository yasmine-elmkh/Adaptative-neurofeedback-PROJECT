# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LSTM_2L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 16:07


> 🔴 **Deployment Readiness Score : 17.8/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0883 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4250 | Erreur quadratique moyenne |
| R² | -0.0374 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4855 | 0.500 |
| PR-AUC | 0.2594 | 0.282 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 1.0000 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.7176 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0000 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.4178 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | 0.0000 | 0.000 |
| Brier Score | 0.2404 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4856 | [0.4588, 0.5102]  — |
| F1 macro | 0.4176 | [0.4103, 0.4241]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.0384 | [-0.0560, -0.0219]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1963 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2404 | < 0.20 |
| Log-Loss | 0.7542 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2092 | proche 0 = pas de biais systématique |
| LoA lower | -4.9457 | limite inférieure d'accord |
| LoA upper | +4.5272 | limite supérieure d'accord |
| LoA width | ±4.7364 | < ±2 pts : excellent |
| % dans LoA | 97.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0009 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.3392 | 0.8151 | 240.3% | 🔴 unstable |
| AUC ROC | 0.4880 | 0.0788 | 16.1% | 🟡 moderate |
| MAE | 2.0882 | 0.5925 | 28.4% | 🟡 moderate |

**Stability Score global : 51.8/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 2.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 99.1 | 10% |

### **SCORE TOTAL : 17.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 16:07*
