# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 04:30


> 🟠 **Deployment Readiness Score : 56.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4080 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0948 | Erreur quadratique moyenne |
| R² | 0.0432 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6863 | 0.500 |
| PR-AUC | 0.6745 | 0.521 |
| Sensitivity (TPR) | 0.4336 | 0.500 |
| Specificity (TNR) | 0.7308 | 0.500 |
| PPV (Precision) | 0.6364 | — |
| NPV | 0.5429 | — |
| Balanced Accuracy | 0.5822 | 0.500 |
| MCC | 0.1716 | 0.000 |
| G-Mean | 0.5629 | 0.500 |
| F1 macro | 0.5694 | 0.500 |
| LR+ | 1.611 | >10 = très utile |
| LR− | 0.775 | <0.1 = très utile |
| Cohen κ | 0.1622 | 0.000 |
| Brier Score | 0.2887 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6869 | [0.6098, 0.7553]  ✅ |
| F1 macro | 0.5677 | [0.5012, 0.6320]  ✅ |
| Sensitivity | 0.4315 | [0.3495, 0.5211]  — |
| Specificity | 0.7319 | [0.6481, 0.8178]  — |
| MCC | 0.1708 | [0.0419, 0.2965]  — |
| R² | 0.0402 | [-0.1301, 0.1956]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0432 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6863 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2328 | < 0.05 |
| MCE | 0.5182 | < 0.10 |
| Brier Score | 0.2887 | < 0.20 |
| Log-Loss | 1.0484 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.9646 | proche 0 = pas de biais systématique |
| LoA lower | -6.7416 | limite inférieure d'accord |
| LoA upper | +4.8124 | limite supérieure d'accord |
| LoA width | ±5.7770 | < ±2 pts : excellent |
| % dans LoA | 94.5% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0456 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0432 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6863 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4080 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 93.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 36.3 | 10% |

### **SCORE TOTAL : 56.9/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 04:30*
