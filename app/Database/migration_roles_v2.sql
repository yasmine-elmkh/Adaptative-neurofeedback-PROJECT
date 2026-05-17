-- NeuroCap — Migration rôles v2 (complète)
-- À exécuter dans l'éditeur SQL Supabase (idempotente — safe à relancer)
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. Colonnes supplémentaires sur users
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS first_name  TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_name   TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS therapist_id UUID REFERENCES public.users(id) ON DELETE SET NULL;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login  TIMESTAMPTZ;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS deleted_at  TIMESTAMPTZ;   -- soft delete

-- 2. Contrainte CHECK sur role
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE public.users ADD CONSTRAINT users_role_check
  CHECK (role IN ('user', 'patient', 'therapist', 'admin'));

-- 3. Index
CREATE INDEX IF NOT EXISTS ix_users_therapist_id ON public.users(therapist_id);
CREATE INDEX IF NOT EXISTS ix_users_role         ON public.users(role);
CREATE INDEX IF NOT EXISTS ix_users_deleted_at   ON public.users(deleted_at) WHERE deleted_at IS NULL;

-- 4. Table therapist_notes
CREATE TABLE IF NOT EXISTS public.therapist_notes (
  id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  therapist_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  patient_id   UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  content      TEXT NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_therapist_notes_therapist ON public.therapist_notes(therapist_id);
CREATE INDEX IF NOT EXISTS ix_therapist_notes_patient   ON public.therapist_notes(patient_id);

-- 5. Table system_settings (configuration admin)
CREATE TABLE IF NOT EXISTS public.system_settings (
  key         TEXT PRIMARY KEY,
  value       TEXT NOT NULL,
  description TEXT,
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Valeurs par défaut (ignorées si clé déjà existante)
INSERT INTO public.system_settings (key, value, description) VALUES
  ('p1_max_sessions',     '5',     'Nombre max de sessions pour le palier P1'),
  ('p2_max_sessions',     '10',    'Nombre max de sessions pour le palier P2'),
  ('p3_max_sessions',     '13',    'Nombre max de sessions pour le palier P3'),
  ('block_duration_min',  '3',     'Durée d''un bloc en minutes'),
  ('n_blocks',            '6',     'Nombre de blocs par session'),
  ('fatigue_tbr_ratio',   '2.0',   'TBR > baseline × ce ratio → mode fatigue'),
  ('rag_enabled',         'true',  'Activer l''assistant RAG'),
  ('anonymous_exports',   'false', 'Anonymiser les exports CSV/PDF')
ON CONFLICT (key) DO NOTHING;

-- 6. Vérification finale
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('users','eeg_profiles','sessions','session_events',
                     'audit_logs','therapist_notes','system_settings');
