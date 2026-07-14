# features_extraction.py — Documentation Détaillée

## Vue d'ensemble

`features_extraction.py` extrait **15 features spectrales et temporelles** par époque EEG pour les modèles baseline ML du projet NeuroCap. Ces features sont conçues pour être calculables en < 10 ms/époque sur le hardware embarqué (AD8232 + ESP32), les rendant aptes au temps réel.

**Fichier :** `src/data/features_extraction.py`  
**Lignes :** ~510  
**Rôle :** Extraction de 15 features légères pour baseline ML

---

## Constantes

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `FS` | 250 | Fréquence d'échantillonnage (Hz) |
| `EPOCH_SAMPLES` | 1000 | Samples par époque |
| `FEATURE_NAMES` | Liste 15 éléments | Noms des features dans l'ordre |

### Liste des 15 features (`FEATURE_NAMES`)

```
['Pδ (0.5-4Hz)', 'Pθ (4-8Hz)', 'Pα (8-13Hz)', 'Pβ (13-30Hz)', 'Pγ (30-40Hz)',
 'TBR (θ/β)', 'ABR (α/β)', 'EI (β/(α+θ))', 'TAR (θ/α)',
 'Hjorth_Activity', 'Hjorth_Mobility', 'Hjorth_Complexity',
 'Power', 'MeanAmp', 'RelEnergy_β']
```

---

## Fonctions d'extraction

### `_psd(x, nperseg=256)`

Calcule la densité spectrale de puissance via la méthode de Welch.

**Paramètres :**
- `x` — Signal 1D (1000 points, numpy float32/64)
- `nperseg` — Taille du segment Welch (défaut 256 points)

**Algorithme :**
- Appelle `scipy.signal.welch(x, fs=FS, window='hann', nperseg=nperseg)`
- Fenêtre de Hann pour réduire les fuites spectrales

**Retourne :** `(freqs, psd)` — numpy arrays

---

### `_band_power(freqs, psd, flo, fhi)`

Intègre la PSD sur une bande fréquentielle par règle des trapèzes.

**Paramètres :**
- `freqs` — Vecteur fréquences (Hz)
- `psd` — Densité spectrale de puissance
- `flo`, `fhi` — Bornes de la bande (Hz)

**Algorithme :**
1. Masquer les fréquences hors [flo, fhi]
2. Intégrer par `np.trapz(psd[mask], freqs[mask])`

**Retourne :** `float` — puissance dans la bande (µV²/Hz intégrée)

---

### `get_feature_vector(epoch)`

**Fonction centrale** — extrait le vecteur de 15 features d'une époque.

**Paramètre :**
- `epoch` — Tableau 1D de 1000 points (µV normalisé)

**Algorithme étape par étape :**

**1. PSD Welch :**
```python
freqs, psd = _psd(epoch)
```

**2. Puissances de bandes (features 1-5) :**
```python
Pd = _band_power(freqs, psd, 0.5, 4.0)   # Delta
Pt = _band_power(freqs, psd, 4.0, 8.0)   # Theta
Pa = _band_power(freqs, psd, 8.0, 13.0)  # Alpha
Pb = _band_power(freqs, psd, 13.0, 30.0) # Beta
Pg = _band_power(freqs, psd, 30.0, 40.0) # Gamma
```

**3. Ratios cognitifs (features 6-9) :**
```python
TBR = Pt / (Pb + eps)              # Theta/Beta Ratio — concentration inverse
ABR = Pa / (Pb + eps)              # Alpha/Beta Ratio
EI  = Pb / (Pa + Pt + eps)         # Engagement Index — concentration
TAR = Pt / (Pa + eps)              # Theta/Alpha Ratio — stress
```

**4. Paramètres de Hjorth (features 10-12) :**
```python
Activity   = var(epoch)                          # Variance (puissance temporelle)
diff1 = np.diff(epoch)                           # Première dérivée
Mobility   = std(diff1) / (std(epoch) + eps)     # Mobilité (dérivée normalisée)
diff2 = np.diff(diff1)                           # Deuxième dérivée
Complexity = (std(diff2)/(std(diff1)+eps)) / Mobility  # Complexité
```

**5. Features temporelles (features 13-15) :**
```python
Power      = np.mean(epoch**2)           # Puissance temporelle totale (RMS²)
MeanAmp    = np.mean(np.abs(epoch))      # Amplitude absolue moyenne
RelEnergy_b = Pb / (sum_all_bands + eps) # Énergie relative beta
```

**Retourne :** `numpy.ndarray` de forme `(15,)` — dtype float32

