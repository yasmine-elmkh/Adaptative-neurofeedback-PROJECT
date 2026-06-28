# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-14 10:13


> 🟡 **Deployment Readiness Score : 66.0/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1898 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7821 | Erreur quadratique moyenne |
| R² | 0.2267 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7241 | 0.500 |
| PR-AUC | 0.6968 | 0.521 |
| Sensitivity (TPR) | 0.6637 | 0.500 |
| Specificity (TNR) | 0.6538 | 0.500 |
| PPV (Precision) | 0.6757 | — |
| NPV | 0.6415 | — |
| Balanced Accuracy | 0.6588 | 0.500 |
| MCC | 0.3174 | 0.000 |
| G-Mean | 0.6588 | 0.500 |
| F1 macro | 0.6586 | 0.500 |
| LR+ | 1.917 | >10 = très utile |
| LR− | 0.514 | <0.1 = très utile |
| Cohen κ | 0.3173 | 0.000 |
| Brier Score | 0.2427 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7240 | [0.6532, 0.7891]  ✅ |
| F1 macro | 0.6580 | [0.5941, 0.7202]  ✅ |
| Sensitivity | 0.6627 | [0.5771, 0.7412]  — |
| Specificity | 0.6555 | [0.5685, 0.7469]  — |
| MCC | 0.3180 | [0.1902, 0.4408]  — |
| R² | 0.2208 | [0.0818, 0.3384]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2267 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7241 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1333 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2427 | < 0.20 |
| Log-Loss | 0.8009 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4977 | proche 0 = pas de biais systématique |
| LoA lower | -5.8751 | limite inférieure d'accord |
| LoA upper | +4.8797 | limite supérieure d'accord |
| LoA width | ±5.3774 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1379 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2267 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7241 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1898 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 44.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 42.8 | 10% |

### **SCORE TOTAL : 66.0/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:13*
