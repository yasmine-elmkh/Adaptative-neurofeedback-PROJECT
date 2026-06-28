# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN2D`  |  **Exp :** `D`  |  **Date :** 2026-06-12 19:42


> 🟡 **Deployment Readiness Score : 60.4/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1407 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6823 | Erreur quadratique moyenne |
| R² | 0.2812 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7106 | 0.500 |
| PR-AUC | 0.6874 | 0.521 |
| Sensitivity (TPR) | 0.4867 | 0.500 |
| Specificity (TNR) | 0.7404 | 0.500 |
| PPV (Precision) | 0.6707 | — |
| NPV | 0.5704 | — |
| Balanced Accuracy | 0.6136 | 0.500 |
| MCC | 0.2340 | 0.000 |
| G-Mean | 0.6003 | 0.500 |
| F1 macro | 0.6042 | 0.500 |
| LR+ | 1.875 | >10 = très utile |
| LR− | 0.693 | <0.1 = très utile |
| Cohen κ | 0.2244 | 0.000 |
| Brier Score | 0.2595 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7114 | [0.6394, 0.7771]  ✅ |
| F1 macro | 0.6042 | [0.5391, 0.6623]  ✅ |
| Sensitivity | 0.4880 | [0.3936, 0.5760]  — |
| Specificity | 0.7408 | [0.6616, 0.8198]  — |
| MCC | 0.2357 | [0.1052, 0.3506]  — |
| R² | 0.2774 | [0.1647, 0.3803]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2812 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7106 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1876 | < 0.05 |
| MCE | 0.4289 | < 0.10 |
| Brier Score | 0.2595 | < 0.20 |
| Log-Loss | 0.7914 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5424 | proche 0 = pas de biais systématique |
| LoA lower | -5.7031 | limite inférieure d'accord |
| LoA upper | +4.6183 | limite supérieure d'accord |
| LoA width | ±5.1607 | < ±2 pts : excellent |
| % dans LoA | 94.9% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1342 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2812 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7106 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1407 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 8.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 41.5 | 10% |

### **SCORE TOTAL : 60.4/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 19:42*
