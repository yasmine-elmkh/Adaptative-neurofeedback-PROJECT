# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-14 02:37


> 🟡 **Deployment Readiness Score : 60.8/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3160 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9339 | Erreur quadratique moyenne |
| R² | 0.1401 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6906 | 0.500 |
| PR-AUC | 0.6435 | 0.521 |
| Sensitivity (TPR) | 0.5310 | 0.500 |
| Specificity (TNR) | 0.6923 | 0.500 |
| PPV (Precision) | 0.6522 | — |
| NPV | 0.5760 | — |
| Balanced Accuracy | 0.6116 | 0.500 |
| MCC | 0.2257 | 0.000 |
| G-Mean | 0.6063 | 0.500 |
| F1 macro | 0.6071 | 0.500 |
| LR+ | 1.726 | >10 = très utile |
| LR− | 0.677 | <0.1 = très utile |
| Cohen κ | 0.2215 | 0.000 |
| Brier Score | 0.2562 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6897 | [0.6129, 0.7579]  ✅ |
| F1 macro | 0.6048 | [0.5424, 0.6635]  ✅ |
| Sensitivity | 0.5307 | [0.4416, 0.6215]  — |
| Specificity | 0.6900 | [0.5948, 0.7789]  — |
| MCC | 0.2230 | [0.0959, 0.3374]  — |
| R² | 0.1354 | [-0.0259, 0.2753]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1401 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6906 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1669 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2562 | < 0.20 |
| Log-Loss | 0.8520 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6617 | proche 0 = pas de biais systématique |
| LoA lower | -6.2770 | limite inférieure d'accord |
| LoA upper | +4.9537 | limite supérieure d'accord |
| LoA width | ±5.6154 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0786 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1401 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6906 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3160 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 95.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 22.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.7 | 10% |

### **SCORE TOTAL : 60.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 02:37*
