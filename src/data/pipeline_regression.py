"""
pipeline_regression.py
=======================
EMPLACEMENT : src/data/pipeline_regression.py

OBJECTIF :
  Coordonne le pipeline complet pour la REGRESSION (scores 0-10)
  en reutilisant les fonctions existantes de pipeline_fp2.py
  et augmentation_eeg.py SANS LES MODIFIER.

CE QUE CE FICHIER FAIT :
  1. Charge les signaux bruts + scores depuis les CSV de scoring
     → pipeline_fp2.load_concentration_with_scores()
     → pipeline_fp2.load_stress_with_scores()

  2. Separation train/val/test PAR SUJET (anti data leakage)
     → pipeline_fp2.split_by_subject()  [fonction existante]

  3. Augmentation sur TRAIN UNIQUEMENT (scores propagés automatiquement)
     → augmentation_eeg.augment_train_set()  [fonction existante]
     (np.tile(y_train, 2) fonctionne pour float comme pour int)

  4. Extraction de features DEUX METHODES (pre-calculees, pour comparaison) :
     → features_extraction.py : feat15 — 15 features legeres (embarquables ESP32)
     → feature_eng.py         : feat78 — 78 features avancees

  5. Sauvegarde :
     Signaux bruts    → data/Regression/augmented/  (pour DL et TL)
     feat15 + feat78  → Features/{conc,stress}/      (pour ML regression, 2 modeles)

SORTIES :
  data/Regression/
  ├── preprocessed/
  │   ├── X_conc.npy + y_conc.npy + subjects_conc.npy + levels_conc.npy
  │   └── X_stress.npy + y_stress.npy + subjects_stress.npy
  │
  └── augmented/
      ├── conc/
      │   ├── X_train_A.npy + y_train_A.npy   (signal brut, original)
      │   ├── X_train_B/C/D/FULL.npy           (signal brut augmente)
      │   ├── X_val.npy + y_val.npy
      │   ├── X_test.npy + y_test.npy
      │   └── subject_ids_train.npy
      └── stress/   (meme structure)

  Features/
  ├── conc/                                     ← MODEL CONCENTRATION (y = conc_score 0-10)
  │   ├── feat15_train_A/B/C/D/FULL.npy  (15 features legeres)
  │   ├── feat78_train_A/B/C/D/FULL.npy  (78 features avancees)
  │   ├── feat15_val.npy + feat15_test.npy
  │   ├── feat78_val.npy + feat78_test.npy
  │   ├── y_train_A/B/C/D/FULL.npy
  │   ├── y_val.npy + y_test.npy
  │   └── subject_ids_train_A/B/C/D/FULL.npy
  └── stress/   (meme structure)                ← MODEL STRESS (y = stress_score 0-10)

UTILISATION POUR ML/DL/TL :
  ML baseline (feat15) : calcule a la volee depuis data/Regression/augmented/
  ML avance (feat78)   : feat78_*.npy → SVR / RFR / XGBRegressor / LGBMRegressor
  DL                   : X_train_*.npy → 19 architectures (sortie 1 neurone)
  TL                   : X_train_*.npy → EEGNet finetuning (sortie 1 neurone)
  Comparaison          : feat15 vs feat78 → gain de 63 features supplementaires
"""

import sys
import numpy as np
from pathlib import Path

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT = Path(__file__).resolve().parents[2]

RAW_CONC   = PROJECT / "data" / "Dataset" / "Cognitive Load Assessment Concentration" / "raw_data"
RAW_STRESS = PROJECT / "data" / "Dataset" / "Stress_dataset" / "raw_data"
SCORE_CONC = PROJECT / "data" / "Scoring" / "scored_concentration.csv"
SCORE_STR  = PROJECT / "data" / "Scoring" / "scored_stress.csv"

OUT_PREP   = PROJECT / "data" / "Regression" / "preprocessed"
OUT_AUG    = PROJECT / "data" / "Regression" / "augmented"
OUT_FEAT   = PROJECT / "Features"

for d in [OUT_PREP,
          OUT_AUG / "conc", OUT_AUG / "stress",
          OUT_FEAT / "conc", OUT_FEAT / "stress"]:
    d.mkdir(parents=True, exist_ok=True)

# Ajouter src/data au path pour importer les modules existants
sys.path.insert(0, str(PROJECT / "src" / "data"))

from pipeline_fp2 import (
    load_concentration_with_scores,
    load_stress_with_scores,
)
from augmentation_eeg import augment_train_set, split_by_subject


# ============================================================================
# ETAPE 1 : CHARGEMENT ET PREPROCESSING
# ============================================================================

