# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN3D`  |  **Exp :** `B`  |  **Date :** 2026-06-12 19:46


> 🟠 **Deployment Readiness Score : 54.3/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4702 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0475 | Erreur quadratique moyenne |
| R² | 0.0722 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6647 | 0.500 |
| PR-AUC | 0.6614 | 0.521 |
| Sensitivity (TPR) | 0.3009 | 0.500 |
| Specificity (TNR) | 0.8077 | 0.500 |
| PPV (Precision) | 0.6296 | — |
| NPV | 0.5153 | — |
| Balanced Accuracy | 0.5543 | 0.500 |
| MCC | 0.1255 | 0.000 |
| G-Mean | 0.4930 | 0.500 |
| F1 macro | 0.5182 | 0.500 |
| LR+ | 1.565 | >10 = très utile |
| LR− | 0.866 | <0.1 = très utile |
| Cohen κ | 0.1062 | 0.000 |
| Brier Score | 0.3570 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6647 | [0.5895, 0.7335]  ✅ |
| F1 macro | 0.5173 | [0.4460, 0.5881]  — |
| Sensitivity | 0.3010 | [0.2143, 0.3836]  — |
| Specificity | 0.8075 | [0.7363, 0.8841]  — |
| MCC | 0.1252 | [-0.0150, 0.2680]  — |
| R² | 0.0672 | [-0.1009, 0.2136]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0722 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6647 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3205 | < 0.05 |
| MCE | 0.5293 | < 0.10 |
| Brier Score | 0.3570 | < 0.20 |
| Log-Loss | 1.2368 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.1820 | proche 0 = pas de biais systématique |
| LoA lower | -6.7003 | limite inférieure d'accord |
| LoA upper | +4.3363 | limite supérieure d'accord |
| LoA width | ±5.5183 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0318 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0722 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6647 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4702 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 82.4 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 37.3 | 10% |

### **SCORE TOTAL : 54.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-12 19:46*
