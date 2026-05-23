"""
NeuroCap — Générateur séquences Mémoire
=========================================
40 séquences JSON : 8 séquences × 5 niveaux
Types : chiffres, couleurs, positions, symboles
Condition : focus | EEG target : theta frontal + gamma

Niveau 1 : séquence 4 items  — très facile
Niveau 2 : séquence 6 items  — facile
Niveau 3 : séquence 8 items  — moyen
Niveau 4 : séquence 10 items — difficile
Niveau 5 : séquence 12 items — expert

Justification : Onton et al. 2005 — working memory
                theta frontal (4-8Hz) + gamma (30-40Hz)

Usage : python generate_memoire.py
→ génère 40 fichiers JSON dans games/focus/memoire/
"""

import json
import random
from pathlib import Path

OUTPUT_DIR = Path(r"C:\neurocap_dataset\games\focus\memoire")

LEVELS = {
    1: {"length": 4,  "label": "Très facile", "display_ms": 1000, "eeg_target": "focus_faible"},
    2: {"length": 6,  "label": "Facile",      "display_ms": 800,  "eeg_target": "focus_faible"},
    3: {"length": 8,  "label": "Moyen",       "display_ms": 700,  "eeg_target": "focus_moyen"},
    4: {"length": 10, "label": "Difficile",   "display_ms": 600,  "eeg_target": "focus_eleve"},
    5: {"length": 12, "label": "Expert",      "display_ms": 500,  "eeg_target": "focus_eleve"},
}

SEQ_PAR_NIVEAU = 8

# ─── Contenus disponibles ──────────────────────────────────────────────────────
CHIFFRES  = list(range(1, 10))

COULEURS  = [
    {"id":"rouge",   "hex":"#E74C3C", "label":"Rouge"},
    {"id":"bleu",    "hex":"#3498DB", "label":"Bleu"},
    {"id":"vert",    "hex":"#2ECC71", "label":"Vert"},
    {"id":"jaune",   "hex":"#F1C40F", "label":"Jaune"},
    {"id":"violet",  "hex":"#9B59B6", "label":"Violet"},
    {"id":"orange",  "hex":"#E67E22", "label":"Orange"},
    {"id":"rose",    "hex":"#FF69B4", "label":"Rose"},
    {"id":"cyan",    "hex":"#1ABC9C", "label":"Cyan"},
]

POSITIONS = [
    {"id":"haut_gauche",  "row":0,"col":0,"label":"Haut gauche"},
    {"id":"haut_centre",  "row":0,"col":1,"label":"Haut centre"},
    {"id":"haut_droite",  "row":0,"col":2,"label":"Haut droite"},
    {"id":"milieu_gauche","row":1,"col":0,"label":"Milieu gauche"},
    {"id":"centre",       "row":1,"col":1,"label":"Centre"},
    {"id":"milieu_droite","row":1,"col":2,"label":"Milieu droite"},
    {"id":"bas_gauche",   "row":2,"col":0,"label":"Bas gauche"},
    {"id":"bas_centre",   "row":2,"col":1,"label":"Bas centre"},
    {"id":"bas_droite",   "row":2,"col":2,"label":"Bas droite"},
]

SYMBOLES  = ["★","●","■","▲","♦","✿","☀","☾","♪","✦","❋","◆","⬟","✚","⬡","✸"]


# ─── Générateurs de séquences ─────────────────────────────────────────────────

def gen_chiffres(length, seed):
    random.seed(seed)
    seq = []
    prev = None
    for _ in range(length):
        choices = [x for x in CHIFFRES if x != prev]
        item = random.choice(choices)
        seq.append(item)
        prev = item
    return {
        "type":     "chiffres",
        "sequence": seq,
        "display":  seq,
        "choices":  sorted(random.sample(CHIFFRES, min(9, len(CHIFFRES)))),
        "description": "Mémorise la suite de chiffres dans l'ordre",
    }


def gen_couleurs(length, seed):
    random.seed(seed)
    pool = COULEURS[:min(length+2, len(COULEURS))]
    seq  = []
    prev = None
    for _ in range(length):
        choices = [c for c in pool if c != prev]
        item = random.choice(choices)
        seq.append(item)
        prev = item
    return {
        "type":     "couleurs",
        "sequence": [c["id"] for c in seq],
        "display":  [{"id":c["id"],"hex":c["hex"],"label":c["label"]} for c in seq],
        "choices":  [{"id":c["id"],"hex":c["hex"],"label":c["label"]} for c in pool],
        "description": "Mémorise la séquence de couleurs dans l'ordre",
    }


