# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 16:34


> 🟠 **Deployment Readiness Score : 59.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1653 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8187 | Erreur quadratique moyenne |
| R² | 0.2063 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7196 | 0.500 |
| PR-AUC | 0.6942 | 0.521 |
| Sensitivity (TPR) | 0.6814 | 0.500 |
| Specificity (TNR) | 0.6538 | 0.500 |
| PPV (Precision) | 0.6814 | — |
| NPV | 0.6538 | — |
| Balanced Accuracy | 0.6676 | 0.500 |
| MCC | 0.3353 | 0.000 |
| G-Mean | 0.6675 | 0.500 |
| F1 macro | 0.6676 | 0.500 |
| LR+ | 1.969 | >10 = très utile |
| LR− | 0.487 | <0.1 = très utile |
| Cohen κ | 0.3353 | 0.000 |
| Brier Score | 0.2446 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7202 | [0.6526, 0.7898]  ✅ |
| F1 macro | 0.6674 | [0.6015, 0.7291]  ✅ |
| Sensitivity | 0.6831 | [0.5991, 0.7716]  — |
| Specificity | 0.6538 | [0.5628, 0.7444]  — |
| MCC | 0.3368 | [0.2037, 0.4583]  — |
| R² | 0.2032 | [0.0557, 0.3396]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2063 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7196 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2039 | < 0.05 |
| MCE | 0.3991 | < 0.10 |
| Brier Score | 0.2446 | < 0.20 |
| Log-Loss | 0.8322 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3839 | proche 0 = pas de biais systématique |
| LoA lower | -5.8698 | limite inférieure d'accord |
| LoA upper | +5.1020 | limite supérieure d'accord |
| LoA width | ±5.4859 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1892 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2063 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7196 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1653 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 41.9 | 10% |

### **SCORE TOTAL : 59.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 16:34*
