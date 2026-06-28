# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-14 10:08


> 🟠 **Deployment Readiness Score : 57.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2188 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8338 | Erreur quadratique moyenne |
| R² | 0.1978 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6914 | 0.500 |
| PR-AUC | 0.6757 | 0.521 |
| Sensitivity (TPR) | 0.6637 | 0.500 |
| Specificity (TNR) | 0.5962 | 0.500 |
| PPV (Precision) | 0.6410 | — |
| NPV | 0.6200 | — |
| Balanced Accuracy | 0.6299 | 0.500 |
| MCC | 0.2604 | 0.000 |
| G-Mean | 0.6290 | 0.500 |
| F1 macro | 0.6300 | 0.500 |
| LR+ | 1.643 | >10 = très utile |
| LR− | 0.564 | <0.1 = très utile |
| Cohen κ | 0.2603 | 0.000 |
| Brier Score | 0.2638 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6913 | [0.6183, 0.7621]  ✅ |
| F1 macro | 0.6274 | [0.5614, 0.6903]  ✅ |
| Sensitivity | 0.6625 | [0.5763, 0.7500]  — |
| Specificity | 0.5942 | [0.5000, 0.6847]  — |
| MCC | 0.2573 | [0.1327, 0.3836]  — |
| R² | 0.1912 | [0.0471, 0.3132]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1978 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6914 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2069 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2638 | < 0.20 |
| Log-Loss | 0.8411 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4290 | proche 0 = pas de biais systématique |
| LoA lower | -5.9319 | limite inférieure d'accord |
| LoA upper | +5.0739 | limite supérieure d'accord |
| LoA width | ±5.5029 | < ±2 pts : excellent |
| % dans LoA | 92.6% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1646 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1978 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6914 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2188 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 95.7 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.4 | 10% |

### **SCORE TOTAL : 57.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:08*
