# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN1D`  |  **Exp :** `FULL`  |  **Date :** 2026-06-12 20:31


> 🟠 **Deployment Readiness Score : 59.3/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1115 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7288 | Erreur quadratique moyenne |
| R² | 0.2561 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7520 | 0.500 |
| PR-AUC | 0.7095 | 0.521 |
| Sensitivity (TPR) | 0.6283 | 0.500 |
| Specificity (TNR) | 0.7308 | 0.500 |
| PPV (Precision) | 0.7172 | — |
| NPV | 0.6441 | — |
| Balanced Accuracy | 0.6795 | 0.500 |
| MCC | 0.3602 | 0.000 |
| G-Mean | 0.6776 | 0.500 |
| F1 macro | 0.6772 | 0.500 |
| LR+ | 2.334 | >10 = très utile |
| LR− | 0.509 | <0.1 = très utile |
| Cohen κ | 0.3572 | 0.000 |
| Brier Score | 0.2426 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7519 | [0.6818, 0.8168]  ✅ |
| F1 macro | 0.6773 | [0.6123, 0.7411]  ✅ |
| Sensitivity | 0.6307 | [0.5422, 0.7236]  — |
| Specificity | 0.7301 | [0.6328, 0.8093]  — |
| MCC | 0.3617 | [0.2327, 0.4845]  — |
| R² | 0.2522 | [0.0932, 0.3891]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2561 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7520 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2169 | < 0.05 |
| MCE | 0.4743 | < 0.10 |
| Brier Score | 0.2426 | < 0.20 |
| Log-Loss | 0.8275 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.2185 | proche 0 = pas de biais systématique |
| LoA lower | -5.5621 | limite inférieure d'accord |
| LoA upper | +5.1250 | limite supérieure d'accord |
| LoA width | ±5.3436 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.3220 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2561 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7520 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1115 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 43.3 | 10% |

### **SCORE TOTAL : 59.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 20:31*
