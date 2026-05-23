# Analyse — Dossier `Feedback METADATA`

> NeuroCap EEG · PFE Ingénierie Biomédicale · Oumama SENDADI · ENSAM Rabat

---

## Vue d'ensemble

Le dossier `Feedback METADATA` est le **cœur du système de recommandation adaptatif** de NeuroCap. Il contient la pipeline complète qui va de l'extraction de features multimédia jusqu'à la sélection en temps réel du contenu thérapeutique en fonction de l'état EEG du patient.

```
Feedback METADATA/
├── Scripts de pipeline
│   ├── extract_games_features.py   → extraction features jeux
│   ├── merge_and_mapping.py        → fusion CSV + construction mapping
│   ├── db.py                       → population PostgreSQL (Supabase)
│   ├── games_upload.py             → upload jeux vers Cloudinary
│   └── recommender.py              → moteur de recommandation (runtime)
│
├── Données brutes (features extraites)
│   ├── audio_features.csv          → features acoustiques (10 dims)
│   ├── image_features_complete.csv → features visuelles (8 dims)
│   ├── video_features_v2.csv       → features vidéo (6 dims)
│   └── games_features_clean.csv    → features jeux
│
├── Artefacts générés
│   ├── merged_features.csv         → fusion des 3 CSV (entrée moteur)
│   ├── mapping.json                → table lookup EEG state → fichiers
│   ├── item_weights.json           → poids Thompson Sampling (persistance)
│   ├── games_uploaded.csv          → log uploads Cloudinary
│   └── rename_log.csv              → log renommages fichiers
```

---

## Architecture 3 couches du moteur de recommandation

```
┌─────────────────────────────────────────────────────────────────┐
│  Couche 1 — Content-Based Filtering                             │
│  Similarité cosinus item ↔ vecteur cible EEG                   │
│  (Adomavicius & Tuzhilin 2005, Lops et al. 2011)               │
├─────────────────────────────────────────────────────────────────┤
│  Couche 2 — Thompson Sampling (bandit contextuel)               │
│  Prior informé par features statiques + mise à jour par delta   │
│  (Chapelle & Li 2011, NeurIPS)                                  │
├─────────────────────────────────────────────────────────────────┤
│  Couche 3 — Rapport IA post-séance (Claude API)                 │
│  Génération asynchrone non-bloquante                            │
│  (Bickmore & Picard 2005, TOCHI)                                │
└─────────────────────────────────────────────────────────────────┘
```

Le score final d'un item est : **`score = sim_cosinus × thompson_sample`**

---

## Composants Python (`recommender.py`)

### `EEGBuffer`
Buffer circulaire (max 20 époques) pour le lissage temporel du signal EEG.

| Paramètre | Valeur | Référence |
|-----------|--------|-----------|
| Fenêtre delta EEG | 32 s (8 époques × 4 s) | Birbaumer et al. 1999 |
| Buffer état stable | 28 s (7 époques × 4 s) | Makeig et al. 1999 |

Méthodes clés :
- `push(features, state)` — ajoute une époque
- `get_stable_state(window=7)` — état majoritaire sur 28 s (mode)
- `compute_delta(feature, window=8)` — différence avant/après sur 32 s
- `get_mean_features(window=4)` — moyenne lissée sur 16 s

### `ThompsonSampler`
Bandit contextuel Beta-Bernoulli avec prior informé.

- **Prior** : basé sur la similarité cosinus item ↔ vecteur cible EEG (pas un prior uniforme naïf)
- **Update binaire** : `alpha += 1` (succès : Δalpha > 0.05 ET Δbeta < -0.05) / `beta += 1` (échec)
- **Update SAM** : score subjectif Self-Assessment Manikin — ajustement pondéré `±0.5` par point d'écart à la neutralité (3/5)
- **Persistance** : `item_weights.json` sauvegardé à chaque update

### `RecommendationEngine`
Orchestrateur principal. Chargé une fois au démarrage.

**Méthode `select(eeg_state, eeg_features, media_type, exclude)`** :
1. Cold start epsilon-greedy (5 premières séances, ε décroissant)
2. Filtre candidats par `condition` mappée depuis l'état EEG
3. Calcule similarité cosinus avec vecteur cible littérature
4. Multiplie par échantillon Thompson → argmax

