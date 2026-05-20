# NeuroCap Database — Supabase v3.0

Toutes les données sont stockées dans **Supabase** (PostgreSQL hébergé). Le backend communique via le client async `supabase-py` ; aucune requête SQL directe n'est émise depuis le code applicatif.

---

## Déploiement

**Un seul fichier à exécuter** dans l'éditeur SQL Supabase :

```
app/Database/schema_v3.sql
```

> Idempotent — safe à relancer plusieurs fois (`IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS`).  
> Ce fichier remplace et consolide tous les anciens fichiers de migration.

---

## Schéma v3.0

```
┌─────────────────────────────────────────────────────────────────────────┐
│  users                                                                   │
│  id · email · username · first_name · last_name                         │
│  role (patient|therapist|admin) · is_active                             │
│  therapist_id (FK → users) · deleted_at · created_at                   │
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
      ▼        │ last_finetune│  └──────┬──────┘
┌──────────────│   _at        │         │ 1:N
│session_events│ last_20_sess │         ▼
│ id           │   _accuracy  │  ┌─────────────────┐
│ session_id   └──────────────┘  │ training_epochs │
│ concentration                  │ id              │
│ stress_rate                    │ patient_id      │
│ tbr · ei                       │ predicted_label │
│ block_number                   │ confidence      │
└──────────────┘                 │ features (JSONB)│ ← 63 features FeatEng
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
│ model_version · checkpoint_path │
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

---

## Tables

### `users`
Comptes utilisateurs avec rôle (`patient` / `therapist` / `admin`), soft-delete (`deleted_at`), et lien thérapeute assigné (`therapist_id`).

### `eeg_profiles`
Profil cognitif de chaque patient : type A/B/C, IAPF, TBR baseline, palier P1–P4.  
Colonnes fine-tuning v3.0 : `finetuned_version`, `finetuned_model_checkpoint`, `last_finetune_at`, `last_20_sessions_accuracy`.

### `sessions` / `session_events`
Sessions de neurofeedback et leurs événements EEG par bloc (concentration, stress, TBR, qualité signal).

### `eeg_reports`
Rapports d'analyse EEG stockés après chaque analyse fichier (`/api/eeg/analyze_file`) ou session live. Contient le résumé statistique + tableau JSON des époques.

### `training_epochs`
Epochs haute-confiance (≥ 0.85) extraites lors des analyses fichiers. Stockées en JSONB (63 features FeatEng). Utilisées comme données d'entraînement pour le fine-tuning LightGBM.

### `finetuning_jobs`
Historique de chaque run de fine-tuning automatique. Trace le type de déclenchement, le nombre d'epochs utilisées, l'accuracy avant/après, et le chemin du checkpoint sauvegardé.

### `therapist_notes` / `therapist_recommendations`
Notes cliniques et objectifs hebdomadaires définis par le thérapeute pour ses patients.

### `audit_logs`
Journal de toutes les mutations admin (création/modification/suppression d'utilisateurs, changements de settings).

### `system_settings`
Paramètres configurables via l'interface admin : durée blocs, nombre blocs, seuil TBR fatigue, export anonymisé, etc.

---

## Fichiers du dossier

| Fichier | Usage |
|---|---|
| `schema_v3.sql` | **Schéma complet v3.0 — fichier unique à exécuter** |
| `NeuroCap_DB.sql` | Schéma initial v1 (obsolète — conservé pour référence historique) |
| `supabase_migration.sql` | Migration v1 → v2 (obsolète — intégré dans schema_v3.sql) |
| `migration_roles.sql` | Ajout rôles v1 (obsolète — intégré dans schema_v3.sql) |
| `migration_roles_v2.sql` | Ajout rôles v2 (obsolète — intégré dans schema_v3.sql) |
| `historique.sql` | Exemples de requêtes analytiques SQL |
| `inserer_donnees.py` | Script de seed pour données de démo/test |

---

## Rôles

| Valeur | Description |
|---|---|
| `patient` | Utilisateur effectuant des sessions neurofeedback |
| `therapist` | Clinicien supervisant ses patients assignés |
| `admin` | Administrateur système |

---

## Soft delete

Les utilisateurs sont soft-deletés via `deleted_at = NOW()`. La suppression hard est possible via `DELETE /api/admin/users/{id}?hard=true`. Le backend filtre automatiquement les soft-deleted de toutes les requêtes de liste.

---

## Row-Level Security (RLS)

RLS est **désactivé** sur toutes les tables car le backend utilise la **service-role key** côté serveur, qui bypasse RLS. Tout le contrôle d'accès est appliqué au niveau FastAPI (`get_current_user`, `get_therapist_user`, `get_admin_user`).
