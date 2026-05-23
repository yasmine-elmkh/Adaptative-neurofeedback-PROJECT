"""
NeuroCap EEG — Merge features + Construction mapping.json
==========================================================
Fusionne audio_features.csv + image_features.csv + video_features.csv
→ merged_features.csv  (base du moteur de recommandation)
→ mapping.json         (table lookup EEG state → contenu IDs)

Usage :
    cd C:\\neurocap_dataset\\metadata
    python merge_and_mapping.py
"""

import os
import json
import csv
import pandas as pd
from pathlib import Path

# ─── Chemins ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(os.path.dirname(os.path.abspath(__file__)))
METADATA_DIR = SCRIPT_DIR

AUDIO_CSV  = METADATA_DIR / "audio_features.csv"
IMAGE_CSV  = METADATA_DIR / "image_features_complete.csv"
VIDEO_CSV  = METADATA_DIR / "video_features_v2.csv"

MERGED_CSV   = METADATA_DIR / "merged_features.csv"
MAPPING_JSON = METADATA_DIR / "mapping.json"

# Dossiers dataset (pour vérification existence fichiers)
DATASET_ROOT = METADATA_DIR.parent
AUDIO_DIR    = DATASET_ROOT / "audio"
IMAGE_DIR    = DATASET_ROOT / "image"
VIDEO_DIR    = DATASET_ROOT / "videos"
GAMES_DIR    = DATASET_ROOT / "games"

# ─── Mapping état EEG → condition contenu ─────────────────────────────────────
# Basé sur le classifieur server_final.py
# "stress" → relax | "focus" → focus | "neutral" → transition
EEG_STATE_TO_CONDITION = {
    "stress":     "relax",
    "focus":      "focus",
    "neutral":    "transition",
    # Aliases
    "relax":      "relax",
    "transition": "transition",
}


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — CHARGEMENT ET NORMALISATION DES CSV
# ══════════════════════════════════════════════════════════════════════════════

