# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 11:27


> 🔴 **Deployment Readiness Score : 38.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3742 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9150 | Erreur quadratique moyenne |
| R² | 0.1143 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6555 | 0.500 |
| PR-AUC | 0.6121 | 0.515 |
| Sensitivity (TPR) | 0.6385 | 0.500 |
| Specificity (TNR) | 0.5812 | 0.500 |
| PPV (Precision) | 0.6182 | — |
| NPV | 0.6021 | — |
| Balanced Accuracy | 0.6098 | 0.500 |
| MCC | 0.2200 | 0.000 |
| G-Mean | 0.6091 | 0.500 |
| F1 macro | 0.6098 | 0.500 |
| LR+ | 1.524 | >10 = très utile |
| LR− | 0.622 | <0.1 = très utile |
| Cohen κ | 0.2199 | 0.000 |
| Brier Score | 0.2741 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6548 | [0.6258, 0.6833]  ✅ |
| F1 macro | 0.6088 | [0.5832, 0.6338]  ✅ |
| Sensitivity | 0.6372 | [0.6005, 0.6714]  — |
| Specificity | 0.5808 | [0.5456, 0.6172]  — |
| MCC | 0.2183 | [0.1671, 0.2685]  — |
| R² | 0.1116 | [0.0541, 0.1688]  ✅ |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1849 | < 0.05 |
| MCE | 0.4243 | < 0.10 |
| Brier Score | 0.2741 | < 0.20 |
| Log-Loss | 0.9353 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0324 | proche 0 = pas de biais systématique |
| LoA lower | -5.7474 | limite inférieure d'accord |
| LoA upper | +5.6826 | limite supérieure d'accord |
| LoA width | ±5.7150 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2596 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0902 | 0.1826 | 202.4% | 🔴 unstable |
| AUC ROC | 0.6436 | 0.0837 | 13.0% | 🟢 stable |
| MAE | 2.3623 | 0.2712 | 11.5% | 🟢 stable |

**Stability Score global : 58.5/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 77.8 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 10.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 95.0 | 10% |

### **SCORE TOTAL : 38.0/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 11:27*
