-- ============================================================
-- Migration 006 — Progression calendaire par utilisateur
-- Table : user_protocol_progress
-- Vues  : v_user_protocol_summary, v_protocol_media_engagement
-- Idempotent — safe à relancer
-- Adapté au schéma existant : users.id = TEXT
-- ============================================================

-- ── 1. Table user_protocol_progress ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.user_protocol_progress (

    id                          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id                     TEXT        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Séance courante
    current_session_number      INTEGER     NOT NULL DEFAULT 0,
    total_sessions_completed    INTEGER     NOT NULL DEFAULT 0,

    -- Phase & Palier courants
    current_phase               TEXT        NOT NULL DEFAULT 'not_started',
        -- 'not_started' | 'phase1_discovery' | 'phase2_training' | 'phase3_consolidation'
        -- | 'completed' | 'suspended' | 'early_stop'
    current_palier              TEXT        NOT NULL DEFAULT 'P1',
        -- 'P1' | 'P2' | 'P3' | 'P4'

    -- Profil cognitif (détecté à S1)
    cognitive_profile           TEXT        DEFAULT NULL,           -- 'A' | 'B' | 'C'
    profile_detected_at         TIMESTAMPTZ DEFAULT NULL,

    -- Calendrier prévisionnel (généré après S1)
    planned_start_date          DATE        DEFAULT NULL,
    planned_end_date            DATE        DEFAULT NULL,
    planned_session_dates       JSONB       DEFAULT '[]',
        -- [{session_num, planned_date, phase, palier, is_bilan, is_calibration}]

    -- Calendrier réel (mis à jour après chaque séance)
    actual_start_date           DATE        DEFAULT NULL,
    actual_session_dates        JSONB       DEFAULT '[]',
        -- [{session_num, actual_date, duration_min, status, score, palier}]

    -- Bilans de progression (S5, S10, S15)
    bilan_b1_completed          BOOLEAN     DEFAULT FALSE,
    bilan_b1_date               TIMESTAMPTZ DEFAULT NULL,
    bilan_b1_score              FLOAT8      DEFAULT NULL,
    bilan_b1_decision           TEXT        DEFAULT NULL,   -- 'continue' | 'repeat_phase' | 'adjust_palier'

    bilan_b2_completed          BOOLEAN     DEFAULT FALSE,
    bilan_b2_date               TIMESTAMPTZ DEFAULT NULL,
    bilan_b2_score              FLOAT8      DEFAULT NULL,
    bilan_b2_decision           TEXT        DEFAULT NULL,

    bilan_b3_completed          BOOLEAN     DEFAULT FALSE,
    bilan_b3_date               TIMESTAMPTZ DEFAULT NULL,
    bilan_b3_score              FLOAT8      DEFAULT NULL,
    bilan_b3_decision           TEXT        DEFAULT NULL,

    -- Séance de suivi S16 (optionnelle)
    followup_completed          BOOLEAN     DEFAULT FALSE,
    followup_date               TIMESTAMPTZ DEFAULT NULL,
    followup_retention_score    FLOAT8      DEFAULT NULL,

    -- Indicateurs de progression globaux
    avg_session_score           FLOAT8      DEFAULT NULL,
    success_rate_global         FLOAT8      DEFAULT NULL,
    alpha_beta_trend            FLOAT8      DEFAULT NULL,
    last_threshold_value        FLOAT8      DEFAULT NULL,

    -- Critères d'arrêt anticipé
    early_stop_reason           TEXT        DEFAULT NULL,
        -- 'no_progress' | 'fatigue' | 'wellbeing' | 'artifacts' | 'user_request'
    early_stop_session          INTEGER     DEFAULT NULL,
    early_stop_date             TIMESTAMPTZ DEFAULT NULL,

    -- Statut global
    status                      TEXT        NOT NULL DEFAULT 'enrolled',
        -- 'enrolled' | 'in_progress' | 'completed' | 'early_stopped' | 'suspended'

    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS idx_upp_user_id ON public.user_protocol_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_upp_status  ON public.user_protocol_progress(status);
CREATE INDEX IF NOT EXISTS idx_upp_phase   ON public.user_protocol_progress(current_phase);
CREATE INDEX IF NOT EXISTS idx_upp_profile ON public.user_protocol_progress(cognitive_profile);

ALTER TABLE public.user_protocol_progress DISABLE ROW LEVEL SECURITY;


-- ── 2. Vue récapitulative pour dashboard thérapeute ───────────────────────────

CREATE OR REPLACE VIEW public.v_user_protocol_summary AS
SELECT
    upp.user_id,
    u.email,
    u.username,
    u.first_name,
    u.last_name,
    u.role,
    upp.current_session_number,
    upp.total_sessions_completed,
    upp.current_phase,
    upp.current_palier,
    upp.cognitive_profile,
    upp.planned_start_date,
    upp.actual_start_date,
    upp.planned_end_date,
    upp.status,
    upp.avg_session_score,
    upp.success_rate_global,
    upp.bilan_b1_completed,
    upp.bilan_b2_completed,
    upp.bilan_b3_completed,
    upp.followup_completed,
    -- Progression en %
    CASE
        WHEN upp.cognitive_profile = 'A' THEN ROUND(upp.total_sessions_completed::numeric / 12 * 100, 1)
        WHEN upp.cognitive_profile = 'C' THEN ROUND(upp.total_sessions_completed::numeric / 18 * 100, 1)
        ELSE ROUND(upp.total_sessions_completed::numeric / 15 * 100, 1)
    END AS progress_percent,
    -- Prochaine séance attendue
    CASE
        WHEN upp.status = 'completed'     THEN 'Programme terminé'
        WHEN upp.status = 'early_stopped' THEN 'Arrêt anticipé : ' || COALESCE(upp.early_stop_reason, '?')
        WHEN upp.current_session_number = 0 THEN 'En attente de S1 (calibration)'
        ELSE 'S' || (upp.current_session_number + 1)::text
    END AS next_session,
    upp.early_stop_reason,
    upp.updated_at
FROM public.user_protocol_progress upp
JOIN public.users u ON upp.user_id = u.id;


-- ── 3. Vue engagement média × progression protocole ──────────────────────────

CREATE OR REPLACE VIEW public.v_protocol_media_engagement AS
SELECT
    upp.user_id,
    upp.current_session_number,
    upp.current_phase,
    upp.current_palier,
    upp.cognitive_profile,
    -- Interactions média (table existante)
    COUNT(DISTINCT mi.id)                                                   AS total_media_interactions,
    COUNT(DISTINCT mi.media_id)                                             AS total_media_interacted,
    COUNT(DISTINCT CASE WHEN mi.liked = TRUE  THEN mi.media_id END)        AS media_liked,
    COUNT(DISTINCT CASE WHEN mi.was_skipped = TRUE THEN mi.media_id END)   AS media_skipped,
    AVG(mi.sam_score)                                                       AS avg_sam_score,
    -- Playlists
    COUNT(DISTINCT p.id)                                                    AS playlists_created,
    COUNT(DISTINCT CASE WHEN p.is_therapeutic THEN p.id END)               AS therapeutic_playlists,
    -- Recommandations (nouvelles tables)
    COUNT(DISTINCT rm.media_id)                                             AS recommendations_received,
    COUNT(DISTINCT CASE WHEN rm.is_clicked THEN rm.media_id END)           AS recommendations_clicked,
    AVG(rm.score)                                                           AS avg_recommendation_score,
    -- Offline recommendations
    COUNT(DISTINCT ore.id)                                                  AS offline_recommendations,
    COUNT(DISTINCT CASE WHEN ore.liked = TRUE THEN ore.id END)             AS offline_liked
FROM public.user_protocol_progress upp
LEFT JOIN public.media_interactions   mi  ON upp.user_id = mi.patient_id
LEFT JOIN public.playlists             p  ON upp.user_id = p.user_id
LEFT JOIN public.recommendations_media rm ON upp.user_id = rm.user_id
LEFT JOIN public.offline_recommendations ore ON upp.user_id = ore.user_id
GROUP BY
    upp.user_id, upp.current_session_number, upp.current_phase,
    upp.current_palier, upp.cognitive_profile;


-- ── Vérification ─────────────────────────────────────────────────────────────

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name = 'user_protocol_progress';
