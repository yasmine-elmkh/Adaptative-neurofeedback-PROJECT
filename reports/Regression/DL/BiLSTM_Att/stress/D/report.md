# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-14 01:39


> 🟠 **Deployment Readiness Score : 40.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3936 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7651 | Erreur quadratique moyenne |
| R² | 0.0251 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5599 | 0.500 |
| PR-AUC | 0.4151 | 0.366 |
| Sensitivity (TPR) | 0.0380 | 0.500 |
| Specificity (TNR) | 0.9927 | 0.500 |
| PPV (Precision) | 0.7500 | — |
| NPV | 0.6415 | — |
| Balanced Accuracy | 0.5153 | 0.500 |
| MCC | 0.1096 | 0.000 |
| G-Mean | 0.1942 | 0.500 |
| F1 macro | 0.4258 | 0.500 |
| LR+ | 5.203 | >10 = très utile |
| LR− | 0.969 | <0.1 = très utile |
| Cohen κ | 0.0384 | 0.000 |
| Brier Score | 0.2435 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5579 | [0.5039, 0.6093]  ✅ |
| F1 macro | 0.4265 | [0.3935, 0.4648]  — |
| Sensitivity | 0.0386 | [0.0123, 0.0728]  — |
| Specificity | 0.9924 | [0.9807, 1.0000]  — |
| MCC | 0.1077 | [0.0101, 0.2010]  — |
| R² | 0.0219 | [-0.0123, 0.0514]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0251 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5599 | p=0.0160 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1252 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2435 | < 0.20 |
| Log-Loss | 0.6938 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1194 | proche 0 = pas de biais systématique |
| LoA lower | -5.3014 | limite inférieure d'accord |
| LoA upper | +5.5401 | limite supérieure d'accord |
| LoA width | ±5.4207 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0287 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0251 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5599 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3936 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 29.9 | 25% |
| Significativité (p-value) | 29.1 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 49.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 63.0 | 10% |

### **SCORE TOTAL : 40.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 01:39*
