# CHANGES — Intégration Schéma EEG ↔ Recommandation Média

**Date :** 2026-06-03  
**Version :** NeuroCap v2.3.0  
**Périmètre :** Pont complet entre le schéma EEG (sessions, profils, rapports) et le moteur de recommandation média (playlists, scoring, préférences)

---

## Analyse de l'existant

Avant ces modifications, la base contenait :

| Table | Statut |
|---|---|
| `users` | ✅ Existait |
| `eeg_profiles` | ✅ Existait |
| `sessions` | ✅ Existait |
| `session_events` | ✅ Existait |
| `eeg_reports` | ✅ Existait |
| `training_epochs` | ✅ Existait |
| `finetuning_jobs` | ✅ Existait |
| `medias` | ✅ Existait (sans category, tempo_bpm, brightness, saturation, contrast) |
| `media_interactions` | ✅ Existait (liée à `feedback_sessions`, pas à `sessions`) |
| `feedback_sessions` | ✅ Existait |
| `feedback_session_events` | ✅ Existait |
| `user_media_preferences` | ❌ Manquait |
| `recommendations_media` | ❌ Manquait |
| `playlists` | ❌ Manquait |
| `playlist_media` | ❌ Manquait |
| `offline_recommendations` | ❌ Manquait |

---

## Fichiers créés

### 1. `app/Database/migrations/005_media_recommendations.sql`

**Nouvelles colonnes sur `medias` :**
- `category TEXT` — classification sémantique (nature, binaural, focus, rhythmic…)
- `tempo_bpm FLOAT8` — tempo musical pour adaptation par palier
- `brightness FLOAT8` — luminosité [0,1] pour adaptation au stress
- `saturation FLOAT8` — saturation colorimétrique [0,1]
- `contrast FLOAT8` — contraste [0,1]
- `metadata JSONB` — métadonnées libres

**Nouvelles tables :**

| Table | Description |
|---|---|
| `user_media_preferences` | Préférences audio/visuelles apprises (PK: user_id + preferred_categorie) |
| `recommendations_media` | Recommandations générées avec score [0,1], expires_at, is_clicked (UNIQUE user_id+media_id) |
| `playlists` | Playlists personnelles ou thérapeutiques (champ is_therapeutic, created_by_role) |
| `playlist_media` | Items ordonnés d'une playlist (PK: playlist_id + media_id, position) |
| `offline_recommendations` | Recommandations par époque EEG fichier (report_id FK, liked différé) |

**Contraintes d'intégrité ajoutées :**
- `offline_recommendations.report_id → eeg_reports(id)` — lien clé : rapport EEG ↔ recommandations offline
- Toutes les tables référencent `users(id)` et `medias(id)` avec ON DELETE CASCADE
- RLS désactivé sur toutes les nouvelles tables

**Note d'adaptation :** `medias.id` reste **UUID** (non BIGINT) pour compatibilité avec l'existant.

---

### 2. `app/Backend/app/schemas/media_reco.py`

Modèles Pydantic correspondant aux nouvelles tables et aux entrées/sorties API :

- `MediaOut` — Média enrichi avec category, tempo_bpm, brightness, etc.
- `UserMediaPreferencesOut` — Sortie préférences utilisateur
- `RecommendationsMediaOut / WithMedia` — Recommandation avec optionnel média jointure
- `PlaylistCreate / PlaylistOut / PlaylistWithMedia` — CRUD playlists
- `OfflineRecommendationOut / OfflineRecommendationFeedback` — Recos offline + like différé
- `SessionMediaRecommendRequest` — Entrée endpoint recommandation live
- `MediaFeedbackItem / SessionMediaFeedbackRequest` — Entrée feedback post-session
- `TherapeuticPlaylistRequest` — Entrée création playlist thérapeute
- `MediaScoringInput` — Paramètres internes du moteur de scoring
- `PatientDashboard` — Vue unifiée patient (sessions + profil + recos + playlists + rapports)
- `SessionWithMediaSummary / EEGReportSummary` — Résumés pour le dashboard

---

### 3. `app/Backend/app/services/media_recommendation.py`

Service central de scoring et de gestion des recommandations :

