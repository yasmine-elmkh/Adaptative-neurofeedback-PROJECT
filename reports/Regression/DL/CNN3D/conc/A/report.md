# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN3D`  |  **Exp :** `A`  |  **Date :** 2026-06-12 18:26


> 🟠 **Deployment Readiness Score : 56.7/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2774 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7416 | Erreur quadratique moyenne |
| R² | 0.2491 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6858 | 0.500 |
| PR-AUC | 0.6489 | 0.521 |
| Sensitivity (TPR) | 0.4602 | 0.500 |
| Specificity (TNR) | 0.7115 | 0.500 |
| PPV (Precision) | 0.6341 | — |
| NPV | 0.5481 | — |
| Balanced Accuracy | 0.5859 | 0.500 |
| MCC | 0.1769 | 0.000 |
| G-Mean | 0.5722 | 0.500 |
| F1 macro | 0.5763 | 0.500 |
| LR+ | 1.595 | >10 = très utile |
| LR− | 0.759 | <0.1 = très utile |
| Cohen κ | 0.1697 | 0.000 |
| Brier Score | 0.2727 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6872 | [0.6119, 0.7604]  ✅ |
| F1 macro | 0.5765 | [0.5113, 0.6450]  ✅ |
| Sensitivity | 0.4618 | [0.3624, 0.5641]  — |
| Specificity | 0.7122 | [0.6281, 0.7991]  — |
| MCC | 0.1791 | [0.0451, 0.3140]  — |
| R² | 0.2449 | [0.1375, 0.3398]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2491 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6858 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2200 | < 0.05 |
| MCE | 0.3731 | < 0.10 |
| Brier Score | 0.2727 | < 0.20 |
| Log-Loss | 0.7972 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.3810 | proche 0 = pas de biais systématique |
| LoA lower | -5.7148 | limite inférieure d'accord |
| LoA upper | +4.9527 | limite supérieure d'accord |
| LoA width | ±5.3337 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1674 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2491 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6858 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2774 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 92.9 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 34.4 | 10% |

### **SCORE TOTAL : 56.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 18:26*
