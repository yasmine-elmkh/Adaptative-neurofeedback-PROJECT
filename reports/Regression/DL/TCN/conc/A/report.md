# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `TCN`  |  **Exp :** `A`  |  **Date :** 2026-06-13 19:50


> 🟠 **Deployment Readiness Score : 58.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3671 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9336 | Erreur quadratique moyenne |
| R² | 0.1403 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7034 | 0.500 |
| PR-AUC | 0.6554 | 0.521 |
| Sensitivity (TPR) | 0.3805 | 0.500 |
| Specificity (TNR) | 0.7885 | 0.500 |
| PPV (Precision) | 0.6615 | — |
| NPV | 0.5395 | — |
| Balanced Accuracy | 0.5845 | 0.500 |
| MCC | 0.1843 | 0.000 |
| G-Mean | 0.5478 | 0.500 |
| F1 macro | 0.5619 | 0.500 |
| LR+ | 1.799 | >10 = très utile |
| LR− | 0.786 | <0.1 = très utile |
| Cohen κ | 0.1659 | 0.000 |
| Brier Score | 0.2950 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7023 | [0.6268, 0.7692]  ✅ |
| F1 macro | 0.5606 | [0.4930, 0.6272]  — |
| Sensitivity | 0.3805 | [0.2968, 0.4687]  — |
| Specificity | 0.7875 | [0.7072, 0.8715]  — |
| MCC | 0.1831 | [0.0430, 0.3005]  — |
| R² | 0.1347 | [-0.0146, 0.2758]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1403 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7034 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2495 | < 0.05 |
| MCE | 0.6556 | < 0.10 |
| Brier Score | 0.2950 | < 0.20 |
| Log-Loss | 0.9586 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7503 | proche 0 = pas de biais systématique |
| LoA lower | -6.3217 | limite inférieure d'accord |
| LoA upper | +4.8211 | limite supérieure d'accord |
| LoA width | ±5.5714 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0668 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1403 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7034 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3671 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 38.4 | 10% |

### **SCORE TOTAL : 58.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 19:50*
