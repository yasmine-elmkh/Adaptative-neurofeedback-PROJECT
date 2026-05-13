"""
NeuroCap – Fusion réelle des datasets (version corrigée)
Cognitive Load : lecture adaptative des .txt (détection du format)
SAM40 : utilise la variable 'Data' des .mat, extrait canal Fp2 (index 1)
"""

import numpy as np
import pandas as pd
from scipy import signal
from scipy.io import loadmat
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONSTANTES
# ============================================================================
FS_TARGET = 250
FS_SAM40 = 128
EPOCH_S = 4.0
EPOCH_SAMPLES = int(EPOCH_S * FS_TARGET)
OVERLAP = 0.5
STRESS_THRESHOLD = 6

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
COGNITIVE_ARITH = PROJECT_ROOT  / "data" /"Dataset" / "Cognitive Load Assessment Concentration" / "raw_data" / "Arithmetic_Data"
COGNITIVE_STROOP = PROJECT_ROOT  / "data" / "Dataset" / "Cognitive Load Assessment Concentration" / "raw_data" / "Stroop_Data"
SAM40_RAW = PROJECT_ROOT / "data" / "Dataset" / "Stress_dataset" / "raw_data"
SCALES_FILE = PROJECT_ROOT / "data" / "Dataset" / "Stress_dataset" / "scales.xls"

# ============================================================================
# FONCTIONS
# ============================================================================
def segment_epochs(signal_1d, fs, epoch_s, overlap=0.5):
    epoch_samples = int(fs * epoch_s)
    step = int(epoch_samples * (1 - overlap))
    epochs = []
    for start in range(0, len(signal_1d) - epoch_samples + 1, step):
        epochs.append(signal_1d[start:start+epoch_samples])
    return np.array(epochs)

def preprocess_and_normalize(epoch, fs):
    b, a = signal.butter(4, 0.5/(fs/2), btype='high')
    epoch = signal.filtfilt(b, a, epoch)
    b, a = signal.butter(4, 40/(fs/2), btype='low')
    epoch = signal.filtfilt(b, a, epoch)
    b, a = signal.iirnotch(50/(fs/2), Q=30)
    epoch = signal.filtfilt(b, a, epoch)
    mu, sigma = epoch.mean(), epoch.std()
    if sigma > 1e-10:
        epoch = (epoch - mu) / sigma
    return epoch

def resample_epoch(epoch, fs_orig, fs_target):
    n_target = int(len(epoch) * fs_target / fs_orig)
    return signal.resample(epoch, n_target)

# ----------------------------------------------------------------------
# COGNITIVE LOAD : lecture adaptative avec inspection
# ----------------------------------------------------------------------
def inspect_cognitive_file(filepath):
    """Affiche les premières lignes d'un fichier pour déboguer."""
    print(f"\n--- Inspection de {filepath.name} ---")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines[:10]):
        print(f"Ligne {i+1}: {repr(line[:100])}")

