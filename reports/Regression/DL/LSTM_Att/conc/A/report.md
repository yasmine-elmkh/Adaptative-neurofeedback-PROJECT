# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `A`  |  **Date :** 2026-06-14 10:01


> 🟠 **Deployment Readiness Score : 54.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4947 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1143 | Erreur quadratique moyenne |
| R² | 0.0311 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6657 | 0.500 |
| PR-AUC | 0.6462 | 0.521 |
| Sensitivity (TPR) | 0.0354 | 0.500 |
| Specificity (TNR) | 0.9712 | 0.500 |
| PPV (Precision) | 0.5714 | — |
| NPV | 0.4810 | — |
| Balanced Accuracy | 0.5033 | 0.500 |
| MCC | 0.0185 | 0.000 |
| G-Mean | 0.1854 | 0.500 |
| F1 macro | 0.3550 | 0.500 |
| LR+ | 1.227 | >10 = très utile |
| LR− | 0.993 | <0.1 = très utile |
| Cohen κ | 0.0063 | 0.000 |
| Brier Score | 0.3458 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6652 | [0.5921, 0.7340]  ✅ |
| F1 macro | 0.3542 | [0.3122, 0.4048]  — |
| Sensitivity | 0.0347 | [0.0084, 0.0755]  — |
| Specificity | 0.9714 | [0.9353, 1.0000]  — |
| MCC | 0.0165 | [-0.1104, 0.1453]  — |
| R² | 0.0226 | [-0.1369, 0.1631]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0311 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6657 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3286 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3458 | < 0.20 |
| Log-Loss | 1.1589 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3526 | proche 0 = pas de biais systématique |
| LoA lower | -6.8636 | limite inférieure d'accord |
| LoA upper | +4.1585 | limite supérieure d'accord |
| LoA width | ±5.5111 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0210 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0311 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6657 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4947 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 82.8 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.7 | 10% |

### **SCORE TOTAL : 54.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:01*
