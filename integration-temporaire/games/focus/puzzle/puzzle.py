"""
NeuroCap — Génération Puzzle Focus
====================================
40 configurations JSON : 8 × 5 niveaux
Condition : focus | EEG target : beta préfrontal
Justification : Shepard & Metzler 1971 — rotation mentale → beta

Usage : python puzzle_focus.py
→ génère 40 JSON + puzzle_focus_features.csv dans games/focus/puzzle/
"""

import json
import csv
import math
from pathlib import Path

BASE_DIR = Path(r"C:\neurocap_dataset\games\focus\puzzle")

LEVELS = {
    1: {"grid": [3, 3], "label": "Très facile", "eeg_target": "focus_faible"},
    2: {"grid": [4, 4], "label": "Facile",      "eeg_target": "focus_faible"},
    3: {"grid": [5, 5], "label": "Moyen",       "eeg_target": "focus_moyen"},
    4: {"grid": [6, 6], "label": "Difficile",   "eeg_target": "focus_eleve"},
    5: {"grid": [8, 8], "label": "Expert",      "eeg_target": "focus_eleve"},
}

GRIDS_PER_LEVEL = 8


def calculate_features(grid_x, grid_y, level):
    n_pieces = grid_x * grid_y

    # Complexité combinatoire via log(n!) — Shepard & Metzler 1971
    combinatorial = math.lgamma(n_pieces + 1)
    max_complex   = math.lgamma(64 + 1)
    cognitive_load = round(combinatorial / max_complex, 4)

    # Temps estimé : plus le niveau est élevé, plus chaque pièce prend du temps
    time_per_piece    = 5 + (level * 2.5)
    expected_time_s   = int(n_pieces * time_per_piece)

    return {
        "n_pieces":                   n_pieces,
        "grid_rows":                  grid_x,
        "grid_cols":                  grid_y,
        "cognitive_load":             cognitive_load,
        "visual_search_complexity":   round(n_pieces / 64, 4),
        "expected_completion_time_s": expected_time_s,
        "difficulty_index":           round(level / 5, 2),
        "beta_demand":                round(0.3 + level * 0.14, 2),
    }


def generate_puzzles():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    total = 0

    print("=" * 55)
    print("NeuroCap — Génération Puzzle Focus")
    print("=" * 55)

    for level, info in LEVELS.items():
        grid_x, grid_y = info["grid"]
        feats = calculate_features(grid_x, grid_y, level)

        print(f"\nNiveau {level} — {info['label']} "
              f"({grid_x}×{grid_y} = {feats['n_pieces']} pièces)")

        for i in range(1, GRIDS_PER_LEVEL + 1):
            puzzle_id = f"PUZ_NIV{level}_{i:03d}"
            filepath  = BASE_DIR / f"{puzzle_id}.json"

            data = {
                "id":         puzzle_id,
                "filename":   f"{puzzle_id}.json",
                "level":      level,
                "label":      info["label"],
                "eeg_target": info["eeg_target"],
                "condition":  "focus",
                "grid_size":  [grid_x, grid_y],
                "n_pieces":   feats["n_pieces"],
                "features":   feats,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            total += 1
            print(f"  [{total:02d}] {puzzle_id}  "
                  f"pieces={feats['n_pieces']:>3}  "
                  f"cog_load={feats['cognitive_load']:.3f}  "
                  f"beta={feats['beta_demand']:.2f}")

            all_metadata.append({
                "filename":                   f"{puzzle_id}.json",
                "condition":                  "focus",
                "level":                      level,
                "label":                      info["label"],
                "eeg_target":                 info["eeg_target"],
                "n_pieces":                   feats["n_pieces"],
                "grid_rows":                  feats["grid_rows"],
                "grid_cols":                  feats["grid_cols"],
                "cognitive_load":             feats["cognitive_load"],
                "visual_search_complexity":   feats["visual_search_complexity"],
                "expected_completion_time_s": feats["expected_completion_time_s"],
                "difficulty_index":           feats["difficulty_index"],
                "beta_demand":                feats["beta_demand"],
            })

    # Export CSV features
    meta_path = BASE_DIR / "puzzle_focus_features.csv"
    with open(meta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_metadata[0].keys())
        w.writeheader()
        w.writerows(all_metadata)

    print(f"\n{'='*55}")
    print(f"Terminé : {total} puzzles générés")
    print(f"CSV     : {meta_path}")
    print(f"Dossier : {BASE_DIR}")
    print(f"{'='*55}")


if __name__ == "__main__":
    generate_puzzles()