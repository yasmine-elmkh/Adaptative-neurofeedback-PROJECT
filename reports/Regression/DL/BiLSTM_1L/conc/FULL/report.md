# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_1L`  |  **Exp :** `FULL`  |  **Date :** 2026-06-13 20:54


> 🟠 **Deployment Readiness Score : 58.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1646 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9484 | Erreur quadratique moyenne |
| R² | 0.1316 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7271 | 0.500 |
| PR-AUC | 0.6848 | 0.521 |
| Sensitivity (TPR) | 0.7699 | 0.500 |
| Specificity (TNR) | 0.6346 | 0.500 |
| PPV (Precision) | 0.6960 | — |
| NPV | 0.7174 | — |
| Balanced Accuracy | 0.7023 | 0.500 |
| MCC | 0.4089 | 0.000 |
| G-Mean | 0.6990 | 0.500 |
| F1 macro | 0.7023 | 0.500 |
| LR+ | 2.107 | >10 = très utile |
| LR− | 0.363 | <0.1 = très utile |
| Cohen κ | 0.4064 | 0.000 |
| Brier Score | 0.2462 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7284 | [0.6543, 0.7994]  ✅ |
| F1 macro | 0.7008 | [0.6409, 0.7623]  ✅ |
| Sensitivity | 0.7684 | [0.6884, 0.8530]  — |
| Specificity | 0.6353 | [0.5394, 0.7306]  — |
| MCC | 0.4080 | [0.2874, 0.5286]  — |
| R² | 0.1264 | [-0.0675, 0.3161]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1316 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7271 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2132 | < 0.05 |
| MCE | 0.3438 | < 0.10 |
| Brier Score | 0.2462 | < 0.20 |
| Log-Loss | 0.9219 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1552 | proche 0 = pas de biais systématique |
| LoA lower | -5.9393 | limite inférieure d'accord |
| LoA upper | +5.6289 | limite supérieure d'accord |
| LoA width | ±5.7841 | < ±2 pts : excellent |
| % dans LoA | 92.2% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.3331 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1316 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7271 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.1646 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 36.6 | 10% |

### **SCORE TOTAL : 58.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:54*
