# NeuroCap — Feature Engineering

Extraction and engineering of spectral, temporal, and wavelet features from preprocessed EEG epochs for use in baseline and deep-learning classifiers.

---

## Structure

```
features/
├── features_extraction/   # Scripts: raw epoch → feature matrix
└── Features_eng/          # Engineered feature sets (selected, normalised)
```

---

## Feature categories

### Spectral (frequency-domain) features
Computed via **Welch PSD** (4 s window, 50% overlap, Hann window):

| Feature | Description |
|---|---|
| Delta power (1–4 Hz) | Deep relaxation indicator |
| Theta power (4–8 Hz) | Drowsiness, memory encoding |
| Alpha power (8–13 Hz) | Relaxation, idling rhythm |
| Beta power (13–30 Hz) | Active concentration, alertness |
| Gamma power (30–45 Hz) | High-level cognition |
| **TBR** (Theta/Beta ratio) | Key neurofeedback metric |
| **EI** (Engagement Index) | β / (α + θ) |
| **IAPF** | Individual Alpha Peak Frequency |
| Spectral centroid | Weighted mean frequency |
| Spectral entropy | Frequency distribution complexity |

### Temporal (time-domain) features

| Feature | Description |
|---|---|
| Mean, variance, std | Signal statistics |
| Skewness, kurtosis | Distribution shape |
| RMS amplitude | Signal energy |
| Peak-to-peak amplitude | Artefact sensitivity indicator |
| Zero-crossing rate | Frequency proxy |
| Hjorth mobility | Signal complexity (1st derivative variance) |
| Hjorth complexity | Signal complexity (2nd derivative) |

### Wavelet features
Computed via **Discrete Wavelet Transform** (DWT, Daubechies db4, 5 levels):

| Level | Approximate frequency | Band |
|---|---|---|
| D1 | 62.5–125 Hz | High-gamma |
| D2 | 31.25–62.5 Hz | Gamma |
| D3 | 15.6–31.25 Hz | Beta |
| D4 | 7.8–15.6 Hz | Alpha |
| D5 | 3.9–7.8 Hz | Theta |
| A5 | 0–3.9 Hz | Delta |

Features per level: energy, entropy, mean, std.

---

## Pipeline

```python
# Example usage
from features_extraction.extractor import extract_features

epoch = np.load("epoch.npy")           # shape: (1000,) @ 250 Hz
features = extract_features(epoch, fs=250)
# Returns dict with ~40 features
```

---

## Feature selection

Feature importance ranking was performed using:
- **Random Forest** feature importance (mean decrease impurity)
- **Mutual information** with the class label
- **Recursive Feature Elimination** (RFE) with SVM

Top features consistently selected: **TBR**, **Alpha power**, **IAPF**, **Beta power**, **Hjorth mobility**.

Results saved in `reports/Comparison_Baselines_Features/`.

---

## Output format

```
features/Features_eng/
├── features_train.csv    # Training feature matrix (N_epochs × N_features + label)
├── features_test.csv     # Test set
└── feature_names.txt     # Ordered list of feature names
```

Columns: `delta`, `theta`, `alpha`, `beta`, `gamma`, `tbr`, `ei`, `iapf`, `rms`, `hjorth_mob`, `hjorth_comp`, ..., `label`
