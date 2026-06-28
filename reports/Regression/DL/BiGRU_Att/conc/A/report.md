# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-13 12:22


> 🟠 **Deployment Readiness Score : 59.3/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2580 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0085 | Erreur quadratique moyenne |
| R² | 0.0958 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7183 | 0.500 |
| PR-AUC | 0.6840 | 0.521 |
| Sensitivity (TPR) | 0.5044 | 0.500 |
| Specificity (TNR) | 0.7692 | 0.500 |
| PPV (Precision) | 0.7037 | — |
| NPV | 0.5882 | — |
| Balanced Accuracy | 0.6368 | 0.500 |
| MCC | 0.2826 | 0.000 |
| G-Mean | 0.6229 | 0.500 |
| F1 macro | 0.6271 | 0.500 |
| LR+ | 2.186 | >10 = très utile |
| LR− | 0.644 | <0.1 = très utile |
| Cohen κ | 0.2703 | 0.000 |
| Brier Score | 0.2802 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7180 | [0.6481, 0.7835]  ✅ |
| F1 macro | 0.6267 | [0.5609, 0.6973]  ✅ |
| Sensitivity | 0.5048 | [0.4019, 0.6021]  — |
| Specificity | 0.7699 | [0.6915, 0.8493]  — |
| MCC | 0.2837 | [0.1488, 0.4104]  — |
| R² | 0.0878 | [-0.1117, 0.2536]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0958 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7183 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2237 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2802 | < 0.20 |
| Log-Loss | 1.0421 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0560 | proche 0 = pas de biais systématique |
| LoA lower | -6.5903 | limite inférieure d'accord |
| LoA upper | +4.4783 | limite supérieure d'accord |
| LoA width | ±5.5343 | < ±2 pts : excellent |
| % dans LoA | 92.6% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0458 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0958 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7183 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2580 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 43.0 | 10% |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:22*
