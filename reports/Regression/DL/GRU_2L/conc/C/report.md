# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_2L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 12:09


> 🟠 **Deployment Readiness Score : 53.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4621 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0635 | Erreur quadratique moyenne |
| R² | 0.0625 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6697 | 0.500 |
| PR-AUC | 0.6276 | 0.521 |
| Sensitivity (TPR) | 0.3274 | 0.500 |
| Specificity (TNR) | 0.7981 | 0.500 |
| PPV (Precision) | 0.6379 | — |
| NPV | 0.5220 | — |
| Balanced Accuracy | 0.5628 | 0.500 |
| MCC | 0.1417 | 0.000 |
| G-Mean | 0.5112 | 0.500 |
| F1 macro | 0.5320 | 0.500 |
| LR+ | 1.622 | >10 = très utile |
| LR− | 0.843 | <0.1 = très utile |
| Cohen κ | 0.1229 | 0.000 |
| Brier Score | 0.2968 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6672 | [0.5843, 0.7447]  ✅ |
| F1 macro | 0.5300 | [0.4628, 0.5965]  — |
| Sensitivity | 0.3275 | [0.2454, 0.4091]  — |
| Specificity | 0.7955 | [0.7098, 0.8745]  — |
| MCC | 0.1388 | [0.0019, 0.2729]  — |
| R² | 0.0530 | [-0.1051, 0.2073]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0625 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6697 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2547 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2968 | < 0.20 |
| Log-Loss | 0.9770 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0118 | proche 0 = pas de biais systématique |
| LoA lower | -6.6923 | limite inférieure d'accord |
| LoA upper | +4.6687 | limite supérieure d'accord |
| LoA width | ±5.6805 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0375 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0625 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6697 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4621 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 84.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 26.4 | 10% |

### **SCORE TOTAL : 53.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:09*