**Méthode `select_game(eeg_state, eeg_features, session_history)`** :
| État EEG | Jeu | Logique |
|----------|-----|---------|
| `stress` | Coloriage | Mandala/nature/géométrique selon stress_idx + historique complétion |
| `focus`  | Sudoku/mémoire/calcul/énigmes | Thompson sur delta_alpha par type + niveau adaptatif |
| `neutral`| Puzzle | Type (sliding/jigsaw/tangram) selon ratio α/β |

Niveau adaptatif (`_adaptive_level`) basé sur la Zone Proximale de Développement (Vygotsky 1978) : monte si error_rate < 20% ET delta_beta > 0.05, descend si error_rate > 60% OU delta_beta < -0.1.

### `Session`
Gère le cycle de vie d'une séance fermée (closed-loop).

**Flux d'événements :**
```
on_epoch()  ← toutes les 4 s depuis server_final.py
  → push EEG dans buffer
  → détecte état stable (28 s)
  → décide changement d'item (durée min/max + changement d'état)
  → appelle _select_and_play()
    → calcule delta EEG sur item précédent
    → update weights
    → sélectionne nouvel item
    → broadcast WebSocket

on_skip()   ← patient passe l'item
on_sam_rating(score)  ← évaluation 1-5

end_session()  ← fin de séance (async)
  → résumé stats
  → sauvegarde historique (100 séances max)
  → generate_report_async() ← tâche asyncio non-bloquante
    → appel Claude API (modèle claude-sonnet-4-20250514)
    → fallback texte si erreur réseau
    → broadcast {"type": "session_report"}
```

**Paramètres de durée par type :**
| Type | Min | Max |
|------|-----|-----|
| audio | 120 s | 300 s |
| image | 30 s | 60 s |
| video | 45 s | 120 s |
| game | 120 s | 600 s |

**Anti-habituation** (Grill-Spector & Malach 2001) — seuil par type avant rotation :
| Type | Seuil consécutif |
|------|-----------------|
| image | 2 |
| audio | 3 |
| video | 2 |
| game | 1 |

---

## Vecteurs cibles EEG (features multimédia normalisées [0,1])

### Audio (10 features)
| Feature | stress→relax | focus | neutral |
|---------|-------------|-------|---------|
| tempo_bpm | 0.15 (lent) | 0.55 | 0.35 |
| harm_perc_ratio | 0.85 (harmonique) | 0.55 | 0.65 |
| spectral_stationarity | 0.80 (stable) | 0.45 | 0.60 |

> Base : Thaut et al. 1999 (entraînement neuronal 60-75 BPM → alpha ↑), Sammler et al. 2007 (harmonicité → relaxation)

### Image (8 features)
| Feature | stress→relax | focus | neutral |
|---------|-------------|-------|---------|
| brightness_global | 0.70 (clair) | 0.55 | 0.60 |
| glcm_homogeneity | 0.80 (homogène) | 0.45 | 0.62 |
| contrast_rms | 0.20 (faible) | 0.55 | 0.38 |

> Base : Valdez & Mehrabian 1994 (luminosité → valence), Berman et al. 2014 (complexité visuelle → arousal)

### Vidéo (6 features)
| Feature | stress→relax | focus | neutral |
|---------|-------------|-------|---------|
| optical_flow_mean | 0.10 (quasi-statique) | 0.50 | 0.30 |
| motion_regularity | 0.85 (régulier) | 0.55 | 0.70 |
| scene_change_rate | 0.05 (rare) | 0.35 | 0.15 |

---

## Pipeline de données (`merge_and_mapping.py`)

```
audio_features.csv  ──┐
image_features.csv  ──┼──► merge_features() ──► merged_features.csv
video_features.csv  ──┘                              │
                                                      ▼
                                            build_mapping() ──► mapping.json
                                                      │
                                              _add_games()
                                         (scan dossiers SVG/JSON)
```

**Mapping EEG state → condition :**
| État EEG | Condition contenu |
|----------|------------------|
| stress | relax |
| focus | focus |
| neutral | transition |

Le `mapping.json` final a la structure :
```json
{
  "stress": { "audio": [...], "image": [...], "video": [...],
              "game": { "coloriage": { "mandala": [...], ... } } },
  "focus":  { ..., "game": { "sudoku": [...], "memoire": [...] } },
  "neutral":{ ..., "game": { "puzzle": [...] } }
}
```

---

## Population base de données (`db.py`)

Script one-shot qui lit `merged_features.csv` et insère dans **Supabase PostgreSQL**.

