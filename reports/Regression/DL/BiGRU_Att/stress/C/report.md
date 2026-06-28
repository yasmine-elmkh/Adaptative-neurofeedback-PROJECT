# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiGRU_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-13 16:33


> 🔴 **Deployment Readiness Score : 26.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4244 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7821 | Erreur quadratique moyenne |
| R² | 0.0131 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4991 | 0.500 |
| PR-AUC | 0.3533 | 0.366 |
| Sensitivity (TPR) | 0.0063 | 0.500 |
| Specificity (TNR) | 0.9781 | 0.500 |
| PPV (Precision) | 0.1429 | — |
| NPV | 0.6306 | — |
| Balanced Accuracy | 0.4922 | 0.500 |
| MCC | -0.0594 | 0.000 |
| G-Mean | 0.0787 | 0.500 |
| F1 macro | 0.3895 | 0.500 |
| LR+ | 0.289 | >10 = très utile |
| LR− | 1.016 | <0.1 = très utile |
| Cohen κ | -0.0195 | 0.000 |
| Brier Score | 0.2560 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4992 | [0.4434, 0.5531]  — |
| F1 macro | 0.3899 | [0.3684, 0.4139]  — |
| Sensitivity | 0.0065 | [0.0000, 0.0211]  — |
| Specificity | 0.9781 | [0.9596, 0.9929]  — |
| MCC | -0.0578 | [-0.1156, 0.0238]  — |
| R² | 0.0106 | [-0.0177, 0.0360]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0131 | p=0.0020 | ✅ p<0.05 |
| AUC ROC | 0.4991 | p=0.5160 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1499 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2560 | < 0.20 |
| Log-Loss | 0.7205 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0825 | proche 0 = pas de biais systématique |
| LoA lower | -5.3743 | limite inférieure d'accord |
| LoA upper | +5.5393 | limite supérieure d'accord |
| LoA width | ±5.4568 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0190 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0131 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.4991 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4244 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 0.0 | 25% |
| Significativité (p-value) | 0.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 33.4 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 60.2 | 10% |

### **SCORE TOTAL : 26.0/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 16:33*