def gen_positions(length, seed):
    random.seed(seed)
    seq = []
    prev = None
    for _ in range(length):
        choices = [p for p in POSITIONS if p != prev]
        item = random.choice(choices)
        seq.append(item)
        prev = item
    return {
        "type":     "positions",
        "sequence": [p["id"] for p in seq],
        "display":  [{"id":p["id"],"row":p["row"],"col":p["col"],"label":p["label"]} for p in seq],
        "grid_size": 3,
        "description": "Mémorise les cases allumées dans l'ordre sur la grille 3×3",
    }


def gen_symboles(length, seed):
    random.seed(seed)
    pool = random.sample(SYMBOLES, min(length+3, len(SYMBOLES)))
    seq  = []
    prev = None
    for _ in range(length):
        choices = [s for s in pool if s != prev]
        item = random.choice(choices)
        seq.append(item)
        prev = item
    # Distracteurs pour les choix
    distractors = [s for s in SYMBOLES if s not in pool]
    choices_pool = pool + random.sample(distractors, min(3, len(distractors)))
    random.shuffle(choices_pool)
    return {
        "type":     "symboles",
        "sequence": seq,
        "display":  seq,
        "choices":  choices_pool,
        "description": "Mémorise la séquence de symboles dans l'ordre",
    }


GENERATORS = [gen_chiffres, gen_couleurs, gen_positions, gen_symboles]


# ─── Features statiques ────────────────────────────────────────────────────────

def compute_features(seq_data, level_cfg):
    length = len(seq_data["sequence"])
    return {
        "sequence_length":  length,
        "display_ms":       level_cfg["display_ms"],
        "total_display_ms": length * level_cfg["display_ms"],
        "type":             seq_data["type"],
        "wm_load":          round(length / 7.0, 3),  # Miller 1956 : 7±2
        "difficulty_score": round(length * (1000 / level_cfg["display_ms"]), 1),
    }


# ─── Pipeline principal ────────────────────────────────────────────────────────

def generate_all():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    total = 0

    print("=" * 55)
    print("NeuroCap — Génération séquences Mémoire")
    print("=" * 55)

    for level, cfg in LEVELS.items():
        print(f"\nNiveau {level} — {cfg['label']} (longueur {cfg['length']})")

        for i in range(1, SEQ_PAR_NIVEAU+1):
            seed     = level * 1000 + i
            gen_fn   = GENERATORS[(i-1) % len(GENERATORS)]
            seq_data = gen_fn(cfg["length"], seed)
            feats    = compute_features(seq_data, cfg)

            filename = f"MEM_NIV{level}_{i:03d}.json"
            filepath = OUTPUT_DIR / filename

            data = {
                "id":          filename.replace(".json",""),
                "filename":    filename,
                "level":       level,
                "label":       cfg["label"],
                "eeg_target":  cfg["eeg_target"],
                "display_ms":  cfg["display_ms"],
                "recall_mode": "sequential",
                "features":    feats,
                **seq_data,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            total += 1
            print(f"  [{total:02d}] {filename}  "
                  f"type={seq_data['type']:<10}  "
                  f"length={cfg['length']}  "
                  f"wm_load={feats['wm_load']:.2f}")

            all_metadata.append({
                "filename":        filename,
                "level":           level,
                "label":           cfg["label"],
                "eeg_target":      cfg["eeg_target"],
                "type":            seq_data["type"],
                "sequence_length": feats["sequence_length"],
                "display_ms":      feats["display_ms"],
                "wm_load":         feats["wm_load"],
                "difficulty_score":feats["difficulty_score"],
            })

    # Export CSV features
    import csv
    meta_path = OUTPUT_DIR / "memoire_features.csv"
    with open(meta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_metadata[0].keys())
        w.writeheader()
        w.writerows(all_metadata)

    print(f"\n{'='*55}")
    print(f"Terminé : {total} séquences générées")
    print(f"Types   : chiffres, couleurs, positions, symboles")
    print(f"CSV     : {meta_path}")
    print(f"{'='*55}")


if __name__ == "__main__":
    generate_all()