**Constantes métier :**
- `PROFILE_CATEGORIES` : Profil A → apaisant, B → équilibré, C → stimulant
- `PALIER_TEMPO` : P1 (60–80 BPM), P2 (70–90), P3 (80–100), P4 (variable)
- `PALIER_MAX_DURATION` : P1 = 3 min, P2 = 5 min, P3 = 10 min, P4 = illimité
- `CALMING_CATEGORIES` : catégories prioritaires lors de stress prolongé

**Fonctions clés :**

| Fonction | Description |
|---|---|
| `determine_eeg_state(conc, stress)` | stress>0.6 → stress, conc>0.7 → focus, sinon neutral |
| `score_media(media, profile, state, palier, liked, calming)` | Score [0,1] = Thompson × profile_weight × state_weight × liked_bonus |
| `generate_live_recommendations(...)` | Upsert top-5 dans recommendations_media, retourne les médias |
| `update_user_preferences(user_id, media, rating, db)` | Mise à jour pondérée de user_media_preferences (bayesian update) |
| `recalculate_scores_after_finetuning(patient_id, accuracy, db)` | score × (1 + accuracy_after − 0.5), clampé [0,1] |
| `purge_expired_recommendations(db)` | Supprime les recos expirées (> 7 jours) |

---

### 4. `app/Backend/app/services/session_media_bridge.py`

Pont entre session_events EEG et le moteur de recommandation :

| Fonction | Description |
|---|---|
| `get_session_eeg_state(session_id, db)` | Calcule eeg_state depuis les 30 derniers session_events (hors artefacts) |
| `check_consecutive_stress_blocks(session_id, db)` | Détecte 3+ blocs consécutifs avec avg_stress > 0.7 |
| `get_patient_eeg_profile(user_id, db)` | Retourne (profile_type, palier) depuis eeg_profiles |
| `mark_recommendation_clicked(user_id, media_id, db)` | Met is_clicked = True dans recommendations_media |
| `get_session_feedback_sessions_id(session_id, db)` | Résout l'ID de feedback_session correspondant si existant |

---

### 5. `app/Backend/app/routes/recommendations.py`

**9 nouveaux endpoints API :**

| Méthode | Chemin | Description |
|---|---|---|
| POST | `/api/sessions/{id}/media-recommendation` | Reco live basée sur state EEG courant |
| POST | `/api/sessions/{id}/media-feedback` | Feedback post-session → MAJ préférences |
| POST | `/api/eeg-reports/{id}/generate-media-recommendations` | Recos offline par époque |
| POST | `/api/finetuning/{id}/update-media-scoring` | Recalcul scores après fine-tuning |
| GET | `/api/patients/{id}/dashboard` | Tableau de bord unifié patient |
| POST | `/api/patients/{id}/playlists` | Créer playlist personnelle |
| GET | `/api/patients/{id}/playlists` | Lister playlists |
| GET | `/api/patients/{id}/offline-recommendations/{report_id}` | Recos offline d'un rapport |
| PATCH | `/api/patients/{id}/offline-recommendations/{rec_id}/feedback` | Like/dislike différé |

**Sécurité :** Vérification rôle patient/thérapeute/admin sur chaque endpoint. Un patient ne peut accéder qu'à ses propres données.

---

## Fichiers modifiés

### 6. `app/Backend/app/routes/therapist.py`

**Ajout :** `POST /api/therapist/patients/{patient_id}/therapeutic-playlist`

- Crée automatiquement une playlist thérapeutique basée sur l'objectif de la recommandation du thérapeute
- Filtre les médias par catégorie alignée avec l'objectif (concentration → focus, relaxation → calming, stress → calming)
- Priorise les médias déjà likés par le patient
- Alterne focus/relax dans l'ordre pour équilibre thérapeutique
- Marque `is_therapeutic = True` et `created_by_role = 'therapist'`

**Nouveaux imports ajoutés :**
- `TherapeuticPlaylistRequest, PlaylistWithMedia` depuis `schemas.media_reco`
- `get_profile_categories, score_media, get_liked_media_ids, PALIER_MAX_DURATION, CALMING_CATEGORIES` depuis `services.media_recommendation`
- `get_patient_eeg_profile` depuis `services.session_media_bridge`

