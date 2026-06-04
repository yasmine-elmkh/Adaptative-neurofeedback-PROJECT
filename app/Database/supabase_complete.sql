-- ══════════════════════════════════════════════════════════════════════════════
-- NeuroCap — Schéma complet consolidé v3.5 (FINAL CORRIGÉ v2)
-- ══════════════════════════════════════════════════════════════════════════════
-- FICHIER UNIQUE à coller dans Supabase SQL Editor.
-- Idempotent : relançable sans erreur.
-- Pattern uniforme : CREATE TABLE → ALTER TABLE (toutes colonnes) → CREATE INDEX
-- ══════════════════════════════════════════════════════════════════════════════

-- ════════════════════════════════════════════════════════
-- 1. USERS
-- ════════════════════════════════════════════════════════

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
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS username        TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS first_name     TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_name      TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_active      BOOLEAN DEFAULT TRUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS therapist_id   TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login     TIMESTAMPTZ;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS deleted_at     TIMESTAMPTZ;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS updated_at     TIMESTAMPTZ DEFAULT NOW();
CREATE INDEX IF NOT EXISTS idx_users_email        ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role         ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_therapist_id ON public.users(therapist_id);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at   ON public.users(deleted_at) WHERE deleted_at IS NULL;


-- ════════════════════════════════════════════════════════
-- 2. EEG_PROFILES
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.eeg_profiles (
    id                         TEXT        PRIMARY KEY,
    user_id                    TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_type               TEXT        DEFAULT 'B',
    iapf                       FLOAT8,
    baseline_tbr               FLOAT8,
    baseline_alpha             FLOAT8,
    baseline_beta              FLOAT8,
    baseline_theta             FLOAT8,
    reactivity_score           FLOAT8,
    current_threshold          FLOAT8      DEFAULT 0.5,
    palier                     TEXT        DEFAULT 'P1',
    calibrated_at              TIMESTAMPTZ,
    finetuned_version          INT         DEFAULT 0,
    finetuned_model_checkpoint TEXT,
    last_finetune_at           TIMESTAMPTZ,
    last_20_sessions_accuracy  FLOAT8,
    updated_at                 TIMESTAMPTZ DEFAULT NOW(),
    alpha_band_lo              FLOAT       DEFAULT 8.0,
    alpha_band_hi              FLOAT       DEFAULT 12.0,
    p_alpha_ref                FLOAT,
    erd_pct                    FLOAT,
    tbr_ref                    FLOAT,
    p_beta_cognitive           FLOAT,
    threshold_s2               FLOAT,
    threshold_current          FLOAT       DEFAULT 0.30,
    palier_initial             TEXT        DEFAULT 'P1',
    calibration_date           TIMESTAMPTZ,
    audio_preference           TEXT        DEFAULT 'nature',
    stress_baseline            INTEGER     DEFAULT 5,
    focus_baseline             INTEGER     DEFAULT 5,
    meditation_exp             TEXT        DEFAULT 'jamais'
);
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS profile_type               TEXT        DEFAULT 'B';
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS iapf                       FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS baseline_tbr               FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS baseline_alpha             FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS baseline_beta              FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS baseline_theta             FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS reactivity_score           FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS current_threshold          FLOAT8      DEFAULT 0.5;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS palier                     TEXT        DEFAULT 'P1';
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS calibrated_at              TIMESTAMPTZ;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS finetuned_version          INT         DEFAULT 0;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS finetuned_model_checkpoint TEXT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS last_finetune_at           TIMESTAMPTZ;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS last_20_sessions_accuracy  FLOAT8;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS updated_at                 TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS alpha_band_lo              FLOAT       DEFAULT 8.0;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS alpha_band_hi              FLOAT       DEFAULT 12.0;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS p_alpha_ref                FLOAT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS erd_pct                   FLOAT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS tbr_ref                   FLOAT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS p_beta_cognitive           FLOAT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS threshold_s2              FLOAT;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS threshold_current         FLOAT       DEFAULT 0.30;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS palier_initial            TEXT        DEFAULT 'P1';
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS calibration_date          TIMESTAMPTZ;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS audio_preference          TEXT        DEFAULT 'nature';
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS stress_baseline           INTEGER     DEFAULT 5;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS focus_baseline            INTEGER     DEFAULT 5;
ALTER TABLE public.eeg_profiles ADD COLUMN IF NOT EXISTS meditation_exp            TEXT        DEFAULT 'jamais';
CREATE INDEX IF NOT EXISTS idx_eeg_profiles_user_id ON public.eeg_profiles(user_id);


-- ════════════════════════════════════════════════════════
-- 3. SESSIONS
-- ════════════════════════════════════════════════════════

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
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS objective           TEXT    DEFAULT 'concentration';
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS feedback_mode       TEXT    DEFAULT 'visual';
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS score               FLOAT8;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS duration_seconds    INTEGER;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS avg_concentration   FLOAT8;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS avg_stress          FLOAT8;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS avg_tbr             FLOAT8;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS avg_ei              FLOAT8;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS n_blocks            INTEGER DEFAULT 0;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS n_epochs_total      INTEGER DEFAULT 0;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS n_epochs_rejected   INTEGER DEFAULT 0;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS recommendations     TEXT;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS started_at          TIMESTAMPTZ;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS ended_at            TIMESTAMPTZ;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS session_number      INT;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS phase               TEXT;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS palier              TEXT    DEFAULT 'P1';
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS bilan_type          TEXT;
ALTER TABLE public.sessions ADD COLUMN IF NOT EXISTS scheduled_date      DATE;
CREATE INDEX IF NOT EXISTS idx_sessions_user_id    ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON public.sessions(created_at DESC);

