-- ============================================================
-- NeuroCap — Migration fine-tuning DualClassifier
-- À exécuter UNE SEULE FOIS dans l'éditeur SQL de Supabase
-- ============================================================

-- ── 1. Nouvelles colonnes dans training_epochs ───────────────
-- epoch_filtered : signal EEG filtré z-scoré (1000 floats) — pour GRU_Att + EEGNet
-- conc_score     : score 0-10 concentration (DualClassifier) — label GRU_Att
-- stress_score   : score 0-10 stress (DualClassifier)        — label EEGNet
-- + colonnes manquantes pour compatibilité avec le runner

ALTER TABLE training_epochs
    ADD COLUMN IF NOT EXISTS epoch_index         INTEGER   DEFAULT 0,
    ADD COLUMN IF NOT EXISTS epoch_filtered      JSONB,
    ADD COLUMN IF NOT EXISTS conc_score          FLOAT,
    ADD COLUMN IF NOT EXISTS stress_score        FLOAT,
    ADD COLUMN IF NOT EXISTS predicted_confidence FLOAT    DEFAULT 0,
    ADD COLUMN IF NOT EXISTS is_reliable         BOOLEAN   DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS report_id           UUID      REFERENCES eeg_reports(id) ON DELETE SET NULL;

-- ── 2. Nouvelles colonnes dans eeg_profiles ───────────────────
-- conc_checkpoint   : chemin vers le modèle GRU_Att personnel (.pt)
-- stress_checkpoint : chemin vers le modèle EEGNet stress personnel (.pt)

ALTER TABLE eeg_profiles
    ADD COLUMN IF NOT EXISTS conc_checkpoint   TEXT,
    ADD COLUMN IF NOT EXISTS stress_checkpoint TEXT;

-- ── 3. Nouvelles colonnes dans finetuning_jobs ────────────────
ALTER TABLE finetuning_jobs
    ADD COLUMN IF NOT EXISTS version               INTEGER  DEFAULT 1,
    ADD COLUMN IF NOT EXISTS trigger_type          TEXT     DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS model_checkpoint_path TEXT,
    ADD COLUMN IF NOT EXISTS completed_at          TIMESTAMPTZ;

-- ── 4. Index performances ────────────────────────────────────
-- Accélère la requête "époques non utilisées, haute confiance" du runner

CREATE INDEX IF NOT EXISTS idx_training_epochs_finetune
    ON training_epochs (patient_id, is_high_confidence, used_in_finetuning, created_at);

-- ── 5. Vérification ──────────────────────────────────────────
-- Après exécution, vérifier avec :
--   SELECT column_name, data_type
--   FROM information_schema.columns
--   WHERE table_name IN ('training_epochs', 'eeg_profiles', 'finetuning_jobs')
--   ORDER BY table_name, ordinal_position;