**Gestion des valeurs aberrantes :**
- Division par zéro protégée par `eps = 1e-10`
- Les NaN/Inf sont remplacés par 0 dans la fonction appelante

---

## Fonction principale

### `main()`

Orchestre l'extraction de features pour toutes les expériences et les splits val/test.

**Algorithme :**

```
Pour chaque dataset (concentration, stress) :
    Pour chaque expérience (A, B, C, D, FULL) :
        X_train = np.load("datasets_augmented/X_train_{exp}.npy")
        y_train = np.load("datasets_augmented/y_train_{exp}.npy")
        
        features_train = [get_feature_vector(ep) for ep in X_train]
        → sauvegarde "Features/{dataset}/feat15_train_{exp}.npy"
        → sauvegarde "Features/{dataset}/y_train_{exp}.npy"
    
    X_val  = np.load("datasets_augmented/X_val.npy")
    X_test = np.load("datasets_augmented/X_test.npy")
    
    features_val  = [get_feature_vector(ep) for ep in X_val]
    features_test = [get_feature_vector(ep) for ep in X_test]
    → sauvegarde feat15_val.npy et feat15_test.npy
```

**Gestion des subject_ids :**
Pour les expériences augmentées, les subject_ids sont dupliqués avec une stratégie de "tile" :
- Exp A : 1× → subject_ids originaux
- Exp B : 2× → `np.tile(subject_ids, 2)`
- Exp C : 3× → `np.tile(subject_ids, 3)`
- Exp D : 2× → `np.tile(subject_ids, 2)`
- Exp FULL : 4× → `np.tile(subject_ids, 4)`

---

### `_print_summary(out_dir, experiments)`

Affiche un tableau récapitulatif des shapes extraites pour chaque expérience.

**Exemple de sortie :**
```
Exp | Shape train | Shape val | Shape test
A   | (1240, 15)  | (186, 15) | (186, 15)
B   | (2480, 15)  | (186, 15) | (186, 15)
...
```

---

## Structure des fichiers de sortie

```
Features/
├── conc/
│   ├── feat15_train_A.npy      # (N_train, 15)
│   ├── feat15_train_B.npy      # (N_train×2, 15)
│   ├── feat15_train_C.npy      # (N_train×3, 15)
│   ├── feat15_train_D.npy      # (N_train×2, 15)
│   ├── feat15_train_FULL.npy   # (N_train×4, 15)
│   ├── feat15_val.npy          # (N_val, 15)
│   ├── feat15_test.npy         # (N_test, 15)
│   ├── y_train_{exp}.npy       # scores continus 0-10
│   └── subject_ids_train_{exp}.npy
└── stress/
    └── (même structure)
```

---

## Signification des features

### Features PSD (1-5)
- **Pδ** — Puissance delta (0.5-4 Hz) : sommeil profond, relaxation extrême
- **Pθ** — Puissance thêta (4-8 Hz) : somnolence, mémoire de travail, stress
- **Pα** — Puissance alpha (8-13 Hz) : relaxation éveillée, inhibition cognitive
- **Pβ** — Puissance beta (13-30 Hz) : concentration active, vigilance
- **Pγ** — Puissance gamma (30-40 Hz) : traitement sensoriel rapide

### Ratios cognitifs (6-9)
- **TBR = θ/β** — Theta/Beta Ratio : score de concentration *inverse* (↑TBR = ↓concentration). Salam et al. 2026 : p < 0.001
- **ABR = α/β** — Alpha/Beta Ratio : relaxation relative
- **EI = β/(α+θ)** — Engagement Index : concentration active (Pope et al. 1995)
- **TAR = θ/α** — Theta/Alpha Ratio : stress cognitif (Samsa & Altıntop 2026)

### Paramètres de Hjorth (10-12)
- **Activity** — Variance du signal (puissance temporelle)
- **Mobility** — Variabilité de la fréquence dominante
- **Complexity** — Diversité spectrale (rapport de complexités)

### Features temporelles (13-15)
- **Power** — RMS² du signal
- **MeanAmp** — Amplitude absolue moyenne
- **RelEnergy_β** — Fraction de l'énergie dans la bande beta (0-1)

---

## Performance

| Critère | Valeur |
|---------|--------|
| Temps/époque | < 10 ms (CPU) |
| Dimension sortie | 15 features |
| Mémoire | Négligeable |
| Compatibilité hardware | ESP32 (subset C implémenté) |

---

## Dépendances

| Bibliothèque | Usage |
|-------------|-------|
| `numpy` | Calculs vectoriels |
| `scipy.signal` | Welch PSD, `np.trapz` |
