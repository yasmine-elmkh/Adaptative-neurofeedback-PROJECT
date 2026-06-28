# NeuroCap — Modèles IA (`src/models/`)

Tous les modèles de régression EEG (ML, DL, TL), le module de métriques partagé,  
et la comparaison globale. **Tâche : prédire un score continu 0–10.**

---

## Structure

```
src/models/
├── metrics_professional.py        Module métriques partagé (5 niveaux, toutes familles)
│
├── baselines/                     Régresseurs ML classiques
│   ├── baseline_ML_regression.py              SVR/RF/XGB/LGBM — feat15, sans SMOTE
│   ├── baseline_ML_regression_smote.py        SVR/RF/XGB/LGBM — feat15, avec SMOTE
│   ├── baseline_ML_regression_feature_eng.py      feat78, sans SMOTE
│   ├── baseline_ML_regression_feature_eng_smote.py feat78, avec SMOTE
│   ├── compare_regression_features.py         feat15 vs feat78 (même protocole LOSO)
│   ├── compare_regression_smote.py            sans vs avec SMOTE (impact déséquilibre)
│   └── compare_baseline_global.py             synthèse toutes configs baselines
│
├── deep_learning/                 19 architectures DL (signal brut → score)
│   ├── DL_utils_regression.py     Moteur partagé : CNNPreEncoder, BahdanauAttention,
│   │                               dl_main_regression(), WeightedRandomSampler, AMP
│   ├── architectures/
│   │   ├── EEGNet.py              EEG-specific compact (Lawhern 2018) — backbone TL
│   │   ├── LSTM1L.py / LSTM2L.py / LSTM_ATT.py
│   │   ├── BILSTM1L.py / BILSTM2L.py / BILSTM_ATT.py
│   │   ├── GRU1L.py / GRU2L.py / GRU_ATT.py
│   │   ├── BIGRU1L.py / BIGRU2L.py / BIGRU_ATT.py
│   │   ├── CNN1D.py / CNN2D.py / CNN3D.py
│   │   ├── CNN_LSTM_Att.py / CNN_GRU_Att.py
│   │   ├── TCN.py
│   │   └── EEGNet_finetune.py     Variante EEGNet avec MC Dropout (inférence calibrée)
│   └── compare.py                 Comparaison des 19 architectures (rapports + figures)
│
├── transfer_learning/             Transfer Learning EEGNet (3 stratégies)
│   ├── EEGNet_feature_extraction.py    TL-2 : gèle conv+dw+sep, entraîne FC uniquement
│   ├── EEGNet_full_finetuning.py       TL-1 : dégelée complète, LR réduit
│   ├── EEGNet_layer_replacement.py     TL-3 ★ : remplace conv1+bn1, gèle milieu, entraîne FC
│   └── compare_tl.py                   Comparaison des 3 stratégies (figures + rapport)
│
└── compare/
    └── compare_all_models.py      Comparaison globale ML / DL / TL → décision finale
```

---

## `metrics_professional.py` — Module métriques (5 niveaux)

Importé par **tous** les scripts d'entraînement. Aucune logique de métriques dans les autres fichiers.

| Niveau | Contenu | Fonctions clés |
|--------|---------|---------------|
| 1 — Cliniques | Sensitivity, Specificity, PPV, NPV, MCC, G-Mean, AUC, MAE, RMSE, R² | `compute_full_metrics()` |
| 2 — Statistiques | Bootstrap CI (N=500), permutation test (N=999), Wilcoxon, Friedman | `bootstrap_ci()`, `permutation_test()` |
| 3 — Qualité | Calibration (ECE/MCE), Bland-Altman (LoA ≤ 4 pts), ICC(2,1) ≥ 0.90 | `calibration_analysis()`, `bland_altman_analysis()`, `icc()` |
| 4 — Robustesse | Stability (CV-R² ≤ 5%), bias-variance, per_subject_metrics | `stability_analysis()` |
| 5 — Avancés | Decision Curve Analysis (DCA), DeLong CI, rapport Markdown | `decision_curve_analysis()`, `generate_professional_report()` |

---

## Baselines ML

### Hyperparamètres principaux

