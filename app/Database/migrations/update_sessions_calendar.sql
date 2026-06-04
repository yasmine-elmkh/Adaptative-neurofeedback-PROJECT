-- Migration : Colonnes protocole pour calendrier 15 séances
-- Exécuter dans l'éditeur SQL Supabase

ALTER TABLE sessions ADD COLUMN IF NOT EXISTS session_number  INT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS phase           TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS palier          TEXT DEFAULT 'P1';  -- TEXT cohérent avec eeg_profiles.palier ('P1'..'P4')
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS bilan_type      TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS scheduled_date  DATE;

-- Rétro-remplissage session_number pour les séances existantes
UPDATE sessions s
SET    session_number = sub.rn
FROM  (
    SELECT id,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn
    FROM   sessions
) sub
WHERE  s.id = sub.id
  AND  s.session_number IS NULL;
