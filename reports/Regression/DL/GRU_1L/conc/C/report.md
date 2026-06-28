# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 10:48


> 🟠 **Deployment Readiness Score : 58.1/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2908 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9142 | Erreur quadratique moyenne |
| R² | 0.1516 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6886 | 0.500 |
| PR-AUC | 0.6773 | 0.521 |
| Sensitivity (TPR) | 0.5664 | 0.500 |
| Specificity (TNR) | 0.6827 | 0.500 |
| PPV (Precision) | 0.6598 | — |
| NPV | 0.5917 | — |
| Balanced Accuracy | 0.6245 | 0.500 |
| MCC | 0.2503 | 0.000 |
| G-Mean | 0.6218 | 0.500 |
| F1 macro | 0.6217 | 0.500 |
| LR+ | 1.785 | >10 = très utile |
| LR− | 0.635 | <0.1 = très utile |
| Cohen κ | 0.2475 | 0.000 |
| Brier Score | 0.2666 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6900 | [0.6223, 0.7571]  ✅ |
| F1 macro | 0.6210 | [0.5617, 0.6876]  ✅ |
| Sensitivity | 0.5664 | [0.4711, 0.6547]  — |
| Specificity | 0.6831 | [0.5969, 0.7714]  — |
| MCC | 0.2508 | [0.1346, 0.3824]  — |
| R² | 0.1490 | [0.0108, 0.2795]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1516 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6886 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1980 | < 0.05 |
| MCE | 0.4415 | < 0.10 |
| Brier Score | 0.2666 | < 0.20 |
| Log-Loss | 0.8490 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4900 | proche 0 = pas de biais systématique |
| LoA lower | -6.1334 | limite inférieure d'accord |
| LoA upper | +5.1535 | limite supérieure d'accord |
| LoA width | ±5.6434 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1229 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1516 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6886 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2908 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 94.3 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 1.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 43.5 | 10% |

### **SCORE TOTAL : 58.1/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 10:48*
