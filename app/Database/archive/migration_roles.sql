-- NeuroCap — Migration rôles & contrôle d'accès
-- À exécuter dans l'éditeur SQL Supabase (une seule fois)
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. Ajouter therapist_id à users (null pour patients sans thérapeute assigné)
ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS therapist_id UUID REFERENCES public.users(id) ON DELETE SET NULL;

-- 2. Table therapist_notes — commentaires privés du thérapeute sur ses patients
CREATE TABLE IF NOT EXISTS public.therapist_notes (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  therapist_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  patient_id   UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  content      TEXT NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_therapist_notes_therapist ON public.therapist_notes(therapist_id);
CREATE INDEX IF NOT EXISTS ix_therapist_notes_patient   ON public.therapist_notes(patient_id);

-- 3. S'assurer que les colonnes first_name / last_name existent
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS first_name TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_name  TEXT DEFAULT '';

-- 4. Index sur therapist_id pour les requêtes patients d'un thérapeute
CREATE INDEX IF NOT EXISTS ix_users_therapist_id ON public.users(therapist_id);

-- 5. Contrainte CHECK sur role (patient, therapist, admin, user = rétrocompat)
-- Note : on garde 'user' comme alias de 'patient' pour les données existantes
ALTER TABLE public.users
  DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE public.users
  ADD CONSTRAINT users_role_check
  CHECK (role IN ('user', 'patient', 'therapist', 'admin'));

-- Vérification
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'users'
ORDER BY ordinal_position;
