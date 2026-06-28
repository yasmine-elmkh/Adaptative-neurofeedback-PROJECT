# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 07:22


> 🟠 **Deployment Readiness Score : 45.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3896 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7951 | Erreur quadratique moyenne |
| R² | 0.0038 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5761 | 0.500 |
| PR-AUC | 0.4409 | 0.366 |
| Sensitivity (TPR) | 0.1646 | 0.500 |
| Specificity (TNR) | 0.8978 | 0.500 |
| PPV (Precision) | 0.4815 | — |
| NPV | 0.6508 | — |
| Balanced Accuracy | 0.5312 | 0.500 |
| MCC | 0.0908 | 0.000 |
| G-Mean | 0.3844 | 0.500 |
| F1 macro | 0.4999 | 0.500 |
| LR+ | 1.610 | >10 = très utile |
| LR− | 0.931 | <0.1 = très utile |
| Cohen κ | 0.0725 | 0.000 |
| Brier Score | 0.2527 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5743 | [0.5191, 0.6289]  ✅ |
| F1 macro | 0.4983 | [0.4551, 0.5488]  — |
| Sensitivity | 0.1633 | [0.1129, 0.2229]  — |
| Specificity | 0.8964 | [0.8621, 0.9302]  — |
| MCC | 0.0867 | [-0.0132, 0.1868]  — |
| R² | -0.0002 | [-0.0462, 0.0454]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0038 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.5761 | p=0.0060 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1351 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2527 | < 0.20 |
| Log-Loss | 0.7439 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0260 | proche 0 = pas de biais systématique |
| LoA lower | -5.5106 | limite inférieure d'accord |
| LoA upper | +5.4585 | limite supérieure d'accord |
| LoA width | ±5.4846 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0494 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0038 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5761 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3896 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 38.1 | 25% |
| Significativité (p-value) | 54.2 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 43.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.2 | 10% |

### **SCORE TOTAL : 45.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 07:22*
