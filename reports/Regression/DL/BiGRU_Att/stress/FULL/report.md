# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 17:42


> 🟠 **Deployment Readiness Score : 44.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3876 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7606 | Erreur quadratique moyenne |
| R² | 0.0282 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5703 | 0.500 |
| PR-AUC | 0.3857 | 0.366 |
| Sensitivity (TPR) | 0.0316 | 0.500 |
| Specificity (TNR) | 0.9343 | 0.500 |
| PPV (Precision) | 0.2174 | — |
| NPV | 0.6259 | — |
| Balanced Accuracy | 0.4830 | 0.500 |
| MCC | -0.0730 | 0.000 |
| G-Mean | 0.1719 | 0.500 |
| F1 macro | 0.4024 | 0.500 |
| LR+ | 0.482 | >10 = très utile |
| LR− | 1.036 | <0.1 = très utile |
| Cohen κ | -0.0416 | 0.000 |
| Brier Score | 0.2432 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5687 | [0.5163, 0.6189]  ✅ |
| F1 macro | 0.4026 | [0.3711, 0.4353]  — |
| Sensitivity | 0.0321 | [0.0066, 0.0618]  — |
| Specificity | 0.9332 | [0.9023, 0.9591]  — |
| MCC | -0.0737 | [-0.1517, 0.0074]  — |
| R² | 0.0249 | [-0.0113, 0.0627]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0282 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5703 | p=0.0060 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1395 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2432 | < 0.20 |
| Log-Loss | 0.6888 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1292 | proche 0 = pas de biais systématique |
| LoA lower | -5.2819 | limite inférieure d'accord |
| LoA upper | +5.5403 | limite supérieure d'accord |
| LoA width | ±5.4111 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0354 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0282 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5703 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3876 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 35.1 | 25% |
| Significativité (p-value) | 54.2 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 40.3 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 65.0 | 10% |

### **SCORE TOTAL : 44.5/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 17:42*