def read_cognitive_load_file(filepath, channel_idx=1):
    """
    Lit un fichier .txt du dataset Cognitive Load.
    Détecte automatiquement le nombre de canaux par ligne.
    Retourne le signal du canal spécifié (index 0 = premier canal, 1 = deuxième...).
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Ignorer les premières lignes non numériques (metadata)
    data_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remplacer les virgules par des espaces
        line_clean = line.replace(',', ' ')
        parts = line_clean.split()
        # Tenter de convertir en float au moins la première partie
        try:
            float(parts[0])
            data_lines.append(parts)
        except ValueError:
            # Ligne non numérique, on l'ignore
            continue
    
    if not data_lines:
        return np.array([])
    
    # Déterminer le nombre de canaux (largeur de la ligne)
    n_channels = len(data_lines[0])
    if channel_idx >= n_channels:
        # Si l'index demandé est trop grand, on prend le dernier canal
        channel_idx = n_channels - 1
        print(f"  Avertissement: canal demandé trop grand, utilisation du canal {channel_idx}")
    
    values = []
    for parts in data_lines:
        try:
            val = float(parts[channel_idx])
            values.append(val)
        except:
            continue
    return np.array(values)

def load_cognitive_load_fp2():
    """Charge les époques highlevel des 15 sujets (Arithmetic + Stroop)."""
    X_list, y_list, sids_list = [], [], []
    
    # Premier fichier pour inspection
    first_file = COGNITIVE_ARITH / "highlevel-1.txt"
    if first_file.exists():
        inspect_cognitive_file(first_file)
    else:
        print(f"Fichier test non trouvé: {first_file}")
    
    for subject_id in range(1, 16):
        for task_dir, task_name in [(COGNITIVE_ARITH, "Arithmetic"), (COGNITIVE_STROOP, "Stroop")]:
            filepath = task_dir / f"highlevel-{subject_id}.txt"
            if not filepath.exists():
                continue
            raw_signal = read_cognitive_load_file(filepath, channel_idx=1)  # canal Fp2 (index 1)
            if len(raw_signal) == 0:
                print(f"  [Cognitive] Aucune donnée dans {filepath}")
                continue
            epochs = segment_epochs(raw_signal, FS_TARGET, EPOCH_S, overlap=OVERLAP)
            for ep in epochs:
                ep_proc = preprocess_and_normalize(ep, FS_TARGET)
                X_list.append(ep_proc)
                y_list.append(0)
                sids_list.append(subject_id - 1)
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    sids = np.array(sids_list, dtype=np.int32)
    print(f"  Cognitive Load : {len(X)} époques, {len(np.unique(sids))} sujets (0-14)")
    return X, y, sids

# ----------------------------------------------------------------------
# SAM40 : utilise la variable 'Data' (détectée)
# ----------------------------------------------------------------------
def load_sam40_stress_fp2(threshold=STRESS_THRESHOLD):
    # Lecture de scales.xls
    scales_df = pd.read_excel(SCALES_FILE)
    # Structure connue : première ligne d'en-tête, puis données.
    # La colonne 'Subject No.' contient les numéros de sujet (1-based), puis les colonnes de scores sont Trial_1, Trial_2, Trial_3
    # mais chaque trial contient 3 sous-colonnes (Maths, Symmetry, Stroop). On prend les scores pour Maths (c'est l'arithmétique).
    # D'après l'affichage, les colonnes sont: 'Subject No.', 'Trial_1', 'Unnamed: 2', 'Unnamed: 3', 'Trial_2', ...
    # Les valeurs numériques sont dans les colonnes 'Trial_1', 'Unnamed: 2', etc. Pour Maths, c'est la première colonne de chaque trial (Trial_1, Trial_2, Trial_3)
    # On va extraire les scores pour Maths : colonnes Trial_1, Trial_2, Trial_3 (les valeurs directement sous ces colonnes, pas les sous-colonnes)
    # Mais attention: la ligne 0 contient 'Maths', 'Symmetry', 'Stroop' pour chaque trial. Les valeurs numériques commencent à la ligne 1.
    # On va donc prendre les valeurs des colonnes 'Trial_1', 'Trial_2', 'Trial_3' (elles contiennent les notes de Maths).
    # Cependant, ces colonnes ont des NaN sur les lignes d'en-tête, mais pandas les lit correctement.
    stress_scores = {}
    for idx, row in scales_df.iterrows():
        subj_id = row['Subject No.']
        if pd.isna(subj_id):
            continue
        subj_id = int(subj_id) - 1  # 0-based
        # Prendre les scores des colonnes Trial_1, Trial_2, Trial_3 (qui sont les scores Maths)
        scores = []
        for trial in ['Trial_1', 'Trial_2', 'Trial_3']:
            val = row[trial]
            if pd.notna(val):
                try:
                    scores.append(float(val))
                except:
                    pass
        if scores:
            stress_scores[subj_id] = max(scores)
        else:
            stress_scores[subj_id] = 0
    
    X_list, y_list, sids_list = [], [], []
    for sid in range(40):
        if stress_scores.get(sid, 0) < threshold:
            print(f"  [SAM40] Sujet {sid}: stress {stress_scores.get(sid,0)} < {threshold} → ignoré")
            continue
        
        # Trouver les fichiers .mat pour ce sujet (Arithmetic_sub_{sid+1}_trial*.mat)
        mat_files = sorted(SAM40_RAW.glob(f"*Arithmetic_sub_{sid+1}_trial*.mat"))
        if not mat_files:
            # Essayer sans 'Arithmetic_'
            mat_files = sorted(SAM40_RAW.glob(f"*sub_{sid+1}*.mat"))
        if not mat_files:
            print(f"  [SAM40] Sujet {sid}: aucun fichier .mat trouvé")
            continue
        
        for mat_path in mat_files:
            try:
                mat = loadmat(mat_path)
                if 'Data' not in mat:
                    print(f"  Variable 'Data' absente dans {mat_path.name}, ignoré")
                    continue
                data = mat['Data']  # shape (channels, timepoints)
                if data.ndim == 3:
                    data = data[0,0]
                # Extraire le canal Fp2 (index 1, car 32 canaux)
                if data.shape[0] < 2:
                    print(f"  Pas assez de canaux dans {mat_path.name}")
                    continue
                fp2 = data[1, :]  # 2ème canal = Fp2
                # Segmentation en époques (le signal fait 25s à 128 Hz = 3200 points, donc 25s / 4s = 6.25 époques avec overlap)
                epochs = segment_epochs(fp2, FS_SAM40, EPOCH_S, overlap=OVERLAP)
                for ep in epochs:
                    ep_250 = resample_epoch(ep, FS_SAM40, FS_TARGET)
                    ep_proc = preprocess_and_normalize(ep_250, FS_TARGET)
                    X_list.append(ep_proc)
                    y_list.append(1)
                    sids_list.append(sid)
            except Exception as e:
                print(f"  Erreur traitement {mat_path.name}: {e}")
    
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    sids = np.array(sids_list, dtype=np.int32)
    print(f"  SAM40 (stress ≥ {threshold}) : {len(X)} époques, {len(np.unique(sids))} sujets (0-39)")
    return X, y, sids

# ----------------------------------------------------------------------
# FUSION ET SAUVEGARDE
# ----------------------------------------------------------------------
def merge_datasets(X_conc, y_conc, sids_conc, X_stress, y_stress, sids_stress, offset=15):
    sids_stress_offset = sids_stress + offset
    X = np.concatenate([X_conc, X_stress], axis=0)
    y = np.concatenate([y_conc, y_stress], axis=0)
    sids = np.concatenate([sids_conc, sids_stress_offset], axis=0)
    print("\n" + "="*60)
    print("FUSION DES DATASETS")
    print("="*60)
    print(f"  Concentration : {len(X_conc)} époques")
    print(f"  Stress        : {len(X_stress)} époques")
    print(f"  Total         : {len(X)} époques")
    print(f"  Sujets uniques: {len(np.unique(sids))}")
    print(f"  IDs concentration : [{sids_conc.min()}-{sids_conc.max()}]")
    print(f"  IDs stress        : [{sids_stress_offset.min()}-{sids_stress_offset.max()}]")
    return X, y, sids

def save_merged_dataset(X, y, sids, outdir=PROJECT_ROOT / 'data' / 'Merge_datasets' / 'datasets_merged'):
    os.makedirs(outdir, exist_ok=True)
    np.save(os.path.join(outdir, 'X_merged.npy'), X)
    np.save(os.path.join(outdir, 'y_merged.npy'), y)
    np.save(os.path.join(outdir, 'subject_ids_merged.npy'), sids)
    print(f"\n  ✅ Sauvegardé dans {outdir}/")
    print(f"     X_merged.npy : {X.shape}")
    print(f"     y_merged.npy : {y.shape}")
    print(f"     subject_ids_merged.npy : {sids.shape}")

# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
if __name__ == '__main__':
    print("Chargement des données réelles...\n")
    X_conc, y_conc, sids_conc = load_cognitive_load_fp2()
    X_stress, y_stress, sids_stress = load_sam40_stress_fp2(threshold=STRESS_THRESHOLD)
    
    if len(X_conc) == 0:
        print("\n❌ Aucune donnée Cognitive Load chargée. Vérifiez les chemins et le format des fichiers .txt")
        exit(1)
    if len(X_stress) == 0:
        print("\n❌ Aucune donnée SAM40 chargée.")
        exit(1)
    
    X_merged, y_merged, sids_merged = merge_datasets(
        X_conc, y_conc, sids_conc,
        X_stress, y_stress, sids_stress,
        offset=15
    )
    save_merged_dataset(X_merged, y_merged, sids_merged, PROJECT_ROOT / 'data' / 'Merge_datasets' / 'datasets_merged')
    print("\n✅ Fusion terminée. Lancez maintenant le pipeline d'augmentation.")