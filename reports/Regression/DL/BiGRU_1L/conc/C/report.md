# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `C`  |  **Date :** 2026-06-13 16:00


> 🟠 **Deployment Readiness Score : 55.2/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3947 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0095 | Erreur quadratique moyenne |
| R² | 0.0952 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6703 | 0.500 |
| PR-AUC | 0.6739 | 0.521 |
| Sensitivity (TPR) | 0.5310 | 0.500 |
| Specificity (TNR) | 0.6442 | 0.500 |
| PPV (Precision) | 0.6186 | — |
| NPV | 0.5583 | — |
| Balanced Accuracy | 0.5876 | 0.500 |
| MCC | 0.1760 | 0.000 |
| G-Mean | 0.5849 | 0.500 |
| F1 macro | 0.5848 | 0.500 |
| LR+ | 1.492 | >10 = très utile |
| LR− | 0.728 | <0.1 = très utile |
| Cohen κ | 0.1741 | 0.000 |
| Brier Score | 0.2874 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6717 | [0.5977, 0.7395]  ✅ |
| F1 macro | 0.5851 | [0.5197, 0.6563]  ✅ |
| Sensitivity | 0.5323 | [0.4409, 0.6233]  — |
| Specificity | 0.6456 | [0.5571, 0.7368]  — |
| MCC | 0.1787 | [0.0413, 0.3246]  — |
| R² | 0.0916 | [-0.0671, 0.2297]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0952 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6703 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2183 | < 0.05 |
| MCE | 0.4270 | < 0.10 |
| Brier Score | 0.2874 | < 0.20 |
| Log-Loss | 0.9710 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5692 | proche 0 = pas de biais systématique |
| LoA lower | -6.3748 | limite inférieure d'accord |
| LoA upper | +5.2364 | limite supérieure d'accord |
| LoA width | ±5.8056 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0960 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0952 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6703 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3947 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 85.1 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 38.8 | 10% |

### **SCORE TOTAL : 55.2/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 16:00*
