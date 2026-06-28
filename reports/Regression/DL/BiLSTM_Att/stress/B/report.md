# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `BiLSTM_Att`  |  **Exp :** `B`  |  **Date :** 2026-06-14 00:05


> 🔴 **Deployment Readiness Score : 39.0/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3947 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7700 | Erreur quadratique moyenne |
| R² | 0.0216 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5643 | 0.500 |
| PR-AUC | 0.3826 | 0.366 |
| Sensitivity (TPR) | 0.0823 | 0.500 |
| Specificity (TNR) | 0.8905 | 0.500 |
| PPV (Precision) | 0.3023 | — |
| NPV | 0.6272 | — |
| Balanced Accuracy | 0.4864 | 0.500 |
| MCC | -0.0438 | 0.000 |
| G-Mean | 0.2707 | 0.500 |
| F1 macro | 0.4327 | 0.500 |
| LR+ | 0.751 | >10 = très utile |
| LR− | 1.031 | <0.1 = très utile |
| Cohen κ | -0.0322 | 0.000 |
| Brier Score | 0.2568 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5629 | [0.5111, 0.6149]  ✅ |
| F1 macro | 0.4339 | [0.3933, 0.4720]  — |
| Sensitivity | 0.0836 | [0.0431, 0.1246]  — |
| Specificity | 0.8907 | [0.8532, 0.9303]  — |
| MCC | -0.0408 | [-0.1373, 0.0559]  — |
| R² | 0.0191 | [-0.0218, 0.0602]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0216 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5643 | p=0.0080 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1746 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2568 | < 0.20 |
| Log-Loss | 0.7285 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0245 | proche 0 = pas de biais systématique |
| LoA lower | -5.4108 | limite inférieure d'accord |
| LoA upper | +5.4598 | limite supérieure d'accord |
| LoA width | ±5.4353 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0450 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0216 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5643 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3947 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 32.1 | 25% |
| Significativité (p-value) | 46.8 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 16.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 64.1 | 10% |

### **SCORE TOTAL : 39.0/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 00:05*
