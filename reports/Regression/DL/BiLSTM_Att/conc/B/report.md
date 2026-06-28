# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-13 20:02


> 🟠 **Deployment Readiness Score : 59.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4018 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2127 | Erreur quadratique moyenne |
| R² | -0.0311 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7058 | 0.500 |
| PR-AUC | 0.6766 | 0.521 |
| Sensitivity (TPR) | 0.5575 | 0.500 |
| Specificity (TNR) | 0.6827 | 0.500 |
| PPV (Precision) | 0.6562 | — |
| NPV | 0.5868 | — |
| Balanced Accuracy | 0.6201 | 0.500 |
| MCC | 0.2416 | 0.000 |
| G-Mean | 0.6169 | 0.500 |
| F1 macro | 0.6170 | 0.500 |
| LR+ | 1.757 | >10 = très utile |
| LR− | 0.648 | <0.1 = très utile |
| Cohen κ | 0.2387 | 0.000 |
| Brier Score | 0.2952 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7047 | [0.6308, 0.7680]  ✅ |
| F1 macro | 0.6144 | [0.5412, 0.6806]  ✅ |
| Sensitivity | 0.5567 | [0.4623, 0.6502]  — |
| Specificity | 0.6802 | [0.5922, 0.7784]  — |
| MCC | 0.2383 | [0.0951, 0.3698]  — |
| R² | -0.0403 | [-0.2670, 0.1538]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0311 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7058 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2209 | < 0.05 |
| MCE | 0.9012 | < 0.10 |
| Brier Score | 0.2952 | < 0.20 |
| Log-Loss | 1.2045 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.1706 | proche 0 = pas de biais systématique |
| LoA lower | -7.0481 | limite inférieure d'accord |
| LoA upper | +4.7070 | limite supérieure d'accord |
| LoA width | ±5.8776 | < ±2 pts : excellent |
| % dans LoA | 92.6% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0359 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0311 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7058 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4018 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 41.9 | 10% |

### **SCORE TOTAL : 59.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:02*
