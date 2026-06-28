# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN2D`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 01:44


> 🟠 **Deployment Readiness Score : 52.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4054 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7927 | Erreur quadratique moyenne |
| R² | 0.0055 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5863 | 0.500 |
| PR-AUC | 0.4325 | 0.366 |
| Sensitivity (TPR) | 0.0316 | 0.500 |
| Specificity (TNR) | 0.9708 | 0.500 |
| PPV (Precision) | 0.3846 | — |
| NPV | 0.6348 | — |
| Balanced Accuracy | 0.5012 | 0.500 |
| MCC | 0.0069 | 0.000 |
| G-Mean | 0.1753 | 0.500 |
| F1 macro | 0.4131 | 0.500 |
| LR+ | 1.084 | >10 = très utile |
| LR− | 0.997 | <0.1 = très utile |
| Cohen κ | 0.0030 | 0.000 |
| Brier Score | 0.2462 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5849 | [0.5308, 0.6477]  ✅ |
| F1 macro | 0.4127 | [0.3841, 0.4482]  — |
| Sensitivity | 0.0312 | [0.0063, 0.0599]  — |
| Specificity | 0.9705 | [0.9502, 0.9886]  — |
| MCC | 0.0045 | [-0.0904, 0.1059]  — |
| R² | 0.0023 | [-0.0316, 0.0357]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0055 | p=0.0080 | ✅ p<0.05 |
| AUC ROC | 0.5863 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1368 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2462 | < 0.20 |
| Log-Loss | 0.7055 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0120 | proche 0 = pas de biais systématique |
| LoA lower | -5.4680 | limite inférieure d'accord |
| LoA upper | +5.4920 | limite supérieure d'accord |
| LoA width | ±5.4800 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0233 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0055 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5863 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4054 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 43.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 42.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 55.4 | 10% |

### **SCORE TOTAL : 52.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 01:44*
