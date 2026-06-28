# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN3D`  |  **Exp :** `C`  |  **Date :** 2026-06-13 05:15


> 🔴 **Deployment Readiness Score : 22.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4955 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9544 | Erreur quadratique moyenne |
| R² | -0.1130 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5103 | 0.500 |
| PR-AUC | 0.3849 | 0.366 |
| Sensitivity (TPR) | 0.1582 | 0.500 |
| Specificity (TNR) | 0.8613 | 0.500 |
| PPV (Precision) | 0.3968 | — |
| NPV | 0.6396 | — |
| Balanced Accuracy | 0.5098 | 0.500 |
| MCC | 0.0267 | 0.000 |
| G-Mean | 0.3692 | 0.500 |
| F1 macro | 0.4802 | 0.500 |
| LR+ | 1.141 | >10 = très utile |
| LR− | 0.977 | <0.1 = très utile |
| Cohen κ | 0.0224 | 0.000 |
| Brier Score | 0.2956 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5106 | [0.4628, 0.5665]  — |
| F1 macro | 0.4803 | [0.4378, 0.5301]  — |
| Sensitivity | 0.1591 | [0.1066, 0.2161]  — |
| Specificity | 0.8607 | [0.8189, 0.8987]  — |
| MCC | 0.0268 | [-0.0635, 0.1249]  — |
| R² | -0.1142 | [-0.1882, -0.0421]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1130 | p=0.2800 | ❌ ns |
| AUC ROC | 0.5103 | p=0.3800 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2299 | < 0.05 |
| MCE | 0.9855 | < 0.10 |
| Brier Score | 0.2956 | < 0.20 |
| Log-Loss | 0.9383 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2992 | proche 0 = pas de biais systématique |
| LoA lower | -6.0666 | limite inférieure d'accord |
| LoA upper | +5.4683 | limite supérieure d'accord |
| LoA width | ±5.7675 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0051 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1130 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5103 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4955 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 5.2 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 64.2 | 10% |

### **SCORE TOTAL : 22.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 05:15*
