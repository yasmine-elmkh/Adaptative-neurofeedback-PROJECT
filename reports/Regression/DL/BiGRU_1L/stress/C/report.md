# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 18:03


> 🔴 **Deployment Readiness Score : 32.8/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4097 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8355 | Erreur quadratique moyenne |
| R² | -0.0252 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5628 | 0.500 |
| PR-AUC | 0.4121 | 0.366 |
| Sensitivity (TPR) | 0.0506 | 0.500 |
| Specificity (TNR) | 0.9526 | 0.500 |
| PPV (Precision) | 0.3810 | — |
| NPV | 0.6350 | — |
| Balanced Accuracy | 0.5016 | 0.500 |
| MCC | 0.0071 | 0.000 |
| G-Mean | 0.2196 | 0.500 |
| F1 macro | 0.4257 | 0.500 |
| LR+ | 1.067 | >10 = très utile |
| LR− | 0.997 | <0.1 = très utile |
| Cohen κ | 0.0039 | 0.000 |
| Brier Score | 0.2767 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5611 | [0.5055, 0.6155]  ✅ |
| F1 macro | 0.4263 | [0.3938, 0.4645]  — |
| Sensitivity | 0.0513 | [0.0201, 0.0868]  — |
| Specificity | 0.9524 | [0.9274, 0.9736]  — |
| MCC | 0.0078 | [-0.0809, 0.0960]  — |
| R² | -0.0279 | [-0.0845, 0.0293]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0252 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.5628 | p=0.0180 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2086 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2767 | < 0.20 |
| Log-Loss | 0.8523 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4024 | proche 0 = pas de biais systématique |
| LoA lower | -5.9102 | limite inférieure d'accord |
| LoA upper | +5.1053 | limite supérieure d'accord |
| LoA width | ±5.5077 | < ±2 pts : excellent |
| % dans LoA | 98.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0126 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0252 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5628 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4097 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 31.4 | 25% |
| Significativité (p-value) | 26.1 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.0 | 10% |

### **SCORE TOTAL : 32.8/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 18:03*