def step1_load_and_preprocess():
    """
    Charge les signaux bruts, applique le pipeline fp2 (filtre+DWT+epoch+zscore),
    et attache les scores depuis les CSV.

    Ce qu'on obtient :
      Concentration : X (N, 1000), y_score (N,), subjects (N,), levels (N,)
      Stress        : X (N, 1000), y_score (N,), subjects (N,)

    Pourquoi reutiliser pipeline_fp2 :
      Les filtres HP/LP/Notch/DWT sont scientifiquement valides et identiques
      au hardware. Pas de raison de les modifier pour la regression.
      Seule l'attribution des labels change (float score vs int binaire).
    """
    print("\n" + "="*60)
    print("ETAPE 1 — Chargement + Preprocessing")
    print("="*60)

    # Concentration (OpenBCI, 200 Hz → 250 Hz)
    print("\n[1/2] Concentration...")
    X_conc, y_conc, subs_conc, lvl_conc = load_concentration_with_scores(
        SCORE_CONC, RAW_CONC
    )
    np.save(OUT_PREP / "X_conc.npy",        X_conc)
    np.save(OUT_PREP / "y_conc.npy",        y_conc)
    np.save(OUT_PREP / "subjects_conc.npy", subs_conc)
    np.save(OUT_PREP / "levels_conc.npy",   lvl_conc)
    print(f"  Sauvegarde : X_conc {X_conc.shape}, y_conc [{y_conc.min():.1f}-{y_conc.max():.1f}]")

    # Stress (EMOTIV, 128 Hz → 250 Hz)
    print("\n[2/2] Stress...")
    X_str, y_str, subs_str = load_stress_with_scores(
        SCORE_STR, RAW_STRESS
    )
    np.save(OUT_PREP / "X_stress.npy",        X_str)
    np.save(OUT_PREP / "y_stress.npy",        y_str)
    np.save(OUT_PREP / "subjects_stress.npy", subs_str)
    print(f"  Sauvegarde : X_stress {X_str.shape}, y_stress [{y_str.min():.1f}-{y_str.max():.1f}]")

    return (X_conc, y_conc, subs_conc), (X_str, y_str, subs_str)


# ============================================================================
# ETAPE 2 : SPLIT PAR SUJET
# ============================================================================

def step2_split(X, y, subjects, name):
    """
    Split train/val/test PAR SUJET (70/15/15).
    Reutilise split_by_subject() de pipeline_fp2.py SANS MODIFICATION.

    Pourquoi par sujet (rappel) :
      Si on splitte par epoch, le meme sujet peut etre en train ET en test.
      Ses epochs sont correlees → le modele "memorise" sa signature EEG.
      La vraie generalisation = un sujet JAMAIS vu pendant l'entrainement.
    """
    print(f"\n[split] {name} — {len(X)} epochs, {len(np.unique(subjects))} sujets")

    (X_tr, y_tr, sids_tr,
     X_vl, y_vl, sids_vl,
     X_te, y_te, sids_te) = split_by_subject(
         X, y, subjects, test_ratio=0.15, val_ratio=0.15, seed=42
     )

    print(f"  Train : {len(X_tr)} epochs ({len(np.unique(sids_tr))} sujets)")
    print(f"  Val   : {len(X_vl)} epochs ({len(np.unique(sids_vl))} sujets)")
    print(f"  Test  : {len(X_te)} epochs ({len(np.unique(sids_te))} sujets)")

    # Verifier qu'aucun sujet n'est partage
    assert len(set(sids_tr) & set(sids_te)) == 0, "ERREUR : sujet partage train/test !"
    assert len(set(sids_tr) & set(sids_vl)) == 0, "ERREUR : sujet partage train/val !"
    print("  Anti data leakage : OK (sujets disjoints)")

    return (X_tr, y_tr, sids_tr), (X_vl, y_vl, sids_vl), (X_te, y_te, sids_te)


# ============================================================================
# ETAPE 3 : AUGMENTATION (TRAIN UNIQUEMENT)
# ============================================================================

