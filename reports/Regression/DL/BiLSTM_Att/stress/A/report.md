# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-13 23:33


> 🟠 **Deployment Readiness Score : 42.4/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3634 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7535 | Erreur quadratique moyenne |
| R² | 0.0332 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5797 | 0.500 |
| PR-AUC | 0.3938 | 0.366 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 1.0000 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.6343 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0000 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.3881 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | 0.0000 | 0.000 |
| Brier Score | 0.2579 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5775 | [0.5228, 0.6281]  ✅ |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | 0.0309 | [-0.0112, 0.0712]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0332 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5797 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1853 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2579 | < 0.20 |
| Log-Loss | 0.7482 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1814 | proche 0 = pas de biais systématique |
| LoA lower | -5.5728 | limite inférieure d'accord |
| LoA upper | +5.2100 | limite supérieure d'accord |
| LoA width | ±5.3914 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0345 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0332 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5797 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3634 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 39.8 | 25% |
| Significativité (p-value) | 64.6 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 9.8 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.1 | 10% |

### **SCORE TOTAL : 42.4/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 23:33*
