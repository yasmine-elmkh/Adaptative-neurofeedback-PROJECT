"""
NeuroCap — Populate PostgreSQL (Supabase)
==========================================
Lit merged_features.csv et insère les données dans la table 'medias'.
Génère les URLs Cloudinary automatiquement.
"""


import os
import json
import numpy as np # <-- AJOUTEZ CETTE LIGNE
import pandas as pd
from supabase import create_client, Client
from pathlib import Path
# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

# 1. Supabase (PostgreSQL)
SUPABASE_URL = "https://qwxkhkumyokzykykindv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eGtoa3VteW9renlreWtpbmR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODY4NTYyMiwiZXhwIjoyMDk0MjYxNjIyfQ.t0TAfEJfgeMqmBXh2UwOT4kU0ukZKf7I7IvlwMKHNHQ" # Utilisez la clé "service_role" pour insérer
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Cloudinary (Pour construire les URLs)
CLOUD_NAME = "dctitjh4x"

# 3. Chemins
BASE_DIR = Path(r"C:\neurocap_dataset")
MERGED_CSV = BASE_DIR / "metadata" / "merged_features.csv"

# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def build_cloudinary_url(filename: str, media_type: str, categorie: str) -> str:
    """
    Construit l'URL Cloudinary basée sur la structure de dossiers créée lors de l'upload.
    Audio/Video utilisent 'video/upload', Image utilise 'image/upload'.
    """
    # Cloudinary traite l'audio comme de la vidéo pour le streaming
    resource_type = "image" if media_type == "image" else "video"
    
    # Encoder les espaces potentiels dans le nom de fichier (bonne pratique)
    safe_filename = filename.replace(" ", "%20")
    
    # Format: https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{folder}/{filename}
    url = f"https://res.cloudinary.com/{CLOUD_NAME}/{resource_type}/upload/NeuroCap/{media_type}/{categorie}/{safe_filename}"
    return url

def build_cloudinary_id(filename: str, media_type: str, categorie: str) -> str:
    """Construit le Public ID Cloudinary."""
    return f"NeuroCap/{media_type}/{categorie}/{os.path.splitext(filename)[0]}"

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

def run():
    if not MERGED_CSV.exists():
        print(f"❌ Fichier introuvable : {MERGED_CSV}")
        return

    df = pd.read_csv(MERGED_CSV)
    print(f"🚀 Préparation de l'insertion de {len(df)} lignes dans PostgreSQL...")

    # Vider la table avant de la remplir (pour éviter les doublons si on relance le script)
    print("⚠️ Nettoyage de la table 'medias'...")
    supabase.table("medias").delete().neq("id", 0).execute()

    success = 0
    errors = 0

    for index, row in df.iterrows():
        filename = row['filename']
        media_type = row['type']
        categorie = row['condition']
        
        # Ignorer les fichiers macOS cachés
        if str(filename).startswith("._"):
            continue

        # 1. Construire les features JSONB
        # On enlève les colonnes qui ne sont pas des features
        features_series = row.drop(['filename', 'type', 'condition'])
        features_dict = features_series.fillna(0).to_dict()
        
        # Convertir les types numpy en types python natifs pour le JSON
        for k, v in features_dict.items():
            if isinstance(v, (np.integer)): features_dict[k] = int(v)
            elif isinstance(v, (np.floating)): features_dict[k] = float(v)
            elif isinstance(v, (np.bool_)): features_dict[k] = bool(v)

        # 2. Construire l'URL Cloudinary
        url = build_cloudinary_url(filename, media_type, categorie)
        cloud_id = build_cloudinary_id(filename, media_type, categorie)

        # 3. Préparer la ligne pour PostgreSQL
        data_to_insert = {
            "filename": filename,
            "type": media_type,
            "categorie": categorie,
            "url_cloudinary": url,
            "cloudinary_id": cloud_id,
            "features": features_dict # Supabase transforme ce dict en JSONB automatiquement
        }

        # 4. Insérer dans PostgreSQL via Supabase
        try:
            supabase.table("medias").insert(data_to_insert).execute()
            success += 1
            if success % 50 == 0:
                print(f"  ✅ {success}/{len(df)} lignes insérées...")
        except Exception as e:
            print(f"  ❌ Erreur pour {filename}: {e}")
            errors += 1

    print(f"\n{'='*60}")
    print("🎉 POPULATION POSTGRESQL TERMINÉE !")
    print(f"  Succès : {success}")
    print(f"  Erreurs : {errors}")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()