**Table cible : `medias`**
| Colonne | Type | Contenu |
|---------|------|---------|
| filename | text | nom du fichier |
| type | text | audio / image / video |
| categorie | text | relax / focus / transition |
| url_cloudinary | text | URL CDN construite |
| cloudinary_id | text | public_id Cloudinary |
| features | jsonb | dict de toutes les features |

**URL Cloudinary** construite selon le schéma :
`https://res.cloudinary.com/dctitjh4x/{resource_type}/upload/NeuroCap/{type}/{categorie}/{filename}`

> Audio et vidéo utilisent `resource_type=video` (streaming Cloudinary).

---

## Fichiers CSV de features

| Fichier | Nb features | Description |
|---------|-------------|-------------|
| `audio_features.csv` | 10 | tempo, RMS, ZCR, centroïde spectral, flux, ratio harmonique, stationnarité, MFCC 1-3 |
| `image_features_complete.csv` | 8 | luminosité, contraste RMS, saturation, densité bords, GLCM homogénéité, symétrie, teinte, chroma |
| `video_features_v2.csv` | 6 | optical flow, variance énergie temporelle, taux changement scène, régularité mouvement, ratio HF spatial, luminosité |
| `games_features_clean.csv` | variable | features extraites des jeux thérapeutiques |
| `merged_features.csv` | tous | fusion des 3 CSV (colonnes absentes → 0) |

---

## Intégration `server_final.py` (extrait commenté dans le code)

```python
from recommender import RecommendationEngine, Session

engine  = RecommendationEngine()    # chargé une fois au démarrage

# WebSocket START_SESSION
session = Session(engine, objective="stress_reduction", duration_min=30)
session.set_baseline(current_eeg_features)

# Dans RealTimeProcessor.process_epoch() — toutes les 4 s
action = session.on_epoch(eeg_state, epoch_features)
if action:
    await broadcast(action)          # → frontend play audio/image/jeu

# WebSocket SKIP
action = session.on_skip()

# WebSocket SAM_RATING
session.on_sam_rating(score=4)

# WebSocket END_SESSION
result = await session.end_session()
asyncio.create_task(session.generate_report_async(result, broadcast))
```

---

## Références scientifiques citées

| Référence | Usage dans le code |
|-----------|-------------------|
| Birbaumer et al. 1999 | Fenêtre delta EEG = 32 s |
| Makeig et al. 1999 | Buffer état stable = 28 s |
| Thaut et al. 1999 | Tempo 60-75 BPM → alpha ↑ |
| Sammler et al. 2007 | Harmonicité → relaxation |
| Valdez & Mehrabian 1994 | Luminosité → valence, saturation → arousal |
| Berman et al. 2014 | Complexité visuelle → arousal |
| Grill-Spector & Malach 2001 | Seuils d'habituation par type |
| Chapelle & Li 2011 (NeurIPS) | Thompson Sampling bandit |
| Adomavicius & Tuzhilin 2005 | Content-Based Filtering |
| Lops et al. 2011 | CBF survey |
| Vygotsky 1978 | Zone Proximale de Développement (niveaux jeux) |
| Clément et al. 2015 | Niveau adaptatif coloriage |
| Sitaram et al. 2017 | Closed-loop brain training |
| Zander & Kothe 2011 | BCI passif adaptatif |
| Bickmore & Picard 2005 (TOCHI) | Rapport IA thérapeutique |

---

## Points d'attention

### Sécurité
- `db.py` contient la **clé Supabase `service_role` en clair** (ligne 21). Cette clé donne accès total à la base. Elle doit être déplacée dans une variable d'environnement (`os.environ["SUPABASE_KEY"]`) et ajoutée à `.gitignore` via un fichier `.env`.

### Cohérence des chemins
- `recommender.py` pointe vers `BASE_DIR / "metadata" / ...` (sous-dossier `metadata/`)
- `merge_and_mapping.py` pointe vers `SCRIPT_DIR` (dossier courant)
- `db.py` pointe vers `C:\neurocap_dataset\metadata\` (chemin absolu local)
→ Les 3 scripts utilisent des conventions différentes. À harmoniser avant déploiement.

### Données de jeux
- `games_features_clean.csv` est présent mais les features jeux ne sont **pas intégrées** dans `FEATURE_COLS` de `recommender.py` — les jeux sont sélectionnés uniquement via `mapping.json` (lookup par type/état), sans scoring cosinus.

### Cold start
- Après 5 séances, le moteur bascule automatiquement de l'exploration pure vers l'exploitation pondérée. Les poids sont persistés dans `item_weights.json` entre les séances.
