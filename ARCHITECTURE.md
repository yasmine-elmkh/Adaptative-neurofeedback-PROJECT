# NeuroCap — Fonctionnement du Système

> Description fonctionnelle complète : flux utilisateurs, interfaces, rôles et processus.  
> Version système : **2.2.0**

---

## Table des matières

1. [Les trois rôles du système](#1-les-trois-rôles-du-système)
2. [Flux d'inscription et vérification email](#2-flux-dinscription-et-vérification-email)
3. [Flux de connexion (login)](#3-flux-de-connexion-login)
4. [Interface Patient — parcours complet](#4-interface-patient--parcours-complet)
5. [Interface Thérapeute](#5-interface-thérapeute)
6. [Interface Administrateur](#6-interface-administrateur)
7. [Pipeline EEG en session — ce qui se passe techniquement](#7-pipeline-eeg-en-session--ce-qui-se-passe-techniquement)
8. [Moteur de feedback adaptatif](#8-moteur-de-feedback-adaptatif)
9. [Apprentissage automatique nocturne](#9-apprentissage-automatique-nocturne)
10. [Sécurité transversale](#10-sécurité-transversale)
11. [Architecture technique — Backend & Frontend](#11-architecture-technique--backend--frontend)

---

## 1. Les trois rôles du système

```
┌─────────────────────────────────────────────────────────────┐
│                     RÔLES NEUROCAP                          │
│                                                             │
│   PATIENT ──────────────────────────────────────────────►  │
│   • Fait ses sessions EEG                                   │
│   • Voit son historique et ses progrès                      │
│   • Reçoit du feedback en temps réel                        │
│                                                             │
│   THÉRAPEUTE ───────────────────────────────────────────►  │
│   • Suit ses patients assignés                              │
│   • Lit les profils EEG et les rapports de sessions         │
│   • Écrit des notes cliniques                               │
│   • Ajuste le palier de difficulté du patient               │
│   • Exporte les données CSV                                 │
│                                                             │
│   ADMIN ────────────────────────────────────────────────►  │
│   • Gère tous les utilisateurs (créer, modifier, supprimer) │
│   • Assigne les patients aux thérapeutes                    │
│   • Voit les statistiques globales (6 KPIs)                 │
│   • Envoie des rappels email aux inactifs                   │
│   • Consulte le journal d'audit complet                     │
│   • Modifie les paramètres système                          │
└─────────────────────────────────────────────────────────────┘
```

Un admin peut accéder à toutes les vues thérapeute (bypass de la vérification d'assignation).

---

## 2. Flux d'inscription et vérification email

L'inscription est en **deux étapes obligatoires** — on ne peut pas créer un compte sans avoir validé son email.

```
Étape 1 — Demande de code
─────────────────────────
Utilisateur saisit son email
         │
         ▼
POST /api/auth/send-code
         │
         ├─► Vérifie que l'email n'existe pas déjà en base
         │       si déjà pris → erreur 409 "Compte déjà existant"
         │
         ├─► Génère un code à 8 chiffres aléatoire (TTL : 10 minutes)
         │
         └─► Envoie l'email via Resend (service d'envoi transactionnel)
                 si l'envoi échoue → erreur 503, le code est supprimé


Étape 2 — Inscription avec le code
────────────────────────────────────
Utilisateur remplit : prénom, nom, email, mot de passe, code reçu
         │
         ▼
POST /api/auth/register
         │
         ├─► Vérifie que le code existe et n'a pas expiré
         │       expiré (> 10 min) → erreur 400 "Code expiré"
         │       incorrect → erreur 400 "Code incorrect"
         │
         ├─► Vérifie la force du mot de passe (côté serveur) :
         │       ≥ 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre, 1 spécial
         │
         ├─► Génère le username automatiquement : prenom.nom
         │       si déjà pris → ajoute un suffixe numérique (ex: alice.martin2)
         │
         ├─► Hash du mot de passe (bcrypt)
         │
         ├─► Création en base Supabase avec rôle "user" par défaut
         │
         └─► Retourne directement les tokens (auto-login)
                 access_token  (durée courte)
                 refresh_token (durée longue)
```

**Note :** En environnement sans SMTP configuré (développement), le code est retourné dans la réponse (`_dev_code`) pour faciliter les tests.

---

## 3. Flux de connexion (login)

```
POST /api/auth/login
         │
         ├─► Protection anti-brute-force par IP
         │       trop de tentatives → erreur 429 bloquée par le middleware
         │
         ├─► Recherche l'utilisateur par email
         │       email introuvable → erreur 404 "Aucun compte trouvé"
         │       (message distinct de l'erreur mot de passe — pour la UX)
         │
         ├─► Vérifie le mot de passe avec bcrypt
         │       incorrect → erreur 401 "Mot de passe incorrect"
         │                  + compteur brute-force incrémenté
         │
         ├─► Vérifie que le compte est actif
         │       is_active = false → erreur 403 "Compte désactivé"
         │
         ├─► Réinitialise le compteur brute-force si succès
         │
         ├─► Écrit dans audit_logs : action="LOGIN", IP de l'utilisateur
         │
         └─► Retourne :
                 access_token  → valide X minutes
                 refresh_token → valide plusieurs jours

Refresh automatique du token
─────────────────────────────
POST /api/auth/refresh
   → vérifie le refresh_token (type="refresh", user actif)
   → retourne un nouveau couple access_token + refresh_token
```

**Après connexion**, le frontend lit le rôle de l'utilisateur via `GET /api/auth/me` et redirige vers la bonne interface :

| Rôle | Redirection |
|---|---|
| `patient` / `user` | Dashboard patient |
| `therapist` | Dashboard thérapeute |
| `admin` | Dashboard admin |

---

## 4. Interface Patient — parcours complet

### 4.1 Dashboard

La page d'accueil patient affiche :
- Résumé de la dernière session (score, durée, état dominant)
- Calendrier des 15 séances du protocole avec les créneaux passés et futurs
- Score moyen et progression sur les dernières sessions
- Raccourcis vers : démarrer une session, voir l'historique, consulter le guide électrodes

### 4.2 Protocole de 15 séances et calendrier

Les 15 séances sont organisées en 3 phases avec des délais minimum entre séances :

| Phase | Séances | Délai minimum |
|---|---|---|
| Phase 1 — initiation | 1 à 3 | 5 jours entre séances |
| Phase 2 — apprentissage | 4 à 10 | 2 jours entre séances |
| Phase 3 — maîtrise | 11 à 15 | 2 jours entre séances |

Les séances 5, 10 et 15 sont des **bilans obligatoires** (B1, B2, B3) avec rapport étendu.

### 4.3 Guide de placement des électrodes

Page `ElectrodeGuide` : instructions illustrées pour poser correctement les électrodes sèches Ag/AgCl sur Fp2 (frontal droit) et M2 (mastoïde droite). Accessible avant chaque session.

### 4.4 Démarrer une session EEG en direct

```
Patient clique "Nouvelle session"
         │
         ▼
Page EEGLive
         │
         ├─► Connexion WebSocket ws://backend/ws/eeg?token=<jwt>
         │
         ├─► Message "init" reçu :
         │       - ESP32 connecté ou non
         │       - Baseline calibrée ou non
         │       - État des électrodes
         │
         ├─► Si ESP32 non connecté → affiche guide WiFi
         │       L'ESP32 crée un hotspot → patient connecte son PC au hotspot
         │       → WifiManager configure l'ESP32 sur le réseau local → TCP établi
         │
         ├─► Calibration (60 s minimum)
         │       Patient reste immobile, yeux ouverts
         │       Barre de progression (cal_progress : 0→100%)
         │       → bouton "Valider la calibration" → commande FINALISE_BASELINE
         │
         └─► Session active :
                 Oscilloscope EEG temps réel (~62 Hz)
                 Barres de puissance par bande (delta/theta/alpha/beta/gamma)
                 Jauge concentration + stress
                 Topographie 2D du scalp
                 Fenêtre 3D cerveau animée
                 Indicateur qualité signal (CQE)
```

### 4.5 Session de feedback neurofeedback

La page `FeedbackSession` orchestre **6 phases séquentielles** et deux WebSockets simultanés.

```
Entrée depuis EEGLive (mlPrediction passé via location.state)
         │
         ▼
Phase 1 — PRE_SESSION (3 s auto)
         Affiche l'état EEG détecté, spinner de préparation
         POST /api/feedback/sessions → sessionId (palier, phase 1/2/3, objectif)
         │
         ▼
Phase 2 — BASELINE_CLOSED (2 min yeux fermés)
         Guide respiratoire affiché (BreathingGuide)
         Bouton "Passer la baseline" pour accélérer en développement
         │
         ▼
Phase 3 — FEEDBACK_BLOCK (× 6 blocs de 3 min = 18 min)
         │
         ├─► Deux WebSockets ouverts en parallèle :
         │       WS EEG  → eegFrame (62 Hz), epochFrame (4 s), mlPrediction
         │       WS FB   → /feedback/ws/{sessionId} → action "play" / "session_ended"
         │
         ├─► Sélection du média (Thompson sampling côté backend) :
         │       POST /api/feedback/recommend {session_id, eeg_state}
         │       Backend → _pick_media → broadcast WS action="play"
         │       Frontend → currentMedia mis à jour → MediaZone re-render
         │
         ├─► Composants affichés simultanément :
         │       MiniEEGOscilloscope  — signal brut + état ML (colonne gauche)
         │       Features EEG         — alpha/beta/theta/TBR/EI en temps réel
         │       BreathingGuide       — si état stress
         │       FocusPoint           — si état concentration
         │       MediaZone            — contenu actif (image | vidéo | jeu | audio)
         │       UserFeedbackBar      — liked / SAM 1-5 / skip
         │       SessionBlockTimer    — compte à rebours bloc + progression globale
         │
         ├─► Accumulation epochs pour delta α/β :
         │       epochAlphaRef / epochBetaRef accumulés à chaque epochFrame
         │       calcul : delta = mean(seconde_moitié) − mean(première_moitié)
         │       efficace si delta_alpha > 0.05 ET delta_beta < −0.05
         │
         ├─► Retour utilisateur :
         │       POST /api/feedback/submit {liked, sam_score, delta_alpha, delta_beta}
         │       POST /api/feedback/skip   → pénalité beta += 1
         │       → requestNextMedia() → POST /api/feedback/recommend
         │
         └─► Fin de bloc → handleBlockEnd()
                 blocs restants → Phase 4 (pause)
                 dernier bloc   → Phase 5 (repos guidé)

Phase 4 — INTER_BLOCK_PAUSE (20 s)
         Overlay opaque, compte à rebours, message de détente
         → décompte écoulé → startBlock(idx+1) → retour Phase 3

Phase 5 — GUIDED_REST (3 min)
         Guide respiratoire, bouton "Terminer"
         → handleEndSession() → POST /api/feedback/end
         │
         ▼
Phase 6 — POST_SESSION
         POST /api/feedback/end reçu
         Calcul score : (items_efficaces / items_played) × 70 + 30 si succès global
         Rapport Claude AI généré async (generate_session_report)
         → broadcast WS action="session_ended" {report, metrics}
         → FeedbackReport affiché (texte IA + métriques chiffrés)
```

**Score final :** `score = int(eff_rate × 70 + (30 si delta_alpha_global > 0.05 ET delta_beta_global < −0.05))`

### 4.6 Types de jeux cognitifs disponibles

| Jeu | Objectif cognitif |
|---|---|
| Mémoire | Mémoriser des paires de cartes — mémoire de travail |
| Puzzle | Reconstituer une image — visuospatial |
| Sudoku | Compléter la grille — raisonnement logique |
| Calcul mental | Résoudre des opérations — attention et exécutif |
| Énigme | Résoudre des devinettes — flexibilité cognitive |

### 4.7 Analyse de fichier EEG (mode hors ligne)

```
Page EEGFile
         │
         ├─► Upload d'un fichier CSV (enregistrement précédent)
         │
         ├─► POST /api/eeg/analyze-file
         │
         ├─► Traitement identique au mode temps réel :
         │       Filtre → Détection artefacts → Époques → Features → Classifieur
         │
         └─► Rapport offline :
                 Nombre d'époques totales / acceptées / rejetées
                 État dominant (concentration | stress | uncertain)
                 Pourcentages par état
                 Confiance moyenne du classifieur
                 Chronologie des états sur la session
```

### 4.8 Historique et profil

- `History` : liste de toutes les sessions avec score, durée, date, objectif
- `Profile` : informations personnelles, changement de mot de passe
- Export CSV de n'importe quelle session (données par époque)

### 4.9 Assistant cognitif RAG

Page `Assistant` : chatbot local qui répond aux questions sur le neurofeedback, l'EEG, et les résultats du patient. Les réponses sont ancrées sur un corpus EEG/neurofeedback stocké localement — aucune donnée n'est envoyée vers un service cloud.

---

## 5. Interface Thérapeute

Le thérapeute ne voit que les patients qui lui sont **explicitement assignés** par l'admin.

### 5.1 Dashboard thérapeute

```
Page TherapistDashboard
         │
         ├─► GET /api/therapist/patients
         │       Liste enrichie de tous ses patients :
         │       - Nom, email, statut actif/inactif
         │       - Nombre de sessions complétées
         │       - Score moyen
         │       - Date de la dernière session
         │       - Profil EEG : type A/B/C, palier actuel P1-P4
         │       - Progression sur les 5 dernières sessions (sparkline)
         │
         └─► Filtres : par statut, par palier, par inactivité
```

### 5.2 Fiche détaillée d'un patient

```
Page TherapistPatientDetail
         │
         ├─► Informations générales du patient
         │
         ├─► Profil EEG (lecture seule) :
         │       Type cognitif A / B / C
         │       IAPF (Individual Alpha Peak Frequency)
         │       Baselines : TBR, alpha, beta, theta
         │       Palier actuel (P1 → P4)
         │       Date de calibration
         │       Précision du modèle personnalisé (20 dernières sessions)
         │
         ├─► Historique des sessions :
         │       GET /api/therapist/patients/{id}/sessions
         │       Tableau chronologique : date, durée, score, objectif
         │       Clic → rapport détaillé de la session
         │
         ├─► Notes cliniques :
         │       GET  /api/therapist/patients/{id}/notes → liste des notes
         │       POST /api/therapist/patients/{id}/notes → ajouter une note
         │       Champ libre daté et signé (thérapeute)
         │
         ├─► Recommandation active :
         │       GET  /api/therapist/patients/{id}/recommendation
         │       POST /api/therapist/patients/{id}/recommendation → créer/mettre à jour
         │       Texte libre visible par le patient dans son dashboard
         │
         ├─► Ajustement du palier de difficulté :
         │       PUT /api/therapist/patients/{id}/palier
         │       Paliers : P1 (initiation) → P2 → P3 → P4 (autonomie)
         │       Action tracée en audit_logs
         │
         ├─► Activer / désactiver le compte patient :
         │       PATCH /api/therapist/patients/{id}/active
         │
         └─► Export CSV :
                 GET /api/therapist/patients/{id}/export
                 Fichier CSV de toutes les sessions du patient
                 Colonnes : date, durée, score, concentration, stress, TBR, EI, n_epochs
```

---

## 6. Interface Administrateur

### 6.1 Dashboard administrateur — 6 KPIs globaux

```
GET /api/admin/stats
─────────────────────
Retourne en temps réel :
  total_users           — nombre total d'utilisateurs actifs
  active_users          — comptes non désactivés
  total_therapists      — nombre de thérapeutes
  active_patients       — patients avec au moins 1 session
  total_sessions        — toutes sessions confondues
  completed_sessions    — sessions terminées (statut "completed")
  sessions_this_month   — sessions des 30 derniers jours
  avg_session_score     — score moyen global
  avg_session_duration  — durée moyenne (secondes)
  engagement_rate       — % d'utilisateurs avec ≥ 3 sessions
```

### 6.2 Gestion des utilisateurs

```
Liste des utilisateurs
───────────────────────
GET /api/admin/users?role_filter=patient&limit=50&offset=0

Pour chaque utilisateur :
  - Informations de profil (nom, email, username, rôle)
  - Statut actif / inactif
  - Thérapeute assigné
  - Statistiques de sessions : nombre, score moyen, date dernière session

Filtres disponibles :
  - Par rôle : patient | therapist | admin | user
  - Pagination : limit + offset

Créer un utilisateur (sans vérification email)
────────────────────────────────────────────────
POST /api/admin/users
  - Prénom, nom, email, mot de passe, rôle, thérapeute_id (optionnel)
  - Username généré automatiquement (prenom.nom avec suffixe si doublon)
  - Action tracée en audit_logs : USER_CREATED

Modifier un utilisateur
────────────────────────
PUT /api/admin/users/{id}
  - Peut changer : rôle, statut actif, thérapeute assigné
  - Action tracée : ROLE_CHANGE (ancienRôle → nouveauRôle)

Supprimer un utilisateur
─────────────────────────
DELETE /api/admin/users/{id}?hard=false
  - Soft delete (par défaut) : deleted_at = now(), is_active = false
    → L'utilisateur ne peut plus se connecter, données conservées
  - Hard delete (?hard=true) : suppression définitive de la base
  - Protection : impossible de se supprimer soi-même
  - Action tracée : USER_DELETED (SOFT ou HARD)
```

### 6.3 Assignation patient ↔ thérapeute

```
POST /api/admin/assign-patient
  corps : { patient_id, therapist_id }

  ├─► Vérifie que le patient existe
  ├─► Vérifie que le thérapeute a bien le rôle "therapist" ou "admin"
  ├─► Met à jour users.therapist_id
  └─► therapist_id = null → désassigne le patient (plus de thérapeute)

  Action tracée : PATIENT_ASSIGNED
```

### 6.4 Rappels email aux patients inactifs

```
Rappel individuel
──────────────────
POST /api/admin/send-reminder
  { user_id, message }
  → Envoie un email personnalisé au patient
  → Mentionne le nombre de jours d'inactivité
  → Action tracée : EMAIL_REMINDER_SENT

Rappel en masse
────────────────
POST /api/admin/send-reminder-all
  { days_inactive: 7, message: "..." }
  → Cible tous les patients actifs inactifs depuis N jours
  → Retourne : { sent, failed, skipped, errors }
  → Patients actifs récemment → skipped (pas d'email envoyé)
  → Action tracée : EMAIL_REMINDER_ALL
```

### 6.5 Journal d'audit

```
GET /api/admin/audit-logs
  Filtres disponibles : action, user_id, date_from, date_to

Actions enregistrées automatiquement :
  LOGIN              — toute connexion réussie (+ IP)
  USER_CREATED       — création par l'admin
  ROLE_CHANGE        — changement de rôle ou statut
  USER_DELETED       — suppression soft ou hard
  PATIENT_ASSIGNED   — assignation/désassignation
  EMAIL_REMINDER_SENT / EMAIL_REMINDER_ALL
  SETTINGS_CHANGED   — modification d'un paramètre système
  PALIER_ADJUSTED    — changement de palier par un thérapeute
```

### 6.6 Paramètres système

```
GET /api/admin/settings       → tous les paramètres clé/valeur
PUT /api/admin/settings/{key} → modifier un paramètre
  Exemples : session_duration_min, max_epochs_per_session, finetune_threshold
```

---

## 7. Pipeline EEG en session — ce qui se passe techniquement

```
ESP32 (Fp2/M2, 250 Hz)
         │
         │ TCP port 9000
         │ Chaque paquet : timestamp_us, raw_uV, lo_plus, lo_minus, batt_V, pkt_id
         ▼
TCPReceiver (thread dédié)
         │
         │ → file d'attente (max 5000 échantillons)
         ▼
Boucle DSP asyncio (10 échantillons / itération)
         │
         ├─ 1. FILTRAGE (FilterBank)
         │       Soustraction DC → Notch 50 Hz → Notch 100 Hz
         │       → Butterworth BP [1–45 Hz] ordre 4
         │       → Débruitage ondelette (PyWavelets)
         │
         ├─ 2. STATUT ÉLECTRODES (ElectrodeMonitor)
         │       Lecture bits LO+ / LO− de l'AD8232
         │       + validation variance signal (fallback logiciel)
         │       → electrode_ok (booléen)
         │
         ├─ 3. DIFFUSION WebSocket (1 sample / 4 → 62 Hz côté browser)
         │       payload : uv, filtered, bands, state, electrode_ok, batt_V
         │
         ├─ 4. ACCUMULATION en époque (fenêtre 4 s, pas 0,5 s)
         │       Si époque complète :
         │         └─ Détection artefacts :
         │               EOG : amplitude > seuil → marqué (non rejeté)
         │               EMG : puissance 35-45 Hz / totale > seuil → flag
         │               Rejet dur : amplitude > 200 µV ou signal plat
         │
         ├─ 5. EXTRACTION DE FEATURES (63 dimensions)
         │       PSD Welch → puissances par bande (delta/theta/alpha/beta/gamma)
         │       Ratios cognitifs : TBR, EI, ABR
         │       Temporel : RMS, Hjorth (activité, mobilité, complexité)
         │       Complexité : Higuchi FD (kmax=8)
         │       Entropie spectrale normalisée
         │
         ├─ 6. CLASSIFICATION ML
         │       Modèle personnalisé du patient (si fine-tuned) ou modèle global
         │       Résultat : concentration | stress | uncertain + confiance (0-1)
         │
         └─ 7. DIFFUSION époque (type="epoch")
                 Toutes les features + état + confiance envoyés au frontend
                 → FeedbackSession met à jour le feedback en temps réel
```

---

## 8. Moteur de feedback adaptatif

Le moteur opère sur **deux axes** : sélection du média (Thompson sampling) et ajustement du seuil (paliers inter-sessions).

### 8.1 Sélection du média — Thompson Sampling

```
Chaque appel POST /api/feedback/recommend :
────────────────────────────────────────────

  Table medias (Supabase)
    chaque média possède : item_weights_alpha, item_weights_beta (init: 1.0 / 1.0)

  ┌─ Filtrage par eeg_target_state
  │     eeg_state "focus"   → médias ciblant "focus" ou "all"
  │     eeg_state "stress"  → médias ciblant "stress" ou "all"
  │     eeg_state "neutral" → tous les médias
  │
  ├─ Filtrage par media_type si forcé (image | video | game | audio)
  │
  ├─ Thompson Sampling
  │     Pour chaque média retenu :
  │       score = random.betavariate(alpha, beta)
  │     Sélectionne max(score) → diversité naturelle, convergence vers les efficaces
  │
  └─ Mise à jour des poids après retour utilisateur :
       liked=true OU delta_alpha>0.05 ET delta_beta<−0.05 → alpha += 1  (succès)
       skip / liked=false / sam_score ≤ 2               → beta  += 1  (échec)
       sam_score ≥ 4                                     → alpha += 1  (bonus)
       skip via POST /api/feedback/skip                  → beta  += 1  (pénalité)
```

### 8.2 Seuil adaptatif intra-session (θ)

```
Lissage EWMA à chaque époque (adaptative_engine.py) :
  concentration_lissée = 0.3 × nouvelle + 0.7 × précédente

Fin d'un bloc (3 min = ~45 époques) :
  taux_succès > 60%  → θ ← θ + 0.5   (monte la difficulté)
  taux_succès 40-60% → θ inchangé    (zone optimale)
  taux_succès < 40%  → θ ← θ - 0.5  (réduit la difficulté)
  θ contraint dans [0.2, 0.9]
```

### 8.3 Paliers inter-sessions

| Palier | Plage θ | Profil |
|---|---|---|
| P1 | [0.20, 0.45] | Débutant — initiation |
| P2 | [0.40, 0.60] | Intermédiaire |
| P3 | [0.55, 0.75] | Confirmé |
| P4 | [0.70, 0.90] | Expert — autonomie |

Ajustement : thérapeute via `PUT /api/therapist/patients/{id}/palier` ou automatique selon la progression.

### 8.4 Sélection du type de feedback selon état EEG

| État EEG détecté | Feedback proposé |
|---|---|
| `concentration` (focus) | Jeu cognitif, image stimulante |
| `stress` | Guide respiratoire (`BreathingGuide`), audio apaisant, image calme |
| `uncertain` / `neutral` | Maintien du feedback actuel (`FocusPoint`) |
| Électrodes déconnectées | Alerte visuelle, session suspendue |

### 8.5 Rapport de fin de session (Claude AI)

```
POST /api/feedback/end déclenche (de façon non bloquante) :
  asyncio.create_task(_generate_and_broadcast_report)
     │
     ├─ generate_session_report(session_data)   ← app/services/ai_report.py
     │     contexte : objectif, durée, profil patient, médias joués,
     │                items_efficaces, delta_alpha/beta global
     │
     ├─ Sauvegarde feedback_sessions.report_text dans Supabase
     │
     └─ broadcast WS {action: "session_ended", report, metrics}
           → FeedbackReport.jsx affiché côté patient
```

---

## 9. Apprentissage automatique nocturne

```
Chaque nuit à 02:00 UTC (APScheduler) :
─────────────────────────────────────────

Pour chaque patient avec un profil EEG :
  │
  ├─ Récupère les époques haute confiance non encore utilisées
  │     (training_epochs où is_high_confidence=true ET used_in_finetuning=false)
  │
  ├─ Vérifie les conditions de déclenchement :
  │     v1   : première calibration (assez d'époques pour un premier modèle)
  │     v2   : nouveau lot accumulé depuis le dernier fine-tuning
  │     drift: précision sur 20 dernières sessions < seuil critique
  │     maintenance: run périodique programmé
  │
  ├─ Si déclenchement :
  │     Crée un finetuning_job (statut: pending → running)
  │     Lance le fine-tuning du modèle EEGNet du patient
  │     Mesure la précision avant et après
  │     Sauvegarde le checkpoint du modèle
  │     Met à jour eeg_profiles.finetuned_model_checkpoint
  │     Met à jour le statut du job (done ou failed)
  │
  └─ Le patient bénéficiera du nouveau modèle dès sa prochaine session
```

---

## 10. Sécurité transversale

| Mécanisme | Description |
|---|---|
| **JWT access token** | Durée courte, requis sur toutes les routes protégées |
| **JWT refresh token** | Durée longue, type="refresh" vérifié |
| **bcrypt** | Hash des mots de passe (sel aléatoire par utilisateur) |
| **Brute-force protection** | Compteur d'échecs par IP, blocage après seuil |
| **Vérification email** | Inscription impossible sans code valide (TTL 10 min) |
| **Force du mot de passe** | Vérifiée côté serveur (≥ 8 car, maj, min, chiffre, spécial) |
| **CORS** | Middleware configuré, origines autorisées uniquement |
| **RBAC** | Routes admin : `get_admin_user` · Routes thérapeute : `get_therapist_user` |
| **Soft delete** | Les comptes supprimés sont désactivés, pas effacés par défaut |
| **Audit log** | Toutes les actions sensibles sont tracées avec IP et timestamp |
| **Headers HTTP** | CSP, HSTS, X-Frame-Options (middleware sécurité) |

---

---

## 11. Architecture technique — Backend & Frontend

### 11.1 Backend — `app/Backend/app/`

#### Entrée et configuration

| Fichier | Rôle |
|---|---|
| `main.py` | Point d'entrée FastAPI, montage des routers, CORS, scheduler nocturne |
| `core/config.py` | Variables d'environnement (Supabase URL/key, JWT secret, Resend key…) |
| `core/database.py` | Client Supabase async (`get_db`) |
| `core/security.py` | `get_current_user`, `get_admin_user`, `get_therapist_user`, création JWT |
| `middleware/security.py` | Headers HTTP (CSP, HSTS, X-Frame-Options), brute-force par IP |

#### Routes API

| Fichier | Préfixe | Endpoints principaux |
|---|---|---|
| `routes/auth.py` | `/api/auth` | `send-code`, `register`, `login`, `refresh`, `me`, `change-password` |
| `routes/feedback.py` | `/api/feedback` | `sessions`, `recommend`, `submit`, `skip`, `sam`, `end` + WS `/feedback/ws/{id}` |
| `routes/sessions.py` | `/api/sessions` | `list`, `create`, `report`, `export`, `calendar` |
| `routes/eeg.py` | `/api/eeg` | WS EEG temps réel, `baseline/finalise`, `analyze_file`, `recording`, `wifi/*`, `my-reports` |
| `routes/media.py` | `/api/media` | `list` (filtrage par type et état EEG) |
| `routes/admin.py` | `/api/admin` | `stats`, `users`, `assign-patient`, `send-reminder`, `audit-logs`, `settings` |
| `routes/therapist.py` | `/api/therapist` | `patients`, `notes`, `recommendation`, `palier`, `export`, `eeg-reports` |
| `routes/assistant.py` | `/api/assistant` | `ask` (RAG), `feedback` |
| `routes/Profile.py` | `/api/profile` | `me`, `calibration` |

#### Services

| Fichier | Rôle |
|---|---|
| `services/eeg/eeg_pipeline.py` | Pipeline DSP principal (filtrage → artefacts → époques → features → classifieur → WS) |
| `services/eeg/tcp_receiver.py` | Réception TCP ESP32 (port 9000), file d'attente 5000 samples |
| `services/eeg/dsp/filters.py` | FilterBank : DC, Notch 50/100 Hz, Butterworth BP, ondelette |
| `services/eeg/dsp/artifacts.py` | Détection EOG / EMG / rejet dur (> 200 µV ou signal plat) |
| `services/eeg/dsp/epochs.py` | Fenêtrage 4 s, pas 0,5 s |
| `services/eeg/dsp/features.py` | 63 features : PSD Welch, ratios cognitifs, Hjorth, Higuchi FD, entropie spectrale |
| `services/eeg/dsp/processor.py` | Orchestrateur DSP asyncio (10 samples/itération) |
| `services/eeg/dsp/ml_classifier.py` | Classifieur EEGNet (modèle global ou fine-tuned par patient) |
| `services/eeg/recording/csv_handler.py` | Enregistrement CSV des sessions |
| `services/adaptative_engine.py` | EWMA, seuil θ, paliers P1→P4 |
| `services/ai_report.py` | Génération rapport via Claude API (async, non bloquant) |
| `services/auth.py` | Logique inscription/login (bcrypt, brute-force, tokens) |
| `services/email_service.py` | Envoi emails via Resend (vérification, rappels admin) |
| `services/rag_service.py` | RAG local sur corpus EEG/neurofeedback |
| `services/classifieur.py` | Chargement et inférence du modèle ML |
| `services/finetune/runner.py` | Fine-tuning EEGNet per-patient |
| `services/finetune/scheduler.py` | APScheduler nocturne (02:00 UTC) |
| `services/finetune/conditions.py` | Conditions de déclenchement (v1, v2, drift, maintenance) |

---

### 11.2 Frontend — `app/Frontend/src/`

#### Pages

| Fichier | URL | Rôle |
|---|---|---|
| `pages/FeedbackSession.jsx` | `/feedback/session` | Séance neurofeedback complète (6 phases) |
| `pages/FeedbackPage.jsx` | `/feedback` | Hub — démarrer / historique des séances feedback |
| `pages/EEGLive.jsx` | `/eeg-live` | EEG temps réel, calibration, transition vers feedback |
| `pages/EEGPage.jsx` | `/eeg` | Analyse fichier EEG hors-ligne |
| `pages/Login.jsx` | `/login` | Connexion |
| `pages/Register.jsx` | `/register` | Inscription avec vérification email |
| `pages/DashboardPage.jsx` | `/dashboard` | Dashboard patient |
| `pages/History.jsx` | `/history` | Historique des sessions |
| `pages/AdminPanel.jsx` | `/admin` | Dashboard administrateur |
| `pages/TherapistDashboard.jsx` | `/therapist` | Dashboard thérapeute |

#### Composants feedback — `components/feedback/`

| Fichier | Rôle |
|---|---|
| `MiniEEGOscilloscope.jsx` | Signal brut temps réel + état ML (colonne gauche de la séance) |
| `MediaZone.jsx` | Affiche le contenu actif selon `currentMedia.type` (image / vidéo / jeu / audio) |
| `BreathingGuide.jsx` | Animation respiration guidée (état stress ou baseline) |
| `FocusPoint.jsx` | Point de fixation visuel (état concentration) |
| `UserFeedbackBar.jsx` | Boutons liked / SAM 1-5 / skip après chaque média |
| `SessionBlockTimer.jsx` | Barre de progression + compte à rebours bloc 3 min |
| `FeedbackReport.jsx` | Rapport final (texte Claude AI + métriques numériques) |
| `AudioFeedback.jsx` | Lecteur audio pour médias de type "audio" |
| `ImageFeedback.jsx` | Afficheur d'image |
| `VideoFeedback.jsx` | Lecteur vidéo |
| `GameFeedback.jsx` | Wrapper de sélection du jeu selon `game_prefix` |
| `FeedbackSelector.jsx` | Sélecteur manuel de type de feedback |
| `BrainStateIndicator.jsx` | Indicateur visuel de l'état cognitif classifié |
| `FeedbackJustification.jsx` | Explication texte de la recommandation |

#### Jeux cognitifs — `components/feedback/games/`

| Fichier | Jeu |
|---|---|
| `MemoryGame.jsx` | Paires de cartes à mémoriser |
| `PuzzleGame.jsx` | Reconstruction d'image |
| `SudokuGame.jsx` | Grille Sudoku |
| `CalculGame.jsx` | Calcul mental |
| `EnigmeGame.jsx` | Devinettes |

#### Hooks

| Fichier | Rôle |
|---|---|
| `hooks/useFeedbackSocket.js` | WS `/feedback/ws/{id}` — reçoit `play` (currentMedia) et `session_ended` (rapport) |
| `hooks/useEEGWebSocket.js` | WS EEG — expose `eegFrame` (62 Hz), `epochFrame` (4 s), `mlPrediction` |
| `hooks/useFeedbackEngine.js` | Logique moteur adaptatif côté frontend (EWMA, succès/échec) |
| `hooks/useRecording.js` | Gestion de l'enregistrement CSV |

#### Utilitaires

| Fichier | Rôle |
|---|---|
| `utils/api.js` | Axios + modules : `auth`, `sessions`, `feedback`, `media`, `eeg`, `admin`, `therapist`, `assistant`, `calendar`, `createFeedbackWS`, `createSessionWS` |
| `utils/exportPDF.js` | Export PDF du rapport de session |

#### Flux de données complet en séance

```
ESP32 ──TCP──► Backend DSP ──WS /ws/eeg──► useEEGWebSocket
                                                │
                          eegFrame (62 Hz) ─────┤
                          epochFrame (4 s) ─────┤
                          mlPrediction ──────────┤
                                                 ▼
                                         FeedbackSession
                                                 │
                    POST /api/feedback/sessions ─┤─► sessionId
                                                 │
                    POST /api/feedback/recommend ─┤─► Thompson sampling
                           (eeg_state dérivé ML)  │
                                                 │
                    WS /feedback/ws/{sessionId} ◄─┤── action "play"
                         useFeedbackSocket        │       → currentMedia
                                                 │
                                         MediaZone (render)
                                                 │
                    UserFeedbackBar ─────────────►│
                    (liked / sam / skip)           │
                                                 ▼
                    POST /api/feedback/submit ─────► _update_weights (Thompson)
                    POST /api/feedback/skip  ─────► beta += 1
                                                 │
                    POST /api/feedback/end ────────► score + Claude AI async
                                                 │
                    WS action "session_ended" ────► FeedbackReport
```

---

*Système NeuroCap v2.2.0 — Backend FastAPI (port 8001) + Frontend React/Vite + Supabase (PostgreSQL)*