def step3_augment(X_train, y_train, out_subdir):
    """
    Applique les 4 techniques d'augmentation sur le train uniquement.
    Reutilise augment_train_set() de augmentation_eeg.py SANS MODIFICATION.

    Propagation des scores :
      np.tile(y_train, 2) copie exactement les scores pour chaque epoch augmentee.
      Justification : ajouter du bruit gaussien a un epoch de conc_score=8.5
      ne change pas l'etat cognitif du sujet → score conserve.

    Note : y_train ici est un float array (scores) et non int.
      augment_train_set() utilise np.tile() qui fonctionne pour float ET int.
      Aucune modification de augmentation_eeg.py n'est necessaire.
    """
    print(f"\n[augmentation] {out_subdir.name} — {len(X_train)} epochs train")

    datasets, _, _, _ = augment_train_set(X_train, y_train, seed=42)

    for exp_name, (X_aug, y_aug) in datasets.items():
        np.save(out_subdir / f"X_train_{exp_name}.npy", X_aug.astype(np.float32))
        np.save(out_subdir / f"y_train_{exp_name}.npy", y_aug.astype(np.float32))
        print(f"  Exp {exp_name}: X={X_aug.shape}, y=[{y_aug.min():.1f}-{y_aug.max():.1f}]")


# ============================================================================
# ETAPE 4 : EXTRACTION DE FEATURES (2 METHODES POUR COMPARAISON)
# ============================================================================