### 7. `app/Backend/app/main.py`

- Import ajouté : `from app.routes.recommendations import router as recommendations_router`
- Router enregistré : `app.include_router(recommendations_router)`

---

## Points de jonction EEG ↔ Média implémentés

| Jonction | Implémentation |
|---|---|
| `session_events` ↔ `media_interactions` via session_id | `session_media_bridge.get_session_eeg_state()` lit les events pour piloter la reco. L'endpoint `/media-feedback` insère dans `media_interactions` avec le session_id |
| `eeg_reports.dominant_state` → `offline_recommendations.eeg_state` | `/eeg-reports/{id}/generate-media-recommendations` mappe concentration→focus, stress→stress |
| `eeg_profiles.profile_type` → `user_media_preferences.preferred_categorie` | `PROFILE_CATEGORIES` dans media_recommendation.py : A→apaisant, B→équilibré, C→stimulant |
| `finetuning_jobs` → `recommendations_media` (score ajusté) | `/finetuning/{id}/update-media-scoring` recalcule score × (1 + accuracy − 0.5) |
| `therapist_recommendations` → `playlists` thérapeutiques | `/therapist/patients/{id}/therapeutic-playlist` génère auto une playlist |

---

## Règles métier respectées

- [x] Durée max par palier : P1 = 3 min, P2 = 5 min, P3 = 10 min, P4 = illimité (filtre dur dans `score_media`)
- [x] Stress prolongé (3+ blocs > 0.7) → injection calming prioritaire (`check_consecutive_stress_blocks`)
- [x] Médias likés prioritaires (`liked_bonus = 1.3` dans scoring)
- [x] Recommandations expirent après 7 jours (`expires_at`, `purge_expired_recommendations`)
- [x] Score recalculé après fine-tuning (`recalculate_scores_after_finetuning`)
- [x] `interaction_type = complete` + `progress > 90%` → auto-update préférences
- [x] Playlist thérapeute → `is_therapeutic = True`, non modifiable par le patient (route thérapeute uniquement)

---

---

## Intégration Progression Calendaire (v2.4.0 — 2026-06-03)

### Analyse de l'existant (protocole)

Avant cette mise à jour, le protocole utilisait :

| Table/Fichier | Statut | Contenu |
|---|---|---|
| `protocol_sessions` | ✅ Existait | Séances opérationnelles (session_number, phase, palier, score, dates) |
| `protocol_blocs` | ✅ Existait | Blocs intra-séance |
| `eeg_profiles` | ✅ Existait | Profil cognitif + palier |
| `routes/protocol.py` | ✅ Existait | Status, calendar, start, complete, bilan |
| `ProtocolDashboard.jsx` | ✅ Existait | Grille 15 séances, pas de dates planifiées, pas de refresh |
| `SessionCalendar.jsx` | ✅ Existait | Composant calendrier, pas de dates planifiées |
| `user_protocol_progress` | ❌ Manquait | Suivi calendaire complet |

---

### Fichiers créés (v2.4.0)

#### 1. `app/Database/migrations/006_protocol_progress.sql`

**Nouvelle table `user_protocol_progress` :**
- Suivi complet par utilisateur (UNIQUE sur user_id)
- `planned_session_dates JSONB` — calendrier prévisionnel généré après S1 selon profil A/B/C
- `actual_session_dates JSONB` — historique réel des séances complétées
- `bilan_b1/b2/b3_completed` + `_date` + `_score` + `_decision` (continue/adjust_palier/repeat_phase)
- `early_stop_reason` / `early_stop_session` / `early_stop_date`
- `avg_session_score`, `success_rate_global`, `alpha_beta_trend`
- `followup_completed` + `followup_date` (S16 optionnelle)
- `status` : enrolled | in_progress | completed | early_stopped | suspended

**Vue `v_user_protocol_summary` :**
- Join `users` + `user_protocol_progress`
- Calcul `progress_percent` adaptatif (12/15/18 selon profil cognitif)
- `next_session` lisible (texte)

