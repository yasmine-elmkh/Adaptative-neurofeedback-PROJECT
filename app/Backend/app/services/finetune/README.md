# Fine-tuning automatique — NeuroCap v3.0

Service de personnalisation IA nocturne : adapte les deux modèles EEGNet de production (concentration + stress) à chaque patient, via les epochs EEG haute-confiance collectées au fil du temps.

---

## Architecture

```
APScheduler (02:00 UTC)
    │
    ▼
scheduler.py::_nightly_check()
    │
    ├── Pour chaque profil EEG patient :
    │       conditions.py::get_activity()          → activité récente
    │       conditions.py::check_finetune_trigger() → faut-il fine-tuner ?
    │
    └── Si trigger → runner.py::trigger_finetune()
                        │
                        asyncio.create_task(_do_finetune())
                              │
                        1. Récupère les epochs haute-confiance (training_epochs, signal brut inclus)
                        2. Pour chaque tâche (concentration, stress) :
                             a. Charge le checkpoint personnel (v-1) s'il existe, sinon le modèle FULL de base
                             b. Gèle tout le backbone EEGNet — entraîne uniquement la couche `fc`
                             c. Adam (lr=1e-4, weight_decay=1e-5), MSELoss, 30 epochs
                        3. Sauvegarde les 2 checkpoints (conc + stress)
                        4. Met à jour eeg_profiles + finetuning_jobs
```

> Le modèle personnalisé est la **même architecture EEGNet qu'à l'inférence** — il ne s'agit pas d'un modèle séparé mais d'une adaptation légère (fine-tuning de la tête FC) des deux modèles de production.

---

## Fichiers

### `conditions.py`

Contient les règles d'activité et les seuils de déclenchement.

**Constantes :**
```python
ACTIVITY_MAX_IDLE_DAYS   = 14    # Inactif si dernière action > 14j
ACTIVITY_MIN_ACTIONS_30D = 3     # Au moins 3 sessions/rapports en 30j
ACTIVITY_MIN_EPOCHS_30D  = 100   # Au moins 100 epochs fiables en 30j
V1_EPOCHS_NEEDED         = 2000  # Seuil première personnalisation
V2_EPOCHS_NEEDED         = 4000  # Seuil mise à jour majeure
V2_DELAY_DAYS            = 60
MAINTENANCE_DAYS         = 180
CAL_GRACE_DAYS           = 25
DRIFT_ACCURACY           = 0.85
DRIFT_COOLDOWN           = 7
```

**`get_activity(patient_id, db)`** → dict :
```python
{
    "is_active":           bool,   # Toutes conditions activité réunies
    "last_activity_at":    str,    # max(dernière session, dernier rapport EEG)
    "days_idle":           int,    # Jours depuis dernière action
    "sessions_last_30d":   int,    # Sessions neurofeedback en 30j
    "reports_last_30d":    int,    # Analyses fichiers EEG en 30j
    "activity_total_30d":  int,    # sessions_30d + reports_30d
    "reliable_epochs_30d": int,    # Epochs haute-confiance créées en 30j
}
```

**`check_finetune_trigger(patient_id, profile, db)`** → `(should: bool, reason: str, type: str | None)` :

| Type | Condition |
|---|---|
| `v1` | Version 0 → 2 000 epochs fiables non utilisées + ≥ 25j depuis la calibration |
| `v2` | Version 1 → 4 000 nouvelles epochs fiables + ≥ 60j depuis v1 |
| `maintenance` | Version ≥ 2 → ≥ 180j depuis le dernier fine-tuning |
| `drift` | `last_20_sessions_accuracy` < 0.85 + ≥ 7j depuis le dernier fine-tuning |

---

### `runner.py`

Fine-tune les 2 modèles personnels du patient, avec la même architecture qu'en inférence :

| Tâche | Modèle de base | AUC LOSO | Stratégie |
|---|---|---|---|
| Concentration | `models/Regression/DL/EEGNet/conc/EEGNet_conc_FULL_best.pt` | 0.751 | EEGNet DL FULL |
| Stress | `models/Regression/TL/EEGNet_LayerReplacement/stress/EEGNet_LR_stress_FULL_best.pt` | 0.607 | EEGNet TL-LayerReplacement FULL |

**`trigger_finetune(patient_id, trigger_type, db)`** : crée l'enregistrement `finetuning_jobs` (status=pending) et lance `asyncio.create_task(_run_job(...))`.

**`_do_finetune(job_id, patient_id, db)`** :

1. Récupère les epochs `is_high_confidence=True, used_in_finetuning=False` (max 5 000), avec le signal brut filtré (`epoch_filtered`) et les scores `conc_score` / `stress_score`
2. Pour chaque tâche (`_finetune_eegnet()`), si ≥ `MIN_EPOCHS` (50) epochs disponibles :
   - Charge le state_dict : checkpoint personnel précédent si disponible, sinon le modèle FULL de base
   - Gèle tout le backbone (`param.requires_grad = name.startswith("fc")`)
   - Z-score par epoch, reshape `(N, 1, 1, 1000)` (même format qu'à l'inférence)
   - Entraîne `model.fc` : Adam (lr=1e-4, weight_decay=1e-5), MSELoss sur la sortie sigmoid 0–100, 30 epochs, batch=32
   - Sauvegarde : `models/personal/patient_{id[:8]}_{task}_v{version}.pt`
3. Met à jour `eeg_profiles` (`conc_checkpoint`, `stress_checkpoint`, `finetuned_version`, `last_finetune_at`)
4. Marque les epochs comme utilisées (batch de 100 — limite Supabase `IN`)
5. Finalise `finetuning_jobs` (status=completed, `n_epochs_used`, `accuracy_before`/`after` = MSE avant/après, `model_checkpoint_path`)

Si une tâche a moins de `MIN_EPOCHS` epochs disponibles, elle est simplement passée (`status: "skip (n/MIN_EPOCHS)"`) sans faire échouer l'autre tâche ni le job.

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
| `eeg_profiles` | Lecture profil + écriture `conc_checkpoint`/`stress_checkpoint`/`finetuned_version`/`last_finetune_at` |
| `training_epochs` | Source de données (lecture `epoch_filtered` + scores) + marquage `used_in_finetuning` |
| `finetuning_jobs` | Création + mise à jour du statut de chaque run |
| `sessions` | Proxy activité patient (`sessions_last_30d`) |
| `eeg_reports` | Proxy activité patient (`reports_last_30d` = analyses fichiers) |

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
pip install APScheduler
```

PyTorch et le reste des dépendances EEG (numpy, scipy) sont déjà dans `requirements.txt`.
