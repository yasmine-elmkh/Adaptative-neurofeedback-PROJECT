# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `TCN`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 23:22


> 🟠 **Deployment Readiness Score : 58.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4217 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8704 | Erreur quadratique moyenne |
| R² | 0.1769 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7212 | 0.500 |
| PR-AUC | 0.7223 | 0.521 |
| Sensitivity (TPR) | 0.3982 | 0.500 |
| Specificity (TNR) | 0.8558 | 0.500 |
| PPV (Precision) | 0.7500 | — |
| NPV | 0.5669 | — |
| Balanced Accuracy | 0.6270 | 0.500 |
| MCC | 0.2837 | 0.000 |
| G-Mean | 0.5838 | 0.500 |
| F1 macro | 0.6011 | 0.500 |
| LR+ | 2.761 | >10 = très utile |
| LR− | 0.703 | <0.1 = très utile |
| Cohen κ | 0.2489 | 0.000 |
| Brier Score | 0.2769 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7199 | [0.6475, 0.7889]  ✅ |
| F1 macro | 0.5999 | [0.5341, 0.6668]  ✅ |
| Sensitivity | 0.3993 | [0.3102, 0.4891]  — |
| Specificity | 0.8533 | [0.7788, 0.9242]  — |
| MCC | 0.2815 | [0.1564, 0.4106]  — |
| R² | 0.1720 | [0.0487, 0.2796]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1769 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7212 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2249 | < 0.05 |
| MCE | 0.4770 | < 0.10 |
| Brier Score | 0.2769 | < 0.20 |
| Log-Loss | 0.8515 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6093 | proche 0 = pas de biais systématique |
| LoA lower | -6.1197 | limite inférieure d'accord |
| LoA upper | +4.9012 | limite supérieure d'accord |
| LoA width | ±5.5105 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0744 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1769 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7212 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4217 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 39.0 | 10% |

### **SCORE TOTAL : 58.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 23:22*