| Modèle | Paramètres clés | Justification |
|--------|----------------|--------------|
| SVR (RBF) | C=5, gamma='scale', epsilon=0.1 | C=5 : optimal pour 11 sujets train LOSO |
| Random Forest | n_estimators=300, min_samples_leaf=4 | Stable sur petits folds LOSO |
| XGBoost | n_estimators=300, max_depth=4, lr=0.05, subsample=0.8 | Profondeur réduite contre overfitting |
| LightGBM | n_estimators=300, num_leaves=31, lr=0.05 | Plus rapide qu'XGBoost, leaf-wise |
| Stacking | RF+XGB+LGBM+SVR → Ridge(α=1.0) méta-apprenant | Combiner les 4 modèles |

**Protocole :** GridSearchCV 5-fold sur train interne → LOSO → feat15 vs feat78 × sans/avec SMOTE

### Résultats (LOSO, meilleure config feat78_smote FULL)

| Modèle | Cible | MAE | R² | AUC | MCC |
|--------|-------|-----|-----|-----|-----|
| LightGBM | Concentration | 1.63 | 0.204 | **0.676** | 0.144 |
| Random Forest | Stress | 1.72 | 0.184 | **0.668** | 0.318 |

---

## Deep Learning

### Moteur partagé (`DL_utils_regression.py`)

Toutes les 19 architectures appellent `dl_main_regression(model_name, ModelClass)` — aucune logique d'entraînement dans les fichiers d'architecture.

**Hyperparamètres globaux :**

| Paramètre | Valeur | Rôle |
|-----------|--------|------|
| LR | 3e-3 | Adam, décroît via ReduceLROnPlateau (factor=0.5, patience=5) |
| Weight Decay | 1e-4 | Régularisation L2 |
| Max Epochs | 50 | Avec early stopping |
| Patience (ES) | 10 | Arrêt si val_loss stagne |
| Batch Size | 32 | — |
| Grad Clip | 1.0 | Indispensable pour LSTM/GRU (explosion gradient) |
| Loss | MSELoss | Régression continue |
| Optimizer | Adam | — |
| AMP | Oui (si GPU) | float16 + float32, ×2 vitesse |
| NUM_WORKERS | 0 | Obligatoire Windows (incompatibilité mémoire partagée DataLoader) |

**Modules partagés :**
- `CNNPreEncoder(out_features=64)` : (B,1,1000) → (B,63,64) via 3 Conv1D avec stride
- `BahdanauAttention(hidden_size)` : score(h) = v·tanh(W·h), αₜ = softmax(score), context = Σαₜhₜ
- `_make_weighted_sampler(y)` : WeightedRandomSampler, poids = n_Low/n_High
- `find_youden_threshold(y_true, y_pred)` : τ* = argmax(Sensibilité + Spécificité − 1)

### Interface des architectures

```python
model = ModelClass()          # entrée: (batch, 1, 1000) → sortie: (batch, 1)
# Régression → 1 neurone de sortie, MSELoss
# Chaque fichier: if __name__ == "__main__": dl_main_regression("NomModèle", ModelClass)
```

### 19 architectures

