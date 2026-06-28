# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_2L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 20:54


> 🟠 **Deployment Readiness Score : 59.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1956 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7660 | Erreur quadratique moyenne |
| R² | 0.2357 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6696 | 0.500 |
| PR-AUC | 0.6295 | 0.521 |
| Sensitivity (TPR) | 0.7168 | 0.500 |
| Specificity (TNR) | 0.5481 | 0.500 |
| PPV (Precision) | 0.6328 | — |
| NPV | 0.6404 | — |
| Balanced Accuracy | 0.6324 | 0.500 |
| MCC | 0.2690 | 0.000 |
| G-Mean | 0.6268 | 0.500 |
| F1 macro | 0.6314 | 0.500 |
| LR+ | 1.586 | >10 = très utile |
| LR− | 0.517 | <0.1 = très utile |
| Cohen κ | 0.2664 | 0.000 |
| Brier Score | 0.2462 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6683 | [0.5780, 0.7337]  ✅ |
| F1 macro | 0.6280 | [0.5605, 0.6918]  ✅ |
| Sensitivity | 0.7157 | [0.6310, 0.8009]  — |
| Specificity | 0.5449 | [0.4411, 0.6402]  — |
| MCC | 0.2648 | [0.1296, 0.3912]  — |
| R² | 0.2304 | [0.1196, 0.3393]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2357 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6696 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1467 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2462 | < 0.20 |
| Log-Loss | 0.7350 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4028 | proche 0 = pas de biais systématique |
| LoA lower | -5.7788 | limite inférieure d'accord |
| LoA upper | +4.9732 | limite supérieure d'accord |
| LoA width | ±5.3760 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1744 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2357 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6696 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1956 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 84.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 35.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 29.5 | 10% |

### **SCORE TOTAL : 59.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:54*
