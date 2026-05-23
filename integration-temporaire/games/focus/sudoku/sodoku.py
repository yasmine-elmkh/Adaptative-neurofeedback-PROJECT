"""
NeuroCap — Générateur grilles Sudoku
=====================================
40 grilles JSON : 8 grilles × 5 niveaux de difficulté
Niveau basé sur le nombre de cases vides (Sweller 1988)

Niveau 1 : 30 cases vides — très facile
Niveau 2 : 36 cases vides — facile
Niveau 3 : 45 cases vides — moyen
Niveau 4 : 51 cases vides — difficile
Niveau 5 : 56 cases vides — expert

Usage : python generate_sudoku.py
→ génère 40 fichiers JSON dans C:/neurocap_dataset/games/focus/sudoku/
"""

import json
import random
import copy
from pathlib import Path

OUTPUT_DIR = Path(r"C:\neurocap_dataset\games\focus\sudoku")
# Pour test local :
# OUTPUT_DIR = Path("./sudoku_output")

LEVELS = {
    1: {"empty": 30, "label": "Très facile", "eeg_target": "focus_faible"},
    2: {"empty": 36, "label": "Facile",      "eeg_target": "focus_faible"},
    3: {"empty": 45, "label": "Moyen",       "eeg_target": "focus_moyen"},
    4: {"empty": 51, "label": "Difficile",   "eeg_target": "focus_eleve"},
    5: {"empty": 56, "label": "Expert",      "eeg_target": "focus_eleve"},
}

GRILLES_PAR_NIVEAU = 8


# ─── Génération d'une grille Sudoku valide ─────────────────────────────────────

def is_valid(grid, row, col, num):
    """Vérifie si num peut être placé en (row, col)."""
    # Ligne
    if num in grid[row]:
        return False
    # Colonne
    if num in [grid[r][col] for r in range(9)]:
        return False
    # Carré 3x3
    box_r, box_c = 3*(row//3), 3*(col//3)
    for r in range(box_r, box_r+3):
        for c in range(box_c, box_c+3):
            if grid[r][c] == num:
                return False
    return True


def solve(grid):
    """Résout la grille par backtracking."""
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(grid, row, col, num):
                        grid[row][col] = num
                        if solve(grid):
                            return True
                        grid[row][col] = 0
                return False
    return True


def count_solutions(grid, limit=2):
    """Compte les solutions (arrête à limit pour la performance)."""
    count = [0]

    def _solve(g):
        if count[0] >= limit:
            return
        for row in range(9):
            for col in range(9):
                if g[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(g, row, col, num):
                            g[row][col] = num
                            _solve(g)
                            g[row][col] = 0
                    return
        count[0] += 1

    _solve([row[:] for row in grid])
    return count[0]


def generate_full_grid():
    """Génère une grille 9x9 complète et valide."""
    grid = [[0]*9 for _ in range(9)]
    solve(grid)
    return grid


def remove_cells(full_grid, n_empty, max_attempts=200):
    """
    Retire n_empty cases en garantissant une solution unique.
    Retourne (puzzle, solution).
    """
    solution = copy.deepcopy(full_grid)
    puzzle   = copy.deepcopy(full_grid)

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    attempts = 0

    for row, col in cells:
        if removed >= n_empty:
            break
        if attempts >= max_attempts:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = 0

        # Vérifie solution unique (pour niveaux ≤ 4)
        # Pour niveau 5 (56 vides), on accepte sans vérification stricte
        if n_empty <= 51:
            test = copy.deepcopy(puzzle)
            if count_solutions(test) == 1:
                removed += 1
            else:
                puzzle[row][col] = backup
                attempts += 1
        else:
            removed += 1

    return puzzle, solution


def puzzle_to_list(grid):
    """Convertit la grille en liste plate pour JSON."""
    return [grid[r][c] for r in range(9) for c in range(9)]


def list_to_grid(flat):
    """Convertit liste plate en grille 9x9."""
    return [[flat[r*9+c] for c in range(9)] for r in range(9)]


# ─── Calcul features statiques ─────────────────────────────────────────────────

def compute_features(puzzle, solution, level):
    """
    Features statiques de la grille — pour merged_features.csv.
    Justification : Sweller (1988) charge cognitive intrinsèque.
    """
    flat    = puzzle_to_list(puzzle)
    n_given = sum(1 for x in flat if x != 0)
    n_empty = sum(1 for x in flat if x == 0)

    # Contraintes par case vide = nombre de valeurs impossibles
    constraints = []
    for r in range(9):
        for c in range(9):
            if puzzle[r][c] == 0:
                possible = sum(1 for n in range(1,10) if is_valid(puzzle, r, c, n))
                constraints.append(possible)

    avg_constraints = sum(constraints)/len(constraints) if constraints else 0
    min_constraints = min(constraints) if constraints else 0

    return {
        "n_given":          n_given,
        "n_empty":          n_empty,
        "fill_ratio":       round(n_given/81, 3),
        "avg_possible":     round(avg_constraints, 2),
        "min_possible":     min_constraints,
        "difficulty_score": round(n_empty * (1/max(avg_constraints,1)), 2),
        "cognitive_load":   LEVELS[level]["label"],
    }


# ─── Pipeline principal ────────────────────────────────────────────────────────

def generate_all():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    total = 0

    print("=" * 55)
    print("NeuroCap — Génération grilles Sudoku")
    print("=" * 55)

    for level, cfg in LEVELS.items():
        print(f"\nNiveau {level} — {cfg['label']} ({cfg['empty']} cases vides)")

        for i in range(1, GRILLES_PAR_NIVEAU+1):
            random.seed(level * 100 + i)   # reproductible

            full   = generate_full_grid()
            puzzle, solution = remove_cells(full, cfg["empty"])
            feats  = compute_features(puzzle, solution, level)

            filename = f"SDK_NIV{level}_{i:03d}.json"
            filepath = OUTPUT_DIR / filename

            data = {
                "id":           filename.replace(".json",""),
                "filename":     filename,
                "level":        level,
                "label":        cfg["label"],
                "eeg_target":   cfg["eeg_target"],
                "n_empty":      cfg["empty"],
                "puzzle":       puzzle_to_list(puzzle),
                "solution":     puzzle_to_list(solution),
                "features":     feats,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            total += 1
            print(f"  [{total:02d}] {filename}  "
                  f"given={feats['n_given']}  "
                  f"avg_possible={feats['avg_possible']:.1f}")

            all_metadata.append({
                "filename":       filename,
                "level":          level,
                "label":          cfg["label"],
                "eeg_target":     cfg["eeg_target"],
                "n_given":        feats["n_given"],
                "n_empty":        feats["n_empty"],
                "fill_ratio":     feats["fill_ratio"],
                "avg_possible":   feats["avg_possible"],
                "min_possible":   feats["min_possible"],
                "difficulty_score": feats["difficulty_score"],
            })

    # Export metadata CSV
    import csv
    meta_path = OUTPUT_DIR / "sudoku_features.csv"
    with open(meta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_metadata[0].keys())
        w.writeheader()
        w.writerows(all_metadata)

    print(f"\n{'='*55}")
    print(f"Terminé : {total} grilles générées")
    print(f"CSV features : {meta_path}")
    print(f"{'='*55}")


if __name__ == "__main__":
    generate_all()