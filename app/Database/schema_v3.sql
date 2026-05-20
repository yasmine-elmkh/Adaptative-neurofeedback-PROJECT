-- ══════════════════════════════════════════════════════════════════════════════
-- NeuroCap — Schéma Supabase complet v3.0
-- ══════════════════════════════════════════════════════════════════════════════
-- Fichier UNIQUE à exécuter dans Supabase SQL Editor :
--   https://supabase.com/dashboard/project/<your-project>/sql/new
--
-- Idempotent : safe à relancer plusieurs fois (IF NOT EXISTS + ADD COLUMN IF NOT EXISTS)
-- Remplace : supabase_migration.sql + migration_roles.sql + migration_roles_v2.sql
-- Ajoute    : eeg_reports, training_epochs, finetuning_jobs + colonnes fine-tuning sur eeg_profiles
-- ══════════════════════════════════════════════════════════════════════════════

-- ── 1. USERS ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.users (
    id              TEXT        PRIMARY KEY,
    email           TEXT        UNIQUE NOT NULL,
    username        TEXT        UNIQUE,
    hashed_password TEXT        NOT NULL,
    first_name      TEXT        DEFAULT '',
    last_name       TEXT        DEFAULT '',
    role            TEXT        NOT NULL DEFAULT 'patient',
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    therapist_id    TEXT        REFERENCES public.users(id) ON DELETE SET NULL,
    last_login      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT users_role_check CHECK (role IN ('user','patient','therapist','admin'))
);

CREATE INDEX IF NOT EXISTS idx_users_email        ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role         ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_therapist_id ON public.users(therapist_id);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at   ON public.users(deleted_at) WHERE deleted_at IS NULL;


