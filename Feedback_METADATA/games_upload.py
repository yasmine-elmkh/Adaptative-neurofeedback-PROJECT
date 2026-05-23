import csv
import os
import cloudinary
from cloudinary import uploader

# ==========================================
# CONFIGURATION CLOUDINARY
# Remplacez les valeurs par vos identifiants
# ==========================================
cloudinary.config(
    cloud_name="dctitjh4x",
    api_key="622763345467656",
    api_secret="BM6WsFI4DeBy8L6UTtXWIJCj5rI",
    secure=True
)

BASE_DIR = r"C:\neurocap_dataset\games"
INPUT_CSV = r"C:\neurocap_dataset\games_features_clean.csv"
OUTPUT_CSV = r"C:\neurocap_dataset\games_uploaded.csv"

# Étape 1 : Créer un dictionnaire de tous les fichiers locaux
# C'est indispensable car certains fichiers sont dans des sous-dossiers (ex: coloriage/mandala/)
local_files_map = {}
for root, _, files in os.walk(BASE_DIR):
    for f in files:
        # On ignore les fichiers parasites
        if not f.endswith(('.py', '.csv', '.txt', '.ds_store')) and not f.startswith("._"):
            local_files_map[f] = os.path.join(root, f)

def upload_games():
    uploaded_rows = []
    error_count = 0
    
    with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total_rows = sum(1 for row in reader) # Compter le total
        f.seek(0) # Rembobiner le fichier
        next(reader) # Passer l'en-tête
        
        for index, row in enumerate(reader, start=1):
            filename = row['filename']
            categorie = row['categorie']
            game_folder = row['game_folder']
            
            # Trouver le chemin absolu du fichier sur votre PC
            local_path = local_files_map.get(filename)
            if not local_path:
                print(f"[{index}/{total_rows}] ❌ Fichier introuvable sur le disque : {filename}")
                error_count += 1
                continue
            
            # Déterminer le type de ressource Cloudinary
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp']:
                res_type = "image" # Les SVG et images doivent être uploadés en tant qu'images
            else: 
                res_type = "raw"   # Les fichiers JSON doivent être uploadés en tant que fichiers bruts
            
            # Construire l'ID public pour Cloudinary
            filename_no_ext = os.path.splitext(filename)[0]
            public_id = f"NeuroCap/game/{categorie}/{game_folder}/{filename_no_ext}"
            
            print(f"[{index}/{total_rows}] Upload {res_type} : {categorie}/{game_folder}/{filename}...", end=" ")
            
            try:
                response = uploader.upload(
                    local_path,
                    public_id=public_id,
                    resource_type=res_type,
                    overwrite=True,
                )
                
                # Ajouter les infos Cloudinary à la ligne du CSV
                row['url_cloudinary'] = response['secure_url']
                row['cloudinary_id'] = response['public_id']
                uploaded_rows.append(row)
                print("✅")
                
            except Exception as e:
                print(f"❌ ÉCHEC : {e}")
                error_count += 1

    # Sauvegarder le nouveau CSV avec les URLs Cloudinary
    if uploaded_rows:
        with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = uploaded_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(uploaded_rows)
        print(f"\n✅ Upload terminé ! {len(uploaded_rows)} fichiers uploadés avec succès.")
        print(f"📄 Fichier sauvegardé : {OUTPUT_CSV}")
        if error_count > 0:
            print(f"⚠️ {error_count} fichiers n'ont pas pu être uploadés.")
    else:
        print("\n❌ Aucun fichier n'a été uploadé.")

if __name__ == "__main__":
    upload_games()