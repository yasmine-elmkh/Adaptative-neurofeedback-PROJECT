-- Migration : Table medias (assets feedback adaptatif)
-- Exécuter dans l'éditeur SQL Supabase

CREATE TABLE IF NOT EXISTS medias (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    type        TEXT    NOT NULL CHECK (type IN ('audio', 'image', 'game', 'video')),
    filename    TEXT    NOT NULL,
    url         TEXT    NOT NULL,
    eeg_target_state TEXT DEFAULT 'all'
                    CHECK (eeg_target_state IN ('stress', 'focus', 'neutral', 'all')),
    features            JSONB   DEFAULT '{}',
    item_weights_alpha  FLOAT   DEFAULT 1.0,
    item_weights_beta   FLOAT   DEFAULT 1.0,
    game_prefix         TEXT,
    difficulty_level    INT     DEFAULT 1,
    duration_seconds    INT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_medias_type          ON medias (type);
CREATE INDEX IF NOT EXISTS idx_medias_eeg_state     ON medias (eeg_target_state);
CREATE INDEX IF NOT EXISTS idx_medias_game_prefix   ON medias (game_prefix);
