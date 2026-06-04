-- Migration : Tables feedback_sessions et feedback_session_events
-- Exécuter dans l'éditeur SQL Supabase

CREATE TABLE IF NOT EXISTS feedback_sessions (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      TEXT    REFERENCES users(id) ON DELETE CASCADE,
    session_number  INT,
    phase           TEXT    CHECK (phase IN ('phase1', 'phase2', 'phase3')),
    palier          INT     DEFAULT 1 CHECK (palier BETWEEN 1 AND 4),
    objective       TEXT    DEFAULT 'concentration',
    status          TEXT    DEFAULT 'pending'
                        CHECK (status IN ('pending', 'running', 'completed', 'interrupted')),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    duration_minutes FLOAT,
    score           INT,
    delta_alpha     FLOAT,
    delta_beta      FLOAT,
    session_success BOOLEAN,
    items_played    INT     DEFAULT 0,
    items_efficaces INT     DEFAULT 0,
    eeg_snapshot    JSONB,
    report_text     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback_session_events (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID    REFERENCES feedback_sessions(id) ON DELETE CASCADE,
    event_type  TEXT,
    event_data  JSONB,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS media_interactions (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID    REFERENCES feedback_sessions(id) ON DELETE CASCADE,
    patient_id      TEXT    REFERENCES users(id),
    media_id        UUID    REFERENCES medias(id),
    liked           BOOLEAN,
    sam_score       INT     CHECK (sam_score BETWEEN 1 AND 5),
    note_concentration INT  CHECK (note_concentration BETWEEN 1 AND 5),
    note_stress     INT     CHECK (note_stress BETWEEN 1 AND 5),
    was_skipped     BOOLEAN DEFAULT FALSE,
    delta_alpha     FLOAT,
    delta_beta      FLOAT,
    efficace        BOOLEAN,
    duration_played INT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fb_sessions_patient  ON feedback_sessions (patient_id);
CREATE INDEX IF NOT EXISTS idx_fb_events_session    ON feedback_session_events (session_id);
CREATE INDEX IF NOT EXISTS idx_media_inter_session  ON media_interactions (session_id);
CREATE INDEX IF NOT EXISTS idx_media_inter_patient  ON media_interactions (patient_id);
