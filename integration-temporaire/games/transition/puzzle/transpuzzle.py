"""
NeuroCap — Génération Puzzles Transition (Multitypes)
======================================================
120 configurations JSON : 3 types × 8 niveaux × 5 puzzles
Condition : transition | EEG target : alpha-beta équilibré

Types :
  jigsaw   → reconstruction image, alpha léger
  sliding  → taquin, beta léger
  tangram  → formes géométriques, alpha-beta équilibré

Justification : Csikszentmihalyi 1990 — état de flow
                alpha-beta balance = état de transition optimal

Usage : python transpuzzle.py
→ génère 120 JSON + transpuzzle_features.csv dans games/transition/puzzle/
"""

import json
import csv
import math
from pathlib import Path

BASE_DIR = Path(r"C:\neurocap_dataset\games\transition\puzzle")

PUZZLE_TYPES = {
    "jigsaw": {
        "description":  "Reconstruction image — scan visuel doux",
        "eeg_effect":   "alpha_leger",
        "alpha_weight": 0.65,
        "beta_weight":  0.35,
    },
    "sliding": {
        "description":  "Taquin — logique séquentielle spatiale",
        "eeg_effect":   "beta_leger",
        "alpha_weight": 0.45,
        "beta_weight":  0.55,
    },
    "tangram": {
        "description":  "Formes géométriques — rotation mentale",
        "eeg_effect":   "alpha_beta_equilibre",
        "alpha_weight": 0.50,
        "beta_weight":  0.50,
    },
}

LEVELS = {
    1: {"label": "Ultra doux",  "pieces": 4},
    2: {"label": "Très facile", "pieces": 6},
    3: {"label": "Facile",      "pieces": 9},
    4: {"label": "Modéré",      "pieces": 12},
    5: {"label": "Moyen",       "pieces": 16},
    6: {"label": "Stimulant",   "pieces": 20},
    7: {"label": "Concentré",   "pieces": 25},
    8: {"label": "Avancé",      "pieces": 30},
}

PUZZLES_PER_LEVEL = 5


def calculate_features(puzzle_type, n_pieces, level, type_info):
    """Calcule les features neurofeedback pour la transition."""

    # Indice de récompense dopaminergique
    dopamine_reward_rate = round(1.0 - (n_pieces / 40), 2)

    # Charge spatiale (rotation mentale)
    spatial_load = round(n_pieces / 30, 2)
    if puzzle_type == "tangram":
        spatial_load = round(spatial_load * 1.5, 2)
    spatial_load = min(spatial_load, 1.0)

    # Équilibre alpha/beta
    alpha_beta_balance = round(
        type_info["alpha_weight"] / type_info["beta_weight"], 2
    )

    # Temps estimé
    expected_time_s = n_pieces * (8 - min(level, 7))

    # Complexité combinatoire
    cognitive_load = round(
        math.lgamma(n_pieces + 1) / math.lgamma(30 + 1), 4
    )

    return {
        "n_pieces":                   n_pieces,
        "dopamine_reward_rate":       dopamine_reward_rate,
        "spatial_reasoning_demand":   spatial_load,
        "alpha_beta_balance_index":   alpha_beta_balance,
        "alpha_weight":               type_info["alpha_weight"],
        "beta_weight":                type_info["beta_weight"],
        "cognitive_load":             cognitive_load,
        "expected_completion_time_s": expected_time_s,
        "difficulty_index":           round(level / 8, 2),
    }


def generate_puzzles():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    total = 0

    print("=" * 60)
    print("NeuroCap — Génération Puzzles Transition (Multitypes)")
    print("=" * 60)

    for p_type, type_info in PUZZLE_TYPES.items():
        print(f"\nType : {p_type.upper()} — {type_info['description']}")

        for level, level_info in LEVELS.items():
            n_pieces = level_info["pieces"]
            cols = math.ceil(math.sqrt(n_pieces))
            rows = math.ceil(n_pieces / cols)
            feats = calculate_features(p_type, n_pieces, level, type_info)

            for i in range(1, PUZZLES_PER_LEVEL + 1):
                puzzle_id = f"PUZ_{p_type[:3].upper()}_NIV{level}_{i:03d}"
                filepath  = BASE_DIR / f"{puzzle_id}.json"

                data = {
                    "id":          puzzle_id,
                    "filename":    f"{puzzle_id}.json",
                    "type":        p_type,
                    "level":       level,
                    "label":       level_info["label"],
                    "condition":   "transition",
                    "eeg_target":  "transition",
                    "eeg_effect":  type_info["eeg_effect"],
                    "grid_size":   [rows, cols],
                    "n_pieces":    n_pieces,
                    "features":    feats,
                }

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                total += 1

                all_metadata.append({
                    "filename":                   f"{puzzle_id}.json",
                    "condition":                  "transition",
                    "type":                       p_type,
                    "level":                      level,
                    "label":                      level_info["label"],
                    "eeg_target":                 "transition",
                    "eeg_effect":                 type_info["eeg_effect"],
                    "n_pieces":                   n_pieces,
                    "dopamine_reward_rate":        feats["dopamine_reward_rate"],
                    "spatial_reasoning_demand":    feats["spatial_reasoning_demand"],
                    "alpha_beta_balance_index":    feats["alpha_beta_balance_index"],
                    "cognitive_load":              feats["cognitive_load"],
                    "expected_completion_time_s":  feats["expected_completion_time_s"],
                    "difficulty_index":            feats["difficulty_index"],
                })

            print(f"  Niveau {level} ({level_info['label']:12s} "
                  f"{n_pieces:2d} pièces) : {PUZZLES_PER_LEVEL} puzzles")

    # Export CSV features
    meta_path = BASE_DIR / "transpuzzle_features.csv"
    with open(meta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_metadata[0].keys())
        w.writeheader()
        w.writerows(all_metadata)

    print(f"\n{'='*60}")
    print(f"Terminé : {total} puzzles générés")
    print(f"Types   : jigsaw, sliding, tangram")
    print(f"CSV     : {meta_path}")
    print(f"Dossier : {BASE_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    generate_puzzles()