**Vue `v_protocol_media_engagement` :**
- Join avec `media_interactions`, `playlists`, `recommendations_media`, `offline_recommendations`
- Corrélation entre engagement média et progression protocole

#### 2. `app/Backend/app/services/protocol_progress_service.py`

**Constantes `PROTOCOL_STRUCTURE` :**
- Profil A : 12 séances, phases (1-3, 4-8, 9-12), intervalles 7j/4j/4j
- Profil B : 15 séances, phases (1-3, 4-10, 11-15), intervalles 5j/3j/3j
- Profil C : 18 séances, phases (1-5, 6-13, 14-18), intervalles 7j/4j/4j

**Fonctions clés :**

| Fonction | Description |
|---|---|
| `detect_cognitive_profile(alpha_beta_ratio, alpha_blocking_pct)` | A si ratio>1.5 ET blocage>30%, C si ratio<0.8 OU blocage<15%, sinon B |
| `generate_planned_calendar(profile, start_date)` | Génère la liste planifiée avec phases, paliers, bilans, S16 |
| `initialize_user_progress(user_id, profile_type, start_date, db)` | Crée user_protocol_progress à la calibration S1 |
| `update_progress_after_session(user_id, n, score, sr, palier, artifact_rate, db)` | Mise à jour auto après chaque séance |
| `determine_bilan_decision(avg_success_rate)` | ≥65% → continue, ≥40% → adjust_palier, sinon repeat_phase |
| `merge_calendar_with_progress(sessions, user_id, db)` | Enrichit le calendrier opérationnel avec les dates planifiées |
| `get_therapist_progress_dashboard(therapist_id, db)` | Progression de tous les patients du thérapeute |

---

### Fichiers modifiés (v2.4.0)

#### 3. `app/Backend/app/routes/protocol.py`

**Hooks ajoutés :**
- `complete_calibration()` → appelle `initialize_user_progress()` en `asyncio.create_task` (non bloquant)
- `complete_session()` → appelle `update_progress_after_session()` en `asyncio.create_task` (non bloquant)
- `get_protocol_calendar()` → appelle `merge_calendar_with_progress()` pour enrichir les dates planifiées

**Nouveaux endpoints :**

| Méthode | Chemin | Description |
|---|---|---|
| GET | `/api/protocol/progress` | Progression complète de l'utilisateur (planned_session_dates, bilans, early_stop, progress_percent) |
| GET | `/api/protocol/progress/therapist` | Dashboard thérapeute : progression de tous les patients |
| POST | `/api/protocol/early-stop` | Arrêt anticipé manuel (reason, notes) |
| POST | `/api/protocol/followup-schedule` | Planifie la séance de suivi S16 |

#### 4. `app/Frontend/src/utils/api.js`

Ajout de l'objet `protocol` exporté avec tous les appels API du protocole :
`status`, `calendar`, `progress`, `therapistProgress`, `startSession`, `sessionConfig`, `blocEnd`, `completeSession`, `bilan`, `profile`, `calibrationComplete`, `updatePalier`, `dailyThreshold`, `earlyStop`, `scheduleFollowup`

#### 5. `app/Frontend/src/pages/ProtocolDashboard.jsx`

**Auto-refresh :**
- `fetchData` wrappé dans `useCallback` avec déduplication (3s minimum entre fetchs)
- `document.addEventListener('visibilitychange', ...)` → refresh silencieux quand la page redevient visible (retour depuis une séance)
- Bouton `RefreshCw` dans le header pour refresh manuel

**Dates planifiées :**
- Affichage du profil cognitif (A/B/C) dans le sous-titre
- Nombre de séances adaptatif (12/15/18 selon profil)
- Date planifiée affichée dans la carte "Prochaine séance" (depuis `progress.planned_session_dates`)

#### 6. `app/Frontend/src/components/SessionCalendar.jsx`

**Auto-refresh :**
- Prop `autoRefresh` (boolean) pour activer/désactiver le refresh automatique
- `fetchData` en `useCallback`, refresh silencieux sur `visibilitychange`
- Bouton refresh dans le header du composant
- Renommage de la variable locale `progress` → `calProgress` pour éviter le conflit avec l'état `progress` (user_protocol_progress)

