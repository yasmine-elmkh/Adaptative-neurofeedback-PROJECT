# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN1D`  |  **Exp :** `A`  |  **Date :** 2026-06-12 17:51


> 🟠 **Deployment Readiness Score : 58.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3501 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9609 | Erreur quadratique moyenne |
| R² | 0.1242 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6934 | 0.500 |
| PR-AUC | 0.6572 | 0.521 |
| Sensitivity (TPR) | 0.2920 | 0.500 |
| Specificity (TNR) | 0.8558 | 0.500 |
| PPV (Precision) | 0.6875 | — |
| NPV | 0.5266 | — |
| Balanced Accuracy | 0.5739 | 0.500 |
| MCC | 0.1779 | 0.000 |
| G-Mean | 0.4999 | 0.500 |
| F1 macro | 0.5310 | 0.500 |
| LR+ | 2.025 | >10 = très utile |
| LR− | 0.827 | <0.1 = très utile |
| Cohen κ | 0.1442 | 0.000 |
| Brier Score | 0.3133 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6942 | [0.6254, 0.7613]  ✅ |
| F1 macro | 0.5312 | [0.4700, 0.5997]  — |
| Sensitivity | 0.2936 | [0.2127, 0.3860]  — |
| Specificity | 0.8557 | [0.7885, 0.9191]  — |
| MCC | 0.1794 | [0.0598, 0.2963]  — |
| R² | 0.1207 | [-0.0162, 0.2508]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1242 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6934 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2826 | < 0.05 |
| MCE | 0.4251 | < 0.10 |
| Brier Score | 0.3133 | < 0.20 |
| Log-Loss | 0.9590 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.9688 | proche 0 = pas de biais systématique |
| LoA lower | -6.4655 | limite inférieure d'accord |
| LoA upper | +4.5278 | limite supérieure d'accord |
| LoA width | ±5.4966 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0391 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1242 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6934 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3501 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 96.7 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 42.7 | 10% |

### **SCORE TOTAL : 58.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 17:51*
