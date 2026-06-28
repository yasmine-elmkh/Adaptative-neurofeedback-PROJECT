# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN3D`  |  **Exp :** `A`  |  **Date :** 2026-06-13 04:02


> 🟠 **Deployment Readiness Score : 55.1/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3850 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7611 | Erreur quadratique moyenne |
| R² | 0.0279 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5921 | 0.500 |
| PR-AUC | 0.4441 | 0.366 |
| Sensitivity (TPR) | 0.0190 | 0.500 |
| Specificity (TNR) | 0.9854 | 0.500 |
| PPV (Precision) | 0.4286 | — |
| NPV | 0.6353 | — |
| Balanced Accuracy | 0.5022 | 0.500 |
| MCC | 0.0167 | 0.000 |
| G-Mean | 0.1368 | 0.500 |
| F1 macro | 0.4044 | 0.500 |
| LR+ | 1.301 | >10 = très utile |
| LR− | 0.996 | <0.1 = très utile |
| Cohen κ | 0.0055 | 0.000 |
| Brier Score | 0.2425 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5902 | [0.5389, 0.6425]  ✅ |
| F1 macro | 0.4042 | [0.3774, 0.4335]  — |
| Sensitivity | 0.0185 | [0.0000, 0.0429]  — |
| Specificity | 0.9855 | [0.9703, 0.9965]  — |
| MCC | 0.0152 | [-0.0814, 0.1144]  — |
| R² | 0.0250 | [-0.0038, 0.0548]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0279 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5921 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1280 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2425 | < 0.20 |
| Log-Loss | 0.6906 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0253 | proche 0 = pas de biais systématique |
| LoA lower | -5.3924 | limite inférieure d'accord |
| LoA upper | +5.4431 | limite supérieure d'accord |
| LoA width | ±5.4177 | < ±2 pts : excellent |
| % dans LoA | 96.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0342 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0279 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5921 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3850 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 46.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 48.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 64.3 | 10% |

### **SCORE TOTAL : 55.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 04:02*
