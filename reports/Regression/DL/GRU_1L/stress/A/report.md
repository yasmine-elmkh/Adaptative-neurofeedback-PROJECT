# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `GRU_1L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 12:54


> 🟠 **Deployment Readiness Score : 47.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3668 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7782 | Erreur quadratique moyenne |
| R² | 0.0158 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5900 | 0.500 |
| PR-AUC | 0.4392 | 0.366 |
| Sensitivity (TPR) | 0.0506 | 0.500 |
| Specificity (TNR) | 0.9708 | 0.500 |
| PPV (Precision) | 0.5000 | — |
| NPV | 0.6394 | — |
| Balanced Accuracy | 0.5107 | 0.500 |
| MCC | 0.0547 | 0.000 |
| G-Mean | 0.2217 | 0.500 |
| F1 macro | 0.4315 | 0.500 |
| LR+ | 1.734 | >10 = très utile |
| LR− | 0.978 | <0.1 = très utile |
| Cohen κ | 0.0265 | 0.000 |
| Brier Score | 0.2523 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5878 | [0.5346, 0.6435]  ✅ |
| F1 macro | 0.4319 | [0.3949, 0.4725]  — |
| Sensitivity | 0.0509 | [0.0193, 0.0853]  — |
| Specificity | 0.9710 | [0.9494, 0.9887]  — |
| MCC | 0.0554 | [-0.0451, 0.1501]  — |
| R² | 0.0123 | [-0.0378, 0.0627]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0158 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5900 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1425 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2523 | < 0.20 |
| Log-Loss | 0.7495 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1791 | proche 0 = pas de biais systématique |
| LoA lower | -5.6193 | limite inférieure d'accord |
| LoA upper | +5.2611 | limite supérieure d'accord |
| LoA width | ±5.4402 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0404 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0158 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5900 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3668 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 45.0 | 25% |
| Significativité (p-value) | 64.6 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 38.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.8 | 10% |

### **SCORE TOTAL : 47.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:54*
