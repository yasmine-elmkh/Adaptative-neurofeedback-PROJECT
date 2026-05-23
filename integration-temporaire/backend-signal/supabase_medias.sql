-- ══════════════════════════════════════════════════════════════════════════════
-- NeuroCap — Table MEDIAS (complément schéma v3.0)
-- À exécuter dans Supabase SQL Editor APRÈS le schéma principal v3.0
-- ══════════════════════════════════════════════════════════════════════════════
--
-- Pourquoi ce fichier séparé :
--   Le schéma v3.0 gère users, sessions, eeg_profiles, etc.
--   La table medias est spécifique au moteur de recommandation adaptatif :
--   elle stocke les fichiers Cloudinary + les poids Thompson Sampling.
--
-- Connexion depuis integration-temporaire/frontend-signal/src/lib/supabase.js
-- Connexion depuis neurocap-feedback-v2/src/lib/supabase.js
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.medias (
    id              BIGSERIAL   PRIMARY KEY,
    filename        TEXT        NOT NULL UNIQUE,
    type            TEXT        NOT NULL CHECK (type IN ('image','audio','video','game')),
    categorie       TEXT        NOT NULL CHECK (categorie IN ('relax','focus','transition')),
    -- 'condition' = alias Python du recommender (stress→relax, focus→focus, neutral→transition)
    condition       TEXT        GENERATED ALWAYS AS (categorie) STORED,
    url_cloudinary  TEXT,
    duree_s         INTEGER,
    -- JSONB structure :
    -- {
    --   "ts_weights": {
    --     "relax":      { "alpha": 1, "beta": 1 },
    --     "focus":      { "alpha": 1, "beta": 1 },
    --     "transition": { "alpha": 1, "beta": 1 }
    --   },
    --   "audio": { "tempo_bpm":0, "rms_mean":0, "zcr_mean":0, "spec_centroid_mean":0,
    --              "spectral_flux":0, "harm_perc_ratio":0, "spectral_stationarity":0,
    --              "mfcc1_mean":0, "mfcc2_mean":0, "mfcc3_mean":0 },
    --   "image": { "brightness_global":0, "contrast_rms":0, "saturation_mean":0,
    --              "edge_density":0, "glcm_homogeneity":0, "symmetry_h":0,
    --              "hue_mean":0, "chroma_mean":0 },
    --   "video": { "optical_flow_mean":0, "temporal_energy_var":0, "scene_change_rate":0,
    --              "motion_regularity":0, "spatial_freq_hf_ratio":0, "brightness_mean":0 }
    -- }
    features        JSONB       DEFAULT '{}',
    actif           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_medias_categorie ON public.medias(categorie);
CREATE INDEX IF NOT EXISTS idx_medias_type      ON public.medias(type);
CREATE INDEX IF NOT EXISTS idx_medias_actif     ON public.medias(actif) WHERE actif = TRUE;
CREATE INDEX IF NOT EXISTS idx_medias_filename  ON public.medias(filename);

ALTER TABLE public.medias DISABLE ROW LEVEL SECURITY;

-- ── Données de test ───────────────────────────────────────────────────────────
-- Remplacer url_cloudinary par vos vraies URLs avant mise en production.
-- Le champ 'filename' doit correspondre EXACTEMENT aux noms retournés
-- par Feedback METADATA/mapping.json et merged_features.csv

INSERT INTO public.medias (filename, type, categorie, url_cloudinary, duree_s, features) VALUES

    -- ── RELAX (stress → afficher relax) ──────────────────────────────────────
    ('AUD_REL_001.mp3', 'audio', 'relax',
     'https://res.cloudinary.com/dctitjh4x/video/upload/v1/neurocap/audio/AUD_REL_001.mp3', 180,
     '{"ts_weights":{"relax":{"alpha":1.2,"beta":1.0},"focus":{"alpha":1.0,"beta":1.2},"transition":{"alpha":1.0,"beta":1.0}},"audio":{"tempo_bpm":0,"rms_mean":0.12,"zcr_mean":0.08,"spec_centroid_mean":820,"spectral_flux":0.05,"harm_perc_ratio":0.22,"spectral_stationarity":0.88,"mfcc1_mean":-318,"mfcc2_mean":41,"mfcc3_mean":-17}}'),

    ('AUD_REL_002.mp3', 'audio', 'relax',
     'https://res.cloudinary.com/dctitjh4x/video/upload/v1/neurocap/audio/AUD_REL_002.mp3', 240,
     '{"ts_weights":{"relax":{"alpha":1.5,"beta":1.0},"focus":{"alpha":1.0,"beta":1.3},"transition":{"alpha":1.0,"beta":1.0}},"audio":{"tempo_bpm":0,"rms_mean":0.10,"zcr_mean":0.07,"spec_centroid_mean":750,"spectral_flux":0.04,"harm_perc_ratio":0.19,"spectral_stationarity":0.91,"mfcc1_mean":-325,"mfcc2_mean":44,"mfcc3_mean":-20}}'),

    ('IMG_REL_001.jpg', 'image', 'relax',
     'https://res.cloudinary.com/dctitjh4x/image/upload/v1/neurocap/images/IMG_REL_001.jpg', NULL,
     '{"ts_weights":{"relax":{"alpha":1.3,"beta":1.0},"focus":{"alpha":1.0,"beta":1.2},"transition":{"alpha":1.0,"beta":1.0}},"image":{"brightness_global":0.72,"contrast_rms":0.18,"saturation_mean":0.45,"edge_density":0.12,"glcm_homogeneity":0.81,"symmetry_h":0.93,"hue_mean":0.62,"chroma_mean":0.38}}'),

    ('IMG_REL_002.jpg', 'image', 'relax',
     'https://res.cloudinary.com/dctitjh4x/image/upload/v1/neurocap/images/IMG_REL_002.jpg', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.0},"focus":{"alpha":1.0,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}},"image":{"brightness_global":0.68,"contrast_rms":0.20,"saturation_mean":0.50,"edge_density":0.10,"glcm_homogeneity":0.78,"symmetry_h":0.85,"hue_mean":0.58,"chroma_mean":0.42}}'),

    ('VID_REL_001.mp4', 'video', 'relax',
     'https://res.cloudinary.com/dctitjh4x/video/upload/v1/neurocap/videos/VID_REL_001.mp4', 120,
     '{"ts_weights":{"relax":{"alpha":1.2,"beta":1.0},"focus":{"alpha":1.0,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}},"video":{"optical_flow_mean":0.04,"temporal_energy_var":0.02,"scene_change_rate":0.01,"motion_regularity":0.90,"spatial_freq_hf_ratio":0.15,"brightness_mean":0.61}}'),

    ('GAME_COL_mandala_001.svg', 'game', 'relax',
     'https://res.cloudinary.com/dctitjh4x/raw/upload/v1/neurocap/games/GAME_COL_mandala_001.svg', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.0},"focus":{"alpha":1.0,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}}}'),

    -- ── FOCUS (focus/distracted → jeux cognitifs) ─────────────────────────────
    ('AUD_FOC_001.mp3', 'audio', 'focus',
     'https://res.cloudinary.com/dctitjh4x/video/upload/v1/neurocap/audio/AUD_FOC_001.mp3', 300,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.2},"focus":{"alpha":1.5,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}},"audio":{"tempo_bpm":70,"rms_mean":0.25,"zcr_mean":0.15,"spec_centroid_mean":1800,"spectral_flux":0.12,"harm_perc_ratio":0.75,"spectral_stationarity":0.65,"mfcc1_mean":-280,"mfcc2_mean":38,"mfcc3_mean":-12}}'),

    ('IMG_FOC_001.jpg', 'image', 'focus',
     'https://res.cloudinary.com/dctitjh4x/image/upload/v1/neurocap/images/IMG_FOC_001.jpg', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.2},"focus":{"alpha":1.3,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}},"image":{"brightness_global":0.55,"contrast_rms":0.55,"saturation_mean":0.60,"edge_density":0.55,"glcm_homogeneity":0.45,"symmetry_h":0.50,"hue_mean":0.45,"chroma_mean":0.55}}'),

    ('GAME_CALC_NIV1_001.json', 'game', 'focus',
     'https://res.cloudinary.com/dctitjh4x/raw/upload/v1/neurocap/games/GAME_CALC_NIV1_001.json', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.5},"focus":{"alpha":2.0,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}}}'),

    ('GAME_MEM_NIV2_001.json', 'game', 'focus',
     'https://res.cloudinary.com/dctitjh4x/raw/upload/v1/neurocap/games/GAME_MEM_NIV2_001.json', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.3},"focus":{"alpha":1.8,"beta":1.0},"transition":{"alpha":1.0,"beta":1.0}}}'),

    -- ── TRANSITION (neutral → contenu ambivalent) ──────────────────────────────
    ('AUD_NEU_001.mp3', 'audio', 'transition',
     'https://res.cloudinary.com/dctitjh4x/video/upload/v1/neurocap/audio/AUD_NEU_001.mp3', 240,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.0},"focus":{"alpha":1.0,"beta":1.0},"transition":{"alpha":1.5,"beta":1.0}},"audio":{"tempo_bpm":60,"rms_mean":0.18,"zcr_mean":0.11,"spec_centroid_mean":1200,"spectral_flux":0.08,"harm_perc_ratio":0.55,"spectral_stationarity":0.72,"mfcc1_mean":-300,"mfcc2_mean":40,"mfcc3_mean":-15}}'),

    ('IMG_NEU_001.jpg', 'image', 'transition',
     'https://res.cloudinary.com/dctitjh4x/image/upload/v1/neurocap/images/IMG_NEU_001.jpg', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.0},"focus":{"alpha":1.0,"beta":1.0},"transition":{"alpha":1.2,"beta":1.0}},"image":{"brightness_global":0.62,"contrast_rms":0.30,"saturation_mean":0.42,"edge_density":0.20,"glcm_homogeneity":0.68,"symmetry_h":0.55,"hue_mean":0.52,"chroma_mean":0.35}}'),

    ('GAME_ILL_rotation_001.html', 'game', 'transition',
     'https://res.cloudinary.com/dctitjh4x/raw/upload/v1/neurocap/games/GAME_ILL_rotation_001.html', NULL,
     '{"ts_weights":{"relax":{"alpha":1.0,"beta":1.0},"focus":{"alpha":1.0,"beta":1.0},"transition":{"alpha":1.5,"beta":1.0}}}')

ON CONFLICT (filename) DO NOTHING;

-- ── Vérification ──────────────────────────────────────────────────────────────
SELECT categorie, type, COUNT(*) as n
FROM public.medias
GROUP BY categorie, type
ORDER BY categorie, type;