def step4_extract_features(X_aug_dir, feat_out_dir, dataset_name):
    """
    Extrait feat15 (features_extraction.py) ET feat78 (feature_eng.py).

    Les deux vecteurs sont pre-calcules pour permettre la comparaison directe
    dans les baselines de regression (2 modeles separes : conc et stress).

    Sorties dans Features/{conc,stress}/ :
      feat15_train_{A,B,C,D,FULL}.npy  — 15 features legeres (embarquables ESP32)
      feat78_train_{A,B,C,D,FULL}.npy  — 78 features avancees (feature_eng)
      y_train_{A,B,C,D,FULL}.npy       — scores regression (0-10)
      feat15_val/test.npy + feat78_val/test.npy + y_val/test.npy
      subject_ids_train_{A,B,C,D,FULL}.npy
    """
    from feature_eng import extract_all_features
    from features_extraction import get_feature_vector

    print(f"\n[features] {dataset_name}")

    for exp_name in ['A', 'B', 'C', 'D', 'FULL']:
        x_path = X_aug_dir / f"X_train_{exp_name}.npy"
        y_path = X_aug_dir / f"y_train_{exp_name}.npy"
        if not x_path.exists():
            continue

        X_ep = np.load(x_path)
        y_sc = np.load(y_path)

        # feat15 — 15 features legeres (features_extraction.py)
        feat15 = np.array([get_feature_vector(ep) for ep in X_ep], dtype=np.float32)
        feat15 = np.nan_to_num(feat15, nan=0.0, posinf=0.0, neginf=0.0)
        np.save(feat_out_dir / f"feat15_train_{exp_name}.npy", feat15)
        print(f"  Exp {exp_name}: feat15 {feat15.shape}")

        # feat78 — 78 features avancees (feature_eng.py)
        feat78 = np.array([
            list(extract_all_features(ep).values()) for ep in X_ep
        ], dtype=np.float32)
        feat78 = np.nan_to_num(feat78, nan=0.0, posinf=0.0, neginf=0.0)
        np.save(feat_out_dir / f"feat78_train_{exp_name}.npy", feat78)
        np.save(feat_out_dir / f"y_train_{exp_name}.npy",      y_sc)
        print(f"  Exp {exp_name}: feat78 {feat78.shape}")

        # subject_ids train (tiled selon l'experience) — pour LOSO dans les baselines
        sid_path = X_aug_dir / "subject_ids_train.npy"
        if sid_path.exists():
            sid_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 2, 'FULL': 4}
            sids_orig  = np.load(sid_path)
            sids_tiled = np.tile(sids_orig, sid_mapping.get(exp_name, 1))[:len(feat78)]
            np.save(feat_out_dir / f"subject_ids_train_{exp_name}.npy",
                    sids_tiled.astype(np.int32))

    # Val et Test — feat15 + feat78
    for split in ['val', 'test']:
        x_path = X_aug_dir / f"X_{split}.npy"
        y_path = X_aug_dir / f"y_{split}.npy"
        if not x_path.exists():
            continue
        X_ep = np.load(x_path)
        y_sc = np.load(y_path)

        feat15 = np.array([get_feature_vector(ep) for ep in X_ep], dtype=np.float32)
        feat15 = np.nan_to_num(feat15, nan=0.0, posinf=0.0, neginf=0.0)
        np.save(feat_out_dir / f"feat15_{split}.npy", feat15)

        feat78 = np.array([
            list(extract_all_features(ep).values()) for ep in X_ep
        ], dtype=np.float32)
        feat78 = np.nan_to_num(feat78, nan=0.0, posinf=0.0, neginf=0.0)
        np.save(feat_out_dir / f"feat78_{split}.npy", feat78)
        np.save(feat_out_dir / f"y_{split}.npy",      y_sc)
        print(f"  {split}: feat15 {feat15.shape} | feat78 {feat78.shape}")


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def run_regression_pipeline():
    """
    Execute le pipeline complet dans l'ordre logique :
      1. Load + Preprocess (pipeline_fp2 existant + scores)
      2. Split par sujet   (pipeline_fp2 existant)
      3. Augmentation      (augmentation_eeg existant)
      4. Feature eng       (feat15 a la volee dans baselines, feat78 pre-calcule)
    """
    print("="*60)
    print("NeuroCap — Pipeline Regression Complet")
    print("Reutilise pipeline_fp2 + augmentation_eeg SANS MODIFICATION")
    print("="*60)

    # ── Etape 1 : Chargement + Preprocessing ─────────────────────────────
    (X_conc, y_conc, subs_conc), (X_str, y_str, subs_str) = step1_load_and_preprocess()

    # ── Etape 2 : Split par sujet ─────────────────────────────────────────
    print("\n" + "="*60)
    print("ETAPE 2 — Split par sujet (anti data leakage)")
    print("="*60)

    (Xtr_c, ytr_c, sids_tr_c), (Xvl_c, yvl_c, _), (Xte_c, yte_c, _) = \
        step2_split(X_conc, y_conc, subs_conc, "Concentration")

    (Xtr_s, ytr_s, sids_tr_s), (Xvl_s, yvl_s, _), (Xte_s, yte_s, _) = \
        step2_split(X_str, y_str, subs_str, "Stress")

    # Sauvegarder val, test et subject_ids train (pour LOSO dans les baselines)
    for arr, name in [
        (Xvl_c, "conc/X_val"),    (yvl_c, "conc/y_val"),
        (Xte_c, "conc/X_test"),   (yte_c, "conc/y_test"),
        (Xvl_s, "stress/X_val"),  (yvl_s, "stress/y_val"),
        (Xte_s, "stress/X_test"), (yte_s, "stress/y_test"),
    ]:
        np.save(OUT_AUG / name, arr.astype(np.float32))

    # subject_ids du train (pour LOSO des baselines de régression)
    np.save(OUT_AUG / "conc"   / "subject_ids_train.npy", sids_tr_c.astype(np.int32))
    np.save(OUT_AUG / "stress" / "subject_ids_train.npy", sids_tr_s.astype(np.int32))

    # ── Etape 3 : Augmentation ────────────────────────────────────────────
    print("\n" + "="*60)
    print("ETAPE 3 — Augmentation (train uniquement, scores propagés)")
    print("="*60)

    step3_augment(Xtr_c, ytr_c, OUT_AUG / "conc")
    step3_augment(Xtr_s, ytr_s, OUT_AUG / "stress")

    # ── Etape 4 : Features ────────────────────────────────────────────────
    print("\n" + "="*60)
    print("ETAPE 4 — Extraction features (feat15 + feat78 → Features/{conc,stress}/)")
    print("="*60)

    step4_extract_features(OUT_AUG / "conc",   OUT_FEAT / "conc",   "Concentration")
    step4_extract_features(OUT_AUG / "stress",  OUT_FEAT / "stress", "Stress")

    # ── Resume ────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("PIPELINE REGRESSION TERMINE")
    print("="*60)
    print(f"\n  data/Regression/preprocessed/    ← signaux + scores (0-10)")
    print(f"  data/Regression/augmented/conc/  ← 5 exp x (X, y_conc)  [MODEL CONC]")
    print(f"  data/Regression/augmented/stress/← 5 exp x (X, y_stress)[MODEL STRESS]")
    print(f"  Features/conc/                   ← feat15 + feat78 x 5 exp")
    print(f"  Features/stress/                 ← feat15 + feat78 x 5 exp")
    print()
    print("2 MODELES DE REGRESSION SEPARES :")
    print("  Modele CONC   → predit conc_score  (0-10) depuis epochs Concentration")
    print("  Modele STRESS → predit stress_score(0-10) depuis epochs SAM40")
    print()
    print("COMPARAISON feat15 vs feat78 :")
    print("  feat15 (15 features) : python src/models/baselines/baseline_ML_regression.py")
    print("  feat78 (78 features) : python src/models/baselines/baseline_ML_regression_feature_eng.py")
    print("  Comparaison directe  : python src/models/baselines/compare_regression_features.py")
    print()
    print("DL / TL :")
    print("  DL  : X_train_A.npy → 19 architectures (sortie 1 neurone + HuberLoss)")
    print("  TL  : X_train_A.npy → EEGNet finetuning regression")


if __name__ == '__main__':
    run_regression_pipeline()
