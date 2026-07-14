# NeuroCap Database — Supabase

All data lives in **Supabase** (hosted PostgreSQL). The backend talks to it exclusively through the async `supabase-py` client — no raw SQL is issued from application code.

---

## Deployment

Run **one file** in the Supabase SQL editor:

```
app/Database/supabase_complete.sql
```

> Idempotent — safe to re-run (`IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS`). This is the current, consolidated schema (23 tables): core accounts/sessions/EEG tables, the 15-session protocol engine, the media recommendation engine, and the free-mode feedback system.

Optional, after the schema is created:
```
app/Database/migrations/seed_medias.sql   # seeds demo media assets into Supabase Storage
```

---

## Core Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│  users                                                                   │
│  id · email · username · first_name · last_name                         │
│  role (patient|therapist|admin) · is_active                             │
│  therapist_id (FK → users) · consent_accepted · consent_date            │
│  deleted_at · created_at                                                 │
└────────────────────┬────────────────────────────────────────────────────┘
                     │ 1:N
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌───────────┐  ┌──────────────┐  ┌─────────────┐
│ sessions  │  │ eeg_profiles │  │ eeg_reports │
│ id        │  │ id           │  │ id          │
│ user_id   │  │ user_id      │  │ patient_id  │
│ objective │  │ profile_type │  │ source      │ ← 'file' | 'live'
│ status    │  │ iapf         │  │ filename    │
│ score     │  │ baseline_tbr │  │ n_epochs    │
│ ...       │  │ palier       │  │ dominant_   │
└─────┬─────┘  │ finetuned_   │  │   state     │
      │ 1:N    │   version    │  │ epochs_json │
      ▼        │ conc_checkpoint  └──────┬──────┘
┌──────────────│ stress_checkpoint       │ 1:N
│session_events│ last_finetune_at        ▼
│ id           │ last_20_sess    ┌─────────────────┐
│ session_id   │   _accuracy     │ training_epochs │
│ concentration└──────────────┘  │ id              │
│ stress_rate                    │ patient_id      │
│ tbr · ei                       │ epoch_filtered  │ ← raw samples for EEGNet fine-tune
│ block_number                   │ conc_score      │
└──────────────┘                 │ stress_score    │
                                 │ is_high_conf    │
                                 │ used_in_finetune│
                                 └─────────────────┘

┌─────────────────────────────────┐
│ finetuning_jobs                 │
│ id · patient_id                 │
│ trigger_type (v1|v2|drift|maint)│
│ status (pending|running|done)   │
│ n_epochs_used                   │
│ accuracy_before · accuracy_after│
│ model_checkpoint_path           │
│ started_at · finished_at        │
└─────────────────────────────────┘

┌────────────────────────────┐   ┌───────────────────────────────────┐
│ therapist_notes            │   │ therapist_recommendations         │
│ id · patient_id            │   │ id · patient_id · therapist_id    │
│ therapist_id · content     │   │ recommended_objective             │
│ created_at                 │   │ weekly_target · notes             │
└────────────────────────────┘   └───────────────────────────────────┘

