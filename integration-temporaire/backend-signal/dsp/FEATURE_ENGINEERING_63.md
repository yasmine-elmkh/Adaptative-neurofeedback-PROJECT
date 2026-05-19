# NeuroCap — Feature Engineering : de 15 à 63 features

> Module : `src/data/feature_eng.py` — utilisé par `dsp/epochs.py`

---

## Contexte : pourquoi 63 features ?

### Avant — 15 features (pipeline DSP v7.x)

Le pipeline d'origine extrayait **15 features** par époque, tirées uniquement des puissances spectrales et de quelques descripteurs temporels :

| # | Feature | Catégorie |
|---|---------|-----------|
| 1–5 | `rel_delta`, `rel_theta`, `rel_alpha`, `rel_beta`, `rel_gamma_low` | Puissances relatives |
| 6–9 | `engagement`, `stress_idx`, `theta_alpha`, `alpha_beta` | Ratios cognitifs |
| 10–12 | `hjorth_activity`, `hjorth_mobility`, `hjorth_complexity` | Hjorth |
| 13 | `spectral_entropy` | Complexité |
| 14 | `sef95` | Complexité |
| 15 | `rms_uv` | Amplitude |

**Limites :**
- Pas de décomposition multi-résolution → perd la structure temps-fréquence fine
- Aucune mesure de complexité non-linéaire (entropies d'ordre supérieur)
- Aucune information sur la dynamique des transitions du signal
- Seuils de classification arbitraires, sans validation LOSO

### Maintenant — 63 features (FeatEng v1.0, entraîné LOSO)

Le module `feature_eng.py` extrait **63 features** réparties en **7 catégories**, sur une époque de **4 s normalisée z-score** :

```
Epoch filtrée (1000 éch. @ 250 Hz)
     │
     ▼  z-score : epoch_z = (epoch - mean) / std
     │
     ├── Catégorie 1 — PSD Welch              →  5 features
     ├── Catégorie 2 — Ratios cognitifs        →  5 features
     ├── Catégorie 3 — Hjorth + temporelles    →  6 features
     ├── Catégorie 4 — DWT sous-bandes         → 20 features
     ├── Catégorie 5 — Statistiques texturales → 16 features
     ├── Catégorie 6 — Non-linéaires/entropies →  5 features
     └── Catégorie 7 — Transition patterns     →  6 features
                                               ─────────────
                                      TOTAL :  63 features
     │
     ▼
 StandardScaler (z-score entraînement)
     │
     ▼
 LightGBM (validation LOSO)
     │
     ▼
 { concentration: 0.83, stress: 0.17, state: "concentration",
   confidence: 0.83, uncertain: false }
```

---

## Les 7 catégories en détail

### Catégorie 1 — Puissances spectrales PSD Welch (5 features)

**Méthode :** estimateur de Welch (fenêtre Hann, nperseg=256, intégration trapézoïdale)

**Bandes utilisées (identiques à l'entraînement) :**

| Feature | Bande | Plage |
|---------|-------|-------|
| `Pd` | delta | 0.5 – 4.0 Hz |
| `Pt` | theta | 4.0 – 8.0 Hz |
| `Pa` | alpha | 8.0 – 13.0 Hz |
| `Pb` | beta  | 13.0 – 30.0 Hz |
| `Pg` | gamma | 30.0 – 40.0 Hz |

> **Note :** ces bandes diffèrent légèrement des bandes DSP v8.0 du dashboard (δ 1–4, θ 6–8, γ 30–45 Hz). Elles sont **intentionnellement identiques à celles utilisées lors de l'entraînement** pour ne pas introduire de biais distributional.

**Référence :** CdC NeuroCap §2.3

---

### Catégorie 2 — Ratios cognitifs NeuroCap (5 features)

Calculés à partir des puissances de bande. Invariants au scaling (gain ADC variable).

| Feature | Formule | Interprétation |
|---------|---------|----------------|
| `TBR` | θ / β | < 0.8 = concentration (CdC NeuroCap) |
| `ABR` | α / β | relaxation vs activation |
| `EI`  | β / (α + θ) | > 0.7 = engagement cognitif actif |
| `TAR` | θ / α | p < 0.001 entre conc. et stress (Salam 2026) |
| `RelEnergy_beta` | β / (δ+θ+α+β+γ) | proportion d'énergie beta |

---

### Catégorie 3 — Paramètres de Hjorth + temporelles (6 features)

**Hjorth (1970)** — descripteurs statistiques dans le domaine temporel :

```python
d1 = diff(epoch)         # première dérivée
d2 = diff(d1)            # deuxième dérivée

Activity   = var(epoch)                         # énergie du signal (µV²)
Mobility   = std(d1) / std(epoch)               # fréquence caractéristique
Complexity = (std(d2)/std(d1)) / Mobility       # irrégularité fréquentielle
Power      = mean(epoch²)                       # puissance instantanée
MeanAmp    = mean(|epoch|)                      # amplitude moyenne
ZCR        = Σ(sign_changes) / N               # taux de passage par zéro
```

**Référence :** Samsa & Altıntop 2026 (accuracy 86.25% avec ces 3 features seules + RF)

---

### Catégorie 4 — DWT sous-bandes statistiques (20 features)

**Principe :** décomposition DWT db4 niveau 4 → 5 sous-bandes de fréquence.  
**4 statistiques par sous-bande = 5 × 4 = 20 features.**

```
pywt.wavedec(epoch, 'db4', level=4) → [cA4, cD4, cD3, cD2, cD1]
```

| Sous-bande | Coefficients | Fréquence approximative |
|------------|-------------|-------------------------|
| `dwt_delta` | cA4 | 0 – 3.9 Hz |
| `dwt_theta` | cD4 | 3.9 – 7.8 Hz |
| `dwt_alpha` | cD3 | 7.8 – 15.6 Hz |
| `dwt_beta`  | cD2 | 15.6 – 31.25 Hz |
| `dwt_gamma` | cD1 | 31.25 – 62.5 Hz |

Pour chaque sous-bande :
- `_mean` : amplitude moyenne absolue (tendance centrale)
- `_std` : dispersion (variabilité)
- `_energy` : somme des carrés (intensité de la sous-bande)
- `_entropy` : entropie de Shannon (désordre de la distribution d'énergie)

**Entropie de Shannon sur coefficients DWT :**
```
prob_i = coeff_i² / Σ coeff_j²
entropy = -Σ prob_i × log₂(prob_i)
```
Signal régulier → entropie basse. Signal chaotique → entropie haute.

**Pourquoi db4 ?** L'article "Multiresolution Analysis in EEG Signal Feature Engineering" (2018) montre que DWT-db4 + SVM surpasse db2, db6 et les MFCC pour la classification EEG.

---

### Catégorie 5 — Features statistiques texturales (16 features)

Inspiré de **NeuroFeat** (2025, accuracy 99.22% avec Cosine KNN).

**6 features globales sur le signal entier :**

| Feature | Calcul | Signification |
|---------|--------|---------------|
| `skewness` | skew(epoch) | asymétrie de la distribution |
| `kurtosis` | kurt(epoch) | aplatissement (queues lourdes = artefacts) |
| `IQR` | Q75 − Q25 | dispersion robuste aux outliers |
| `RMS` | √mean(epoch²) | amplitude efficace |
| `peak_to_peak` | max − min | amplitude crête à crête |
| `crest_factor` | max(|epoch|) / RMS | détection artefacts transitoires |

**10 features par sous-bande DWT (skewness + kurtosis × 5 sous-bandes) :**

```
dwt_delta_skew, dwt_delta_kurt
dwt_theta_skew, dwt_theta_kurt
dwt_alpha_skew, dwt_alpha_kurt
dwt_beta_skew,  dwt_beta_kurt
dwt_gamma_skew, dwt_gamma_kurt
```

Ces features capturent la **forme** de la distribution dans chaque bande — pas juste sa puissance.

---

### Catégorie 6 — Features non-linéaires et entropies (5 features)

**Principe :** un signal en état de concentration est **plus régulier** (entropies basses) qu'un signal de stress (entropies hautes).

**Référence :** "Age prediction on EEG signals via hybrid feature engineering approach" (2025)

| Feature | Méthode | Interprétation |
|---------|---------|----------------|
| `ApEn` | Approximate Entropy (Pincus 1991) | probabilité que des patterns similaires le restent au pas suivant |
| `SampEn` | Sample Entropy (Richman & Moorman 2000) | version améliorée d'ApEn, moins biaisée, robuste aux signaux courts |
| `PermEn` | Permutation Entropy (Bandt & Pompe 2002) | analyse des ordres de permutation, très robuste au bruit |
| `SpectralEn` | Entropie Shannon sur PSD normalisée | uniformité du spectre (signal sinusoïdal → 0, bruit blanc → 1) |
| `HFD` | Higuchi Fractal Dimension (Higuchi 1988) | complexité géométrique du signal, kmax=10 |

**Algorithme Higuchi FD :**
```
Pour k = 1..kmax :
    Pour m = 1..k :
        L_m(k) = longueur de la courbe aux indices {m, m+k, m+2k, ...}
                 × facteur de normalisation (N-1) / (⌊(N-m)/k⌋ × k²)
    lk = mean(L_m(k))
pente = polyfit(log(k), log(lk), degré=1)
HFD = -pente
```

Valeurs de référence EEG éveillé frontal : HFD ≈ 1.4–1.7

**Temps de calcul :** < 5 ms par époque (sous-échantillonnage ×2 pour ApEn/SampEn)

---

### Catégorie 7 — Transition patterns (6 features)

**Inspiré de QuadTPat** — Cambay et al., Scientific Reports 2024 (92.95% en 10-fold, 73.63% LOSO)

**Principe :** encoder les transitions entre échantillons consécutifs :
```
+1  si diff > threshold (montée)
-1  si diff < -threshold (descente)
 0  sinon (stable)
```

| Feature | Calcul | Interprétation |
|---------|--------|----------------|
| `pct_up` | % transitions montantes | dominance des montées |
| `pct_down` | % transitions descendantes | dominance des descentes |
| `pct_flat` | % transitions stables | régularité |
| `up_streak` | plus longue série de montées | persistance de tendance |
| `down_streak` | plus longue série de descentes | persistance de tendance |
| `trans_freq` | changements direction / total | fréquence de renversement |

**Simplification par rapport à QuadTPat :** triplets (3 éch.) au lieu de quadruplets (4 éch.) → compatible contrainte latence NeuroCap < 40 ms.

**Interprétation :**
- Concentration → transitions régulières (oscillations beta, `up_streak` et `down_streak` élevés)
- Stress → transitions chaotiques (`trans_freq` élevé, `pct_flat` bas)

---

## Tableau comparatif 15 → 63 features

| Aspect | Avant (15 features) | Maintenant (63 features) |
|--------|---------------------|--------------------------|
| **Spectral** | 6 puissances relatives (v8.0 bandes) | 5 puissances absolues Welch (bandes entraînement) |
| **Ratios** | 4 ratios cognitifs | 5 ratios cognitifs (+ TAR p<0.001) |
| **Temporel** | 3 Hjorth | 6 Hjorth + Power + MeanAmp + ZCR |
| **Multi-résolution** | aucun | 20 features DWT db4 niv.4 |
| **Textural** | 0 | 16 features (NeuroFeat 2025) |
| **Non-linéaire** | spectral_entropy, HFD | ApEn, SampEn, PermEn, SpectralEn, HFD |
| **Dynamique** | 0 | 6 features QuadTPat |
| **Classification** | Z-scores heuristiques, seuils arbitraires | LightGBM, validation LOSO |
| **Normalisation** | aucune | z-score époque + StandardScaler entraînement |

---

## Intégration dans le pipeline backend

### 1. `dsp/epochs.py` — extraction des 63 features

Après le Golden Filter (filtfilt zero-phase), l'époque filtrée est **z-scorée** puis passée à `extract_all_features` :

```python
# dsp/epochs.py — dans EpochExtractor._process()

# Golden Filter (zero-phase)
filtered = self.pipeline.filters.filter_epoch(raw_epoch)

# Z-score époque (Chaudhary 2025, Lawhern 2018)
_std = float(np.std(filtered))
if _std > 1e-10:
    _epoch_z   = (filtered - np.mean(filtered)) / _std
    ml_features = _extract_feateng(_epoch_z)   # → 63 features dict
```

Le z-score par époque aligne la distribution sur celle des données d'entraînement (toutes z-scorées à l'entraînement).

### 2. `dsp/processor.py` — prédiction LightGBM

```python
# dsp/processor.py — dans _process_epoch()
if _ml_clf is not None:
    ml_feats = epoch_result.get("ml_features")
    if ml_feats:
        epoch_result["ml_prediction"] = _ml_clf.predict_from_dict(ml_feats)
```

### 3. `dsp/ml_classifier.py` — chargement du modèle

Le classifieur charge deux artefacts depuis `models/baseline_FeatEng/baseline_models/` :
- `LightGBM_concentration_vs_stress.joblib` — modèle LightGBM entraîné LOSO
- `LightGBM_scaler.joblib` — StandardScaler ajusté sur les données d'entraînement

```python
def predict_from_dict(self, ml_features: dict) -> dict:
    # 1. Aligner les 63 features dans l'ordre canonique du modèle
    vec = np.array([ml_features.get(k, 0.0) for k in self._feature_names])
    
    # 2. Normaliser avec le scaler d'entraînement
    vec_scaled = self._scaler.transform(vec.reshape(1, -1))
    
    # 3. Prédiction LightGBM
    proba = self._model.predict_proba(vec_scaled)[0]
    
    return {
        "concentration": round(float(proba[0]), 4),
        "stress":        round(float(proba[1]), 4),
        "state":         "concentration" if proba[0] > proba[1] else "stress",
        "confidence":    round(float(max(proba)), 4),
        "uncertain":     bool(max(proba) < 0.60),  # seuil CdC §2.5.1
    }
```

### 4. `api.py` — endpoint fichier offline

Pour l'analyse de fichiers EEG offline (.edf/.csv/.txt), `file_processor.py` réutilise le même pipeline :

```
Fichier EEG (brut)
     │
     ▼  read_edf() ou read_csv_txt()
     │
     ▼  _adapt_signal() : resample → 250 Hz + mirror padding si < 1000 éch.
     │
     ▼  FilterBank(250).filter_epoch() : Golden Filter zero-phase
     │
     ▼  z-score époque
     │
     ▼  extract_all_features() : 63 features
     │
     ▼  MLClassifier.predict_from_dict()
     │
     ▼  JSON { epochs[], summary{} }
```

---

## Performances du classifieur

| Validation | Metric | Score |
|-----------|--------|-------|
| LOSO (leave-one-subject-out) | Accuracy | documentée dans `models/baseline_FeatEng/` |
| Seuil d'incertitude | confidence < 0.60 → `uncertain=True` | CdC NeuroCap §2.5.1 |

La validation LOSO est la méthode la plus rigoureuse pour les classificateurs EEG : elle garantit que le modèle n'a jamais vu les données du sujet de test pendant l'entraînement, ce qui évite le "sujet-leakage" observé avec la cross-validation k-fold classique.

---

## Références

1. **Higuchi, T.** (1988). Approach to an irregular time series on the basis of the fractal theory. *Physica D*, 31(2), 277–283.
2. **Hjorth, B.** (1970). EEG analysis based on time domain properties. *EEG Clin. Neurophysiol.*, 29(3), 306–310.
3. **Pincus, S.M.** (1991). Approximate entropy as a measure of system complexity. *PNAS*, 88(6), 2297–2301.
4. **Richman, J.S. & Moorman, J.R.** (2000). Physiological time-series analysis using approximate entropy and sample entropy. *Am. J. Physiol.*, 278(6), H2039–H2049.
5. **Bandt, C. & Pompe, B.** (2002). Permutation entropy: A natural complexity measure for time series. *PRL*, 88(17), 174102.
6. **Multiresolution Analysis in EEG Signal Feature Engineering** (2018) — DWT-db4 classification.
7. **NeuroFeat** (2025) — textural features, 99.22% accuracy.
8. **QuadTPat** — Cambay et al. (2024), *Scientific Reports* — transition patterns pour détection stress, 73.63% LOSO.
9. **Salam, I.** (2026) — TAR significatif p<0.001 entre concentration et stress.
10. **Samsa & Altıntop** (2026) — Hjorth features + RF, 86.25% accuracy.