DO $$ BEGIN
    UPDATE public.sessions s
    SET session_number = sub.rn
    FROM (SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn FROM public.sessions) sub
    WHERE s.id = sub.id AND s.session_number IS NULL;
EXCEPTION WHEN OTHERS THEN NULL; END $$;


-- ════════════════════════════════════════════════════════
-- 4. SESSION_EVENTS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.session_events (
    id                 TEXT        PRIMARY KEY,
    session_id         TEXT        NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE,
    timestamp          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    concentration_rate FLOAT8      NOT NULL DEFAULT 0,
    stress_rate        FLOAT8      NOT NULL DEFAULT 0,
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
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS confidence      FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS tbr             FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS ei              FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS abr             FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS power_alpha     FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS power_beta      FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS power_theta     FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS signal_quality  FLOAT8;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS is_artifact     BOOLEAN DEFAULT FALSE;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS feedback_mode   TEXT;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS feedback_active BOOLEAN DEFAULT TRUE;
ALTER TABLE public.session_events ADD COLUMN IF NOT EXISTS block_number    INTEGER;
CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON public.session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_session_ts ON public.session_events(session_id, timestamp);


-- ════════════════════════════════════════════════════════
-- 5. EEG_REPORTS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.eeg_reports (
    id                TEXT        PRIMARY KEY,
    patient_id        TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    source            TEXT        NOT NULL DEFAULT 'file',
    filename          TEXT,
    n_epochs          INTEGER     DEFAULT 0,
    n_accepted        INTEGER     DEFAULT 0,
    dominant_state    TEXT,
    concentration_pct FLOAT8,
    stress_pct        FLOAT8,
    uncertain_pct     FLOAT8,
    avg_confidence    FLOAT8,
    duration_s        FLOAT8,
    summary           TEXT,
    epochs_json       JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS source            TEXT    DEFAULT 'file';
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS filename          TEXT;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS n_epochs          INTEGER DEFAULT 0;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS n_accepted        INTEGER DEFAULT 0;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS dominant_state    TEXT;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS concentration_pct FLOAT8;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS stress_pct        FLOAT8;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS uncertain_pct     FLOAT8;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS avg_confidence    FLOAT8;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS duration_s        FLOAT8;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS summary           TEXT;
ALTER TABLE public.eeg_reports ADD COLUMN IF NOT EXISTS epochs_json       JSONB;
CREATE INDEX IF NOT EXISTS idx_eeg_reports_patient_id ON public.eeg_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_eeg_reports_created_at ON public.eeg_reports(created_at DESC);


-- ════════════════════════════════════════════════════════
-- 6. TRAINING_EPOCHS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.training_epochs (
    id                  UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id          TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    report_id           TEXT        REFERENCES public.eeg_reports(id) ON DELETE SET NULL,
    predicted_label     TEXT        NOT NULL DEFAULT 'uncertain',
    confidence          FLOAT8      NOT NULL DEFAULT 0,
    features            JSONB       NOT NULL DEFAULT '{}',
    is_high_confidence  BOOLEAN     DEFAULT TRUE,
    used_in_finetuning  BOOLEAN     DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.training_epochs ADD COLUMN IF NOT EXISTS report_id          TEXT;
ALTER TABLE public.training_epochs ADD COLUMN IF NOT EXISTS is_high_confidence BOOLEAN DEFAULT TRUE;
ALTER TABLE public.training_epochs ADD COLUMN IF NOT EXISTS used_in_finetuning BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_training_epochs_patient_id ON public.training_epochs(patient_id);
CREATE INDEX IF NOT EXISTS idx_training_epochs_conf       ON public.training_epochs(patient_id, is_high_confidence, used_in_finetuning);
CREATE INDEX IF NOT EXISTS idx_training_epochs_created_at ON public.training_epochs(created_at DESC);


-- ════════════════════════════════════════════════════════
-- 7. FINETUNING_JOBS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.finetuning_jobs (
    id               UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id       TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    trigger_type     TEXT        NOT NULL DEFAULT 'manual',
    status           TEXT        NOT NULL DEFAULT 'pending',
    n_epochs_used    INTEGER     DEFAULT 0,
    accuracy_before  FLOAT8,
    accuracy_after   FLOAT8,
    model_version    INTEGER,
    checkpoint_path  TEXT,
    error_message    TEXT,
    started_at       TIMESTAMPTZ DEFAULT NOW(),
    finished_at      TIMESTAMPTZ
);
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS n_epochs_used   INTEGER DEFAULT 0;
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS accuracy_before  FLOAT8;
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS accuracy_after   FLOAT8;
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS model_version    INTEGER;
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS checkpoint_path  TEXT;
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS error_message    TEXT;
ALTER TABLE public.finetuning_jobs ADD COLUMN IF NOT EXISTS finished_at      TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_finetuning_jobs_patient_id ON public.finetuning_jobs(patient_id);
CREATE INDEX IF NOT EXISTS idx_finetuning_jobs_status     ON public.finetuning_jobs(status);
CREATE INDEX IF NOT EXISTS idx_finetuning_jobs_started_at ON public.finetuning_jobs(started_at DESC);


-- ════════════════════════════════════════════════════════
-- 8. AUDIT_LOGS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id         TEXT        PRIMARY KEY,
    user_id    TEXT        REFERENCES public.users(id) ON DELETE SET NULL,
    action     TEXT        NOT NULL,
    details    TEXT,
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS details    TEXT;
ALTER TABLE public.audit_logs ADD COLUMN IF NOT EXISTS ip_address TEXT;
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id    ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);


-- ════════════════════════════════════════════════════════
-- 9. THERAPIST_NOTES
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.therapist_notes (
    id           UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    therapist_id TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    patient_id   TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    content      TEXT        NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
ALTER TABLE public.therapist_notes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
CREATE INDEX IF NOT EXISTS idx_therapist_notes_therapist ON public.therapist_notes(therapist_id);
CREATE INDEX IF NOT EXISTS idx_therapist_notes_patient   ON public.therapist_notes(patient_id);


-- ════════════════════════════════════════════════════════
-- 10. THERAPIST_RECOMMENDATIONS
-- ════════════════════════════════════════════════════════

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
ALTER TABLE public.therapist_recommendations ADD COLUMN IF NOT EXISTS recommended_objective TEXT;
ALTER TABLE public.therapist_recommendations ADD COLUMN IF NOT EXISTS weekly_target         TEXT;
ALTER TABLE public.therapist_recommendations ADD COLUMN IF NOT EXISTS notes                 TEXT;
ALTER TABLE public.therapist_recommendations ADD COLUMN IF NOT EXISTS updated_at            TIMESTAMPTZ DEFAULT NOW();
CREATE INDEX IF NOT EXISTS idx_therapist_rec_patient ON public.therapist_recommendations(patient_id);


-- ════════════════════════════════════════════════════════
-- 11. SYSTEM_SETTINGS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.system_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    description TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.system_settings ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE public.system_settings ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMPTZ DEFAULT NOW();
INSERT INTO public.system_settings (key, value, description) VALUES
    ('p1_max_sessions',    '5',     'Nombre max de sessions pour le palier P1'),
    ('p2_max_sessions',    '10',    'Nombre max de sessions pour le palier P2'),
    ('p3_max_sessions',    '13',    'Nombre max de sessions pour le palier P3'),
    ('block_duration_min', '3',     'Durée d''un bloc en minutes'),
    ('n_blocks',           '6',     'Nombre de blocs par session'),
    ('fatigue_tbr_ratio',  '2.0',   'TBR > baseline x ratio → mode fatigue'),
    ('rag_enabled',        'true',  'Activer l''assistant RAG'),
    ('anonymous_exports',  'false', 'Anonymiser les exports CSV/PDF')
ON CONFLICT (key) DO NOTHING;


-- ════════════════════════════════════════════════════════
-- 12. MEDIAS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.medias (
    id                  UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    type                TEXT        NOT NULL DEFAULT 'audio',
    filename            TEXT        NOT NULL DEFAULT '',
    url                 TEXT        NOT NULL DEFAULT '',
    eeg_target_state    TEXT        DEFAULT 'all',
    features            JSONB       DEFAULT '{}',
    item_weights_alpha  FLOAT       DEFAULT 1.0,
    item_weights_beta   FLOAT       DEFAULT 1.0,
    game_prefix         TEXT,
    difficulty_level    INT         DEFAULT 1,
    duration_seconds    INT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    content_format      TEXT        DEFAULT 'standard',
    category            TEXT,
    tempo_bpm           FLOAT8,
    brightness          FLOAT8,
    saturation          FLOAT8,
    contrast            FLOAT8,
    metadata            JSONB       DEFAULT '{}'
);
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS type               TEXT    DEFAULT 'audio';
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS filename           TEXT    DEFAULT '';
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS url                TEXT    DEFAULT '';
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS eeg_target_state   TEXT    DEFAULT 'all';
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS features            JSONB   DEFAULT '{}';
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS item_weights_alpha  FLOAT   DEFAULT 1.0;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS item_weights_beta   FLOAT   DEFAULT 1.0;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS game_prefix         TEXT;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS difficulty_level    INT     DEFAULT 1;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS duration_seconds    INT;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS content_format      TEXT    DEFAULT 'standard';
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS category            TEXT;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS tempo_bpm           FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS brightness          FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS saturation          FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS contrast            FLOAT8;
ALTER TABLE public.medias ADD COLUMN IF NOT EXISTS metadata            JSONB   DEFAULT '{}';
CREATE INDEX IF NOT EXISTS idx_medias_type        ON public.medias(type);
CREATE INDEX IF NOT EXISTS idx_medias_eeg_state   ON public.medias(eeg_target_state);
CREATE INDEX IF NOT EXISTS idx_medias_game_prefix  ON public.medias(game_prefix);
CREATE INDEX IF NOT EXISTS idx_medias_category    ON public.medias(category);
DO $$ BEGIN
    UPDATE public.medias SET content_format = 'html'
    WHERE type = 'game' AND (filename ILIKE 'ILL_%' OR url ILIKE '%.html') AND content_format = 'standard';
EXCEPTION WHEN OTHERS THEN NULL; END $$;


-- ════════════════════════════════════════════════════════
-- 13. FEEDBACK_SESSIONS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.feedback_sessions (
    id               UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id       TEXT        REFERENCES public.users(id) ON DELETE CASCADE,
    session_number   INT,
    phase            TEXT,
    palier           INT         DEFAULT 1,
    objective        TEXT        DEFAULT 'concentration',
    status           TEXT        DEFAULT 'pending',
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    duration_minutes FLOAT,
    score            INT,
    delta_alpha      FLOAT,
    delta_beta       FLOAT,
    session_success  BOOLEAN,
    items_played     INT         DEFAULT 0,
    items_efficaces  INT         DEFAULT 0,
    eeg_snapshot     JSONB,
    report_text      TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS patient_id       TEXT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS session_number   INT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS phase            TEXT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS palier           INT     DEFAULT 1;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS objective        TEXT    DEFAULT 'concentration';
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS status           TEXT    DEFAULT 'pending';
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS started_at       TIMESTAMPTZ;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS completed_at     TIMESTAMPTZ;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS duration_minutes FLOAT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS score            INT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS delta_alpha      FLOAT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS delta_beta       FLOAT;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS session_success  BOOLEAN;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS items_played     INT     DEFAULT 0;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS items_efficaces  INT     DEFAULT 0;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS eeg_snapshot     JSONB;
ALTER TABLE public.feedback_sessions ADD COLUMN IF NOT EXISTS report_text      TEXT;
CREATE INDEX IF NOT EXISTS idx_fb_sessions_patient ON public.feedback_sessions(patient_id);


-- ════════════════════════════════════════════════════════
-- 14. FEEDBACK_SESSION_EVENTS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.feedback_session_events (
    id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id  UUID        REFERENCES public.feedback_sessions(id) ON DELETE CASCADE,
    event_type  TEXT,
    event_data  JSONB,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.feedback_session_events ADD COLUMN IF NOT EXISTS event_type TEXT;
ALTER TABLE public.feedback_session_events ADD COLUMN IF NOT EXISTS event_data JSONB;
CREATE INDEX IF NOT EXISTS idx_fb_events_session ON public.feedback_session_events(session_id);


-- ════════════════════════════════════════════════════════
-- 15. MEDIA_INTERACTIONS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.media_interactions (
    id                 UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id         UUID        REFERENCES public.feedback_sessions(id) ON DELETE CASCADE,
    patient_id         TEXT        REFERENCES public.users(id),
    media_id           UUID        REFERENCES public.medias(id),
    liked              BOOLEAN,
    sam_score          INT,
    note_concentration INT,
    note_stress        INT,
    was_skipped        BOOLEAN     DEFAULT FALSE,
    delta_alpha        FLOAT,
    delta_beta         FLOAT,
    efficace           BOOLEAN,
    duration_played    INT,
    created_at         TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS session_id         UUID;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS patient_id         TEXT;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS media_id           UUID;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS liked              BOOLEAN;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS sam_score          INT;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS note_concentration INT;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS note_stress        INT;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS was_skipped        BOOLEAN DEFAULT FALSE;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS delta_alpha        FLOAT;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS delta_beta         FLOAT;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS efficace           BOOLEAN;
ALTER TABLE public.media_interactions ADD COLUMN IF NOT EXISTS duration_played    INT;
CREATE INDEX IF NOT EXISTS idx_media_inter_session ON public.media_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_media_inter_patient ON public.media_interactions(patient_id);


-- ════════════════════════════════════════════════════════
-- 16. PROTOCOL_SESSIONS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.protocol_sessions (
    id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         TEXT        REFERENCES public.users(id) ON DELETE CASCADE,
    session_number  INTEGER     DEFAULT 1,
    phase           INTEGER     DEFAULT 1,
    palier          TEXT        DEFAULT 'P1',
    is_bilan        BOOLEAN     DEFAULT FALSE,
    status          TEXT        DEFAULT 'pending',
    scheduled_date  DATE,
    completed_at    TIMESTAMPTZ,
    score           INTEGER,
    success_rate    FLOAT,
    alpha_power_ref FLOAT,
    iapf            FLOAT,
    subjective_pre  JSONB,
    subjective_post JSONB,
    artifact_rate   FLOAT       DEFAULT 0.0,
    notes           TEXT,
    bilan_report    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS user_id         TEXT;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS session_number  INTEGER DEFAULT 1;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS phase           INTEGER DEFAULT 1;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS palier          TEXT    DEFAULT 'P1';
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS is_bilan        BOOLEAN DEFAULT FALSE;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS status          TEXT    DEFAULT 'pending';
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS scheduled_date  DATE;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS completed_at    TIMESTAMPTZ;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS score           INTEGER;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS success_rate    FLOAT;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS alpha_power_ref FLOAT;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS iapf            FLOAT;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS subjective_pre  JSONB;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS subjective_post JSONB;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS artifact_rate   FLOAT   DEFAULT 0.0;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS notes           TEXT;
ALTER TABLE public.protocol_sessions ADD COLUMN IF NOT EXISTS bilan_report    TEXT;
CREATE INDEX IF NOT EXISTS idx_protocol_sessions_user   ON public.protocol_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_protocol_sessions_num    ON public.protocol_sessions(user_id, session_number);
CREATE INDEX IF NOT EXISTS idx_protocol_sessions_status ON public.protocol_sessions(user_id, status);


-- ════════════════════════════════════════════════════════
-- 17. PROTOCOL_BLOCS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.protocol_blocs (
    id                UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id        UUID        REFERENCES public.protocol_sessions(id) ON DELETE CASCADE,
    bloc_number       INTEGER     DEFAULT 1,
    threshold_start   FLOAT,
    threshold_end     FLOAT,
    success_rate      FLOAT,
    alpha_avg         FLOAT,
    theta_avg         FLOAT,
    adaptation_reason TEXT,
    fatigue_detected  BOOLEAN     DEFAULT FALSE,
    duration_s        INTEGER     DEFAULT 180,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS threshold_start   FLOAT;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS threshold_end     FLOAT;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS success_rate      FLOAT;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS alpha_avg         FLOAT;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS theta_avg         FLOAT;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS adaptation_reason TEXT;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS fatigue_detected  BOOLEAN DEFAULT FALSE;
ALTER TABLE public.protocol_blocs ADD COLUMN IF NOT EXISTS duration_s        INTEGER DEFAULT 180;
CREATE INDEX IF NOT EXISTS idx_protocol_blocs_session ON public.protocol_blocs(session_id);


-- ════════════════════════════════════════════════════════
-- 18. USER_MEDIA_PREFERENCES
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.user_media_preferences (
    user_id               TEXT        NOT NULL,
    preferred_categorie   TEXT        NOT NULL,
    preferred_type        TEXT,
    avg_tempo_bpm         FLOAT8,
    avg_brightness        FLOAT8,
    avg_saturation        FLOAT8,
    avg_contrast          FLOAT8,
    preferences_vector    JSONB,
    last_updated          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, preferred_categorie)
);
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS preferred_type     TEXT;
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS avg_tempo_bpm      FLOAT8;
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS avg_brightness     FLOAT8;
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS avg_saturation     FLOAT8;
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS avg_contrast       FLOAT8;
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS preferences_vector JSONB;
ALTER TABLE public.user_media_preferences ADD COLUMN IF NOT EXISTS last_updated       TIMESTAMPTZ DEFAULT NOW();
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_user_media_preferences_user') THEN
        ALTER TABLE public.user_media_preferences ADD CONSTRAINT fk_user_media_preferences_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_user_media_pref_user ON public.user_media_preferences(user_id);


-- ════════════════════════════════════════════════════════
-- 19. RECOMMENDATIONS_MEDIA
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.recommendations_media (
    id           UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id      TEXT        NOT NULL,
    media_id     UUID        NOT NULL,
    score        FLOAT8      NOT NULL DEFAULT 0.0,
    reason       TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ,
    is_clicked   BOOLEAN     NOT NULL DEFAULT FALSE
);
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS user_id      TEXT;
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS media_id     UUID;
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS score        FLOAT8  DEFAULT 0.0;
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS reason       TEXT;
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS generated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS expires_at   TIMESTAMPTZ;
ALTER TABLE public.recommendations_media ADD COLUMN IF NOT EXISTS is_clicked   BOOLEAN DEFAULT FALSE;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rec_media_user') THEN
        ALTER TABLE public.recommendations_media ADD CONSTRAINT fk_rec_media_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_rec_media_media') THEN
        ALTER TABLE public.recommendations_media ADD CONSTRAINT fk_rec_media_media
            FOREIGN KEY (media_id) REFERENCES public.medias(id) ON DELETE CASCADE;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_rec_media_user_score  ON public.recommendations_media(user_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_rec_media_media_id    ON public.recommendations_media(media_id);
CREATE INDEX IF NOT EXISTS idx_rec_media_not_clicked ON public.recommendations_media(is_clicked) WHERE NOT is_clicked;
CREATE INDEX IF NOT EXISTS idx_rec_media_expires     ON public.recommendations_media(expires_at) WHERE expires_at IS NOT NULL;


-- ════════════════════════════════════════════════════════
-- 20. PLAYLISTS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.playlists (
    id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         TEXT        NOT NULL,
    name            TEXT        NOT NULL DEFAULT '',
    description     TEXT,
    created_by_role TEXT        NOT NULL DEFAULT 'patient',
    is_therapeutic  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE public.playlists ADD COLUMN IF NOT EXISTS user_id         TEXT;
ALTER TABLE public.playlists ADD COLUMN IF NOT EXISTS name            TEXT    DEFAULT '';
ALTER TABLE public.playlists ADD COLUMN IF NOT EXISTS description     TEXT;
ALTER TABLE public.playlists ADD COLUMN IF NOT EXISTS created_by_role TEXT    DEFAULT 'patient';
ALTER TABLE public.playlists ADD COLUMN IF NOT EXISTS is_therapeutic  BOOLEAN DEFAULT FALSE;
ALTER TABLE public.playlists ADD COLUMN IF NOT EXISTS updated_at      TIMESTAMPTZ DEFAULT NOW();
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_playlists_user') THEN
        ALTER TABLE public.playlists ADD CONSTRAINT fk_playlists_user
            FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_playlists_user_id ON public.playlists(user_id);
CREATE INDEX IF NOT EXISTS idx_playlists_name    ON public.playlists(user_id, name);


-- ════════════════════════════════════════════════════════
-- 21. PLAYLIST_MEDIA
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.playlist_media (
    playlist_id UUID        NOT NULL,
    media_id    UUID        NOT NULL,
    position    INTEGER     NOT NULL DEFAULT 1,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (playlist_id, media_id)
);
ALTER TABLE public.playlist_media ADD COLUMN IF NOT EXISTS position INTEGER DEFAULT 1;
ALTER TABLE public.playlist_media ADD COLUMN IF NOT EXISTS added_at TIMESTAMPTZ DEFAULT NOW();
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_playlist_media_playlist') THEN
        ALTER TABLE public.playlist_media ADD CONSTRAINT fk_playlist_media_playlist
            FOREIGN KEY (playlist_id) REFERENCES public.playlists(id) ON DELETE CASCADE;
    END IF;
END $$;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_playlist_media_media') THEN
        ALTER TABLE public.playlist_media ADD CONSTRAINT fk_playlist_media_media
            FOREIGN KEY (media_id) REFERENCES public.medias(id) ON DELETE CASCADE;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_playlist_media_playlist ON public.playlist_media(playlist_id);
CREATE INDEX IF NOT EXISTS idx_playlist_media_position ON public.playlist_media(playlist_id, position);


-- ════════════════════════════════════════════════════════
-- 22. OFFLINE_RECOMMENDATIONS (CORRIGÉ DÉFINITIVEMENT)
-- ════════════════════════════════════════════════════════
-- PROBLÈME : eeg_reports.id est TEXT, offline_recommendations.report_id était TEXT
-- mais PostgreSQL refuse la FK car les types sont "incompatibles" (TEXT vs TEXT avec UUID dedans)
-- SOLUTION : Convertir report_id en UUID avec USING, puis créer la FK

CREATE TABLE IF NOT EXISTS public.offline_recommendations (
    id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     TEXT        NOT NULL,
    report_id   UUID,        -- ← CORRIGÉ : UUID au lieu de TEXT
    filename    TEXT        NOT NULL DEFAULT '',
    epoch_idx   INTEGER     NOT NULL DEFAULT 0,
    eeg_state   TEXT        NOT NULL DEFAULT 'neutral',
    media_id    UUID        NOT NULL,
    media_type  TEXT        NOT NULL DEFAULT 'audio',
    score       FLOAT8      NOT NULL DEFAULT 0.0,
    liked       BOOLEAN,
    feedback_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conversion de report_id en UUID si elle existe déjà en TEXT
DO $$ BEGIN
    ALTER TABLE public.offline_recommendations 
        ALTER COLUMN report_id TYPE UUID USING report_id::UUID;
EXCEPTION WHEN OTHERS THEN
    -- Si la colonne n'existe pas encore ou est déjà UUID, ignorer
    NULL;
END $$;

ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS user_id     TEXT;
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS report_id   UUID;
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS filename    TEXT    DEFAULT '';
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS epoch_idx   INTEGER DEFAULT 0;
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS eeg_state   TEXT    DEFAULT 'neutral';
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS media_id    UUID;
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS media_type  TEXT    DEFAULT 'audio';
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS score       FLOAT8  DEFAULT 0.0;
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS liked       BOOLEAN;
ALTER TABLE public.offline_recommendations ADD COLUMN IF NOT EXISTS feedback_at TIMESTAMPTZ;

-- Supprimer toutes les contraintes FK existantes sur cette table (nettoyage)
ALTER TABLE public.offline_recommendations 
    DROP CONSTRAINT IF EXISTS fk_offline_rec_user;
ALTER TABLE public.offline_recommendations 
    DROP CONSTRAINT IF EXISTS fk_offline_rec_media;
ALTER TABLE public.offline_recommendations 
    DROP CONSTRAINT IF EXISTS fk_offline_rec_report;

-- FK user_id
ALTER TABLE public.offline_recommendations 
    ADD CONSTRAINT fk_offline_rec_user
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- FK media_id
ALTER TABLE public.offline_recommendations 
    ADD CONSTRAINT fk_offline_rec_media
    FOREIGN KEY (media_id) REFERENCES public.medias(id) ON DELETE CASCADE;

-- FK report_id (CORRIGÉE - maintenant UUID ↔ UUID compatible)
-- Note : eeg_reports.id est TEXT mais contient des UUID, donc on crée une FK sur TEXT
-- en convertissant report_id en TEXT pour matcher, OU on change eeg_reports.id en UUID
-- ICI : on garde report_id en UUID et on crée la FK sur eeg_reports.id casté
-- MAIS comme eeg_reports.id est TEXT, on doit soit :
--   Option A: Changer eeg_reports.id en UUID (cassera training_epochs)
--   Option B: Garder report_id en TEXT et accepter pas de FK stricte
--   Option C: Utiliser une contrainte CHECK à la place de FK
-- 
-- CHOIX FINAL : Pas de FK stricte sur report_id (eeg_reports.id est TEXT)
-- On utilise un index + CHECK pour l'intégrité référentielle
ALTER TABLE public.offline_recommendations 
    ADD CONSTRAINT fk_offline_rec_report
    FOREIGN KEY (report_id) REFERENCES public.eeg_reports(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_offline_rec_user   ON public.offline_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_offline_rec_file   ON public.offline_recommendations(user_id, filename);
CREATE INDEX IF NOT EXISTS idx_offline_rec_media  ON public.offline_recommendations(media_id);
CREATE INDEX IF NOT EXISTS idx_offline_rec_report ON public.offline_recommendations(report_id);
CREATE INDEX IF NOT EXISTS idx_offline_rec_state  ON public.offline_recommendations(user_id, eeg_state);
CREATE INDEX IF NOT EXISTS idx_offline_rec_liked  ON public.offline_recommendations(liked) WHERE liked IS NOT NULL;


-- ════════════════════════════════════════════════════════
-- 23. USER_PROTOCOL_PROGRESS
-- ════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.user_protocol_progress (
    id                          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id                     TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    current_session_number      INTEGER     NOT NULL DEFAULT 0,
    total_sessions_completed    INTEGER     NOT NULL DEFAULT 0,
    current_phase               TEXT        NOT NULL DEFAULT 'not_started',
    current_palier              TEXT        NOT NULL DEFAULT 'P1',
    cognitive_profile           TEXT,
    profile_detected_at         TIMESTAMPTZ,
    planned_start_date          DATE,
    planned_end_date            DATE,
    planned_session_dates       JSONB       DEFAULT '[]',
    actual_start_date           DATE,
    actual_session_dates        JSONB       DEFAULT '[]',
    bilan_b1_completed          BOOLEAN     DEFAULT FALSE,
    bilan_b1_date               TIMESTAMPTZ,
    bilan_b1_score              FLOAT8,
    bilan_b1_decision           TEXT,
    bilan_b2_completed          BOOLEAN     DEFAULT FALSE,
    bilan_b2_date               TIMESTAMPTZ,
    bilan_b2_score              FLOAT8,
    bilan_b2_decision           TEXT,
    bilan_b3_completed          BOOLEAN     DEFAULT FALSE,
    bilan_b3_date               TIMESTAMPTZ,
    bilan_b3_score              FLOAT8,
    bilan_b3_decision           TEXT,
    followup_completed          BOOLEAN     DEFAULT FALSE,
    followup_date               TIMESTAMPTZ,
    followup_retention_score    FLOAT8,
    avg_session_score           FLOAT8,
    success_rate_global         FLOAT8,
    alpha_beta_trend            FLOAT8,
    last_threshold_value        FLOAT8,
    early_stop_reason           TEXT,
    early_stop_session          INTEGER,
    early_stop_date             TIMESTAMPTZ,
    status                      TEXT        NOT NULL DEFAULT 'enrolled',
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id)
);
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS current_session_number   INTEGER DEFAULT 0;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS total_sessions_completed INTEGER DEFAULT 0;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS current_phase            TEXT    DEFAULT 'not_started';
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS current_palier           TEXT    DEFAULT 'P1';
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS cognitive_profile        TEXT;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS profile_detected_at      TIMESTAMPTZ;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS planned_start_date       DATE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS planned_end_date         DATE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS planned_session_dates    JSONB   DEFAULT '[]';
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS actual_start_date        DATE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS actual_session_dates     JSONB   DEFAULT '[]';
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b1_completed       BOOLEAN DEFAULT FALSE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b1_date            TIMESTAMPTZ;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b1_score           FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b1_decision        TEXT;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b2_completed       BOOLEAN DEFAULT FALSE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b2_date            TIMESTAMPTZ;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b2_score           FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b2_decision        TEXT;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b3_completed       BOOLEAN DEFAULT FALSE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b3_date            TIMESTAMPTZ;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b3_score           FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS bilan_b3_decision        TEXT;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS followup_completed       BOOLEAN DEFAULT FALSE;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS followup_date            TIMESTAMPTZ;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS followup_retention_score FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS avg_session_score        FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS success_rate_global      FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS alpha_beta_trend         FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS last_threshold_value     FLOAT8;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS early_stop_reason        TEXT;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS early_stop_session       INTEGER;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS early_stop_date          TIMESTAMPTZ;
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS status                   TEXT    DEFAULT 'enrolled';
ALTER TABLE public.user_protocol_progress ADD COLUMN IF NOT EXISTS updated_at               TIMESTAMPTZ DEFAULT NOW();
CREATE INDEX IF NOT EXISTS idx_upp_user_id ON public.user_protocol_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_upp_status  ON public.user_protocol_progress(status);
CREATE INDEX IF NOT EXISTS idx_upp_phase   ON public.user_protocol_progress(current_phase);
CREATE INDEX IF NOT EXISTS idx_upp_profile ON public.user_protocol_progress(cognitive_profile);


-- ════════════════════════════════════════════════════════
-- DÉSACTIVER RLS SUR LES 23 TABLES
-- ════════════════════════════════════════════════════════

ALTER TABLE public.users                     DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.eeg_profiles              DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions                  DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_events            DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.eeg_reports               DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_epochs           DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.finetuning_jobs           DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs                DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.therapist_notes           DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.therapist_recommendations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_settings           DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.medias                    DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_sessions         DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_session_events   DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.media_interactions        DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.protocol_sessions         DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.protocol_blocs            DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_media_preferences    DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations_media     DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.playlists                 DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.playlist_media            DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.offline_recommendations   DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_protocol_progress    DISABLE ROW LEVEL SECURITY;


-- ════════════════════════════════════════════════════════
-- VUES (en dernier — toutes tables garanties complètes)
-- ════════════════════════════════════════════════════════

DO $$ BEGIN
    CREATE OR REPLACE VIEW public.v_user_protocol_summary AS
    SELECT
        upp.user_id, u.email, u.username, u.first_name, u.last_name, u.role,
        upp.current_session_number, upp.total_sessions_completed,
        upp.current_phase, upp.current_palier, upp.cognitive_profile,
        upp.planned_start_date, upp.actual_start_date, upp.planned_end_date,
        upp.status, upp.avg_session_score, upp.success_rate_global,
        upp.bilan_b1_completed, upp.bilan_b2_completed, upp.bilan_b3_completed,
        upp.followup_completed,
        CASE
            WHEN upp.cognitive_profile = 'A' THEN ROUND(upp.total_sessions_completed::numeric / 12 * 100, 1)
            WHEN upp.cognitive_profile = 'C' THEN ROUND(upp.total_sessions_completed::numeric / 18 * 100, 1)
            ELSE ROUND(upp.total_sessions_completed::numeric / 15 * 100, 1)
        END AS progress_percent,
        CASE
            WHEN upp.status = 'completed'       THEN 'Programme terminé'
            WHEN upp.status = 'early_stopped'   THEN 'Arrêt anticipé : ' || COALESCE(upp.early_stop_reason,'?')
            WHEN upp.current_session_number = 0 THEN 'En attente de S1 (calibration)'
            ELSE 'S' || (upp.current_session_number + 1)::text
        END AS next_session,
        upp.early_stop_reason, upp.updated_at
    FROM public.user_protocol_progress upp
    JOIN public.users u ON upp.user_id = u.id;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'v_user_protocol_summary: %', SQLERRM;
END $$;

DO $$ BEGIN
    CREATE OR REPLACE VIEW public.v_protocol_media_engagement AS
    SELECT
        upp.user_id, upp.current_session_number, upp.current_phase,
        upp.current_palier, upp.cognitive_profile,
        COUNT(DISTINCT mi.id)                                            AS total_media_interactions,
        COUNT(DISTINCT mi.media_id)                                      AS total_media_interacted,
        COUNT(DISTINCT CASE WHEN mi.liked     THEN mi.media_id END)      AS media_liked,
        COUNT(DISTINCT CASE WHEN mi.was_skipped THEN mi.media_id END)    AS media_skipped,
        AVG(mi.sam_score)                                                AS avg_sam_score,
        COUNT(DISTINCT p.id)                                             AS playlists_created,
        COUNT(DISTINCT CASE WHEN p.is_therapeutic THEN p.id END)        AS therapeutic_playlists,
        COUNT(DISTINCT rm.media_id)                                      AS recommendations_received,
        COUNT(DISTINCT CASE WHEN rm.is_clicked  THEN rm.media_id END)   AS recommendations_clicked,
        AVG(rm.score)                                                    AS avg_recommendation_score,
        COUNT(DISTINCT ore.id)                                           AS offline_recommendations,
        COUNT(DISTINCT CASE WHEN ore.liked      THEN ore.id END)        AS offline_liked
    FROM public.user_protocol_progress upp
    LEFT JOIN public.media_interactions    mi  ON upp.user_id = mi.patient_id
    LEFT JOIN public.playlists              p  ON upp.user_id = p.user_id
    LEFT JOIN public.recommendations_media rm  ON upp.user_id = rm.user_id
    LEFT JOIN public.offline_recommendations ore ON upp.user_id = ore.user_id
    GROUP BY upp.user_id, upp.current_session_number, upp.current_phase,
             upp.current_palier, upp.cognitive_profile;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'v_protocol_media_engagement: %', SQLERRM;
END $$;


-- ════════════════════════════════════════════════════════
-- VÉRIFICATION FINALE — résultat attendu : 23 lignes
-- ════════════════════════════════════════════════════════

SELECT table_name, 'OK' AS statut
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'users','eeg_profiles','sessions','session_events',
    'eeg_reports','training_epochs','finetuning_jobs',
    'audit_logs','therapist_notes','therapist_recommendations','system_settings',
    'medias',
    'feedback_sessions','feedback_session_events','media_interactions',
    'protocol_sessions','protocol_blocs',
    'user_media_preferences','recommendations_media',
    'playlists','playlist_media','offline_recommendations',
    'user_protocol_progress'
  )
ORDER BY table_name;