┌──────────────────────────────────┐   ┌───────────────────────────────┐
│ audit_logs                       │   │ system_settings               │
│ id · user_id · action            │   │ key · value · description     │
│ details · ip_address · created_at│   │ updated_at                    │
└──────────────────────────────────┘   └───────────────────────────────┘
```

### `users`
Accounts with role (`patient` / `therapist` / `admin`), soft-delete (`deleted_at`), assigned therapist (`therapist_id`), and consent tracking (`consent_accepted`, `consent_date`).

### `eeg_profiles`
Cognitive profile per patient: type A/B/C, IAPF, baseline TBR, palier P1–P4. Fine-tuning columns: `finetuned_version`, `conc_checkpoint`, `stress_checkpoint`, `last_finetune_at`, `last_20_sessions_accuracy`.

### `sessions` / `session_events`
Neurofeedback sessions and their per-block EEG events (concentration, stress, TBR, signal quality).

### `eeg_reports`
Analysis reports saved after a file analysis (`/api/eeg/analyze_file`) or a live session. Contains the statistical summary + JSON epoch table.

### `training_epochs`
High-confidence epochs (≥ 0.85) captured during file/live analysis, including the raw filtered samples (`epoch_filtered`) needed to fine-tune EEGNet, plus the concentration/stress scores. Used as the personalisation data for nightly fine-tuning.

### `finetuning_jobs`
History of every automated fine-tuning run: trigger type, epochs used, loss before/after, checkpoint path.

### `therapist_notes` / `therapist_recommendations`
Clinical notes and weekly objectives set by the therapist for their patients.

### `audit_logs` / `system_settings`
Admin mutation trail and configurable system parameters (block duration, block count, fatigue TBR threshold, anonymised export, etc.).

---

## Protocol Engine Tables

15-session adaptive protocol — see [`src/services/protocol_engine.py`](../Backend/app/services/protocol_engine.py) and [`app/Backend/README.md`](../Backend/README.md#protocol--apiprotocol).

| Table | Role |
|---|---|
| `protocol_sessions` | Per-session state of the 15-session program (thresholds, blocs config, completion) |
| `protocol_blocs` | Individual block results within a protocol session |
| `user_protocol_progress` | Calendar-level progress tracking, used for the therapist progress dashboard |

## Media Recommendation Tables

EEG-state-driven adaptive media engine — see [`media_recommendation.py`](../Backend/app/services/media_recommendation.py).

| Table | Role |
|---|---|
| `medias` | Media asset catalogue (audio/image/video/game) |
| `media_interactions` | Per-media interaction log (played, skipped, liked) |
| `user_media_preferences` | Learned per-patient preferences, feeds the recommendation scoring |
| `recommendations_media` | Generated recommendations per patient |
| `playlists` / `playlist_media` | Patient-created personal playlists |
| `offline_recommendations` | Recommendations generated after an offline file analysis |

## Free-Mode Feedback Tables

Non-protocol neurofeedback sessions — see [`app/Backend/app/routes/feedback.py`](../Backend/app/routes/feedback.py).

| Table | Role |
|---|---|
| `feedback_sessions` | Free-mode session records |
| `feedback_session_events` | Per-block events within a free-mode session |

---

## Files in this folder

| File | Usage |
|---|---|
| `supabase_complete.sql` | **Current schema — the single file to run (23 tables)** |
| `migrations/seed_medias.sql` | Optional — seeds demo media assets |
| `historique.sql` | Example analytical SQL queries (debugging / reporting) |
| `inserer_donnees.py` | Demo/test data seed script |
| `schema_v3.sql` | Previous consolidated schema (11 core tables) — superseded by `supabase_complete.sql`, kept for history |
| `migrations/004_protocol_15_sessions.sql`, `005_media_recommendations.sql`, `006_protocol_progress.sql`, `add_feedback_sessions.sql`, `add_medias_table.sql`, `update_sessions_calendar.sql` | Incremental migrations, already merged into `supabase_complete.sql` — kept for history, do not run individually against a fresh database |
| `archive/*.sql` | v1/v2 schema and role migrations — archived, do not use |

---

## Roles

| Value | Description |
|---|---|
| `patient` | User performing neurofeedback sessions |
| `therapist` | Clinician supervising assigned patients |
| `admin` | System administrator |

---

## Soft delete

Users are soft-deleted via `deleted_at = NOW()`. Hard delete is available via `DELETE /api/admin/users/{id}?hard=true`. The backend automatically filters soft-deleted users out of every list query.

---

## Row-Level Security (RLS)

RLS is **disabled** on all tables because the backend uses the **service-role key** server-side, which bypasses RLS. All access control is enforced at the FastAPI level (`get_current_user`, `get_therapist_user`, `get_admin_user`).
