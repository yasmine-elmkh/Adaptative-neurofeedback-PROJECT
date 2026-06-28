# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN3D`  |  **Exp :** `C`  |  **Date :** 2026-06-12 21:02


> 🟠 **Deployment Readiness Score : 51.0/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4888 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0783 | Erreur quadratique moyenne |
| R² | 0.0534 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6424 | 0.500 |
| PR-AUC | 0.6178 | 0.521 |
| Sensitivity (TPR) | 0.3097 | 0.500 |
| Specificity (TNR) | 0.7885 | 0.500 |
| PPV (Precision) | 0.6140 | — |
| NPV | 0.5125 | — |
| Balanced Accuracy | 0.5491 | 0.500 |
| MCC | 0.1115 | 0.000 |
| G-Mean | 0.4942 | 0.500 |
| F1 macro | 0.5165 | 0.500 |
| LR+ | 1.464 | >10 = très utile |
| LR− | 0.875 | <0.1 = très utile |
| Cohen κ | 0.0961 | 0.000 |
| Brier Score | 0.3546 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6420 | [0.5640, 0.7168]  ✅ |
| F1 macro | 0.5159 | [0.4459, 0.5842]  — |
| Sensitivity | 0.3105 | [0.2148, 0.4057]  — |
| Specificity | 0.7881 | [0.7177, 0.8637]  — |
| MCC | 0.1114 | [-0.0205, 0.2475]  — |
| R² | 0.0480 | [-0.1018, 0.1901]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0534 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6424 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3242 | < 0.05 |
| MCE | 0.6963 | < 0.10 |
| Brier Score | 0.3546 | < 0.20 |
| Log-Loss | 1.1800 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0339 | proche 0 = pas de biais systématique |
| LoA lower | -6.7300 | limite inférieure d'accord |
| LoA upper | +4.6621 | limite supérieure d'accord |
| LoA width | ±5.6960 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0336 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0534 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6424 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4888 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 71.2 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 31.4 | 10% |

### **SCORE TOTAL : 51.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 21:02*
