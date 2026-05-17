# NeuroCap Database — Supabase (PostgreSQL)

All data is stored in **Supabase** (hosted PostgreSQL). The backend communicates via the `supabase-py` async client; no direct SQL queries are issued from application code.

---

## Schema overview

```
┌─────────────────────────────────────────────────────────────┐
│  users                                                       │
│  id · email · username · first_name · last_name             │
│  role · is_active · hashed_password                         │
│  therapist_id (FK → users.id) · deleted_at · created_at     │
└────────────────────┬────────────────────────────────────────┘
                     │ 1:N
          ┌──────────┴──────────┐
          ▼                     ▼
   ┌─────────────┐      ┌──────────────────┐
   │  sessions   │      │  eeg_profiles    │
   │  id         │      │  id              │
   │  user_id    │      │  user_id         │
   │  objective  │      │  profile_type    │
   │  status     │      │  iapf            │
   │  score      │      │  baseline_tbr    │
   │  ...        │      │  palier          │
   └──────┬──────┘      │  reactivity_score│
          │ 1:N         └──────────────────┘
          ▼
   ┌─────────────────┐
   │  session_events │
   │  id             │
   │  session_id     │
   │  concentration  │
   │  stress_rate    │
   │  tbr · ei       │
   │  block_number   │
   └─────────────────┘

┌────────────────────────────┐   ┌────────────────────────────────────┐
│  therapist_notes           │   │  therapist_recommendations         │
│  id · patient_id           │   │  id · patient_id · therapist_id    │
│  therapist_id · content    │   │  recommended_objective             │
│  created_at                │   │  weekly_sessions_target · message  │
└────────────────────────────┘   └────────────────────────────────────┘

┌──────────────────────────────────┐   ┌───────────────────────────────┐
│  audit_logs                      │   │  system_settings              │
│  id · user_id · action           │   │  key · value · description    │
│  details · ip_address            │   │  updated_at                   │
│  created_at                      │   └───────────────────────────────┘
└──────────────────────────────────┘
```

---

## Migration files

| File | Purpose |
|---|---|
| `NeuroCap_DB.sql` | Full initial schema creation |
| `migration_roles.sql` | Add `role`, `is_active`, `first_name`, `last_name` columns |
| `migration_roles_v2.sql` | Add `therapist_id`, `deleted_at` columns |
| `supabase_migration.sql` | Consolidated migration for fresh Supabase deployments |
| `historique.sql` | Session history views |
| `inserer_donnees.py` | Seed script for demo/test data |

---

## Running migrations

In the **Supabase SQL editor** (or `psql`):

```sql
-- Step 1: core schema
\i NeuroCap_DB.sql

-- Step 2: role system
\i migration_roles_v2.sql

-- Step 3: full consolidated (alternative to steps 1+2)
\i supabase_migration.sql
```

Or run the full consolidated migration:

```sql
-- Add missing columns safely
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS therapist_id UUID REFERENCES public.users(id) ON DELETE SET NULL;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS first_name TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_name TEXT DEFAULT '';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'patient';

-- Clinical notes
CREATE TABLE IF NOT EXISTS public.therapist_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  therapist_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Therapist recommendations
CREATE TABLE IF NOT EXISTS public.therapist_recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  therapist_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  recommended_objective TEXT,
  weekly_sessions_target INTEGER,
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit logs
CREATE TABLE IF NOT EXISTS public.audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  details TEXT DEFAULT '',
  ip_address TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- System settings
CREATE TABLE IF NOT EXISTS public.system_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL DEFAULT '',
  description TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Roles

| Value | Description |
|---|---|
| `patient` | End user performing neurofeedback sessions |
| `therapist` | Clinician monitoring assigned patients |
| `admin` | System administrator |

> Legacy role value `user` is treated as `patient` in the backend for backwards compatibility.

---

## Soft delete

Users are soft-deleted by setting `deleted_at = NOW()`. Hard delete is possible via `DELETE /api/admin/users/{id}?hard=true`. The backend filters out soft-deleted users from all list queries.

---

## Row-Level Security (RLS)

Supabase RLS is intentionally **disabled** on most tables because the backend uses the **service-role key** server-side, which bypasses RLS. All access control is enforced at the FastAPI dependency layer (`get_current_user`, `get_therapist_user`, `get_admin_user`).
