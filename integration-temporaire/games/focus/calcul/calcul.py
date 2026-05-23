"""
NeuroCap — Génération des problèmes de Calcul
==============================================
40 problèmes JSON : 8 problèmes × 5 niveaux
Condition : focus | EEG target : beta préfrontal

Niveau 1 : addition/soustraction simple     (1-10)
Niveau 2 : addition/soustraction 2 chiffres (10-50)
Niveau 3 : multiplication simple            (2-9)
Niveau 4 : multiplication moyenne + addition
Niveau 5 : opérations mixtes avec parenthèses

Justification : Harmony et al. 1996 — activation beta préfrontal
                pendant calcul mental conscient

Usage : python calcul.py
→ génère 40 fichiers JSON dans games/focus/calcul/
"""

import json
import random
from pathlib import Path

BASE_DIR = Path(r"C:\neurocap_dataset\games\focus\calcul")

PROBLEMS_PER_LEVEL = 8

LEVEL_CONFIG = {
    1: {"label": "Très facile", "eeg_target": "beta_faible",  "beta_demand": 0.36},
    2: {"label": "Facile",      "eeg_target": "beta_faible",  "beta_demand": 0.52},
    3: {"label": "Moyen",       "eeg_target": "beta_moyen",   "beta_demand": 0.68},
    4: {"label": "Difficile",   "eeg_target": "beta_moyen",   "beta_demand": 0.84},
    5: {"label": "Expert",      "eeg_target": "beta_eleve",   "beta_demand": 1.00},
}


# ─── Générateurs de problèmes par niveau ──────────────────────────────────────

def generate_operation(level, seed):
    """
    Génère un problème mathématique adapté au niveau.
    Seed fixe → résultats reproductibles entre exécutions.
    """
    random.seed(seed)   # ← CORRECTION : seed fixe pour reproductibilité

    if level == 1:
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a   # évite les résultats négatifs
        expression = f"{a} {op} {b}"
        reponse    = eval(f"{a}{op}{b}")
        op_type    = "addition_soustraction_simple"

    elif level == 2:
        a = random.randint(10, 50)
        b = random.randint(10, 50)
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a
        expression = f"{a} {op} {b}"
        reponse    = eval(f"{a}{op}{b}")
        op_type    = "addition_soustraction_2chiffres"

    elif level == 3:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        expression = f"{a} × {b}"
        reponse    = a * b
        op_type    = "multiplication_simple"

    elif level == 4:
        a = random.randint(10, 30)
        b = random.randint(2, 9)
        op = random.choice(["×", "+"])
        if op == "×":
            expression = f"{a} × {b}"
            reponse    = a * b
            op_type    = "multiplication_moyenne"
        else:
            c = random.randint(10, 30)
            expression = f"{a} + {b} + {c}"
            reponse    = a + b + c
            op_type    = "addition_3_termes"

    elif level == 5:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        c = random.randint(1, 20)
        op = random.choice(["+", "-"])
        if op == "-" and (a*b) < c:
            op = "+"
        expression = f"({a} × {b}) {op} {c}"
        reponse    = (a * b) + c if op == "+" else (a * b) - c
        op_type    = "mixte_parentheses"

    return expression, int(reponse), op_type


# ─── Calcul features statiques ────────────────────────────────────────────────

def compute_features(level, op_type, reponse):
    cfg = LEVEL_CONFIG[level]
    return {
        "beta_demand":              cfg["beta_demand"],
        "operation_type":           op_type,
        "expected_reaction_time_ms": 1000 + (level * 2500),
        "numerical_load":           round(level / 5, 2),
        "result_magnitude":         len(str(abs(reponse))),  # nb chiffres dans la réponse
    }


# ─── Pipeline principal ────────────────────────────────────────────────────────

def generate_calcul():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    total = 0

    print("=" * 55)
    print("NeuroCap — Génération problèmes Calcul")
    print("=" * 55)

    for level, cfg in LEVEL_CONFIG.items():
        print(f"\nNiveau {level} — {cfg['label']}")

        for i in range(1, PROBLEMS_PER_LEVEL + 1):
            seed = level * 100 + i   # seed reproductible
            expression, reponse, op_type = generate_operation(level, seed)
            feats = compute_features(level, op_type, reponse)

            calcul_id = f"CAL_NIV{level}_{i:03d}"
            filepath  = BASE_DIR / f"{calcul_id}.json"

            data = {
                "id":               calcul_id,
                "filename":         f"{calcul_id}.json",
                "level":            level,
                "label":            cfg["label"],
                "eeg_target":       cfg["eeg_target"],
                "expression":       expression,
                "reponse_attendue": reponse,
                "type_reponse":     "integer",
                "features":         feats,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            total += 1
            print(f"  [{total:02d}] {calcul_id}  "
                  f"expr={expression:<20}  "
                  f"rep={reponse:<6}  "
                  f"type={op_type}")

            all_metadata.append({
                "filename":                 f"{calcul_id}.json",
                "level":                    level,
                "label":                    cfg["label"],
                "eeg_target":               cfg["eeg_target"],
                "operation_type":           op_type,
                "beta_demand":              feats["beta_demand"],
                "numerical_load":           feats["numerical_load"],
                "expected_reaction_time_ms": feats["expected_reaction_time_ms"],
            })

    # Export CSV features
    import csv
    meta_path = BASE_DIR / "calcul_features.csv"
    with open(meta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_metadata[0].keys())
        w.writeheader()
        w.writerows(all_metadata)

    print(f"\n{'='*55}")
    print(f"Terminé : {total} problèmes générés")
    print(f"CSV     : {meta_path}")
    print(f"Dossier : {BASE_DIR}")
    print(f"{'='*55}")


if __name__ == "__main__":
    generate_calcul() 