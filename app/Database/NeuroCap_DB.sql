-- =============================================================================
-- NeuroCap — Schéma PostgreSQL Production
-- Version: 1.0.0 | 2025-2026
-- =============================================================================
-- Ordre de création:
--   1. Extensions
--   2. Tables (users → cognitive_profiles → sessions → rag_conversations)
--   3. Index
--   4. Vues analytiques
--   5. Fonctions utilitaires
-- =============================================================================

-- ── Extensions ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- Recherche texte floue (email search)
CREATE EXTENSION IF NOT EXISTS "btree_gin";   -- Index GIN sur colonnes simples


-- ── Table: users ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id                VARCHAR(36)  PRIMARY KEY DEFAULT (uuid_generate_v4()::text),
    email             VARCHAR(255) UNIQUE NOT NULL,
    hashed_password   VARCHAR(255) NOT NULL,
    first_name        VARCHAR(100) NOT NULL,
    last_name         VARCHAR(100) NOT NULL,
    role              VARCHAR(20)  NOT NULL DEFAULT 'user',  -- 'user' | 'admin'
    is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
    gdpr_consent      BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Table: cognitive_profiles ─────────────────────────────────────────────────
-- Profil EEG individualisé — calculé lors de la calibration (S1)
CREATE TABLE IF NOT EXISTS cognitive_profiles (
    id                          VARCHAR(36)  PRIMARY KEY DEFAULT (uuid_generate_v4()::text),
    user_id                     VARCHAR(36)  UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Paramètres EEG individuels
    iapf                        FLOAT,          -- Individual Alpha Peak Frequency (7-13 Hz)
    p_alpha_baseline            FLOAT,          -- Puissance alpha repos (µV²/Hz)
    p_beta_baseline             FLOAT,
    p_theta_baseline            FLOAT,
    p_delta_baseline            FLOAT,
    tbr_baseline                FLOAT,          -- Theta/Beta Ratio de référence
    abr_baseline                FLOAT,          -- Alpha/Beta Ratio de référence
    eeg_reactivity              FLOAT,          -- Capacité de modulation (0-1), ERD

    -- Classification & adaptation
    user_profile                VARCHAR(1)   DEFAULT 'B',  -- 'A' | 'B' | 'C'
    current_threshold_alpha     FLOAT,
    current_tier                INTEGER      DEFAULT 1,    -- Palier 1-4
    finetuned_model_path        VARCHAR(500),              -- Chemin checkpoint .pt/.h5

    -- Statut
    is_calibrated               BOOLEAN      DEFAULT FALSE,
    calibration_date            TIMESTAMPTZ,

    created_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Table: sessions ───────────────────────────────────────────────────────────
-- Une session = 35-40 min | 6 blocs × 3 min | feedback adaptatif
CREATE TABLE IF NOT EXISTS sessions (
    id                          VARCHAR(36)  PRIMARY KEY DEFAULT (uuid_generate_v4()::text),
    user_id                     VARCHAR(36)  NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Identification
    session_number              INTEGER      NOT NULL,
    objective                   VARCHAR(50)  NOT NULL DEFAULT 'concentration',  -- concentration | stress
    status                      VARCHAR(20)  NOT NULL DEFAULT 'pending',         -- pending | in_progress | completed | aborted

    -- Timing
    created_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    started_at                  TIMESTAMPTZ,
    completed_at                TIMESTAMPTZ,

    -- Métriques globales (calculées post-session)
    session_score               FLOAT,          -- 0-100
    success_rate                FLOAT,          -- 0-1
    avg_tbr                     FLOAT,
    avg_abr                     FLOAT,
    avg_engagement_index        FLOAT,
    avg_p_concentration         FLOAT,
    avg_p_stress                FLOAT,

    -- Palier
    tier                        INTEGER      DEFAULT 1,

    -- Détail JSON (flexible)
    blocks_history              JSONB,
    -- Exemple:
    -- [{"block_number":1,"threshold":0.95,"success_rate":0.68,"avg_p_concentration":0.72,
    --   "avg_tbr":0.62,"duration_seconds":180,"threshold_adjustment":0.5}, ...]

    pre_questionnaire           JSONB,
    -- {"fatigue":5,"stress":4,"motivation":8,"sleep_quality":7}

    post_questionnaire          JSONB,
    -- {"focus":7,"calmness":6,"fatigue":4,"nasa_tlx":{...}}

    adaptations_log             JSONB,
    -- [{"timestamp":"14:30:45","event":"threshold_increase","from":0.95,"to":1.45}, ...]

    eeg_summary                 JSONB,
    -- {"p_alpha_mean":4.2,"p_beta_mean":3.1,"p_theta_mean":2.8,"iapf":9.5}

    -- Texte libre
    recommendations             TEXT,
    notes                       TEXT
);

-- ── Table: rag_conversations ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rag_conversations (
    id          VARCHAR(36)  PRIMARY KEY DEFAULT (uuid_generate_v4()::text),
    user_id     VARCHAR(36)  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question    TEXT         NOT NULL,
    answer      TEXT         NOT NULL,
    sources     JSONB,               -- ["TBR interpretation", "Protocole 15 séances"]
    latency_ms  FLOAT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);


-- ── Index ─────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_email
    ON users USING btree (email);

CREATE INDEX IF NOT EXISTS idx_users_is_active
    ON users (is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_cogprof_user
    ON cognitive_profiles (user_id);

CREATE INDEX IF NOT EXISTS idx_sessions_user_created
    ON sessions (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_user_status
    ON sessions (user_id, status);

CREATE INDEX IF NOT EXISTS idx_sessions_created_at
    ON sessions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rag_user
    ON rag_conversations (user_id, created_at DESC);

-- Index JSONB pour recherches avancées dans blocks_history
CREATE INDEX IF NOT EXISTS idx_sessions_blocks_gin
    ON sessions USING GIN (blocks_history);


-- ── Triggers: auto-update updated_at ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_cogprof_updated_at
    BEFORE UPDATE ON cognitive_profiles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ── Vue: user_statistics ──────────────────────────────────────────────────────
-- Statistiques globales par utilisateur — utilisée par le dashboard
CREATE OR REPLACE VIEW user_statistics AS
SELECT
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.created_at                                            AS member_since,
    cp.user_profile,
    cp.iapf,
    cp.current_tier,
    cp.is_calibrated,
    COUNT(s.id)                                             AS total_sessions,
    COUNT(s.id) FILTER (WHERE s.status = 'completed')       AS completed_sessions,
    ROUND(AVG(s.session_score)::numeric, 1)                 AS avg_score,
    ROUND(AVG(s.avg_tbr)::numeric, 3)                       AS avg_tbr,
    ROUND(AVG(s.avg_p_concentration)::numeric, 3)           AS avg_concentration,
    MAX(s.completed_at)                                     AS last_session_date
FROM users u
LEFT JOIN cognitive_profiles cp ON cp.user_id = u.id
LEFT JOIN sessions s ON s.user_id = u.id
WHERE u.is_active = TRUE
GROUP BY u.id, cp.user_profile, cp.iapf, cp.current_tier, cp.is_calibrated;


-- ── Vue: session_progression ──────────────────────────────────────────────────
-- Progression session-par-session (utile pour le graphique linéaire)
CREATE OR REPLACE VIEW session_progression AS
SELECT
    s.user_id,
    s.session_number,
    s.session_score,
    s.avg_tbr,
    s.avg_abr,
    s.avg_p_concentration,
    s.avg_p_stress,
    s.success_rate,
    s.tier,
    s.objective,
    s.completed_at,
    LAG(s.session_score) OVER (PARTITION BY s.user_id ORDER BY s.session_number)
        AS prev_score,
    s.session_score - LAG(s.session_score) OVER (PARTITION BY s.user_id ORDER BY s.session_number)
        AS score_delta
FROM sessions s
WHERE s.status = 'completed'
ORDER BY s.user_id, s.session_number;


-- ── Requête utilitaire: comparer deux sessions consécutives ───────────────────
-- Utilisation: SELECT * FROM compare_consecutive_sessions('user-uuid-here');
CREATE OR REPLACE FUNCTION compare_consecutive_sessions(p_user_id VARCHAR)
RETURNS TABLE (
    s1_number   INTEGER,
    s1_score    FLOAT,
    s1_tbr      FLOAT,
    s2_number   INTEGER,
    s2_score    FLOAT,
    s2_tbr      FLOAT,
    improvement FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.session_number,
        a.session_score,
        a.avg_tbr,
        b.session_number,
        b.session_score,
        b.avg_tbr,
        ROUND(((b.session_score - a.session_score) / NULLIF(a.session_score, 0) * 100)::numeric, 1)::float
    FROM sessions a
    JOIN sessions b ON b.user_id = a.user_id
        AND b.session_number = a.session_number + 1
    WHERE a.user_id = p_user_id
      AND a.status = 'completed'
      AND b.status = 'completed'
    ORDER BY a.session_number;
END;
$$ LANGUAGE plpgsql;


-- ── Requête: top utilisateurs par progression ─────────────────────────────────
-- Usage analytique admin
CREATE OR REPLACE VIEW top_progressors AS
SELECT
    u.id,
    u.first_name || ' ' || u.last_name      AS full_name,
    cp.user_profile,
    COUNT(s.id)                              AS sessions_completed,
    ROUND(AVG(s.session_score)::numeric, 1)  AS avg_score,
    MAX(s.session_score) - MIN(s.session_score) AS score_range
FROM users u
JOIN cognitive_profiles cp ON cp.user_id = u.id
JOIN sessions s ON s.user_id = u.id AND s.status = 'completed'
WHERE s.created_at > NOW() - INTERVAL '4 weeks'
GROUP BY u.id, full_name, cp.user_profile
HAVING COUNT(s.id) >= 3
ORDER BY score_range DESC;


-- ── Seed: Admin par défaut (à supprimer après premier déploiement) ────────────
-- Password: Admin@NeuroCap2026 — changer immédiatement en production
-- INSERT INTO users (id, email, hashed_password, first_name, last_name, role, gdpr_consent)
-- VALUES (
--     uuid_generate_v4()::text,
--     'admin@neurocap.local',
--     '$2b$12$CHANGE_THIS_WITH_REAL_BCRYPT_HASH',
--     'Admin', 'NeuroCap', 'admin', TRUE
-- );

-- =============================================================================
-- SETUP RAPIDE — commandes à exécuter dans l'ordre:
--
-- 1. Créer la base et l'utilisateur:
--    sudo -u postgres psql
--    CREATE USER neurocap_user WITH PASSWORD 'neurocap_pass';
--    CREATE DATABASE neurocap_db OWNER neurocap_user;
--    GRANT ALL PRIVILEGES ON DATABASE neurocap_db TO neurocap_user;
--    \q
--
-- 2. Appliquer le schéma:
--    psql -U neurocap_user -d neurocap_db -f neurocap_schema.sql
--
-- 3. Vérifier:
--    psql -U neurocap_user -d neurocap_db -c "\dt"
--
-- Pour les migrations futures, utiliser Alembic:
--    alembic init alembic
--    alembic revision --autogenerate -m "initial"
--    alembic upgrade head
-- =============================================================================