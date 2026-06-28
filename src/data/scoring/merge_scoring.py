"""
merge_scoring.py
================
EMPLACEMENT : src/data/scoring/merge_scoring.py

OBJECTIF GLOBAL :
  Lire les fichiers RAW (.txt concentration + .mat stress),
  extraire les epochs, les resampler a 250Hz,
  et y attacher les scores depuis les CSV de scoring.

  Produit 2 datasets prets pour la regression :
    Concentration : X (N_conc, 1000) + y_conc (N_conc,)  — score 0-10
    Stress        : X (N_stress, 1000) + y_stress (N_stress,) — score 0-10

POURQUOI CE FICHIER ET PAS LES .npy EXISTANTS :
  Les X_train_A.npy existants ont des labels BINAIRES (0/1).
  Pour la regression on a besoin de labels CONTINUS (score 0-10).
  Ce fichier cree les datasets avec les bons labels depuis les CSV de scoring.

RESAMPLING :
  Concentration : 800 samples @200Hz → 1000 samples @250Hz
  Stress        : 512 samples @128Hz → 1000 samples @250Hz
  Methode : scipy.signal.resample (interpolation polyphase, sans distorsion)

SORTIES :
  data/Scoring/merged/
    X_concentration.npy        (N_conc, 1000)   signal EEG concentration @250Hz
    y_conc_score.npy           (N_conc,)        score concentration 0-10
    subjects_concentration.npy (N_conc,)        IDs sujets (anti data leakage)
    levels_concentration.npy   (N_conc,)        niveau cognitif 0/1/2/3

    X_stress.npy               (N_stress, 1000) signal EEG stress @250Hz
    y_stress_score.npy         (N_stress,)      score stress 0-10
    subjects_stress.npy        (N_stress,)      IDs sujets

UTILISATION AVAL :
  Ces fichiers alimentent :
    - ML  : feature_eng.extract_all_features() → 63 features → LGBMRegressor
    - DL  : X brut → architectures CNN/LSTM/etc → regression
    - TL  : X brut → EEGNet finetuning → regression
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.io
from pathlib import Path
from scipy.signal import resample as scipy_resample

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT    = Path(__file__).resolve().parents[3]
RAW_CONC   = PROJECT / "data" / "Dataset" / "Cognitive Load Assessment Concentration" / "raw_data"
RAW_STRESS = PROJECT / "data" / "Dataset" / "Stress_dataset" / "raw_data"
SCORE_DIR  = PROJECT / "data" / "Scoring"
OUT_DIR    = PROJECT / "data" / "Scoring" / "merged"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# CONSTANTES
# ============================================================================
FS_CONC   = 200   # Hz OpenBCI
FS_STRESS = 128   # Hz EMOTIV
FS_TARGET = 250   # Hz attendu par DL et feature_eng
TARGET_SAMPLES = 1000   # 4s x 250Hz

EPOCH_CONC   = 800    # 4s x 200Hz
EPOCH_STRESS = 512    # 4s x 128Hz

CHANNEL_CONC   = 1    # colonne 1 du .txt = CH1 (electrode frontale)
CHANNEL_STRESS = 0    # canal 0 du .mat  = AF3 (frontal gauche)

# Mapping niveau → code entier (pour npy)
LEVEL_CODE = {
    'natural':   0,
    'lowlevel':  1,
    'midlevel':  2,
    'highlevel': 3,
}


# ============================================================================
# FONCTION 1 : construire le dataset concentration
# ============================================================================
def build_concentration_dataset(df_scores: pd.DataFrame) -> dict:
    """
    OBJECTIF :
      Pour chaque epoch dans scored_concentration.csv, lire le signal brut
      depuis le fichier .txt correspondant, le resampler a 250Hz,
      et l'associer a son conc_score.

    STRUCTURE DE df_scores :
      file | epoch_idx | task | level | subject | conc_score | ...

    RESAMPLING :
      800 samples @200Hz → 1000 samples @250Hz
      via scipy.signal.resample (methode de Fourier → pas de distorsion)

    RETOURNE :
      dict avec cles :
        X       : (N, 1000) float32  signaux EEG
        y       : (N,) float32       conc_score 0-10
        subjects: (N,) int           IDs sujets
        levels  : (N,) int           0=natural,1=low,2=mid,3=high
    """
    X_list, y_list, subj_list, level_list = [], [], [], []

    # Grouper par (task, file) pour eviter de re-lire le meme fichier
    groups = df_scores.groupby(['task', 'file'])
    total_groups = len(groups)

    print(f"[concentration] {len(df_scores)} epochs dans {total_groups} fichiers")

    for (task, fn), grp in groups:
        filepath = RAW_CONC / task / fn
        if not filepath.exists():
            print(f"  [SKIP] Fichier manquant : {filepath}")
            continue

        # Lire le signal brut complet
        df_raw = pd.read_csv(filepath, header=None)
        signal = df_raw.iloc[1:, CHANNEL_CONC].astype(float).values

        # Traiter chaque epoch referencee dans le CSV
        for _, row in grp.iterrows():
            idx  = int(row['epoch_idx'])
            start = idx * EPOCH_CONC
            end   = start + EPOCH_CONC

            if end > len(signal):
                continue  # epoch incomplete, ignorer

            epoch_raw = signal[start:end]

            # Resampler 200Hz → 250Hz
            epoch_250 = scipy_resample(epoch_raw, TARGET_SAMPLES)

            # Z-score (meme normalisation que le pipeline existant)
            mu, sigma = epoch_250.mean(), epoch_250.std()
            epoch_norm = (epoch_250 - mu) / (sigma + 1e-9)

            X_list.append(epoch_norm.astype(np.float32))
            y_list.append(float(row['conc_score']))
            subj_list.append(int(row['subject']))
            level_list.append(LEVEL_CODE.get(row['level'], -1))

    return {
        'X':        np.array(X_list,     dtype=np.float32),
        'y':        np.array(y_list,     dtype=np.float32),
        'subjects': np.array(subj_list,  dtype=np.int32),
        'levels':   np.array(level_list, dtype=np.int32),
    }


# ============================================================================
# FONCTION 2 : construire le dataset stress
# ============================================================================
def build_stress_dataset(df_scores: pd.DataFrame) -> dict:
    """
    OBJECTIF :
      Pour chaque epoch dans scored_stress.csv, lire le signal brut
      depuis le fichier .mat correspondant, le resampler a 250Hz,
      et l'associer a son stress_score.

    STRUCTURE DE df_scores :
      file | epoch_idx | task | subject | trial | stress_score | scales_score

    RESAMPLING :
      512 samples @128Hz → 1000 samples @250Hz

    CANAL UTILISE :
      Canal 0 = AF3 (electrode frontale gauche EMOTIV)
      Le plus proche de Fp2 (electrode utilisee dans l'app NeuroCap)

    RETOURNE :
      dict avec cles : X, y, subjects
    """
    X_list, y_list, subj_list = [], [], []

    groups = df_scores.groupby('file')
    print(f"[stress] {len(df_scores)} epochs dans {len(groups)} fichiers")

    for fn, grp in groups:
        filepath = RAW_STRESS / fn
        if not filepath.exists():
            print(f"  [SKIP] Fichier manquant : {filepath}")
            continue

        mat  = scipy.io.loadmat(filepath)
        data = mat['Data']   # (32, 3200)
        signal = data[CHANNEL_STRESS, :].astype(float)

        for _, row in grp.iterrows():
            idx   = int(row['epoch_idx'])
            start = idx * EPOCH_STRESS
            end   = start + EPOCH_STRESS

            if end > signal.shape[0]:
                continue

            epoch_raw = signal[start:end]

            # Resampler 128Hz → 250Hz
            epoch_250 = scipy_resample(epoch_raw, TARGET_SAMPLES)

            # Z-score
            mu, sigma = epoch_250.mean(), epoch_250.std()
            epoch_norm = (epoch_250 - mu) / (sigma + 1e-9)

            X_list.append(epoch_norm.astype(np.float32))
            y_list.append(float(row['stress_score']))
            subj_list.append(int(row['subject']))

    return {
        'X':        np.array(X_list,    dtype=np.float32),
        'y':        np.array(y_list,    dtype=np.float32),
        'subjects': np.array(subj_list, dtype=np.int32),
    }


# ============================================================================
# FONCTION 3 : valider et afficher les statistiques
# ============================================================================
def validate_and_print(name: str, data: dict) -> None:
    """
    OBJECTIF :
      Verifier que les arrays ont les bonnes dimensions et que les
      scores couvrent bien la plage [0, 10].

    VERIFIE :
      - len(X) == len(y) == len(subjects)
      - Pas de NaN ou Inf dans X
      - Scores dans [0, 10]
      - Distribution des scores par quantile
    """
    X, y = data['X'], data['y']
    subs = data['subjects']

    print(f"\n=== Validation {name} ===")
    print(f"  X shape         : {X.shape}")
    print(f"  y shape         : {y.shape}")
    print(f"  Sujets uniques  : {len(np.unique(subs))}")
    print(f"  Score min/max   : {y.min():.2f} / {y.max():.2f}")
    print(f"  Score moyenne   : {y.mean():.2f} (std={y.std():.2f})")
    print(f"  Quantiles [25,50,75] : {np.percentile(y,25):.2f} / "
          f"{np.percentile(y,50):.2f} / {np.percentile(y,75):.2f}")

    # NaN / Inf
    n_bad = np.isnan(X).sum() + np.isinf(X).sum()
    print(f"  NaN/Inf dans X  : {n_bad} {'(OK)' if n_bad==0 else 'PROBLEME !'}")

    # Scores hors [0, 10]
    out = ((y < 0) | (y > 10)).sum()
    print(f"  Scores hors [0,10]: {out} {'(OK)' if out==0 else 'ERREURS !'}")

    if 'levels' in data:
        for code, name_lvl in [(0,'natural'),(1,'lowlevel'),(2,'midlevel'),(3,'highlevel')]:
            mask = data['levels'] == code
            if mask.sum() > 0:
                print(f"  {name_lvl:12s}: {mask.sum():4d} epochs, "
                      f"score_moy={y[mask].mean():.2f}")


# ============================================================================
# FONCTION 4 : sauvegarder
# ============================================================================
def save_dataset(name: str, data: dict) -> None:
    """
    OBJECTIF :
      Sauvegarder les arrays dans data/Scoring/merged/.

    FICHIERS PRODUITS pour 'concentration' :
      X_concentration.npy        (N, 1000) float32
      y_conc_score.npy           (N,)      float32
      subjects_concentration.npy (N,)      int32
      levels_concentration.npy   (N,)      int32

    FICHIERS PRODUITS pour 'stress' :
      X_stress.npy               (N, 1000) float32
      y_stress_score.npy         (N,)      float32
      subjects_stress.npy        (N,)      int32
    """
    prefix = 'conc' if name == 'concentration' else 'stress'

    np.save(OUT_DIR / f"X_{name}.npy",        data['X'])
    np.save(OUT_DIR / f"y_{prefix}_score.npy", data['y'])
    np.save(OUT_DIR / f"subjects_{name}.npy",  data['subjects'])

    if 'levels' in data:
        np.save(OUT_DIR / f"levels_{name}.npy", data['levels'])

    print(f"\n  Sauvegarde {name} :")
    print(f"    X_{name}.npy              {data['X'].shape}")
    print(f"    y_{prefix}_score.npy       {data['y'].shape}")
    print(f"    subjects_{name}.npy        {data['subjects'].shape}")
    if 'levels' in data:
        print(f"    levels_{name}.npy          {data['levels'].shape}")


# ============================================================================
# POINT D'ENTREE
# ============================================================================
def main():
    """
    OBJECTIF :
      Orchestrer la creation des 2 datasets de regression.

    ORDRE :
      1. Charger les CSV de scoring
      2. Construire dataset concentration (X + y_conc_score)
      3. Construire dataset stress (X + y_stress_score)
      4. Valider + sauvegarder
    """
    print("=" * 60)
    print("NeuroCap — Merge Scoring → Datasets Regression")
    print("=" * 60)

    # ── Charger les CSV de scoring ────────────────────────────────────────
    csv_conc   = SCORE_DIR / "scored_concentration.csv"
    csv_stress = SCORE_DIR / "scored_stress.csv"

    if not csv_conc.exists():
        raise FileNotFoundError(f"Manquant : {csv_conc}\nExecutez concentration_scoring.py")
    if not csv_stress.exists():
        raise FileNotFoundError(f"Manquant : {csv_stress}\nExecutez stress_scoring.py")

    df_conc   = pd.read_csv(csv_conc)
    df_stress = pd.read_csv(csv_stress)
    print(f"\n  scored_concentration.csv : {len(df_conc)} epochs")
    print(f"  scored_stress.csv        : {len(df_stress)} epochs")

    # ── Dataset Concentration ─────────────────────────────────────────────
    print("\n[1/2] Construction dataset Concentration...")
    data_conc = build_concentration_dataset(df_conc)
    validate_and_print("Concentration", data_conc)
    save_dataset("concentration", data_conc)

    # ── Dataset Stress ────────────────────────────────────────────────────
    print("\n[2/2] Construction dataset Stress...")
    data_stress = build_stress_dataset(df_stress)
    validate_and_print("Stress", data_stress)
    save_dataset("stress", data_stress)

    # ── Resume final ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("DATASETS PRETS POUR LA REGRESSION")
    print("=" * 60)
    print(f"\n  data/Scoring/merged/")
    print(f"    X_concentration.npy        {data_conc['X'].shape}")
    print(f"    y_conc_score.npy           {data_conc['y'].shape}")
    print(f"    subjects_concentration.npy {data_conc['subjects'].shape}")
    print(f"    levels_concentration.npy   {data_conc['levels'].shape}")
    print()
    print(f"    X_stress.npy               {data_stress['X'].shape}")
    print(f"    y_stress_score.npy         {data_stress['y'].shape}")
    print(f"    subjects_stress.npy        {data_stress['subjects'].shape}")
    print()
    print("PROCHAINES ETAPES :")
    print("  ML  → extraire 63 features → LGBMRegressor (x4 modeles) x2 cibles")
    print("  DL  → X brut → 19 architectures (sortie 1 neurone) x2 cibles")
    print("  TL  → EEGNet finetuning (sortie 1 neurone) x2 cibles")


if __name__ == '__main__':
    main()
