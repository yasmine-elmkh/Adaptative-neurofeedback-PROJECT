# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-14 01:09


> 🟠 **Deployment Readiness Score : 42.1/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3867 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7771 | Erreur quadratique moyenne |
| R² | 0.0166 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5749 | 0.500 |
| PR-AUC | 0.4046 | 0.366 |
| Sensitivity (TPR) | 0.1392 | 0.500 |
| Specificity (TNR) | 0.8650 | 0.500 |
| PPV (Precision) | 0.3729 | — |
| NPV | 0.6354 | — |
| Balanced Accuracy | 0.5021 | 0.500 |
| MCC | 0.0059 | 0.000 |
| G-Mean | 0.3470 | 0.500 |
| F1 macro | 0.4677 | 0.500 |
| LR+ | 1.031 | >10 = très utile |
| LR− | 0.995 | <0.1 = très utile |
| Cohen κ | 0.0048 | 0.000 |
| Brier Score | 0.2595 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5728 | [0.5148, 0.6199]  ✅ |
| F1 macro | 0.4670 | [0.4237, 0.5129]  — |
| Sensitivity | 0.1388 | [0.0900, 0.1905]  — |
| Specificity | 0.8646 | [0.8212, 0.9047]  — |
| MCC | 0.0050 | [-0.0877, 0.0974]  — |
| R² | 0.0129 | [-0.0310, 0.0539]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0166 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5749 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1823 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2595 | < 0.20 |
| Log-Loss | 0.7341 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0584 | proche 0 = pas de biais systématique |
| LoA lower | -5.3899 | limite inférieure d'accord |
| LoA upper | +5.5066 | limite supérieure d'accord |
| LoA width | ±5.4482 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0451 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0166 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5749 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3867 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 37.4 | 25% |
| Significativité (p-value) | 64.6 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 11.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.3 | 10% |

### **SCORE TOTAL : 42.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 01:09*
