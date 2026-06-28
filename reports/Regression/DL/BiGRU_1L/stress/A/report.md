# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 17:33


> 🟠 **Deployment Readiness Score : 55.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3980 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7762 | Erreur quadratique moyenne |
| R² | 0.0172 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5862 | 0.500 |
| PR-AUC | 0.4146 | 0.366 |
| Sensitivity (TPR) | 0.1835 | 0.500 |
| Specificity (TNR) | 0.8905 | 0.500 |
| PPV (Precision) | 0.4915 | — |
| NPV | 0.6542 | — |
| Balanced Accuracy | 0.5370 | 0.500 |
| MCC | 0.1039 | 0.000 |
| G-Mean | 0.4043 | 0.500 |
| F1 macro | 0.5108 | 0.500 |
| LR+ | 1.676 | >10 = très utile |
| LR− | 0.917 | <0.1 = très utile |
| Cohen κ | 0.0854 | 0.000 |
| Brier Score | 0.2351 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5837 | [0.5227, 0.6349]  ✅ |
| F1 macro | 0.5082 | [0.4641, 0.5566]  — |
| Sensitivity | 0.1808 | [0.1258, 0.2411]  — |
| Specificity | 0.8897 | [0.8487, 0.9252]  — |
| MCC | 0.0989 | [0.0035, 0.1940]  — |
| R² | 0.0128 | [-0.0264, 0.0472]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0172 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5862 | p=0.0020 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.0881 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2351 | < 0.20 |
| Log-Loss | 0.6649 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2785 | proche 0 = pas de biais systématique |
| LoA lower | -5.1417 | limite inférieure d'accord |
| LoA upper | +5.6986 | limite supérieure d'accord |
| LoA width | ±5.4201 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0172 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0172 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5862 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3980 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 43.1 | 25% |
| Significativité (p-value) | 82.3 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 74.6 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 58.5 | 10% |

### **SCORE TOTAL : 55.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 17:33*
