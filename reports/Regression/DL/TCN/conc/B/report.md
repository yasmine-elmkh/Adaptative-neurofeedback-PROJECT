# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `TCN`  |  **Exp :** `B`  |  **Date :** 2026-06-13 20:35


> 🟠 **Deployment Readiness Score : 58.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4736 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1678 | Erreur quadratique moyenne |
| R² | -0.0025 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7055 | 0.500 |
| PR-AUC | 0.6733 | 0.521 |
| Sensitivity (TPR) | 0.2301 | 0.500 |
| Specificity (TNR) | 0.8846 | 0.500 |
| PPV (Precision) | 0.6842 | — |
| NPV | 0.5140 | — |
| Balanced Accuracy | 0.5574 | 0.500 |
| MCC | 0.1508 | 0.000 |
| G-Mean | 0.4512 | 0.500 |
| F1 macro | 0.4973 | 0.500 |
| LR+ | 1.994 | >10 = très utile |
| LR− | 0.870 | <0.1 = très utile |
| Cohen κ | 0.1115 | 0.000 |
| Brier Score | 0.3456 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7037 | [0.6274, 0.7718]  ✅ |
| F1 macro | 0.4944 | [0.4311, 0.5609]  — |
| Sensitivity | 0.2277 | [0.1560, 0.3094]  — |
| Specificity | 0.8838 | [0.8241, 0.9415]  — |
| MCC | 0.1467 | [0.0268, 0.2648]  — |
| R² | -0.0112 | [-0.2127, 0.1553]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0025 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7055 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3373 | < 0.05 |
| MCE | 0.5508 | < 0.10 |
| Brier Score | 0.3456 | < 0.20 |
| Log-Loss | 1.1956 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.4088 | proche 0 = pas de biais systématique |
| LoA lower | -6.9827 | limite inférieure d'accord |
| LoA upper | +4.1652 | limite supérieure d'accord |
| LoA width | ±5.5739 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0213 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0025 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7055 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4736 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.1 | 10% |

### **SCORE TOTAL : 58.7/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:35*
