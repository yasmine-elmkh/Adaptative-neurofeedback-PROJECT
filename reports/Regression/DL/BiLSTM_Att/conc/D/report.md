# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-13 20:55


> 🟠 **Deployment Readiness Score : 57.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3275 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0196 | Erreur quadratique moyenne |
| R² | 0.0891 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6941 | 0.500 |
| PR-AUC | 0.6692 | 0.521 |
| Sensitivity (TPR) | 0.5133 | 0.500 |
| Specificity (TNR) | 0.7500 | 0.500 |
| PPV (Precision) | 0.6905 | — |
| NPV | 0.5865 | — |
| Balanced Accuracy | 0.6316 | 0.500 |
| MCC | 0.2700 | 0.000 |
| G-Mean | 0.6204 | 0.500 |
| F1 macro | 0.6235 | 0.500 |
| LR+ | 2.053 | >10 = très utile |
| LR− | 0.649 | <0.1 = très utile |
| Cohen κ | 0.2604 | 0.000 |
| Brier Score | 0.3007 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6937 | [0.6135, 0.7630]  ✅ |
| F1 macro | 0.6225 | [0.5567, 0.6849]  ✅ |
| Sensitivity | 0.5132 | [0.4173, 0.6064]  — |
| Specificity | 0.7500 | [0.6608, 0.8333]  — |
| MCC | 0.2700 | [0.1311, 0.3944]  — |
| R² | 0.0817 | [-0.0903, 0.2307]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0891 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6941 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2777 | < 0.05 |
| MCE | 0.4763 | < 0.10 |
| Brier Score | 0.3007 | < 0.20 |
| Log-Loss | 1.0657 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.9324 | proche 0 = pas de biais systématique |
| LoA lower | -6.5747 | limite inférieure d'accord |
| LoA upper | +4.7099 | limite supérieure d'accord |
| LoA width | ±5.6423 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0547 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0891 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6941 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3275 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 97.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 33.7 | 10% |

### **SCORE TOTAL : 57.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:55*
