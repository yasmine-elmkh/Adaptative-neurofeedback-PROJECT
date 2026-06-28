# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-13 20:33


> 🟠 **Deployment Readiness Score : 59.5/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3400 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1367 | Erreur quadratique moyenne |
| R² | 0.0171 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7160 | 0.500 |
| PR-AUC | 0.6865 | 0.521 |
| Sensitivity (TPR) | 0.5752 | 0.500 |
| Specificity (TNR) | 0.7212 | 0.500 |
| PPV (Precision) | 0.6915 | — |
| NPV | 0.6098 | — |
| Balanced Accuracy | 0.6482 | 0.500 |
| MCC | 0.2988 | 0.000 |
| G-Mean | 0.6441 | 0.500 |
| F1 macro | 0.6444 | 0.500 |
| LR+ | 2.063 | >10 = très utile |
| LR− | 0.589 | <0.1 = très utile |
| Cohen κ | 0.2942 | 0.000 |
| Brier Score | 0.2800 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7143 | [0.6465, 0.7785]  ✅ |
| F1 macro | 0.6413 | [0.5713, 0.7032]  ✅ |
| Sensitivity | 0.5732 | [0.4803, 0.6667]  — |
| Specificity | 0.7190 | [0.6262, 0.8095]  — |
| MCC | 0.2946 | [0.1581, 0.4148]  — |
| R² | 0.0084 | [-0.1962, 0.1981]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0171 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7160 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2223 | < 0.05 |
| MCE | 0.4043 | < 0.10 |
| Brier Score | 0.2800 | < 0.20 |
| Log-Loss | 1.1102 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.9415 | proche 0 = pas de biais systématique |
| LoA lower | -6.8195 | limite inférieure d'accord |
| LoA upper | +4.9365 | limite supérieure d'accord |
| LoA width | ±5.8780 | < ±2 pts : excellent |
| % dans LoA | 91.2% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0533 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0171 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7160 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3400 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 45.3 | 10% |

### **SCORE TOTAL : 59.5/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:33*
