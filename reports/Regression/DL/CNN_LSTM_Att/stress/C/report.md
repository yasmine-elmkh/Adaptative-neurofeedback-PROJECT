# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `CNN_LSTM_Att`  |  **Exp :** `C`  |  **Date :** 2026-06-13 15:02


> 🟠 **Deployment Readiness Score : 52.6/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3883 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7735 | Erreur quadratique moyenne |
| R² | 0.0191 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5871 | 0.500 |
| PR-AUC | 0.3992 | 0.366 |
| Sensitivity (TPR) | 0.2025 | 0.500 |
| Specificity (TNR) | 0.7883 | 0.500 |
| PPV (Precision) | 0.3556 | — |
| NPV | 0.6316 | — |
| Balanced Accuracy | 0.4954 | 0.500 |
| MCC | -0.0108 | 0.000 |
| G-Mean | 0.3996 | 0.500 |
| F1 macro | 0.4797 | 0.500 |
| LR+ | 0.957 | >10 = très utile |
| LR− | 1.012 | <0.1 = très utile |
| Cohen κ | -0.0101 | 0.000 |
| Brier Score | 0.2484 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5857 | [0.5331, 0.6332]  ✅ |
| F1 macro | 0.4793 | [0.4331, 0.5239]  — |
| Sensitivity | 0.2031 | [0.1451, 0.2613]  — |
| Specificity | 0.7873 | [0.7402, 0.8324]  — |
| MCC | -0.0114 | [-0.1061, 0.0808]  — |
| R² | 0.0154 | [-0.0328, 0.0633]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0191 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5871 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1497 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2484 | < 0.20 |
| Log-Loss | 0.6982 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2456 | proche 0 = pas de biais systématique |
| LoA lower | -5.1755 | limite inférieure d'accord |
| LoA upper | +5.6667 | limite supérieure d'accord |
| LoA width | ±5.4211 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0273 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0191 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5871 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3883 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 43.6 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 33.5 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 66.6 | 10% |

### **SCORE TOTAL : 52.6/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 15:02*