**Dates planifiées :**
- `plannedMap` : dictionnaire `session_num → planned_date` depuis `user_protocol_progress`
- `SessionCard` reçoit `plannedDate` prop et l'affiche si `scheduled_date` absent
- "Prochaine séance" affiche la date planifiée en bleu si disponible
- Total séances adaptatif (12/15/18 selon profil)

---

## Ordre d'exécution Supabase

Exécuter dans cet ordre dans l'éditeur SQL Supabase :

```
1. schema_v3.sql                    (si base vierge)
2. migrations/004_protocol_15_sessions.sql
3. migrations/add_feedback_sessions.sql
4. migrations/add_medias_table.sql
5. migrations/update_sessions_calendar.sql
6. migrations/005_media_recommendations.sql  ← NOUVEAU
```

Le fichier `005_media_recommendations.sql` est idempotent (safe à relancer).

```
7. migrations/006_protocol_progress.sql     ← NOUVEAU
```

Le fichier `006_protocol_progress.sql` est idempotent (safe à relancer).

---

## Schéma consolidé v3.5 — Fichier unique idempotent (2026-06-03)

---

## Intégration complète v3.6 — Implémentation app ↔ supabase_complete (2026-06-04)

### Contexte

Le fichier `supabase_complete.sql` consolide les 23 tables en un script idempotent unique. Cette mise à jour aligne l'ensemble de l'application (backend, modèles ORM, API frontend, pages) avec ce schéma final.

---

### Bug corrigé

#### `app/Frontend/src/pages/ProtocolDashboard.jsx`

**Problème :** `const progress = Math.round(...)` à la ligne 115 écrasait le state React `const [progress, setProgress] = useState(null)` déclaré ligne 62. Résultat : `progress?.cognitive_profile` retournait `undefined`, le badge profil cognitif ne s'affichait jamais, et les dates planifiées étaient invisibles.

**Correction :**
- Renommage `progress` → `progressPct` pour la valeur calculée
- Ajout de `totalTarget` adaptatif (12/15/18 selon `progress.cognitive_profile`)
- Référence `completed/15` → `completed/totalTarget` dans la carte stats et le test de complétion

---

### Fichiers modifiés

#### `app/Frontend/src/utils/api.js`

**Ajout de l'objet `recommendations` :**

| Méthode | Endpoint | Description |
|---|---|---|
| `sessionMediaReco(sessionId, blockNumber, forceCalming)` | POST `/sessions/{id}/media-recommendation` | Reco live EEG |
| `sessionMediaFeedback(sessionId, items)` | POST `/sessions/{id}/media-feedback` | Feedback post-session |
| `generateOfflineReco(reportId)` | POST `/eeg-reports/{id}/generate-media-recommendations` | Recos offline par époque |
| `updateScoringAfterFinetune(jobId)` | POST `/finetuning/{id}/update-media-scoring` | Recalcul scores post fine-tuning |
| `patientDashboard(patientId)` | GET `/patients/{id}/dashboard` | Dashboard unifié patient |
| `createPlaylist(patientId, name, description)` | POST `/patients/{id}/playlists` | Créer playlist |
| `listPlaylists(patientId)` | GET `/patients/{id}/playlists` | Lister playlists |
| `offlineRecs(patientId, reportId)` | GET `/patients/{id}/offline-recommendations/{report_id}` | Recos offline d'un rapport |
| `offlineRecFeedback(patientId, recId, liked)` | PATCH `/patients/{id}/offline-recommendations/{rec_id}/feedback` | Like/dislike différé |

**Ajout de l'objet `therapistExtended` :**
- `createTherapeuticPlaylist(patientId, name, description, recommendedObjective)` → POST `/therapist/patients/{id}/therapeutic-playlist`

#### `app/Backend/app/models/user.py`

**18 modèles SQLAlchemy ajoutés** (pour SQLite dev mode — production utilise le client Supabase direct) :

