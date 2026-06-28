# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_2L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 10:23


> 🟠 **Deployment Readiness Score : 55.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3945 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0728 | Erreur quadratique moyenne |
| R² | 0.0568 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6762 | 0.500 |
| PR-AUC | 0.6424 | 0.521 |
| Sensitivity (TPR) | 0.3097 | 0.500 |
| Specificity (TNR) | 0.7692 | 0.500 |
| PPV (Precision) | 0.5932 | — |
| NPV | 0.5063 | — |
| Balanced Accuracy | 0.5395 | 0.500 |
| MCC | 0.0887 | 0.000 |
| G-Mean | 0.4881 | 0.500 |
| F1 macro | 0.5088 | 0.500 |
| LR+ | 1.342 | >10 = très utile |
| LR− | 0.897 | <0.1 = très utile |
| Cohen κ | 0.0774 | 0.000 |
| Brier Score | 0.3168 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6758 | [0.6016, 0.7475]  ✅ |
| F1 macro | 0.5066 | [0.4428, 0.5697]  — |
| Sensitivity | 0.3090 | [0.2318, 0.3934]  — |
| Specificity | 0.7672 | [0.6827, 0.8470]  — |
| MCC | 0.0856 | [-0.0600, 0.2119]  — |
| R² | 0.0519 | [-0.1218, 0.1951]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0568 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6762 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2821 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3168 | < 0.20 |
| Log-Loss | 1.1014 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.1085 | proche 0 = pas de biais systématique |
| LoA lower | -6.7386 | limite inférieure d'accord |
| LoA upper | +4.5216 | limite supérieure d'accord |
| LoA width | ±5.6301 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0355 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0568 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6762 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3945 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 88.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.1 | 10% |

### **SCORE TOTAL : 55.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 10:23*
