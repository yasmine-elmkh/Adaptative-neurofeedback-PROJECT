-- ============================================================
-- Migration 005 — Schéma Recommandation Média NeuroCap
-- Tables manquantes + colonnes supplémentaires sur medias
-- Idempotent : safe à relancer plusieurs fois
-- Adapté au schéma existant : medias.id = UUID, users.id = TEXT
-- ============================================================

-- ── 1. Colonnes manquantes sur la table medias ───────────────────────────────

ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS category       TEXT;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS tempo_bpm      FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS brightness     FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS saturation     FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS contrast       FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS metadata       JSONB DEFAULT '{}';

-- Index sur category pour les filtres de recommandation
CREATE INDEX IF NOT EXISTS idx_medias_category ON public.medias(category);

-- ── 2. user_media_preferences ─────────────────────────────────────────────────
-- Préférences audio/visuelles apprises par retour utilisateur

CREATE TABLE IF NOT EXISTS public.user_media_preferences (
    user_id               TEXT        NOT NULL,
    preferred_categorie   TEXT        NOT NULL,
    preferred_type        TEXT        NULL,
    avg_tempo_bpm         FLOAT8      NULL,
    avg_brightness        FLOAT8      NULL,
    avg_saturation        FLOAT8      NULL,
    avg_contrast          FLOAT8      NULL,
    preferences_vector    JSONB       NULL,
    last_updated          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, preferred_categorie)
);

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_user_media_preferences_user') THEN
        ALTER TABLE public.user_media_preferences
            ADD CONSTRAINT fk_user_media_preferences_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_user_media_pref_user ON public.user_media_preferences(user_id);

-- ── 3. recommendations_media ──────────────────────────────────────────────────
-- Recommandations générées (live ou offline) pour un patient

CREATE TABLE IF NOT EXISTS public.recommendations_media (
    id             UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id        TEXT        NOT NULL,
    media_id       UUID        NOT NULL,
    score          FLOAT8      NOT NULL DEFAULT 0.0 CHECK (score >= 0 AND score <= 1),
    reason         TEXT        NULL,
    generated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at     TIMESTAMPTZ NULL,
    is_clicked     BOOLEAN     NOT NULL DEFAULT FALSE,
    UNIQUE (user_id, media_id)
);

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_recommendations_media_user') THEN
        ALTER TABLE public.recommendations_media
            ADD CONSTRAINT fk_recommendations_media_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_recommendations_media_media') THEN
        ALTER TABLE public.recommendations_media
            ADD CONSTRAINT fk_recommendations_media_media
            FOREIGN KEY (media_id) REFERENCES public.medias(id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_rec_media_user_score  ON public.recommendations_media(user_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_rec_media_media_id    ON public.recommendations_media(media_id);
CREATE INDEX IF NOT EXISTS idx_rec_media_not_clicked ON public.recommendations_media(is_clicked) WHERE NOT is_clicked;
CREATE INDEX IF NOT EXISTS idx_rec_media_expires     ON public.recommendations_media(expires_at) WHERE expires_at IS NOT NULL;

-- ── 4. playlists ──────────────────────────────────────────────────────────────
-- Playlists personnelles ou thérapeutiques

CREATE TABLE IF NOT EXISTS public.playlists (
    id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         TEXT        NOT NULL,
    name            TEXT        NOT NULL,
    description     TEXT        NULL,
    created_by_role TEXT        NOT NULL DEFAULT 'patient' CHECK (created_by_role IN ('patient', 'therapist', 'admin')),
    is_therapeutic  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_playlists_user') THEN
        ALTER TABLE public.playlists
            ADD CONSTRAINT fk_playlists_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_playlists_user_id ON public.playlists(user_id);
CREATE INDEX IF NOT EXISTS idx_playlists_name    ON public.playlists(user_id, name);

-- ── 5. playlist_media ─────────────────────────────────────────────────────────
-- Éléments ordonnés d'une playlist

CREATE TABLE IF NOT EXISTS public.playlist_media (
    playlist_id  UUID        NOT NULL,
    media_id     UUID        NOT NULL,
    position     INTEGER     NOT NULL,
    added_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (playlist_id, media_id)
);

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_playlist_media_playlist') THEN
        ALTER TABLE public.playlist_media
            ADD CONSTRAINT fk_playlist_media_playlist
            FOREIGN KEY (playlist_id) REFERENCES public.playlists(id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_playlist_media_media') THEN
        ALTER TABLE public.playlist_media
            ADD CONSTRAINT fk_playlist_media_media
            FOREIGN KEY (media_id) REFERENCES public.medias(id) ON DELETE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_playlist_media_playlist  ON public.playlist_media(playlist_id);
CREATE INDEX IF NOT EXISTS idx_playlist_media_position  ON public.playlist_media(playlist_id, position);

-- ── 6. offline_recommendations ───────────────────────────────────────────────
-- Recommandations par époque générées depuis un rapport EEG fichier

CREATE TABLE IF NOT EXISTS public.offline_recommendations (
    id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         TEXT        NOT NULL,
    report_id       TEXT        NULL,
    filename        TEXT        NOT NULL,
    epoch_idx       INTEGER     NOT NULL,
    eeg_state       TEXT        NOT NULL CHECK (eeg_state IN ('stress', 'focus', 'neutral')),
    media_id        UUID        NOT NULL,
    media_type      TEXT        NOT NULL CHECK (media_type IN ('audio', 'image', 'video', 'game')),
    score           FLOAT8      NOT NULL DEFAULT 0.0,
    liked           BOOLEAN     DEFAULT NULL,
    feedback_at     TIMESTAMPTZ DEFAULT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_offline_rec_user') THEN
        ALTER TABLE public.offline_recommendations
            ADD CONSTRAINT fk_offline_rec_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_offline_rec_media') THEN
        ALTER TABLE public.offline_recommendations
            ADD CONSTRAINT fk_offline_rec_media
            FOREIGN KEY (media_id) REFERENCES public.medias(id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_offline_rec_report') THEN
        ALTER TABLE public.offline_recommendations
            ADD CONSTRAINT fk_offline_rec_report
            FOREIGN KEY (report_id) REFERENCES public.eeg_reports(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_offline_rec_user    ON public.offline_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_offline_rec_file    ON public.offline_recommendations(user_id, filename);
CREATE INDEX IF NOT EXISTS idx_offline_rec_media   ON public.offline_recommendations(media_id);
CREATE INDEX IF NOT EXISTS idx_offline_rec_report  ON public.offline_recommendations(report_id);
CREATE INDEX IF NOT EXISTS idx_offline_rec_state   ON public.offline_recommendations(user_id, eeg_state);
CREATE INDEX IF NOT EXISTS idx_offline_rec_liked   ON public.offline_recommendations(liked) WHERE liked IS NOT NULL;

-- ── 7. Désactiver RLS ─────────────────────────────────────────────────────────

ALTER TABLE public.user_media_preferences  DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations_media   DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.playlists               DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.playlist_media          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.offline_recommendations DISABLE ROW LEVEL SECURITY;

-- ── Vérification ─────────────────────────────────────────────────────────────

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'user_media_preferences', 'recommendations_media',
    'playlists', 'playlist_media', 'offline_recommendations'
  )
ORDER BY table_name;
