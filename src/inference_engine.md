# inference_engine.py — Documentation Détaillée

## Vue d'ensemble

`inference_engine.py` est le module central d'inférence en production de NeuroCap. Il charge les modèles entraînés (EEGNet TL-3), applique le pipeline de préprocessing en temps réel sur les signaux provenant de l'ESP32, et retourne un état cognitif structuré avec score de confiance.

**Fichier :** `src/inference_engine.py`  
**Lignes :** ~566  
**Rôle :** Inférence temps réel — ESP32 → modèle → état cognitif

---

## Constantes

```python
CONFIDENCE_THR = 0.60   # Seuil de confiance minimum pour une décision fiable
SCORE_THRESHOLD = 5.0   # Seuil Low/High (même que dans l'entraînement)
FS = 250                # Fréquence d'échantillonnage (Hz)
EPOCH_SAMPLES = 1000    # Échantillons par epoch (4s × 250Hz)
```

---

## Enum `ModelType`

Identifie le type de modèle chargé.

```python
class ModelType(Enum):
    CONCENTRATION = "concentration"
    STRESS        = "stress"
    DUAL          = "dual"   # Charge les deux modèles
```

---

## Classe `InferenceEngine`

Moteur d'inférence chargé une fois en mémoire.

### `__init__(model_path_conc, model_path_stress, model_type)`

Initialise le moteur et charge les modèles.

**Paramètres :**
- `model_path_conc` — Chemin vers le modèle concentration (.pt)
- `model_path_stress` — Chemin vers le modèle stress (.pt)
- `model_type` — `ModelType.DUAL` (par défaut)

**Actions :**
```python
self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
self.model_conc  = self._load_model(model_path_conc)
self.model_stress = self._load_model(model_path_stress)
```

---

### `_load_model(path)`

Charge un modèle EEGNet depuis un fichier .pt.

**Algorithme :**
```python
checkpoint = torch.load(path, map_location=self.device)
model = EEGNet(n_out=1)               # Architecture identique à l'entraînement
model.load_state_dict(checkpoint)
model.eval()                           # Mode inférence (désactive BatchNorm/Dropout)
return model
```

---

### `_preprocess(raw_signal)`

Applique le pipeline complet sur un signal brut de l'ESP32.

**Paramètre :** `raw_signal` — numpy array (1000,) en µV (ADC converti)

**Pipeline :**
1. **HP filter** (0.5 Hz, ordre 4) — élimination drift DC
2. **LP filter** (40 Hz, ordre 4) — élimination artefacts musculaires
3. **Notch** (50 Hz, Q=30) — élimination bruit secteur
4. **DWT denoising** (db4, niveau 4, seuillage universel)
5. **Rejet amplitude** — NaN si max|signal| > 500 µV
6. **Z-score** — normalisation par mean et std du signal

**Retourne :** numpy array (1000,) ou `None` si artefact détecté

---

### `predict(raw_signal)`

Fonction principale d'inférence — retourne l'état cognitif complet.

**Paramètre :** `raw_signal` — numpy array (1000,) — 4 secondes de signal Fp2

**Algorithme :**
```python
t0 = time.time()

# Préprocessing
signal = self._preprocess(raw_signal)
if signal is None:
    return {'error': 'artifact', 'uncertain': True}

# Inférence modèle concentration
x = torch.tensor(signal).unsqueeze(0).unsqueeze(0)  # (1, 1, 1000)
with torch.no_grad():
    score_conc   = self.model_conc(x).item()
    score_stress = self.model_stress(x).item()

# Clip scores dans [0, 10]
score_conc   = float(np.clip(score_conc,   0, 10))
score_stress = float(np.clip(score_stress, 0, 10))

# Calcul état et confiance
state, confidence = self._determine_state(score_conc, score_stress)

return {
    'concentration': score_conc,      # Float [0-10]
    'stress':        score_stress,     # Float [0-10]
    'state':         state,            # str: 'focused'/'stressed'/'relaxed'/'overloaded'
    'confidence':    confidence,       # Float [0-1]
    'uncertain':     confidence < CONFIDENCE_THR,
    'latency_ms':    (time.time() - t0) * 1000
}
```

---

### `_determine_state(score_conc, score_stress)`

Mappe les deux scores en un état cognitif qualitatif.

**Logique :**

| Concentration | Stress | État | 
|---------------|--------|------|
| ≥ 5.0 | < 5.0 | `'focused'` |
| < 5.0 | ≥ 5.0 | `'stressed'` |
| < 5.0 | < 5.0 | `'relaxed'` |
| ≥ 5.0 | ≥ 5.0 | `'overloaded'` |

**Calcul de la confiance :**
```python
# Distance normalisée au seuil 5.0 pour les deux scores
margin_conc   = abs(score_conc   - 5.0) / 5.0   # ∈ [0, 1]
margin_stress = abs(score_stress - 5.0) / 5.0   # ∈ [0, 1]
confidence    = 0.5 * (margin_conc + margin_stress)
```

---

### `predict_batch(signals)`

Inférence par batch pour l'historique ou l'entraînement en ligne.

**Paramètre :** `signals` — (N, 1000)

**Retourne :** Liste de N dictionnaires `predict()`.

---

### `get_model_info()`

Retourne des métadonnées sur les modèles chargés.

**Retourne :**
```python
{
    'model_type': 'EEGNet_LayerReplacement',
    'n_params_conc': 2847,
    'n_params_stress': 2847,
    'device': 'cpu',
    'confidence_thr': 0.60
}
```

---

## Format de retour de `predict()`

| Clé | Type | Description |
|-----|------|-------------|
| `concentration` | float | Score concentration [0-10] |
| `stress` | float | Score stress [0-10] |
| `state` | str | État cognitif qualitatif |
| `confidence` | float | Confiance [0-1] |
| `uncertain` | bool | True si confidence < 0.60 |
| `latency_ms` | float | Temps d'inférence en ms |
| `error` | str | 'artifact' si artefact détecté |

---

## Intégration avec le Backend

```python
# Dans app/Backend/app/services/eeg/dsp/processor.py
from src.inference_engine import InferenceEngine, ModelType

engine = InferenceEngine(
    model_path_conc='models/eegnet_conc.pt',
    model_path_stress='models/eegnet_stress.pt',
    model_type=ModelType.DUAL
)

# Par epoch (appeléé chaque 1s avec overlap 75%)
result = engine.predict(epoch_signal)
if not result['uncertain']:
    send_to_frontend(result)
```

---

## Performances cibles

| Métrique | Cible | Notes |
|----------|-------|-------|
| Latence inférence | < 50 ms | Sur CPU Raspberry Pi 4 |
| Latence totale | < 200 ms | Preprocessing + inférence |
| Confiance moy. | > 0.65 | Sur données de test |
| Cas uncertains | < 25% | Signaux de qualité acceptable |
