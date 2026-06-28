# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN2D`  |  **Exp :** `B`  |  **Date :** 2026-06-12 18:30


> 🟠 **Deployment Readiness Score : 56.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2162 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6541 | Erreur quadratique moyenne |
| R² | 0.2963 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6705 | 0.500 |
| PR-AUC | 0.6508 | 0.521 |
| Sensitivity (TPR) | 0.6991 | 0.500 |
| Specificity (TNR) | 0.4808 | 0.500 |
| PPV (Precision) | 0.5940 | — |
| NPV | 0.5952 | — |
| Balanced Accuracy | 0.5899 | 0.500 |
| MCC | 0.1845 | 0.000 |
| G-Mean | 0.5798 | 0.500 |
| F1 macro | 0.5871 | 0.500 |
| LR+ | 1.346 | >10 = très utile |
| LR− | 0.626 | <0.1 = très utile |
| Cohen κ | 0.1813 | 0.000 |
| Brier Score | 0.2472 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6699 | [0.6010, 0.7354]  ✅ |
| F1 macro | 0.5864 | [0.5205, 0.6477]  ✅ |
| Sensitivity | 0.7030 | [0.6122, 0.7911]  — |
| Specificity | 0.4783 | [0.3889, 0.5641]  — |
| MCC | 0.1862 | [0.0555, 0.3113]  — |
| R² | 0.2910 | [0.1971, 0.3891]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2963 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6705 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1880 | < 0.05 |
| MCE | 0.4263 | < 0.10 |
| Brier Score | 0.2472 | < 0.20 |
| Log-Loss | 0.7067 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2777 | proche 0 = pas de biais systématique |
| LoA lower | -4.9077 | limite inférieure d'accord |
| LoA upper | +5.4631 | limite supérieure d'accord |
| LoA width | ±5.1854 | < ±2 pts : excellent |
| % dans LoA | 99.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2408 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2963 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6705 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2162 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 85.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 8.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.7 | 10% |

### **SCORE TOTAL : 56.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 18:30*
