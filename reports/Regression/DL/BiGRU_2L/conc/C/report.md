# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 20:35


> 🟡 **Deployment Readiness Score : 63.5/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1517 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7491 | Erreur quadratique moyenne |
| R² | 0.2450 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6809 | 0.500 |
| PR-AUC | 0.6559 | 0.521 |
| Sensitivity (TPR) | 0.8319 | 0.500 |
| Specificity (TNR) | 0.4808 | 0.500 |
| PPV (Precision) | 0.6351 | — |
| NPV | 0.7246 | — |
| Balanced Accuracy | 0.6563 | 0.500 |
| MCC | 0.3354 | 0.000 |
| G-Mean | 0.6324 | 0.500 |
| F1 macro | 0.6492 | 0.500 |
| LR+ | 1.602 | >10 = très utile |
| LR− | 0.350 | <0.1 = très utile |
| Cohen κ | 0.3169 | 0.000 |
| Brier Score | 0.2370 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6801 | [0.6047, 0.7522]  ✅ |
| F1 macro | 0.6481 | [0.5860, 0.7113]  ✅ |
| Sensitivity | 0.8333 | [0.7570, 0.8964]  — |
| Specificity | 0.4797 | [0.3891, 0.5699]  — |
| MCC | 0.3361 | [0.2164, 0.4504]  — |
| R² | 0.2383 | [0.1144, 0.3519]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2450 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6809 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1258 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2370 | < 0.20 |
| Log-Loss | 0.7272 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1898 | proche 0 = pas de biais systématique |
| LoA lower | -5.5775 | limite inférieure d'accord |
| LoA upper | +5.1980 | limite supérieure d'accord |
| LoA width | ±5.3878 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2939 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2450 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6809 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1517 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 90.5 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 49.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.0 | 10% |

### **SCORE TOTAL : 63.5/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:35*