-- ── 2. EEG_PROFILES ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.eeg_profiles (
    id                         TEXT        PRIMARY KEY,
    user_id                    TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    -- Profil cognitif A/B/C
    profile_type               TEXT        DEFAULT 'B',   -- 'A' | 'B' | 'C'
    iapf                       FLOAT8,
    baseline_tbr               FLOAT8,
    baseline_alpha             FLOAT8,
    baseline_beta              FLOAT8,
    baseline_theta             FLOAT8,
    reactivity_score           FLOAT8,
    current_threshold          FLOAT8      DEFAULT 0.5,
    palier                     TEXT        DEFAULT 'P1',  -- 'P1'..'P4'
    calibrated_at              TIMESTAMPTZ,
    -- Fine-tuning automatique (ajoutés v3.0)
    finetuned_version          INT         DEFAULT 0,
    finetuned_model_checkpoint TEXT,
    last_finetune_at           TIMESTAMPTZ,
    last_20_sessions_accuracy  FLOAT8,
    updated_at                 TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eeg_profiles_user_id ON public.eeg_profiles(user_id);

-- Colonnes fine-tuning (idempotent pour bases existantes)
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS finetuned_version          INT         DEFAULT 0;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS finetuned_model_checkpoint TEXT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS last_finetune_at           TIMESTAMPTZ;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS last_20_sessions_accuracy  FLOAT8;


-- ── 3. SESSIONS ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.sessions (
    id                  TEXT        PRIMARY KEY,
    user_id             TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    objective           TEXT        DEFAULT 'concentration',
    feedback_mode       TEXT        DEFAULT 'visual',
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


-- ── 4. SESSION_EVENTS ────────────────────────────────────────────────────────

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

CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON public.session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_session_ts ON public.session_events(session_id, timestamp);


-- ── 5. EEG_REPORTS (analyses fichiers offline + sessions live) ───────────────

CREATE TABLE IF NOT EXISTS public.eeg_reports (
    id              TEXT        PRIMARY KEY,
    patient_id      TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    source          TEXT        NOT NULL DEFAULT 'file',   -- 'file' | 'live'
    filename        TEXT,
    n_epochs        INTEGER     DEFAULT 0,
    n_accepted      INTEGER     DEFAULT 0,
    dominant_state  TEXT,
    concentration_pct FLOAT8,
    stress_pct      FLOAT8,
    uncertain_pct   FLOAT8,
    avg_confidence  FLOAT8,
    duration_s      FLOAT8,
    summary         TEXT,
    epochs_json     JSONB,                                  -- tableau résumé des époques
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eeg_reports_patient_id  ON public.eeg_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_eeg_reports_created_at  ON public.eeg_reports(created_at DESC);


-- ── 6. TRAINING_EPOCHS (epochs haute-confiance pour fine-tuning) ─────────────

CREATE TABLE IF NOT EXISTS public.training_epochs (
    id                  UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id          TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    report_id           TEXT        REFERENCES public.eeg_reports(id) ON DELETE SET NULL,
    predicted_label     TEXT        NOT NULL,               -- 'concentration' | 'stress' | 'uncertain'
    confidence          FLOAT8      NOT NULL,
    features            JSONB       NOT NULL,               -- 63 features FeatEng
    is_high_confidence  BOOLEAN     DEFAULT TRUE,
    used_in_finetuning  BOOLEAN     DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_epochs_patient_id ON public.training_epochs(patient_id);
CREATE INDEX IF NOT EXISTS idx_training_epochs_conf       ON public.training_epochs(patient_id, is_high_confidence, used_in_finetuning);
CREATE INDEX IF NOT EXISTS idx_training_epochs_created_at ON public.training_epochs(created_at DESC);


-- ── 7. FINETUNING_JOBS (historique des runs de fine-tuning) ──────────────────

CREATE TABLE IF NOT EXISTS public.finetuning_jobs (
    id               UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id       TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    trigger_type     TEXT        NOT NULL,                  -- 'v1' | 'v2' | 'drift' | 'maintenance'
    status           TEXT        NOT NULL DEFAULT 'pending',-- 'pending' | 'running' | 'done' | 'failed'
    n_epochs_used    INTEGER     DEFAULT 0,
    accuracy_before  FLOAT8,
    accuracy_after   FLOAT8,
    model_version    INTEGER,
    checkpoint_path  TEXT,
    error_message    TEXT,
    started_at       TIMESTAMPTZ DEFAULT NOW(),
    finished_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_finetuning_jobs_patient_id ON public.finetuning_jobs(patient_id);
CREATE INDEX IF NOT EXISTS idx_finetuning_jobs_status     ON public.finetuning_jobs(status);
CREATE INDEX IF NOT EXISTS idx_finetuning_jobs_started_at ON public.finetuning_jobs(started_at DESC);


-- ── 8. AUDIT_LOGS ────────────────────────────────────────────────────────────

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


-- ── 9. THERAPIST_NOTES ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.therapist_notes (
    id           UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    therapist_id TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    patient_id   TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    content      TEXT        NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_therapist_notes_therapist ON public.therapist_notes(therapist_id);
CREATE INDEX IF NOT EXISTS idx_therapist_notes_patient   ON public.therapist_notes(patient_id);


-- ── 10. THERAPIST_RECOMMENDATIONS ────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.therapist_recommendations (
    id                     UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    therapist_id           TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    patient_id             TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    recommended_objective  TEXT,
    weekly_target          TEXT,
    notes                  TEXT,
    created_at             TIMESTAMPTZ DEFAULT NOW(),
    updated_at             TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_therapist_rec_patient ON public.therapist_recommendations(patient_id);


-- ── 11. SYSTEM_SETTINGS ──────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.system_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    description TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO public.system_settings (key, value, description) VALUES
    ('p1_max_sessions',    '5',     'Nombre max de sessions pour le palier P1'),
    ('p2_max_sessions',    '10',    'Nombre max de sessions pour le palier P2'),
    ('p3_max_sessions',    '13',    'Nombre max de sessions pour le palier P3'),
    ('block_duration_min', '3',     'Durée d''un bloc en minutes'),
    ('n_blocks',           '6',     'Nombre de blocs par session'),
    ('fatigue_tbr_ratio',  '2.0',   'TBR > baseline × ce ratio → mode fatigue'),
    ('rag_enabled',        'true',  'Activer l''assistant RAG'),
    ('anonymous_exports',  'false', 'Anonymiser les exports CSV/PDF')
ON CONFLICT (key) DO NOTHING;


-- ── 12. DÉSACTIVER RLS (accès via service_role) ──────────────────────────────

ALTER TABLE public.users                    DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.eeg_profiles             DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions                 DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_events           DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.eeg_reports              DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_epochs          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.finetuning_jobs          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs               DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.therapist_notes          DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.therapist_recommendations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_settings          DISABLE ROW LEVEL SECURITY;


-- ── Vérification ─────────────────────────────────────────────────────────────

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'users','eeg_profiles','sessions','session_events',
    'eeg_reports','training_epochs','finetuning_jobs',
    'audit_logs','therapist_notes','therapist_recommendations','system_settings'
  )
ORDER BY table_name;
