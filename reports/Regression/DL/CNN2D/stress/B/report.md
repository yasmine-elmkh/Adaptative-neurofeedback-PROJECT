# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN2D`  |  **Exp :** `B`  |  **Date :** 2026-06-12 22:53


> 🟠 **Deployment Readiness Score : 47.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3882 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8686 | Erreur quadratique moyenne |
| R² | -0.0493 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5991 | 0.500 |
| PR-AUC | 0.4279 | 0.366 |
| Sensitivity (TPR) | 0.0063 | 0.500 |
| Specificity (TNR) | 0.9818 | 0.500 |
| PPV (Precision) | 0.1667 | — |
| NPV | 0.6315 | — |
| Balanced Accuracy | 0.4940 | 0.500 |
| MCC | -0.0491 | 0.000 |
| G-Mean | 0.0788 | 0.500 |
| F1 macro | 0.3904 | 0.500 |
| LR+ | 0.347 | >10 = très utile |
| LR− | 1.012 | <0.1 = très utile |
| Cohen κ | -0.0150 | 0.000 |
| Brier Score | 0.2879 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5973 | [0.5416, 0.6582]  ✅ |
| F1 macro | 0.3905 | [0.3684, 0.4119]  — |
| Sensitivity | 0.0061 | [0.0000, 0.0200]  — |
| Specificity | 0.9816 | [0.9631, 0.9963]  — |
| MCC | -0.0493 | [-0.1094, 0.0440]  — |
| R² | -0.0510 | [-0.1169, 0.0074]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0493 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5991 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2471 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2879 | < 0.20 |
| Log-Loss | 0.9010 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6660 | proche 0 = pas de biais systématique |
| LoA lower | -6.1412 | limite inférieure d'accord |
| LoA upper | +4.8092 | limite supérieure d'accord |
| LoA width | ±5.4752 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0052 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0493 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5991 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3882 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 49.5 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 55.6 | 10% |

### **SCORE TOTAL : 47.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 22:53*
