# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `GRU_1L`  |  **Exp :** `B`  |  **Date :** 2026-06-13 09:22


> 🟠 **Deployment Readiness Score : 58.4/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3412 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9365 | Erreur quadratique moyenne |
| R² | 0.1385 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6951 | 0.500 |
| PR-AUC | 0.6638 | 0.521 |
| Sensitivity (TPR) | 0.5044 | 0.500 |
| Specificity (TNR) | 0.7308 | 0.500 |
| PPV (Precision) | 0.6706 | — |
| NPV | 0.5758 | — |
| Balanced Accuracy | 0.6176 | 0.500 |
| MCC | 0.2407 | 0.000 |
| G-Mean | 0.6071 | 0.500 |
| F1 macro | 0.6099 | 0.500 |
| LR+ | 1.874 | >10 = très utile |
| LR− | 0.678 | <0.1 = très utile |
| Cohen κ | 0.2327 | 0.000 |
| Brier Score | 0.2735 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6959 | [0.6260, 0.7656]  ✅ |
| F1 macro | 0.6085 | [0.5414, 0.6680]  ✅ |
| Sensitivity | 0.5026 | [0.4113, 0.5964]  — |
| Specificity | 0.7321 | [0.6488, 0.8134]  — |
| MCC | 0.2404 | [0.1139, 0.3590]  — |
| R² | 0.1372 | [-0.0047, 0.2607]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1385 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6951 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2171 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2735 | < 0.20 |
| Log-Loss | 0.8954 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.7662 | proche 0 = pas de biais systématique |
| LoA lower | -6.3353 | limite inférieure d'accord |
| LoA upper | +4.8029 | limite supérieure d'accord |
| LoA width | ±5.5691 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0671 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1385 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6951 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3412 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 97.6 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 40.3 | 10% |

### **SCORE TOTAL : 58.4/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 09:22*
