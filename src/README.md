# NeuroCap — Code Source IA (`src/`)

Pipeline complet d'intelligence artificielle pour la détection d'états cognitifs par EEG monocanal (Fp2).  
**Tâche : régression continue → scores 0–10 pour la Concentration et le Stress.**

---

## Architecture du dossier

```
src/
├── data/                         Traitement des données EEG
│   ├── pipeline_fp2.py           Prétraitement complet (HP/LP/Notch/DWT/epoch/zscore)
│   ├── augmentation_eeg.py       Augmentation EEG (Noise/Scaling/Shift/DWT/MagWarp)
│   ├── features_extraction.py    15 features légères (embarquables, < 40 ms)
│   ├── feature_eng.py            78 features avancées (8 catégories, ~35 ms)
│   ├── pipeline_regression.py    Coordinateur pipeline régression (scoring → feat)
│   ├── visualize_regression.py   Visualisations du pipeline (16 figures → reports/)
│   ├── scoring/                  Attribution scores 0–10 aux epochs
│   │   ├── concentration_scoring.py
│   │   ├── stress_scoring.py
│   │   ├── merge_scoring.py
│   │   └── visualize_scoring.py
│   └── validate_data/            Validation qualité des datasets bruts
│       ├── validate_concentration.py
│       └── validate_stress.py
│
├── models/                       Modèles IA et évaluation
│   ├── metrics_professional.py   Module métriques partagé (5 niveaux, LOSO)
│   ├── baselines/                ML classiques (SVR, RF, XGBoost, LightGBM)
│   │   ├── baseline_ML_regression.py            feat15, sans SMOTE
│   │   ├── baseline_ML_regression_smote.py      feat15, avec SMOTE
│   │   ├── baseline_ML_regression_feature_eng.py      feat78, sans SMOTE
│   │   ├── baseline_ML_regression_feature_eng_smote.py feat78, avec SMOTE
│   │   ├── compare_regression_features.py       feat15 vs feat78
│   │   ├── compare_regression_smote.py          sans vs avec SMOTE
│   │   └── compare_baseline_global.py           comparaison globale baselines
│   ├── deep_learning/            19 architectures DL (régression)
│   │   ├── DL_utils_regression.py  Moteur partagé (CNNPreEncoder, Bahdanau, LOSO)
│   │   ├── architectures/          19 fichiers .py (une classe par architecture)
│   │   └── compare.py             Comparaison des 19 architectures DL
│   ├── transfer_learning/        Transfer Learning EEGNet (3 stratégies)
│   │   ├── EEGNet_feature_extraction.py  TL-2 : backbone gelé
│   │   ├── EEGNet_full_finetuning.py     TL-1 : toutes couches dégelées
│   │   ├── EEGNet_layer_replacement.py   TL-3 ★ : remplacement conv1+bn1
│   │   └── compare_tl.py                Comparaison des 3 stratégies TL
│   └── compare/                  Comparaison globale ML / DL / TL
│       └── compare_all_models.py
│
└── inference_engine.py           Interface unifiée backend (InferenceEngine)
```

---

## Datasets et tâches

| Dataset | Source | Sujets | Hz origine | Cible | Modèle retenu |
|---------|--------|--------|-----------|-------|---------------|
| CLA (Concentration) | OpenBCI Cyton | 15 | 200 Hz | conc_score 0–10 | EEGNet DL FULL ★ |
| SAM40 (Stress) | Emotiv Epoc Flex | 40 | 128 Hz | stress_score 0–10 | EEGNet TL-LR FULL ★ |

Les deux datasets sont **complètement indépendants** — deux pipelines séparés.

---

## Ordre d'exécution complet

### Étape 1 — Validation des données brutes
```bash
python src/data/validate_data/validate_concentration.py
python src/data/validate_data/validate_stress.py
```

### Étape 2 — Attribution des scores 0–10
```bash
python src/data/scoring/concentration_scoring.py
python src/data/scoring/stress_scoring.py
python src/data/scoring/visualize_scoring.py   # optionnel — 7 figures
```

### Étape 3 — Pipeline régression (preprocessing + split + augmentation + features)
```bash
python src/data/pipeline_regression.py
python src/data/visualize_regression.py         # optionnel — 16 figures
```

### Étape 4 — Entraînement Baselines ML
```bash
python src/models/baselines/baseline_ML_regression_feature_eng_smote.py
python src/models/baselines/compare_regression_features.py
```

### Étape 5 — Entraînement Deep Learning (19 architectures)
```bash
# Chaque fichier s'entraîne et sauvegarde ses résultats automatiquement
python src/models/deep_learning/architectures/EEGNet.py
python src/models/deep_learning/architectures/LSTM_ATT.py
# ... (19 architectures, 2 cibles × 5 expériences = 190 runs)
python src/models/deep_learning/compare.py      # comparaison des 19 architectures
```

### Étape 6 — Transfer Learning EEGNet
```bash
python src/models/transfer_learning/EEGNet_layer_replacement.py  # TL-3 ★
python src/models/transfer_learning/EEGNet_full_finetuning.py
python src/models/transfer_learning/EEGNet_feature_extraction.py
python src/models/transfer_learning/compare_tl.py
```

### Étape 7 — Comparaison globale
```bash
python src/models/compare/compare_all_models.py
# → reports/Regression/Comparaison_Globale/recommendation.txt
```

---

## Résultats obtenus (LOSO strict)

| Famille | Modèle | Cible | AUC | R² | Statut |
|---------|--------|-------|-----|-----|--------|
| Deep Learning | EEGNet FULL | Concentration | **0.751** | 0.072 | **✓ PRODUCTION** |
| Transfer Learning | TL-LayerReplacement FULL | Stress | **0.607** | −0.052 | **⚠ CONDITIONNEL** |
| Machine Learning | LightGBM feat78_smote | Concentration | 0.676 | 0.204 | (référence ML) |
| Machine Learning | RF feat78_smote | Stress | 0.668 | 0.184 | (référence ML) |

---

## Points clés de l'architecture IA

- **Validation LOSO** : Leave-One-Subject-Out — garantit que le sujet test n'est jamais dans l'entraînement
- **Split avant augmentation** : les epochs augmentées ne contaminent jamais le test set
- **5 expériences d'augmentation** : A (original), B (Noise+Scale+Shift), C (B+DWT), D (MagWarp), FULL (A+B+C+D)
- **2 sets de features** : feat15 (< 10 ms, embarquable ESP32) et feat78 (35 ms, R² +5 pts)
- **Fine-tuning production** : personnalisation par patient via `app/Backend/services/finetune/runner.py`

---

## Dépendances

```
torch>=2.0, numpy, scipy, scikit-learn, xgboost, lightgbm, pywavelets, joblib
```
Voir `app/Backend/requirements.txt` pour l'environnement complet.
