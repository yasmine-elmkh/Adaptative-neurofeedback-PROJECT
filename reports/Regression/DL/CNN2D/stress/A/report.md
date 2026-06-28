# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN2D`  |  **Exp :** `A`  |  **Date :** 2026-06-12 22:05


> 🟠 **Deployment Readiness Score : 47.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4505 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9933 | Erreur quadratique moyenne |
| R² | -0.1425 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5981 | 0.500 |
| PR-AUC | 0.4379 | 0.366 |
| Sensitivity (TPR) | 0.0253 | 0.500 |
| Specificity (TNR) | 0.9781 | 0.500 |
| PPV (Precision) | 0.4000 | — |
| NPV | 0.6351 | — |
| Balanced Accuracy | 0.5017 | 0.500 |
| MCC | 0.0109 | 0.000 |
| G-Mean | 0.1574 | 0.500 |
| F1 macro | 0.4089 | 0.500 |
| LR+ | 1.156 | >10 = très utile |
| LR− | 0.997 | <0.1 = très utile |
| Cohen κ | 0.0043 | 0.000 |
| Brier Score | 0.3061 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5959 | [0.5400, 0.6581]  ✅ |
| F1 macro | 0.4085 | [0.3774, 0.4393]  — |
| Sensitivity | 0.0247 | [0.0057, 0.0518]  — |
| Specificity | 0.9781 | [0.9587, 0.9928]  — |
| MCC | 0.0089 | [-0.0821, 0.1039]  — |
| R² | -0.1434 | [-0.2135, -0.0756]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1425 | p=0.1480 | ❌ ns |
| AUC ROC | 0.5981 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2789 | < 0.05 |
| MCE | 0.9622 | < 0.10 |
| Brier Score | 0.3061 | < 0.20 |
| Log-Loss | 1.0131 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8829 | proche 0 = pas de biais systématique |
| LoA lower | -6.4952 | limite inférieure d'accord |
| LoA upper | +4.7293 | limite supérieure d'accord |
| LoA width | ±5.6123 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0011 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1425 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5981 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4505 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 49.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 54.6 | 10% |

### **SCORE TOTAL : 47.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 22:05*
