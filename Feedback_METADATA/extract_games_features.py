import os
import csv
import json
import re

# Le chemin racine de vos jeux
BASE_DIR = r"C:\neurocap_dataset\games"
OUTPUT_CSV = r"C:\neurocap_dataset\games_features_clean.csv"

# Dictionnaire pour attribuer les features neuro-cognitives de base
# J'ai ajouté "coloriage" au cas où le dossier s'appelle comme ça
GAME_FEATURES_MAP = {
    # FOCUS
    "calcul": {"game_type": "logic", "cognitive_load": 0.9, "logic_demand": 0.9, "memory_demand": 0.3, "motor_skill": False},
    "sudoku": {"game_type": "logic", "cognitive_load": 0.8, "logic_demand": 0.9, "memory_demand": 0.4, "motor_skill": False},
    "enigmes": {"game_type": "logic", "cognitive_load": 0.7, "logic_demand": 0.8, "memory_demand": 0.3, "motor_skill": False},
    "puzzle": {"game_type": "spatial", "cognitive_load": 0.6, "logic_demand": 0.5, "memory_demand": 0.2, "motor_skill": True},
    "memoire": {"game_type": "memory", "cognitive_load": 0.5, "logic_demand": 0.2, "memory_demand": 0.9, "motor_skill": True},
    # TRANSITION (Le script détectera le dossier "puzzle" dans transition aussi)
    # RELAX
    "coloriage": {"game_type": "coloring", "cognitive_load": 0.1, "logic_demand": 0.0, "memory_demand": 0.0, "motor_skill": True},
    "geometrique": {"game_type": "coloring", "cognitive_load": 0.2, "logic_demand": 0.0, "memory_demand": 0.0, "motor_skill": True},
    "mandala": {"game_type": "coloring", "cognitive_load": 0.1, "logic_demand": 0.0, "memory_demand": 0.0, "motor_skill": True},
    "nature": {"game_type": "coloring", "cognitive_load": 0.1, "logic_demand": 0.0, "memory_demand": 0.0, "motor_skill": True},
}

# Extensions à IGNORER (scripts, CSV et fichiers cachés macOS)
IGNORED_EXTENSIONS = ['.py', '.csv', '.txt', '.ds_store']

def get_features_from_path(filepath):
    """Cherche le nom du dossier dans le chemin pour trouver les bonnes features"""
    # Convertir les antislash Windows en slash normaux et mettre en minuscule
    parts = filepath.replace("\\", "/").lower().split("/")
    # On parcourt les dossiers du plus profond au plus haut pour trouver une correspondance
    for part in reversed(parts):
        if part in GAME_FEATURES_MAP:
            return GAME_FEATURES_MAP[part].copy(), part
    # Si rien trouvé, features par défaut
    return {"game_type": "unknown", "cognitive_load": 0.5, "logic_demand": 0.5, "memory_demand": 0.5, "motor_skill": False}, "unknown"

def process_games():
    csv_rows = []
    
    # os.walk parcourt TOUS les sous-dossiers automatiquement
    for root, dirs, files in os.walk(BASE_DIR):
        # Trouver la catégorie principale (focus, relax, transition)
        rel_path = os.path.relpath(root, BASE_DIR)
        categorie = rel_path.split(os.sep)[0].lower()
        
        if categorie not in ['focus', 'relax', 'transition']:
            continue # Ignore les fichiers à la racine de games

        for filename in files:
            # Ignorer les fichiers cachés macOS
            if filename.startswith("._") or filename.startswith("."): continue
            
            # Ignorer les scripts et CSV
            ext = os.path.splitext(filename)[1].lower()
            if ext in IGNORED_EXTENSIONS:
                print(f"Ignoré (parasite) : {filename}")
                continue
            
            filepath = os.path.join(root, filename)
            
            # Trouver les features grâce au chemin du fichier
            current_features, game_folder = get_features_from_path(filepath)

            # Détection automatique du NIVEAU (NIV1, NIV2, etc.)
            level_match = re.search(r'NIV(\d+)', filename)
            if level_match:
                level = int(level_match.group(1))
                current_features['game_level'] = level
                # Ajustement dynamique de la difficulté selon le niveau
                if level <= 2: current_features['difficulty'] = 'easy'
                elif level <= 4: current_features['difficulty'] = 'medium'
                else: current_features['difficulty'] = 'hard'
            else:
                # Si pas de niveau (ex: SVG de coloriage), niveau par défaut
                current_features['game_level'] = 1
                current_features['difficulty'] = 'easy'

            row = {
                "filename": filename,
                "type": "game",
                "categorie": categorie,
                "game_folder": game_folder,
                "features_json": json.dumps(current_features)
            }
            csv_rows.append(row)
            print(f"Traité : {categorie}/{game_folder}/{filename}")

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "type", "categorie", "game_folder", "features_json"])
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"\n✅ CSV PROPRE généré : {OUTPUT_CSV} ({len(csv_rows)} jeux traités)")

if __name__ == "__main__":
    process_games()