| Modèle | Table |
|---|---|
| `EEGReport` | `eeg_reports` |
| `TrainingEpoch` | `training_epochs` |
| `FinetuningJob` | `finetuning_jobs` |
| `TherapistNote` | `therapist_notes` |
| `TherapistRecommendation` | `therapist_recommendations` |
| `SystemSetting` | `system_settings` |
| `Media` | `medias` (avec category, tempo_bpm, brightness, saturation, contrast, metadata) |
| `FeedbackSession` | `feedback_sessions` |
| `FeedbackSessionEvent` | `feedback_session_events` |
| `MediaInteraction` | `media_interactions` |
| `ProtocolSession` | `protocol_sessions` |
| `ProtocolBloc` | `protocol_blocs` |
| `UserMediaPreference` | `user_media_preferences` |
| `RecommendationMedia` | `recommendations_media` |
| `Playlist` | `playlists` |
| `PlaylistMedia` | `playlist_media` |
| `OfflineRecommendation` | `offline_recommendations` |
| `UserProtocolProgress` | `user_protocol_progress` |

Import ajouté : `Date`, `JSON` (avec fallback `Text` pour SQLite).

#### `app/Frontend/src/pages/DashboardPage.jsx`

- Ajout du widget "Médias & Recommandations" (carte cliquable → `/media-dashboard`)
- Import `Music` depuis lucide-react

#### `app/Frontend/src/App.jsx`

- Import `PatientMediaDashboard`
- Nouvelle route : `<Route path="/media-dashboard" element={<PatientMediaDashboard />} />`

---

### Fichiers créés

#### `app/Frontend/src/pages/PatientMediaDashboard.jsx`

Nouvelle page accessible à `/media-dashboard` depuis le dashboard patient.

**Onglets :**

| Onglet | Contenu |
|---|---|
| Recommandations | Liste des `recommendations_media` non cliquées (score décroissant), état vide avec CTA vers session EEG |
| Playlists | Grid des `playlists` (personnelles + thérapeutiques), bouton créer, modal création |
| Analyses EEG | Sélection d'un rapport EEG → affichage des `offline_recommendations` par époque avec like/dislike différé |

**Composants internes :**
- `StatBadge` — KPI en en-tête
- `RecommendationCard` — une recommandation avec score
- `PlaylistCard` — playlist avec badge thérapeutique
- `OfflineRecCard` — époque EEG + média recommandé + boutons like/dislike
- `CreatePlaylistModal` — modal création playlist (nom + description)
- `OfflineRecsSection` — sélecteur rapport + liste recos

---

### Couverture finale des 23 tables

| # | Table | Backend | Frontend API | Frontend UI |
|---|---|---|---|---|
| 1 | `users` | auth.py, admin.py | auth.*, admin.* | Login, Register, Admin |
| 2 | `eeg_profiles` | Profile.py, protocol.py | profile.*, protocol.* | Profile, ProtocolDashboard |
| 3 | `sessions` | sessions.py | sessions.* | History, DashboardPage |
| 4 | `session_events` | sessions.py, eeg.py | — (WS) | EEGLive |
| 5 | `eeg_reports` | eeg.py | eeg.myReports, eeg.sendReport | EEGFile, DashboardPage |
| 6 | `training_epochs` | eeg.py (auto) | — | — |
| 7 | `finetuning_jobs` | eeg.py | eeg.finetuningStatus | Profile |
| 8 | `audit_logs` | admin.py | admin.auditLogs | AdminPanel |
| 9 | `therapist_notes` | therapist.py | therapist.getNotes | TherapistPatientDetail |
| 10 | `therapist_recommendations` | therapist.py | therapist.getRecommendation | TherapistPatientDetail |
| 11 | `system_settings` | admin.py | admin.getSettings | AdminPanel |
| 12 | `medias` | media.py, feedback.py | media.list | FeedbackSession |
| 13 | `feedback_sessions` | feedback.py | feedback.startSession | FeedbackSession |
| 14 | `feedback_session_events` | feedback.py | — (WS) | FeedbackSession |
| 15 | `media_interactions` | recommendations.py | recommendations.sessionMediaFeedback | PatientMediaDashboard |
| 16 | `protocol_sessions` | protocol.py | protocol.* | ProtocolDashboard, ProtocolSession |
| 17 | `protocol_blocs` | protocol.py | protocol.blocEnd | ProtocolSession |
| 18 | `user_media_preferences` | recommendations.py (auto) | — | — |
| 19 | `recommendations_media` | recommendations.py | recommendations.patientDashboard | PatientMediaDashboard |
| 20 | `playlists` | recommendations.py, therapist.py | recommendations.listPlaylists | PatientMediaDashboard |
| 21 | `playlist_media` | recommendations.py, therapist.py | — | PatientMediaDashboard |
| 22 | `offline_recommendations` | recommendations.py | recommendations.offlineRecs | PatientMediaDashboard |
| 23 | `user_protocol_progress` | protocol.py, protocol_progress_service.py | protocol.progress | ProtocolDashboard, SessionCalendar |

