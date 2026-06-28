# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_2L`  |  **Exp :** `A`  |  **Date :** 2026-06-13 19:36


> 🟠 **Deployment Readiness Score : 53.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6346 | Erreur absolue moyenne (0-10) |
| RMSE | 3.4600 | Erreur quadratique moyenne |
| R² | -0.1959 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6598 | 0.500 |
| PR-AUC | 0.6295 | 0.521 |
| Sensitivity (TPR) | 0.5221 | 0.500 |
| Specificity (TNR) | 0.6538 | 0.500 |
| PPV (Precision) | 0.6211 | — |
| NPV | 0.5574 | — |
| Balanced Accuracy | 0.5880 | 0.500 |
| MCC | 0.1772 | 0.000 |
| G-Mean | 0.5843 | 0.500 |
| F1 macro | 0.5845 | 0.500 |
| LR+ | 1.508 | >10 = très utile |
| LR− | 0.731 | <0.1 = très utile |
| Cohen κ | 0.1748 | 0.000 |
| Brier Score | 0.3208 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6576 | [0.5836, 0.7299]  ✅ |
| F1 macro | 0.5814 | [0.5205, 0.6403]  ✅ |
| Sensitivity | 0.5205 | [0.4202, 0.6109]  — |
| Specificity | 0.6512 | [0.5583, 0.7364]  — |
| MCC | 0.1730 | [0.0492, 0.2889]  — |
| R² | -0.2085 | [-0.4497, 0.0081]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1959 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6598 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2331 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3208 | < 0.20 |
| Log-Loss | 1.3179 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3276 | proche 0 = pas de biais systématique |
| LoA lower | -7.6045 | limite inférieure d'accord |
| LoA upper | +4.9493 | limite supérieure d'accord |
| LoA width | ±6.2769 | < ±2 pts : excellent |
| % dans LoA | 93.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0189 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1959 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6598 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.6346 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 79.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 35.8 | 10% |

### **SCORE TOTAL : 53.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 19:36*
