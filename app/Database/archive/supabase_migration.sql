-- ══════════════════════════════════════════════════════════════════════════════
-- NeuroCap — Migration SQL Supabase
-- ══════════════════════════════════════════════════════════════════════════════
-- Exécuter dans : https://supabase.com/dashboard/project/qwxkhkumyokzykykindv/sql/new
-- Idempotent (safe à relancer plusieurs fois grâce à IF NOT EXISTS)
-- ══════════════════════════════════════════════════════════════════════════════

-- ── Table 1 : users ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.users (
    id              TEXT        PRIMARY KEY,               -- UUID généré par Python
    email           TEXT        UNIQUE NOT NULL,
    username        TEXT        UNIQUE NOT NULL,
    hashed_password TEXT        NOT NULL,
    role            TEXT        NOT NULL DEFAULT 'user',   -- 'user' | 'admin'
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- ── Table 2 : eeg_profiles ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.eeg_profiles (
    id                TEXT        PRIMARY KEY,
    user_id           TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_type      TEXT        DEFAULT 'B',             -- 'A' | 'B' | 'C'
    iapf              FLOAT8,                              -- Fréquence Alpha de Pointe Individuelle
    baseline_tbr      FLOAT8,                              -- Theta/Beta Ratio de base
    baseline_alpha    FLOAT8,
    baseline_beta     FLOAT8,
    baseline_theta    FLOAT8,
    reactivity_score  FLOAT8,
    current_threshold FLOAT8      DEFAULT 0.5,
    palier            TEXT        DEFAULT 'P1',            -- 'P1'..'P4'
    calibrated_at     TIMESTAMPTZ,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eeg_profiles_user_id ON public.eeg_profiles(user_id);

-- ── Table 3 : sessions ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.sessions (
    id                  TEXT        PRIMARY KEY,
    user_id             TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    objective           TEXT        DEFAULT 'concentration',  -- 'concentration' | 'relaxation'
    feedback_mode       TEXT        DEFAULT 'visual',         -- 'visual' | 'audio' | 'game'
    status              TEXT        NOT NULL DEFAULT 'pending',
    score               FLOAT8,
    duration_seconds    INTEGER,
    avg_concentration   FLOAT8,
    avg_stress          FLOAT8,
    avg_tbr             FLOAT8,
    avg_ei              FLOAT8,
    n_blocks            INTEGER     DEFAULT 0,
    n_epochs_total      INTEGER     DEFAULT 0,
    n_epochs_rejected   INTEGER     DEFAULT 0,
    recommendations     TEXT,
    started_at          TIMESTAMPTZ,
    ended_at            TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id    ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON public.sessions(created_at DESC);

-- ── Table 4 : session_events ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.session_events (
    id                 TEXT        PRIMARY KEY,
    session_id         TEXT        NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE,
    timestamp          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    concentration_rate FLOAT8      NOT NULL,
    stress_rate        FLOAT8      NOT NULL,
    confidence         FLOAT8,
    tbr                FLOAT8,
    ei                 FLOAT8,
    abr                FLOAT8,
    power_alpha        FLOAT8,
    power_beta         FLOAT8,
    power_theta        FLOAT8,
    signal_quality     FLOAT8,
    is_artifact        BOOLEAN     DEFAULT FALSE,
    feedback_mode      TEXT,
    feedback_active    BOOLEAN     DEFAULT TRUE,
    block_number       INTEGER
);

CREATE INDEX IF NOT EXISTS idx_session_events_session_id
    ON public.session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_session_ts
    ON public.session_events(session_id, timestamp);

-- ── Table 5 : audit_logs ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id         TEXT        PRIMARY KEY,
    user_id    TEXT        REFERENCES public.users(id) ON DELETE SET NULL,
    action     TEXT        NOT NULL,
    details    TEXT,
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id    ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- ── Désactiver RLS pour permettre l'accès via service_role ───────────────────
-- (La service_role key bypasse RLS de toute façon, mais c'est explicite)
ALTER TABLE public.users         DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.eeg_profiles  DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions      DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_events DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs    DISABLE ROW LEVEL SECURITY;

-- ══════════════════════════════════════════════════════════════════════════════
-- Vérification : sélectionner les tables créées
-- ══════════════════════════════════════════════════════════════════════════════
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('users','eeg_profiles','sessions','session_events','audit_logs')
ORDER BY table_name;