| Fichier | Famille | Description | Résultat LOSO concentration |
|---------|---------|-------------|---------------------------|
| `EEGNet.py` | Compact EEG | Conv2D temporelle + Depthwise + Separable (Lawhern 2018) | AUC=0.613 (DL), AUC=0.751 (FULL) ★ |
| `LSTM1L.py` | LSTM | CNNPreEncoder + LSTM(64, 1 couche) + FC | AUC=0.582 |
| `LSTM2L.py` | LSTM | CNNPreEncoder + LSTM(64, 2 couches, drop=0.3) + FC | AUC=0.604 |
| `LSTM_ATT.py` | LSTM | CNNPreEncoder + LSTM + BahdanauAtt + FC | AUC=0.656 ★ |
| `BILSTM1L.py` | BiLSTM | CNNPreEncoder + BiLSTM(64, 1L) + FC(128→32→1) | AUC=0.612 |
| `BILSTM2L.py` | BiLSTM | CNNPreEncoder + BiLSTM(64, 2L, drop=0.3) + FC | AUC=0.571 |
| `BILSTM_ATT.py` | BiLSTM | CNNPreEncoder + BiLSTM + BahdanauAtt(128) + FC | AUC=0.605 |
| `GRU1L.py` | GRU | CNNPreEncoder + GRU(64, 1L) + FC | AUC=0.609 |
| `GRU2L.py` | GRU | CNNPreEncoder + GRU(64, 2L) + FC | AUC=0.602 |
| `GRU_ATT.py` | GRU | CNNPreEncoder + GRU + BahdanauAtt + FC | AUC=0.622 |
| `BIGRU1L.py` | BiGRU | CNNPreEncoder + BiGRU(64, 1L) + FC | AUC=0.606 |
| `BIGRU2L.py` | BiGRU | CNNPreEncoder + BiGRU(64, 2L) + FC | AUC=0.637 |
| `BIGRU_ATT.py` | BiGRU | CNNPreEncoder + BiGRU + BahdanauAtt + FC | AUC=0.622 |
| `CNN1D.py` | CNN | 4 blocs Conv1D + BN + ReLU + AvgPool → FC | AUC=0.633 |
| `CNN2D.py` | CNN | Spectrogram 2D + Conv2D × 3 → FC | AUC=0.596 |
| `CNN3D.py` | CNN | Extension CNN2D + Conv3D → FC | AUC=0.633 |
| `CNN_GRU_Att.py` | Hybride | CNN1D + GRU + BahdanauAtt + FC | AUC=0.632 |
| `CNN_LSTM_Att.py` | Hybride | CNN1D + LSTM + BahdanauAtt + FC | AUC=0.608 |
| `TCN.py` | Temporel | 4 TCNBlocks (dilat.1,2,4,8), kernel=7 + AdaptiveAvgPool + FC | AUC=0.607 |

---

## Transfer Learning

3 stratégies comparées sur EEGNet pré-entraîné (depuis `models/Regression/DL/EEGNet/`).  
Données de calibration : `X_val` (15% des sujets).

| Stratégie | Fichier | Couches gelées | Couches entraînées | AUC conc. |
|-----------|---------|---------------|-------------------|-----------|
| TL-1 Full FT | `EEGNet_full_finetuning.py` | Aucune | Toutes (LR=5e-5) | 0.685 |
| TL-2 Feature Extraction | `EEGNet_feature_extraction.py` | conv→sep_pw→bn3→pool2 | FC uniquement | 0.658 |
| TL-3 Layer Replacement ★ | `EEGNet_layer_replacement.py` | dw→sep_pw→bn3→pool2 | conv1+bn1 (nouveau) + FC | **0.723** |

**Hyperparamètres fine-tuning (communs) :**
```
FT_LR = 5e-5      # 60× plus faible que l'entraînement initial (3e-3)
FT_EPOCHS = 60    # Plus d'epochs car LR petit
FT_PATIENCE = 12  # Early stopping plus patient
FT_BATCH = 32
```

**TL-3 en production :** `EEGNet_LR_stress_B_best.pt` → utilisé par `app/Backend/services/finetune/runner.py`

---

## Comparaison globale (`compare/compare_all_models.py`)

Compare ML / DL / TL avec score composite S = 0.40×AUC + 0.30×Sens + 0.20×MCC + 0.10×Spec.

### Décision finale

| Cible | Modèle retenu | S | AUC | Sensibilité | Statut |
|-------|--------------|---|-----|-------------|--------|
| **Concentration** | **EEGNet DL FULL** | **0.789** | **0.751** | **0.994** | **✓ PRODUCTION** |
| **Stress** | **EEGNet TL-LR FULL** | **0.525** | **0.607** | **0.615** | **⚠ CONDITIONNEL** |

Le modèle stress est conditionnel car domain gap structurel AF3 (Emotiv SAM40) → Fp2 (NeuroCap).  
Afficher : *"Indicateur orientatif — non validé cliniquement"*.

---

## `inference_engine.py` (racine `src/`)

Interface unifiée backend. L'ESP32 envoie 1000 échantillons bruts → `InferenceEngine.predict(epoch)`.

```python
from src.inference_engine import InferenceEngine, ModelType

engine = InferenceEngine(ModelType.BEST_AUTO)
result = engine.predict(epoch)  # epoch: np.array (1000,) @ 250 Hz
# → {'concentration': 72.3, 'stress': 27.7, 'state': 'Concentration',
#    'confidence': 72.3, 'uncertain': False}
```

`CONFIDENCE_THR = 0.60` — en dessous → `uncertain: True` (CdC §2.5.1).
