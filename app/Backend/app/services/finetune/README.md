# Fine-tuning automatique — NeuroCap v3.0

Service de personnalisation IA nocturne : adapte le modèle LightGBM à chaque patient via des epochs EEG haute-confiance collectées au fil du temps.

---

## Architecture

```
APScheduler (02:00 UTC)
    │
    ▼
scheduler.py::_nightly_check()
    │
    ├── Pour chaque profil EEG patient :
    │       conditions.py::get_activity()         → activité récente
    │       conditions.py::check_finetune_trigger() → faut-il fine-tuner ?
    │
    └── Si trigger → runner.py::trigger_finetune()
                        │
                        asyncio.create_task(_do_finetune())
                              │
                        1. Récupère epochs haute-confiance (training_epochs)
                        2. Charge modèle actuel (personal/ ou LOSO base)
                        3. LightGBM incremental (init_model, lr=0.01)
                        4. Sauvegarde checkpoint
                        5. Met à jour eeg_profiles + finetuning_jobs
```

---

## Fichiers

### `conditions.py`

Contient les règles d'activité et les seuils de déclenchement.

**Constantes :**
```python
ACTIVITY_MAX_IDLE_DAYS  = 14    # Inactif si dernière action > 14j
ACTIVITY_MIN_ACTIONS_30D = 3    # Au moins 3 sessions/rapports en 30j
ACTIVITY_MIN_EPOCHS_30D  = 100  # Au moins 100 epochs fiables en 30j
V1_EPOCHS_NEEDED         = 2000 # Seuil première personnalisation
V2_EPOCHS_NEEDED         = 4000 # Seuil mise à jour majeure
```

**`get_activity(patient_id, db)`** → dict :
```python
{
    "is_active":          bool,   # Toutes conditions activité réunies
    "days_idle":          int,    # Jours depuis dernière action
    "sessions_30d":       int,    # Sessions neurofeedback en 30j
    "reports_30d":        int,    # Analyses fichiers EEG en 30j
    "activity_total_30d": int,    # sessions_30d + reports_30d
    "reliable_epochs_30d":int,    # Epochs haute-confiance créées en 30j
}
```

**`check_finetune_trigger(patient_id, profile, db)`** → `(should: bool, reason: str, type: str)` :

| Type | Condition |
|---|---|
| `v1` | 2 000 epochs ≥ 0.85 confiance + ≥ 25j depuis calibration |
| `v2` | 4 000 nouvelles epochs + ≥ 60j depuis v1 |
| `drift` | Accuracy 20 dernières sessions < 85% + ≥ 7j depuis dernier FT |
| `maintenance` | ≥ 180j depuis dernier fine-tuning |

---

### `runner.py`

Exécute le fine-tuning LightGBM de façon asynchrone.

**`trigger_finetune(patient_id, trigger_type, db)`** : crée l'enregistrement `finetuning_jobs` (status=pending) et lance `asyncio.create_task(_do_finetune(...))`.

**`_do_finetune(job_id, patient_id, db)`** :

1. Récupère les epochs `is_high_confidence=True, used_in_finetuning=False` (max 5 000)
2. Construit X (np.float64, 63 features) et y (labels)
3. Charge le modèle actuel : checkpoint personnel si `finetuned_model_checkpoint` existe, sinon modèle LOSO base
4. Calcule `accuracy_before` sur le set d'entraînement
5. Fine-tune : `LGBMClassifier(n_estimators=100, learning_rate=0.01, init_model=base_clf).fit(X, y)`
6. Fallback si `init_model` échoue : entraînement from scratch (`n_estimators=200, lr=0.03`)
7. Calcule `accuracy_after`
8. Sauvegarde : `models/personal/patient_{id[:8]}_v{n}.joblib`
9. Met à jour `eeg_profiles` (checkpoint, version, last_finetune_at)
10. Marque les epochs comme utilisées (batch de 100)
11. Finalise `finetuning_jobs` (status=done, accuracy_before/after, finished_at)

---

### `scheduler.py`

Wrappeur APScheduler avec import **lazy** (optionnel).

```python
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    _APSCHEDULER_AVAILABLE = True
except ImportError:
    _APSCHEDULER_AVAILABLE = False
```

Si APScheduler n'est pas installé, le backend démarre normalement et log :
```
[FTScheduler] APScheduler non installé — fine-tuning automatique désactivé.
              Installez-le avec : pip install APScheduler
```

**Fonctions exportées :**
- `start_scheduler()` — appelé depuis `main.py` lifespan au démarrage
- `stop_scheduler()` — appelé au shutdown

---

## Tables Supabase utilisées

| Table | Usage |
|---|---|
| `eeg_profiles` | Lecture profil + écriture checkpoint/version/last_finetune_at |
| `training_epochs` | Source de données (lecture) + marquage used_in_finetuning |
| `finetuning_jobs` | Création + mise à jour statut de chaque run |
| `sessions` | Proxy activité patient (sessions_30d) |
| `eeg_reports` | Proxy activité patient (reports_30d = analyses fichiers) |

---

## Règles d'activité patient

Le fine-tuning est déclenché **uniquement pour les patients actifs** :

| Condition | Valeur |
|---|---|
| Dernière action (session ou rapport) | ≤ 14 jours |
| Actions en 30 jours | ≥ 3 |
| Epochs haute-confiance en 30 jours | ≥ 100 |

3 états visibles dans `Profile.jsx` :
- **Actif** (vert) — toutes conditions réunies, collecte en cours
- **En attente** (jaune) — activité insuffisante, fine-tuning suspendu
- **Inactif longue durée** (rouge) — aucune activité > 30j, personnalisation désactivée

---

## Installation

```bash
pip install APScheduler lightgbm joblib
```

Le reste des dépendances EEG (numpy, scipy, mne, pywavelets) est déjà dans `requirements.txt`.
