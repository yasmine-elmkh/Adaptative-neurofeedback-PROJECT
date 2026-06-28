# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-13 12:39


> 🟠 **Deployment Readiness Score : 59.8/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3349 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1236 | Erreur quadratique moyenne |
| R² | 0.0253 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7172 | 0.500 |
| PR-AUC | 0.7101 | 0.521 |
| Sensitivity (TPR) | 0.6460 | 0.500 |
| Specificity (TNR) | 0.6635 | 0.500 |
| PPV (Precision) | 0.6759 | — |
| NPV | 0.6330 | — |
| Balanced Accuracy | 0.6547 | 0.500 |
| MCC | 0.3092 | 0.000 |
| G-Mean | 0.6547 | 0.500 |
| F1 macro | 0.6543 | 0.500 |
| LR+ | 1.920 | >10 = très utile |
| LR− | 0.534 | <0.1 = très utile |
| Cohen κ | 0.3089 | 0.000 |
| Brier Score | 0.2717 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7175 | [0.6507, 0.7794]  ✅ |
| F1 macro | 0.6539 | [0.5888, 0.7139]  ✅ |
| Sensitivity | 0.6470 | [0.5516, 0.7308]  — |
| Specificity | 0.6638 | [0.5792, 0.7547]  — |
| MCC | 0.3105 | [0.1777, 0.4300]  — |
| R² | 0.0184 | [-0.1929, 0.1942]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0253 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7172 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2075 | < 0.05 |
| MCE | 0.4148 | < 0.10 |
| Brier Score | 0.2717 | < 0.20 |
| Log-Loss | 1.0971 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7539 | proche 0 = pas de biais systématique |
| LoA lower | -6.7089 | limite inférieure d'accord |
| LoA upper | +5.2012 | limite supérieure d'accord |
| LoA width | ±5.9550 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0767 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0253 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7172 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3349 | 0.0000 | 0.0% | 🟢 stable |

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
| CI 95% étroit | 47.6 | 10% |

### **SCORE TOTAL : 59.8/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 12:39*
