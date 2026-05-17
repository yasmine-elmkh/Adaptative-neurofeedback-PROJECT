import psycopg2
import numpy as np
from pathlib import Path

# Connexion
conn = psycopg2.connect(
    host="localhost",
    database="neurocap",
    user="votre_user",
    password="votre_mot_de_passe"
)
cur = conn.cursor()

# Exemple : insérer un sujet
cur.execute("""
    INSERT INTO subjects (subject_id, dataset_source, label_conc_stress)
    VALUES (%s, %s, %s)
    ON CONFLICT (subject_id) DO NOTHING
""", (0, 'cognitive_load', 0))

# Insérer les époques et features à partir des fichiers .npy
X = np.load("Merge_datasets/datasets_merged/X_merged.npy")
y = np.load("Merge_datasets/datasets_merged/y_merged.npy")
sids = np.load("Merge_datasets/datasets_merged/subject_ids_merged.npy")

for i, (epoch, label, sid) in enumerate(zip(X, y, sids)):
    # Insérer d'abord la session (simplifié)
    cur.execute("""
        INSERT INTO epochs (session_id, start_time_sec, end_time_sec, label, is_valid)
        VALUES (1, %s, %s, %s, %s) RETURNING epoch_id
    """, (0.0, 4.0, int(label), True))
    epoch_id = cur.fetchone()[0]
    # Ici vous appelleriez votre fonction extract_features(epoch) pour obtenir les 15 valeurs
    # et les insérer dans la table features
    # ...

conn.commit()
cur.close()
conn.close()