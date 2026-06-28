# NeuroCap — Validation des Données Brutes (`src/data/validate_data/`)

Scripts de validation qualité sur les datasets bruts **avant** tout prétraitement.  
À exécuter en premier dans le pipeline.

---

## Fichiers

| Script | Dataset cible | Description |
|--------|--------------|-------------|
| `validate_concentration.py` | CLA (OpenBCI 200 Hz) | Vérifie intégrité des fichiers .txt |
| `validate_stress.py` | SAM40 (Emotiv 128 Hz) | Vérifie intégrité des fichiers .mat |

---

## Contrôles effectués

### `validate_concentration.py` — Dataset CLA

- **Inventaire fichiers** : nombre de fichiers .txt par sujet (attendu : 15 sujets × 8 conditions = 120 fichiers)
- **Format** : présence colonne CH1, séparateur tabulation, encodage UTF-8
- **Fréquence d'échantillonnage** : vérification empirique de la durée des fichiers (attendu : 200 Hz)
- **Niveaux** : détection des 4 niveaux (natural / lowlevel / midlevel / highlevel) dans les noms de fichiers
- **Amplitude** : vérification que les signaux sont dans une plage physiologique (typiquement ±200 µV bruts)
- **Rapport** : `reports/EDA/Validation/validate_concentration.json` + histogrammes

### `validate_stress.py` — Dataset SAM40

- **Inventaire fichiers** : nombre de fichiers .mat par sujet (attendu : 40 sujets × 4 tâches × 3 essais)
- **Structure matrice** : dimensions (40 canaux × N échantillons), présence du canal AF3 (index 0)
- **Fréquence d'échantillonnage** : champ `fs` dans le .mat (attendu : 128 Hz)
- **Tâches** : détection des 4 types (Relax / Arithmetic / SocialStress / Stroop)
- **Fichier scales.xls** : présence et format (colonnes subject_id / task / trial / score)
- **Rapport** : `reports/EDA/Validation/validate_stress.json` + histogrammes

---

## Usage

```bash
# Valider les données brutes (étape 1 du pipeline)
python src/data/validate_data/validate_concentration.py
python src/data/validate_data/validate_stress.py
```

---

## Sorties

```
reports/EDA/Validation/
├── validate_concentration.json    rapport d'intégrité CLA
├── validate_stress.json           rapport d'intégrité SAM40
├── inventaire_concentration.png   distribution epochs par sujet
└── inventaire_stress.png          distribution epochs par sujet
```

---

## Contexte des datasets

| Paramètre | CLA (Concentration) | SAM40 (Stress) |
|-----------|---------------------|----------------|
| Source | OpenBCI Cyton | Emotiv Epoc Flex |
| Canal EEG | Fp2 (index 0 dans .txt) | AF3 (index 0 dans matrice 40-canaux) |
| Fréquence | 200 Hz → 250 Hz (resample) | 128 Hz → 250 Hz (resample) |
| Sujets | 15 (IDs 0–14) | 40 (IDs 15–54) |
| Epochs après pipeline | ~1 859 | ~2 879 |
| Ground truth | 4 niveaux dans les noms de fichiers | Questionnaire scales.xls (1–10) |

> **Note :** Les deux datasets sont traités par des pipelines complètement indépendants.  
> Ne jamais fusionner CLA et SAM40 (matériels différents, électrodes différentes).