### Contexte

Les 6+ fichiers de migration distincts devenaient difficiles à maintenir et à rejouer sur une base fraîche. Un fichier unique consolidé remplace l'ancienne séquence ordonnée.

### Fichier créé

#### `app/Database/supabase_complete.sql`

Schéma complet NeuroCap en un seul fichier SQL idempotent, couvrant les 23 tables dans l'ordre :

| # | Table | Notes |
|---|---|---|
| 1 | `users` | |
| 2 | `eeg_profiles` | |
| 3 | `sessions` | |
| 4 | `session_events` | |
| 5 | `eeg_reports` | |
| 6 | `training_epochs` | |
| 7 | `finetuning_jobs` | |
| 8 | `audit_logs` | |
| 9 | `therapist_notes` | |
| 10 | `therapist_recommendations` | |
| 11 | `system_settings` | données seed incluses |
| 12 | `medias` | |
| 13 | `feedback_sessions` | |
| 14 | `feedback_session_events` | |
| 15 | `media_interactions` | |
| 16 | `protocol_sessions` | |
| 17 | `protocol_blocs` | |
| 18 | `user_media_preferences` | |
| 19 | `recommendations_media` | |
| 20 | `playlists` | |
| 21 | `playlist_media` | |
| 22 | `offline_recommendations` | correctif UUID décrit ci-dessous |
| 23 | `user_protocol_progress` | |

**Pattern uniforme par table :** `CREATE TABLE IF NOT EXISTS` → `ALTER TABLE ADD COLUMN IF NOT EXISTS` (toutes colonnes) → `CREATE INDEX IF NOT EXISTS`

**RLS :** désactivé explicitement sur les 23 tables (`DISABLE ROW LEVEL SECURITY`).

**Vues créées en fin de fichier** (après garantie de toutes les tables) :
- `v_user_protocol_summary` — progression protocole par utilisateur avec `progress_percent` adaptatif (12/15/18 séances selon profil A/B/C)
- `v_protocol_media_engagement` — corrélation engagement média ↔ avancement protocole

---

### Correctif `offline_recommendations.report_id` (UUID vs TEXT)

**Problème :** `eeg_reports.id` est de type `TEXT`. La colonne `offline_recommendations.report_id` était aussi `TEXT`, mais PostgreSQL refusait la création de la clé étrangère lors de certaines reconstructions à cause d'une incompatibilité de typage interne.

**Solution retenue :**
1. `offline_recommendations.report_id` est déclaré `UUID` dans le `CREATE TABLE`.
2. Un bloc `DO $$ BEGIN ALTER COLUMN report_id TYPE UUID USING report_id::UUID ... END $$` convertit la colonne si elle existait déjà en `TEXT`.
3. La FK `fk_offline_rec_report → eeg_reports(id) ON DELETE SET NULL` est recrée proprement après suppression de l'ancienne contrainte.

> `eeg_reports.id` reste `TEXT` (pour compatibilité `training_epochs.report_id TEXT`). La FK fonctionne car PostgreSQL accepte `UUID → TEXT` lorsque le texte contient un UUID valide.

---

### Ordre de déploiement simplifié

**Nouvelle base vierge :** coller uniquement `supabase_complete.sql` dans l'éditeur SQL Supabase.

**Base existante :** le fichier est idempotent — safe à rejouer sans perte de données ni erreur.
