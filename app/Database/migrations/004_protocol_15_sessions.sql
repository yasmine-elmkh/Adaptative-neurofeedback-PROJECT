-- ═══════════════════════════════════════════════════════════════════════════════
-- NeuroCap — Migration 004 : Protocole 15 séances
-- Tables : protocol_sessions, protocol_blocs
-- ALTER  : eeg_profiles (IAPF, P_alpha_ref, ERD, palier, profil A/B/C)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ── 1. Enrichissement table eeg_profiles ─────────────────────────────────────

ALTER TABLE eeg_profiles
  ADD COLUMN IF NOT EXISTS profile_type      TEXT    DEFAULT 'B',
  ADD COLUMN IF NOT EXISTS iapf              FLOAT,
  ADD COLUMN IF NOT EXISTS alpha_band_lo     FLOAT   DEFAULT 8.0,
  ADD COLUMN IF NOT EXISTS alpha_band_hi     FLOAT   DEFAULT 12.0,
  ADD COLUMN IF NOT EXISTS p_alpha_ref       FLOAT,
  ADD COLUMN IF NOT EXISTS erd_pct           FLOAT,
  ADD COLUMN IF NOT EXISTS tbr_ref           FLOAT,
  ADD COLUMN IF NOT EXISTS p_beta_cognitive  FLOAT,
  ADD COLUMN IF NOT EXISTS threshold_s2      FLOAT,
  ADD COLUMN IF NOT EXISTS threshold_current FLOAT   DEFAULT 0.30,
  ADD COLUMN IF NOT EXISTS palier            TEXT    DEFAULT 'P1',
  ADD COLUMN IF NOT EXISTS palier_initial    TEXT    DEFAULT 'P1',
  ADD COLUMN IF NOT EXISTS calibration_date  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS audio_preference  TEXT    DEFAULT 'nature',
  ADD COLUMN IF NOT EXISTS stress_baseline   INTEGER DEFAULT 5,
  ADD COLUMN IF NOT EXISTS focus_baseline    INTEGER DEFAULT 5,
  ADD COLUMN IF NOT EXISTS meditation_exp    TEXT    DEFAULT 'jamais';

-- ── 2. Table protocol_sessions ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS protocol_sessions (
  id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id         TEXT        REFERENCES users(id) ON DELETE CASCADE,  -- TEXT pour correspondre à users.id TEXT
  session_number  INTEGER     NOT NULL,            -- 1 à 15 (+ 16 optionnelle)
  phase           INTEGER     NOT NULL,            -- 1, 2 ou 3
  palier          TEXT        NOT NULL DEFAULT 'P1',
  is_bilan        BOOLEAN     DEFAULT FALSE,       -- TRUE pour S5, S10, S15
  status          TEXT        DEFAULT 'pending',   -- pending | in_progress | completed | skipped
  scheduled_date  DATE,
  completed_at    TIMESTAMPTZ,
  score           INTEGER,                          -- 0–100
  success_rate    FLOAT,                            -- % blocs réussis
  alpha_power_ref FLOAT,                            -- puissance alpha du jour
  iapf            FLOAT,
  subjective_pre  JSONB,                            -- {fatigue, stress, motivation}
  subjective_post JSONB,                            -- {focus, calme, fatigue}
  artifact_rate   FLOAT       DEFAULT 0.0,
  notes           TEXT,
  bilan_report    TEXT,                             -- texte rapport IA (S5, S10, S15)
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_protocol_sessions_user   ON protocol_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_protocol_sessions_num    ON protocol_sessions (user_id, session_number);
CREATE INDEX IF NOT EXISTS idx_protocol_sessions_status ON protocol_sessions (user_id, status);

-- ── 3. Table protocol_blocs ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS protocol_blocs (
  id                UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id        UUID        REFERENCES protocol_sessions(id) ON DELETE CASCADE,
  bloc_number       INTEGER     NOT NULL,   -- 1 à 6
  threshold_start   FLOAT,
  threshold_end     FLOAT,
  success_rate      FLOAT,
  alpha_avg         FLOAT,
  theta_avg         FLOAT,
  adaptation_reason TEXT,
  fatigue_detected  BOOLEAN     DEFAULT FALSE,
  duration_s        INTEGER     DEFAULT 180,
  created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_protocol_blocs_session ON protocol_blocs (session_id);

-- ── 4. Table medias — colonne format html ─────────────────────────────────────

ALTER TABLE medias
  ADD COLUMN IF NOT EXISTS content_format TEXT DEFAULT 'standard';  -- standard | html | svg

-- Mettre à jour les illusions HTML existantes
-- Note : seule la colonne 'url' existe sur medias (pas url_cloudinary)
UPDATE medias
SET content_format = 'html'
WHERE type = 'game'
  AND (
    filename ILIKE 'ILL_%'
    OR url    ILIKE '%.html'
  );

-- ── 5. Sécurité RLS ──────────────────────────────────────────────────────────
-- Désactivé : le backend utilise la clé service_role qui bypasse le RLS.
-- Cohérent avec schema_v3.sql, 005 et 006 qui désactivent tous le RLS.
-- Note : CREATE POLICY IF NOT EXISTS n'existe pas en PostgreSQL standard — supprimé.

ALTER TABLE protocol_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE protocol_blocs    DISABLE ROW LEVEL SECURITY;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DONNÉES DE TEST (optionnel — commenter en production)
-- ═══════════════════════════════════════════════════════════════════════════════
-- INSERT INTO medias (type, filename, url_cloudinary, eeg_target_state, content_format)
-- VALUES
--   ('game', 'ILL_rotating_circles.html', 'https://example.com/ill_rotating.html', 'all', 'html'),
--   ('game', 'ILL_checker_shadow.html',   'https://example.com/ill_checker.html',  'all', 'html');
