# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-14 10:18


> 🟠 **Deployment Readiness Score : 49.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7941 | Erreur absolue moyenne (0-10) |
| RMSE | 3.5635 | Erreur quadratique moyenne |
| R² | -0.2686 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6286 | 0.500 |
| PR-AUC | 0.6061 | 0.521 |
| Sensitivity (TPR) | 0.0796 | 0.500 |
| Specificity (TNR) | 0.9519 | 0.500 |
| PPV (Precision) | 0.6429 | — |
| NPV | 0.4877 | — |
| Balanced Accuracy | 0.5158 | 0.500 |
| MCC | 0.0642 | 0.000 |
| G-Mean | 0.2753 | 0.500 |
| F1 macro | 0.3933 | 0.500 |
| LR+ | 1.657 | >10 = très utile |
| LR− | 0.967 | <0.1 = très utile |
| Cohen κ | 0.0304 | 0.000 |
| Brier Score | 0.3879 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6281 | [0.5564, 0.7026]  ✅ |
| F1 macro | 0.3949 | [0.3381, 0.4533]  — |
| Sensitivity | 0.0815 | [0.0349, 0.1409]  — |
| Specificity | 0.9530 | [0.9078, 0.9902]  — |
| MCC | 0.0694 | [-0.0631, 0.1930]  — |
| R² | -0.2783 | [-0.5106, -0.0725]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2686 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6286 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3606 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3879 | < 0.20 |
| Log-Loss | 1.5762 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.7871 | proche 0 = pas de biais systématique |
| LoA lower | -7.8436 | limite inférieure d'accord |
| LoA upper | +4.2693 | limite supérieure d'accord |
| LoA width | ±6.0565 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0095 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2686 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6286 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.7941 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 64.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.9 | 10% |

### **SCORE TOTAL : 49.7/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:18*