def load_csv(path: Path, media_type: str) -> pd.DataFrame:
    """
    Charge un CSV de features et ajoute la colonne 'type'.
    Retourne un DataFrame avec au minimum : filename, condition, type.
    """
    if not path.exists():
        print(f"  [SKIP] Introuvable : {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["type"] = media_type

    # Normalise la colonne condition (minuscules, strip)
    if "condition" in df.columns:
        df["condition"] = df["condition"].str.lower().str.strip()

    print(f"  ✓ {path.name:<30} {len(df):>4} lignes  {len(df.columns):>3} colonnes")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — MERGE
# ══════════════════════════════════════════════════════════════════════════════

def merge_features():
    """
    Concatène les 3 DataFrames.
    Les colonnes spécifiques à un type auront NaN pour les autres — normal.
    """
    print("\n─── Chargement des CSV ───────────────────────────────")
    df_audio = load_csv(AUDIO_CSV, "audio")
    df_image = load_csv(IMAGE_CSV, "image")
    df_video = load_csv(VIDEO_CSV, "video")

    frames = [df for df in [df_audio, df_image, df_video] if not df.empty]

    if not frames:
        print("ERREUR : aucun CSV trouvé.")
        return pd.DataFrame()

    merged = pd.concat(frames, ignore_index=True, sort=False)

    # Colonnes prioritaires en premier
    priority = ["filename", "condition", "type"]
    rest     = [c for c in merged.columns if c not in priority]
    merged   = merged[priority + rest]

    # Remplir les NaN numériques par 0 (colonnes spécifiques à un type)
    num_cols = merged.select_dtypes(include="number").columns
    merged[num_cols] = merged[num_cols].fillna(0)

    print(f"\n  → merged_features.csv : {len(merged)} lignes × {len(merged.columns)} colonnes")

    # Résumé par type et condition
    print("\n  Répartition :")
    summary = merged.groupby(["type","condition"]).size().reset_index(name="count")
    for _, row in summary.iterrows():
        print(f"    {row['type']:<8} | {row['condition']:<12} | {row['count']:>4} items")

    merged.to_csv(MERGED_CSV, index=False)
    print(f"\n  ✓ Sauvegardé : {MERGED_CSV}")
    return merged


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — CONSTRUCTION mapping.json
# ══════════════════════════════════════════════════════════════════════════════

def build_mapping(merged: pd.DataFrame):
    """
    Construit la table de lookup :
    { eeg_state: { media_type: [filename, ...] } }

    Structure finale utilisée par server_final.py pour le lookup direct.
    """
    print("\n─── Construction mapping.json ────────────────────────")

    # Mapping EEG state → contenu
    mapping = {
        "stress": {
            "audio": [], "image": [], "video": [],
            "game":  {
                "coloriage": {
                    "mandala":     [],
                    "nature":      [],
                    "geometrique": []
                }
            }
        },
        "focus": {
            "audio": [], "image": [], "video": [],
            "game":  {
                "sudoku":  [],
                "memoire": [],
                "calcul":  [],
                "enigmes": []
            }
        },
        "neutral": {
            "audio": [], "image": [], "video": [],
            "game":  {
                "puzzle": []
            }
        }
    }

    # Condition → EEG state (inverse du mapping)
    condition_to_eeg = {
        "relax":      "stress",
        "focus":      "focus",
        "transition": "neutral",
    }

    # Remplir depuis merged_features.csv
    for _, row in merged.iterrows():
        condition = row.get("condition", "").lower().strip()
        media_type = row.get("type", "").lower().strip()
        filename   = str(row.get("filename", "")).strip()

        eeg_state = condition_to_eeg.get(condition)
        if not eeg_state:
            continue

        if media_type in ["audio", "image", "video"]:
            if filename not in mapping[eeg_state][media_type]:
                mapping[eeg_state][media_type].append(filename)

    # Ajouter les jeux depuis les dossiers (SVG + JSON)
    _add_games(mapping)

    # Statistiques
    print("\n  Contenu par état EEG :")
    for state, content in mapping.items():
        audio_n = len(content.get("audio", []))
        image_n = len(content.get("image", []))
        video_n = len(content.get("video", []))
        game_n  = sum(
            len(v) if isinstance(v, list) else sum(len(vv) for vv in v.values())
            for v in content.get("game", {}).values()
        )
        print(f"    {state:<10} → audio:{audio_n:>4}  image:{image_n:>4}  "
              f"video:{video_n:>4}  game:{game_n:>4}")

    with open(MAPPING_JSON, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ Sauvegardé : {MAPPING_JSON}")
    return mapping


def _add_games(mapping):
    """Ajoute les fichiers jeux au mapping depuis les dossiers."""

    # ── Coloriage (relax/stress) ───────────────────────────────────────────────
    for sub in ["mandala", "nature", "geometrique"]:
        folder = GAMES_DIR / "relax" / "coloriage" / sub
        if folder.exists():
            files = sorted(f.name for f in folder.iterdir() if f.suffix == ".svg")
            mapping["stress"]["game"]["coloriage"][sub] = files
            if files:
                print(f"    + coloriage/{sub} : {len(files)} SVG")

    # ── Focus games ───────────────────────────────────────────────────────────
    focus_games = {
        "sudoku":  ("focus", "sudoku",  ".json"),
        "memoire": ("focus", "memoire", ".json"),
        "calcul":  ("focus", "calcul",  ".json"),
        "enigmes": ("focus", "enigmes", ".json"),
    }
    for game_key, (cond_folder, sub_folder, ext) in focus_games.items():
        folder = GAMES_DIR / cond_folder / sub_folder
        if folder.exists():
            files = sorted(f.name for f in folder.iterdir() if f.suffix == ext)
            mapping["focus"]["game"][game_key] = files
            if files:
                print(f"    + {game_key} : {len(files)} JSON")

    # ── Puzzle (transition/neutral) ───────────────────────────────────────────
    puzzle_folder = GAMES_DIR / "transition" / "puzzle"
    if puzzle_folder.exists():
        files = sorted(f.name for f in puzzle_folder.iterdir() if f.suffix == ".json")
        mapping["neutral"]["game"]["puzzle"] = files
        if files:
            print(f"    + puzzle : {len(files)} JSON")


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — VÉRIFICATION FINALE
# ══════════════════════════════════════════════════════════════════════════════

def verify(mapping):
    """Vérifie que les fichiers référencés dans mapping.json existent réellement."""
    print("\n─── Vérification fichiers ────────────────────────────")

    missing = []
    checked = 0

    dir_map = {
        "audio": AUDIO_DIR,
        "image": IMAGE_DIR,
        "video": VIDEO_DIR,
    }

    for state, content in mapping.items():
        for media_type, files in content.items():
            if media_type == "game" or not isinstance(files, list):
                continue
            base_dir = dir_map.get(media_type)
            if not base_dir:
                continue
            for fname in files:
                # Chercher dans les sous-dossiers relax/focus/transition
                found = False
                for sub in ["relax", "focus", "transition"]:
                    path = base_dir / sub / fname
                    if path.exists():
                        found = True
                        break
                if not found:
                    missing.append(f"{media_type}/{fname}")
                checked += 1

    print(f"  Fichiers vérifiés : {checked}")
    if missing:
        print(f"  ⚠ Manquants ({len(missing)}) :")
        for m in missing[:10]:
            print(f"    - {m}")
        if len(missing) > 10:
            print(f"    ... et {len(missing)-10} autres")
    else:
        print(f"  ✓ Tous les fichiers sont présents")

    return len(missing) == 0


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def run():
    print("=" * 55)
    print("NeuroCap — Merge features + Mapping")
    print("=" * 55)

    # Étape 1+2 : Merge
    merged = merge_features()
    if merged.empty:
        print("\nERREUR : merge échoué — vérifier les CSV.")
        return

    # Étape 3 : Mapping
    mapping = build_mapping(merged)

    # Étape 4 : Vérification
    verify(mapping)

    print(f"\n{'='*55}")
    print("TERMINÉ")
    print(f"  merged_features.csv → {MERGED_CSV}")
    print(f"  mapping.json        → {MAPPING_JSON}")
    print(f"\nProchaine étape : intégrer mapping.json dans server_final.py")
    print(f"{'='*55}")


if __name__ == "__main__":
    run()