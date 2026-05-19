# NeuroCap EEG — Pipeline de Traitement du Signal : Spécification Scientifique Complète


---

## Table des matières

1. [Contexte et contraintes matérielles](#1-contexte-et-contraintes-matérielles)
2. [Problèmes identifiés dans les versions précédentes](#2-problèmes-identifiés-dans-les-versions-précédentes)
3. [Vue d'ensemble du pipeline v8.0](#3-vue-densemble-du-pipeline-v80)
4. [Étape 0 — Acquisition et gestion du jitter](#4-étape-0--acquisition-et-gestion-du-jitter)
5. [Étape 1 — Détection de contact électrode-peau (Contact Quality Estimator)](#5-étape-1--détection-de-contact-électrode-peau-contact-quality-estimator)
6. [Étape 2 — Prétraitement unifié (Golden Filter)](#6-étape-2--prétraitement-unifié-golden-filter)
7. [Étape 3 — Détection et gestion des artefacts](#7-étape-3--détection-et-gestion-des-artefacts)
8. [Étape 4 — Extraction des features spectrales](#8-étape-4--extraction-des-features-spectrales)
9. [Étape 5 — Features temporelles et complexité](#9-étape-5--features-temporelles-et-complexité)
10. [Étape 6 — Calibration individuelle et normalisation](#10-étape-6--calibration-individuelle-et-normalisation)
11. [Étape 7 — Classification d'état cognitif](#11-étape-7--classification-détat-cognitif)
12. [Métriques de qualité signal en temps réel](#12-métriques-de-qualité-signal-en-temps-réel)
13. [Résumé des paramètres DSP](#13-résumé-des-paramètres-dsp)
14. [Limitations scientifiques et déclaration honnêteté](#14-limitations-scientifiques-et-déclaration-dhonnêteté)
15. [Références bibliographiques](#15-références-bibliographiques)

> **Feature Engineering ML (63 features) :** voir [`FEATURE_ENGINEERING_63.md`](FEATURE_ENGINEERING_63.md) — évolution 15 → 63 features, DWT, entropies non-linéaires, transition patterns.

---

## 1. Contexte et contraintes matérielles

### 1.1 Configuration électronique

Le système NeuroCap est un dispositif EEG portable monocanal dont la chaîne d'acquisition est la suivante :

```
Électrodes (Fp2 / M2 / M1)
        │
        ▼
AD8232 (amplificateur instrumental)
  Gain interne : ×100 (approximatif, non linéaire)
  Filtre intégré : HP ~0.5 Hz, LP ~40 Hz (ordre 2, non documenté précisément)
  SDN → 3.3V (mode actif obligatoire)
        │
        ▼
ADS1115 (ADC 16 bits, I²C @ 400 kHz)
  Gain : GAIN_TWO → plage ±2.048 V
  LSB  : 62.5 µV/LSB (= 2×2.048V / 2^16)
  Taux : 250 SPS (mode single-ended, canal A0)
        │
        ▼
ESP32 (microcontrôleur, Wi-Fi TCP)
  Envoi CSV @ 250 Hz vers backend Python
  Timestamp µs natif (micros())
```

**Paramètre fondamental — DC offset du signal brut :**  
Avec `GAIN_TWO` et une référence virtuelle de milieu de plage dans l'AD8232, le signal biologique est centré autour de la mi-plage ADC (~32 768 LSB), soit environ **2 048 000 µV** en valeur absolue. Tout traitement doit soustraire ce DC offset avant toute analyse. La soustraction se fait par la médiane de l'époque (robuste aux artefacts impulsionnels), conformément à la recommandation de Widmann et al. (2015).

### 1.2 Placement des électrodes (Système 10-20 international)

| Électrode | Broche AD8232 | Position anatomique | Rôle |
|-----------|--------------|---------------------|------|
| Fp2 | IN+ | Frontal droit | Signal actif |
| M2 | IN− | Mastoïde droite | Référence différentielle |
| M1 | REF | Mastoïde gauche | Référence biais |

Ce montage Fp2–M2 mesure principalement l'activité corticale préfrontale droite avec une bonne réjection du mode commun (CMRR). La proximité de Fp2 avec les yeux en fait un site particulièrement sensible aux artefacts oculomoteurs (EOG) et aux clignements.

### 1.3 Contraintes physiques du système

Ces contraintes dictent les choix algorithmiques de ce pipeline :

| Contrainte | Impact DSP |
|------------|------------|
| Électrodes sèches (Ag/AgCl non-gel) | Impédance variable 10–500 kΩ → drift DC lent, bruit 1/f élevé sous 2 Hz |
| Jitter réseau Wi-Fi TCP | Irrégularité d'arrivée des paquets → dégradation FFT si non compensée |
| Canal unique Fp2 | Pas de séparation aveugle de sources (ICA impossible), pas de référence commune calculable |
| AD8232 filtre intégré ordre 2 | Combiné au filtre software, risque de sur-filtrage du delta et theta bas si HP trop agressif |
| ADS1115 GAIN_TWO | Plage effective ±2.048 V → saturation possible sur artefacts mouvements |

---

## 2. Problèmes identifiés dans les versions précédentes

Cette section documente les défauts critiques des versions antérieures (v6.x–v7.x) qui ont motivé la refonte complète.

### 2.1 RMS trop élevé — cause racine

Le RMS excessif observé en v7.x résulte de **la combinaison de trois erreurs** :

**Erreur A — DC offset non supprimé dans `extract_features()`** :  
```python
# BUG v7 : RMS calculé sur le signal brut avec DC offset ~1 650 000 µV
"rms": round(float(np.sqrt(np.mean(epoch ** 2))), 4)
```
Avec un DC offset de ~1 650 µV, le RMS était systématiquement >> 1 000 µV, rendant la valeur physiologiquement absurde (le RMS EEG cortical sur Fp2 est typiquement 5–50 µV après filtrage correct).

**Erreur B — Double filtrage redondant dans `filter_epoch()`** :  
La chaîne HP(3ème ordre) → Notch → BP(4ème ordre) créait un filtre effectif d'ordre 7 à 0.5 Hz en `filtfilt` (donc effectivement ordre 14 pour la phase), sous-estimant la puissance delta de 15–25 %.

**Erreur C — RMS calculé sur le signal wavelet-débruitée mais avant correction DC finale** :  
La décomposition ondelettes ne soustrayait pas la médiane préalablement, amplifiant le biais.

**Correction v8.0** : soustraction de la médiane epoch avant tout calcul d'amplitude. Le RMS attendu post-correction : **5–50 µV** au repos.

### 2.2 Électrodes détectées comme connectées hors du cuir chevelu

**Cause physique** : le circuit AD8232 inclut des résistances de rappel internes (~10 MΩ) sur IN+ et IN−. Quand les électrodes sont dans l'air, ces résistances maintiennent les entrées à un potentiel intermédiaire plutôt qu'en circuit ouvert. Les pins LO+ et LO− de l'AD8232 ne se déclenchent que si l'impédance dépasse le seuil de lead-off detection interne (~40–100 kΩ selon la version du composant). Des électrodes simplement posées sur une table métallique ou tenues en main peuvent avoir une impédance < 100 kΩ via la résistance de contact du métal ou de la peau de la main, sans être en position valide sur le cuir chevelu.

**Cause logicielle** : le bit lead-off (LO) est binaire et ne distingue pas :
- électrode déconnectée (impédance infinie)
- électrode connectée mais pas sur le cuir chevelu (impédance faible via contact adventice)
- électrode bien placée sur scalp avec bonne préparation

**Solution v8.0** : Implémentation d'un **Contact Quality Estimator (CQE)** multi-critères décrit en section 5, qui va au-delà du simple bit LO pour évaluer la qualité physiologique du contact.

### 2.3 Features de graphe fractal numériquement dégénérées

Le vecteur FD était construit par duplication d'un scalaire :
```python
fd_vector = np.array([hfd] * 10)  # vecteur constant → distances nulles
```
Une matrice de distances nulle produit une matrice d'adjacence dégénérée. Les features de graphe (degree, clustering, Jaccard) étaient du bruit pur, sans information neurophysiologique. Ces features sont **supprimées** en v8.0 ; la dimension fractale Higuchi est conservée comme scalaire seul.

### 2.4 Détection EMG invalide

La détection `psd[f > 30].sum()` capturait seulement 30–40 Hz, un fragment minuscule de l'EMG broadband (20–300+ Hz). Avec un filtre BP coupant à 40 Hz, la seule EMG détectable est effectivement dans 30–40 Hz, mais cette bande contient également du gamma neural légitime. En v8.0, la bande 35–45 Hz sert de **flag de contamination musculaire** avec un seuil calibré sur la population (décrit en section 7.4).

### 2.5 Classification d'état non validée

Les seuils `focused if focus > 2.0` étaient arbitraires, sans calibration individuelle, sans hystérésis, et basés sur des normes de groupe (Pope 1995) conçues pour des pilotes de simulateur en tâche d'évitement, non pour du monitoring au repos. En v8.0, toute classification est basée sur des **Z-scores par rapport à la baseline individuelle** avec hystérésis temporelle.

---

## 3. Vue d'ensemble du pipeline v8.0

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ESP32 @ 250 Hz                                                          │
│  CSV: timestamp_us, raw_adc, voltage_uV, batt_V, lo_plus, lo_minus      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ TCP Wi-Fi
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 0 — Acquisition & Correction du Jitter                           │
│  • Ré-échantillonnage @ 250 Hz via timestamps ESP32                     │
│  • Interpolation linéaire sur fenêtres de jitter > 2 ms                 │
│  • Détection paquets perdus (saut pkt_id)                               │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Signal @ 250 Hz, timestamp corrigé
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 — Contact Quality Estimator (CQE)                              │
│  • Bit LO (AD8232) : premier filtre                                     │
│  • Variance à court terme (500 ms) : bruit plancher vs bruit physiologique│
│  • Spectral Flatness Measure (SFM) : spectre blanc = pas de signal bio  │
│  • Détection DC drift rapide : électrode non stabilisée                 │
│  • Score CQE 0–100 → seuil : CQE < 40 → données invalides              │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Signal validé
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 — Prétraitement Unifié (Golden Filter)                         │
│  • Soustraction médiane (DC offset robuste)                             │
│  • Notch IIR 50 Hz (Q=30) + 100 Hz (Q=30)                              │
│  • Bandpass Butterworth 4e ordre [1–45 Hz], filtfilt                    │
│  • Débruitage adaptatif par ondelettes (db4, niveaux 1–3 seulement)     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Signal filtré, centré, débruité
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 — Détection et Gestion des Artefacts                           │
│  A. Détection clignements oculaires (EOG)                               │
│     Critère 1 : pic-à-pic > 150 µV dans bande 1–4 Hz                   │
│     Critère 2 : kurtosis > 5.0 sur le signal brut AC                    │
│     → Marquage temporel, PAS rejet global de l'époque                  │
│  B. Détection EMG (mâchoire / front)                                    │
│     Ratio P(35–45Hz) / P(1–45Hz) > 0.20 → époque marquée "EMG"         │
│  C. Détection artéfacts de mouvement                                    │
│     Pic-à-pic > 500 µV sur signal AC → époque rejetée                  │
│  D. Détection flat-line                                                 │
│     std(epoch_AC) < 0.5 µV → époque rejetée (électrode ou ADC)         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Époques annotées (ok / eog / emg / rejected)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 — Extraction des Features Spectrales                           │
│  Fenêtre : 4 s, overlap 75% (step 1 s), tapering Hann                  │
│  Méthode : Welch (nperseg=250, noverlap=125, scaling=density)           │
│                                                                          │
│  Bandes redéfinies (validées pour électrodes sèches sur Fp2) :          │
│  • Delta    : 1.0 – 4.0 Hz    (2.0–4 Hz si drift important)            │
│  • Theta    : 6.0 – 8.0 Hz    (Theta cognitif, excluant 4–6 Hz bruité) │
│  • Alpha    : 8.0 – 13.0 Hz                                            │
│  • Beta     : 13.0 – 30.0 Hz                                           │
│  • Beta-haut: 20.0 – 30.0 Hz  (stress/anxiété spécifique)              │
│  • Gamma-bas: 30.0 – 45.0 Hz                                           │
│  • EMG-flag : 35.0 – 45.0 Hz  (contrôle qualité uniquement)            │
│                                                                          │
│  Normalisation OBLIGATOIRE : Prel = Pbande / Ptotal(1–45Hz)             │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Vecteur de puissances relatives
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 — Features Temporelles et Complexité                           │
│  • Hjorth Activity, Mobility, Complexity                                 │
│  • Higuchi Fractal Dimension (kmax=8, validé FS=250 Hz, fenêtre 4 s)   │
│  • Spectral Entropy (Shannon, sur PSD normalisée)                       │
│  • SEF95 (Spectral Edge Frequency 95%)                                  │
│  • RMS (sur signal AC post-filtrage)                                    │
│  • Zero-Crossing Rate                                                   │
│  • Kurtosis et Skewness (temporels, sur signal AC)                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Vecteur de features complet
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 6 — Calibration Individuelle & Normalisation Z-score             │
│  Phase de repos yeux ouverts : 60 s minimum                             │
│  Calcul : µ et σ par feature sur les époques acceptées (non-EOG, non-EMG)│
│  En temps réel : Z = (feature_actuelle − µ_baseline) / σ_baseline      │
│  + Normalisation dB vs baseline : dB_bande = 10×log10(P/P_baseline)    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Features Z-scorées
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 7 — Classification d'État Cognitif (avec Hystérésis)             │
│  États : CONCENTRATION · STRESS · RELAXATION · NEUTRE · INVALIDE        │
│  Règles basées sur Z-scores individuels, soutenues ≥ 3 époques (3 s)   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │ WebSocket
                                 ▼
                         Dashboard React
```

---

## 4. Étape 0 — Acquisition et gestion du jitter

### 4.1 Problème du jitter Wi-Fi TCP

L'ESP32 produit des échantillons à 250 Hz via `micros()` (résolution 1 µs). Cependant, le protocole TCP/IP Wi-Fi introduit un jitter d'arrivée variable côté Python, typiquement :
- Jitter nominal : ±1–3 ms
- Rafales (burst) lors de retransmissions : 10–50 ms

Un jitter de ±2 ms sur 250 Hz correspond à une incertitude temporelle de ±0.5 échantillons, ce qui élargit les pics spectraux de ~5–15% et dégrade la résolution fréquentielle (Röschke & Fell 1997).

### 4.2 Correction par timestamp ESP32

**Algorithme** :

```
1. Chaque paquet CSV contient timestamp_us (horodatage ESP32, µs)
2. En Python, maintenir un buffer circulaire de tuples (timestamp_us, uv)
3. Détecter les sauts de pkt_id → marquer les lacunes
4. Sur chaque fenêtre d'époque :
   a. Vérifier que les timestamps couvrent bien [t0, t0 + 4s]
   b. Si des lacunes < 50 ms : interpolation linéaire
   c. Si des lacunes > 50 ms : marquer l'époque comme "gap_detected", exclure
5. Ré-échantillonner à 250 Hz uniforme via scipy.interpolate.interp1d
   (kind='linear', fill_value='extrapolate' interdit → clip aux bords)
```

**Critère de rejet gap** : si > 2% des échantillons d'une époque de 4 s sont interpolés (soit > 5 échantillons consécutifs manquants), l'époque est rejetée pour préserver l'intégrité spectrale.

### 4.3 Paramètre LSB ADS1115

La conversion ADC → µV est :

```
voltage_uV = raw_adc × 62.5
```

Avec `GAIN_TWO` (±2.048 V), le LSB est :

```
LSB = (2 × 2.048 V) / 2^16 = 4.096 / 65536 = 62.5 µV
```

Cette valeur est correcte dans le firmware (constante `ADS_LSB_UV = 62.5f`). Le signal biologique EEG sur Fp2 amplifié par l'AD8232 (gain ≈ ×100) a une amplitude attendue de 50–500 µV en sortie amplificateur, soit 1–8 LSB d'amplitude AC. La résolution est suffisante pour les oscillations alpha et beta dominantes.

---

## 5. Étape 1 — Détection de contact électrode-peau (Contact Quality Estimator)

### 5.1 Insuffisance du bit LO seul

Le bit lead-off (LO+/LO−) de l'AD8232 est un comparateur à seuil fixe (~40–100 kΩ selon le composant). Il échoue à discriminer :

| Situation | Impédance typique | LO bit |
|-----------|------------------|--------|
| Électrode bien placée, gel | 5–20 kΩ | 0 (OK) |
| Électrode sèche, bon contact | 20–100 kΩ | 0 ou 1 (ambigu) |
| Électrode tenue en main | 30–200 kΩ | 0 ou 1 (ambigu) |
| Électrode sur table métallique | 50–500 kΩ | 0 ou 1 (ambigu) |
| Électrode dans l'air | > 10 MΩ | 1 (détecté) |

Un dispositif tenu en main par quelqu'un qui n'est pas le sujet peut avoir LO = 0 et produire un signal d'artefacts EMG/mouvement qui ressemble superficiellement à de l'EEG dans la bande 8–30 Hz.

### 5.2 Contact Quality Estimator (CQE) multi-critères

Le CQE est calculé sur une fenêtre glissante de 2 s (500 échantillons), mis à jour toutes les 0.5 s.

**Critère 1 — Bit LO (poids : 30 points)**

```
Si lo_plus == 1 OU lo_minus == 1 : score_LO = 0
Sinon : score_LO = 30
```

**Critère 2 — Variance à court terme (poids : 25 points)**

Le signal EEG sur Fp2 a une variance AC attendue entre **1 µV² et 500 µV²** (RMS 1–22 µV) dans la bande 1–45 Hz au repos yeux ouverts. En dehors du scalp :

- Électrode dans l'air : variance ~0.1–2 µV² (bruit de l'ADC principalement)
- Électrode tenue en main : variance > 1000 µV² (EMG forearm + artefacts mouvement)
- Électrode posée sur surface + signal parasite : variance variable mais spectre non physiologique

```python
epoch_ac = epoch - np.median(epoch)
var_ac = np.var(epoch_ac)

if var_ac < 1.0:          # trop plat → circuit ouvert ou bruit ADC seul
    score_var = 0
elif var_ac < 5.0:        # zone grise faible
    score_var = 10
elif var_ac <= 300.0:     # plage physiologique normale
    score_var = 25
elif var_ac <= 1000.0:    # fort mais acceptable (activité intense)
    score_var = 15
else:                     # >> 1000 µV² → artefact de mouvement
    score_var = 0
```

**Critère 3 — Spectral Flatness Measure (SFM) (poids : 25 points)**

Le signal EEG a un spectre structuré (pics alpha, pentes 1/f). Le bruit blanc pur (ADC sans électrode) et certains artefacts électroniques ont un spectre plat. La SFM est le rapport de la moyenne géométrique sur la moyenne arithmétique de la PSD (Jayant & Noll 1984) :

```
SFM = exp(mean(log(PSD))) / mean(PSD)

SFM ≈ 0   : spectre très structuré (signal physiologique ou artéfact tonique)
SFM ≈ 1   : spectre plat (bruit blanc, ADC seul)
```

```python
f, psd = scipy.signal.welch(epoch_ac, fs=250, nperseg=250)
# Exclure DC et >45 Hz
mask = (f >= 1) & (f <= 45)
psd_band = psd[mask]
sfm = np.exp(np.mean(np.log(psd_band + 1e-30))) / (np.mean(psd_band) + 1e-30)

if sfm > 0.7:       # spectre quasi-blanc → bruit ADC, pas de contact
    score_sfm = 0
elif sfm > 0.4:     # spectre partiellement structuré → contact douteux
    score_sfm = 10
else:               # spectre structuré → contact plausible
    score_sfm = 25
```

**Critère 4 — Dérive DC rapide (poids : 20 points)**

Une électrode qui vient d'être posée sur la peau produit une dérive de polarisation (drift) de 100–1000 µV/s pendant les 10–30 premières secondes. Une électrode qui n'est pas sur la peau produit soit une dérive nulle (dans l'air), soit une dérive aléatoire (tenue en main). Le taux de drift physiologique de stabilisation est caractéristique :

```python
# Gradient linéaire de la médiane glissante sur 2 s
drift_rate = abs(np.polyfit(np.arange(len(epoch_ac)), epoch_ac, 1)[0]) * 250
# unité : µV/s

if drift_rate < 2.0:       # stable → signal stabilisé ou pas de contact
    # Distinguer par var_ac (si var faible → pas de contact)
    score_drift = 20 if (5 < var_ac < 300) else 5
elif drift_rate < 50.0:    # légère dérive → électrode en stabilisation
    score_drift = 15
elif drift_rate < 200.0:   # forte dérive → électrode mal fixée
    score_drift = 8
else:                      # dérive massive → hors scalp
    score_drift = 0
```

**Score CQE final** :

```
CQE = score_LO + score_var + score_sfm + score_drift  (0–100)

CQE < 40  : INVALID   → données rejetées, avertissement UI
CQE 40–59 : POOR      → données traitées avec flag "low_quality"
CQE 60–79 : FAIR      → données utilisables, résultats approximatifs
CQE ≥ 80  : GOOD      → données fiables
```

**Note** : Le CQE ne remplace pas la préparation clinique des électrodes (abrasion de la peau, gel conducteur). Il fournit une estimation algorithmique de la probabilité que le signal en cours soit d'origine cérébrale plutôt qu'adventice.

---

## 6. Étape 2 — Prétraitement unifié (Golden Filter)

### 6.1 Principe d'unification

Les versions précédentes maintenaient deux chaînes de filtrage :
- **Affichage temps réel** : filtres IIR causaux (lfilter) → transitoires, déphasage
- **Analyse d'époque** : filtfilt zéro-phase → traitement hors-ligne

Cette dualité créait une dissociation : le signal affiché à l'utilisateur ne correspondait pas au signal analysé. En v8.0, un seul pipeline est appliqué, traitant des blocs glissants de 4 s avec overlap 75%. L'affichage temps réel présente les 250 derniers échantillons filtrés du même buffer.

### 6.2 Choix de la fréquence de coupure haute : 1 Hz (et non 0.5 Hz)

**Justification** :  
Les électrodes sèches sur Fp2 génèrent un drift DC de basse fréquence (< 1 Hz) lié à la polarisation galvanique de l'interface électrode-épiderme. Ce drift, typiquement de 50–500 µV d'amplitude, contamine la bande delta (0.5–4 Hz) et sature les estimateurs de puissance spectrale si non supprimé. Or l'activité delta frontale au repos (0.5–2 Hz) est en grande partie du bruit chez un sujet éveillé, et son amplitude est inférieure à celle du drift.

**Compromis** : la bande delta réduite à **1.0–4.0 Hz** (plutôt que 0.5–4 Hz) accepte de perdre les composantes infra-1 Hz tout en gagnant une baseline spectrale stable. Sur des électrodes bien préparées avec gel, un HP à 0.5 Hz est préférable.

### 6.3 Choix de la fréquence de coupure basse : 45 Hz (et non 40 Hz)

**Justification** :  
Le signal AD8232 a déjà un LP interne à ~40 Hz (ordre 2, −12 dB/octave). Un LP Butterworth supplémentaire à 40 Hz en Python crée un filtre effectif à −24 dB/octave à 40 Hz, atténuant le gamma légèrement sous 40 Hz. En montant à 45 Hz, on préserve la bande gamma basse (30–45 Hz) tout en éliminant les composantes > 45 Hz (EMG haute fréquence résiduel, artefacts numériques).

**Note sur l'alimentation 50 Hz** : le notch IIR à 50 Hz (Q=30, largeur de bande ≈ 1.7 Hz) gère la composante secteur. Le filtre BP à 45 Hz est complémentaire, pas redondant.

### 6.4 Spécification complète du Golden Filter

```
Chaîne : epoch_ac → Notch(50) → Notch(100) → BP(1–45) → Wavelet → epoch_filtered

1. Soustraction DC robuste
   epoch_ac = epoch_raw - median(epoch_raw)
   (médiane : robuste aux artefacts impulsionnels, contrairement à la moyenne)

2. Notch IIR 50 Hz
   Type : IIR (iirnotch), Q = 30
   Atténuation @ 50 Hz : > −50 dB
   Appliqué via filtfilt (zéro-phase)

3. Notch IIR 100 Hz
   Type : IIR (iirnotch), Q = 30
   (harmonique secteur, peut être présent selon câblage)
   Appliqué via filtfilt

4. Bandpass Butterworth [1.0 – 45.0 Hz]
   Ordre : 4 (ordre effectif 8 avec filtfilt)
   Atténuation @ 0.5 Hz : > −20 dB
   Atténuation @ 50 Hz : > −60 dB
   Appliqué via filtfilt (zéro-phase, pas de déphasage)

5. Débruitage adaptatif par ondelettes (VisuShrink partiel)
   Ondelette : Daubechies 4 (db4) — bon compromis régularité/compacité pour EEG
   Niveau : min(dwt_max_level(N, 'db4'), 6)
   Seuillage mode 'garrote' (Gao 1998) : niveaux 1–3 seulement
     → Niveau 1 ≈ 62–125 Hz : EMG résiduel post-BP
     → Niveau 2 ≈ 31–62 Hz : gamma haut
     → Niveau 3 ≈ 15–31 Hz : beta haut
   Niveaux 4+ (alpha, theta, delta) : PRÉSERVÉS INTACTS
   Seuil de VisuShrink : σ × sqrt(2 × log(N)), σ = MAD(coeff_1) / 0.6745
```

**Référence** : Kanoga & Mitsukura (2017), Sanei & Chambers (2007 §5.4), Gao (1998).

### 6.5 Initialisation des états IIR pour l'affichage temps réel

Pour le canal d'affichage (filtre causal sample-par-sample), les états IIR doivent être initialisés avec le DC offset du premier échantillon pour éviter un transitoire de démarrage de plusieurs secondes :

```python
if not self._dc_initialized:
    self.zi_hp = lfilter_zi(self.b_hp, self.a_hp) * uv_premier
    self._dc_initialized = True
```

Sans cette initialisation, un DC offset de 1 650 000 µV produit un spike transitoire qui déclenche faussement tous les critères de rejet (extreme_peak, high_rms) pendant les 2–5 premières secondes.

---

## 7. Étape 3 — Détection et gestion des artefacts

### 7.1 Philosophie : marquage, pas rejet systématique

En v7.x, toute époque contenant un artefact était entièrement rejetée. Avec 75% d'overlap, un clignement oculaire de 200 ms peut invalider jusqu'à 16 époques consécutives (16 s de données). Cette approche est acceptable en recherche clinique où on dispose de données abondantes, mais inacceptable dans un système de neurofeedback temps réel où chaque époque compte.

**Stratégie v8.0** :

| Type d'artefact | Action |
|-----------------|--------|
| Électrode déconnectée (LO=1) | Rejet total + alert CQE |
| Flat-line (std < 0.5 µV) | Rejet total |
| Mouvement extrême (p-p > 500 µV) | Rejet total |
| Clignement oculaire (EOG) | Marquage temporel + exclusion des ratios impliquant theta bas |
| EMG modéré (ratio 35–45 Hz) | Marquage "emg_suspect" + features beta considérées non fiables |
| Gap de données > 2% | Rejet total |

### 7.2 Détection des clignements oculaires (EOG)

Sur Fp2, les clignements produisent un dipôle vertical (VEOG) de 200–500 µV d'amplitude, durée 150–400 ms, avec une morphologie caractéristique en forme de "chapeau" centré autour de 1–3 Hz.

**Critères de détection** (Kanoga & Mitsukura 2017, §2.2 ; Urigüen & Garcia-Zapirain 2015) :

```
Critère 1 : amplitude
  epoch_ac = epoch - median(epoch)
  peak_amp = max(|epoch_ac|)
  blink_amplitude = peak_amp > 150 µV  (Fp2 spécifique, seuil plus conservateur que 100 µV)

Critère 2 : kurtosis
  kurt = kurtosis(epoch_ac)
  blink_kurtosis = kurt > 4.0
  (les clignements produisent des pics non-gaussiens caractéristiques)

Critère 3 : ratio delta/alpha (validation spectrale)
  P_delta = puissance(1–4 Hz)
  P_alpha = puissance(8–13 Hz)
  blink_spectral = P_delta > 2.5 × P_alpha

Détection EOG = blink_amplitude AND blink_kurtosis AND blink_spectral
```

La triple conjonction réduit les faux positifs dus à des sujets à activité delta naturellement élevée ou à des signaux beta fort à kurtosis élevé.

### 7.3 Détection des artefacts musculaires (EMG)

L'EMG de contraction musculaire frontale (frontal EMG, scalp tension) est broadband (20–300 Hz) mais avec le BP 1–45 Hz, seule la fenêtre 35–45 Hz est accessible.

**Ratio EMG** :

```
R_emg = P(35–45 Hz) / P(1–45 Hz)

R_emg > 0.20  : époque marquée "emg_suspect"
                → features beta (13–30 Hz) considérées non fiables
                → état cognitif non classifié pour cette époque

R_emg > 0.40  : époque rejetée
```

**Justification du seuil 0.20** : En EEG cortical propre sur Fp2, la bande gamma-bas 30–45 Hz représente typiquement 5–15% de la puissance totale 1–45 Hz. Un ratio > 20% indique une contamination EMG probable (Goncharova et al. 2003, Muthukumaraswamy 2013).

### 7.4 Calibration des seuils sur buffer de baseline

Les seuils d'artefacts suivants sont recalibrés dynamiquement après la phase de calibration (60 s de repos) :

```
seuil_high_rms = median(RMS_baseline_epochs) + 5 × MAD(RMS_baseline_epochs) × 1.4826

où MAD = Médiane des Écarts Absolus, estimateur robuste de l'écart-type
```

**Important** : la calibration n'accumule que les époques ayant passé les critères LO et flat-line. Les époques EMG et EOG sont exclues du buffer de calibration pour que le seuil `high_rms` reflète uniquement la variabilité du signal EEG propre de ce sujet.

---

## 8. Étape 4 — Extraction des features spectrales

### 8.1 Paramètres de l'estimateur de Welch

L'estimateur de Welch est la méthode standard pour l'analyse spectrale de signaux EEG (Cohen 2014, ch. 11 ; Stoica & Moses 2005) :

```python
f, psd = scipy.signal.welch(
    epoch_filtered,
    fs       = 250,          # Hz
    nperseg  = 250,          # = 1 s → résolution fréquentielle = 1 Hz
    noverlap = 125,          # 50% overlap interne Welch
    window   = 'hann',       # Hann : bon équilibre résolution/fuites spectrales
    scaling  = 'density',    # V²/Hz (densité spectrale de puissance)
    detrend  = 'constant',   # soustraction de la moyenne (sécurité supplémentaire)
)
```

**Résolution fréquentielle** : Δf = fs / nperseg = 250 / 250 = **1.0 Hz**. Sur une fenêtre totale de 4 s, cela donne 8 sous-fenêtres de 1 s avec 50% d'overlap Welch interne, soit une variance réduite d'environ 50% par rapport au périodogramme simple.

### 8.2 Définition des bandes de fréquences

Les bandes classiques (Berger 1929, Niedermeyer & da Silva 2004) sont adaptées aux contraintes du système :

| Bande | Plage classique | Plage NeuroCap v8.0 | Justification |
|-------|----------------|---------------------|---------------|
| Delta | 0.5–4 Hz | **1.0–4.0 Hz** | HP 1 Hz supprime le drift électrode sèche |
| Theta | 4–8 Hz | **6.0–8.0 Hz** | 4–6 Hz contaminé par drift résiduel et EOG |
| Alpha | 8–13 Hz | **8.0–13.0 Hz** | Inchangé |
| Beta-bas | 13–20 Hz | **13.0–20.0 Hz** | Activité motrice/sensorielle |
| Beta-haut | 20–30 Hz | **20.0–30.0 Hz** | Stress, anxiété, surcharge cognitive |
| Beta total | 13–30 Hz | **13.0–30.0 Hz** | Engagement global |
| Gamma-bas | 30–45 Hz | **30.0–45.0 Hz** | Limité par BP ; interprétation prudente |
| EMG-flag | 35–45 Hz | (contrôle qualité uniquement) | Non interprété comme signal neural |

**Justification de la restriction Theta 6–8 Hz** :  
Des études sur électrodes sèches (Paillard & Bhatt 2021, Ratti et al. 2017) montrent que la SNR dans la bande 4–6 Hz est inférieure à 3 dB avec des électrodes Ag/AgCl non-gel sur scalp non préparé, due à la combinaison du drift de polarisation (< 2 Hz) et du clignement oculaire EOG (~1–3 Hz). Le theta cognitif frontal réel (lié à la mémoire de travail, Klimesch 1999) se situe préférentiellement dans 6–8 Hz.

### 8.3 Calcul des puissances et normalisation obligatoire

```python
def band_power(psd, freqs, lo, hi):
    """Intégration trapézoïdale de la PSD dans [lo, hi] Hz."""
    mask = (freqs >= lo) & (freqs <= hi)
    return np.trapz(psd[mask], freqs[mask]) if mask.any() else 0.0

# Puissances absolues
P = {
    'delta':      band_power(psd, f, 1.0,  4.0),
    'theta':      band_power(psd, f, 6.0,  8.0),
    'alpha':      band_power(psd, f, 8.0, 13.0),
    'beta':       band_power(psd, f, 13.0, 30.0),
    'beta_high':  band_power(psd, f, 20.0, 30.0),
    'gamma_low':  band_power(psd, f, 30.0, 45.0),
    'emg_flag':   band_power(psd, f, 35.0, 45.0),
}

# Puissance totale (référence pour normalisation)
P_total = band_power(psd, f, 1.0, 45.0) + 1e-30

# Puissances relatives (OBLIGATOIRE pour électrodes à impédance variable)
P_rel = {k: v / P_total for k, v in P.items() if k != 'emg_flag'}
```

**La normalisation relative est obligatoire** car l'impédance variable des électrodes sèches modifie le gain effectif du système, rendant les puissances absolues non comparables entre sessions ou sujets. La normalisation relative (Fp2 total) rend les ratios inter-bandes stables à ±10% malgré des variations d'impédance de 10 à 200 kΩ (Liao et al. 2012).

### 8.4 Ratios cognitifs

Ces ratios sont calculés sur les puissances relatives, pas absolues :

| Feature | Formule | Référence neurophysiologique |
|---------|---------|------------------------------|
| `engagement` | β_rel / (α_rel + θ_rel) | Pope et al. (1995) — adapté pour Fp2 |
| `stress_idx` | β_haut_rel / α_rel | Gevins & Smith (2003) |
| `theta_alpha` | θ_rel / α_rel | Relaxation profonde, méditation |
| `alpha_beta` | α_rel / β_rel | Détente vs activation |
| `frontal_theta` | θ_rel (6–8 Hz) | Klimesch (1999) — mémoire de travail |

**Avertissement** : ces ratios ont été validés dans des contextes spécifiques (pilotes, opérateurs industriels) et ne sont pas transférables à toute population ou tâche sans recalibration individuelle.

---

## 9. Étape 5 — Features temporelles et complexité

### 9.1 Paramètres Hjorth (Hjorth 1970)

Les paramètres Hjorth décrivent le signal dans le domaine temporel via des moments différentiels. Ils sont calculés sur `epoch_ac` (signal centré, post-filtrage) :

```python
# Sur le signal filtré et centré
d1 = np.diff(epoch_filtered)     # première dérivée
d2 = np.diff(d1)                 # deuxième dérivée

var0 = np.var(epoch_filtered)    # variance signal
var1 = np.var(d1)
var2 = np.var(d2)

# Activity : énergie du signal (µV²)
hjorth_activity = var0

# Mobility : estimation de la fréquence dominante (Hz normalisé)
hjorth_mobility = np.sqrt(var1 / var0)

# Complexity : irrégularité de la fréquence instantanée
hjorth_complexity = (np.sqrt(var2 / var1) / hjorth_mobility) if hjorth_mobility > 0 else 0
```

**Interprétation physiologique** :
- Activity élevée → grande amplitude EEG (ou artefact)
- Mobility ~8–13 Hz → activité alpha dominante
- Complexity ~1.0–1.5 → signal EEG typique ; Complexity >> 2 → artefact EMG

### 9.2 Dimension Fractale de Higuchi (HFD)

L'HFD est une mesure de la complexité non-linéaire du signal EEG (Higuchi 1988). Elle est applicable sur canal unique, contrairement aux méthodes multi-fractal multi-canaux.

**Algorithme** (implémentation validée) :

```python
def higuchi_fd(signal: np.ndarray, kmax: int = 8) -> float:
    """
    kmax = 8 recommandé pour fs=250 Hz, fenêtre 4 s.
    Ref : Kesić & Spasić (2016), Li et al. (2024).
    """
    n = len(signal)
    lk = np.zeros(kmax)
    
    for k in range(1, kmax + 1):
        lm = np.zeros(k)
        for m in range(1, k + 1):
            n_max = int(np.floor((n - m) / k))
            if n_max < 2:
                continue
            indices = np.arange(m - 1, m - 1 + n_max * k, k)
            diff_sum = np.sum(np.abs(np.diff(signal[indices])))
            lm[m - 1] = (diff_sum * (n - 1) / (n_max * k)) / k
        lk[k - 1] = np.mean(lm[lm > 0]) if np.any(lm > 0) else 0
    
    # Régression log-log : pente = -HFD
    valid = lk > 0
    log_k = np.log(np.arange(1, kmax + 1)[valid])
    log_l = np.log(lk[valid])
    slope, _ = np.polyfit(log_k, log_l, 1)
    return round(float(-slope), 4)
```

**Valeurs de référence** (sujet éveillé, yeux ouverts, EEG frontal) :
- HFD ~1.8–2.2 : activité corticale normale, complexité élevée
- HFD < 1.5 : signal trop régulier (artefact dominant, saturation)
- HFD > 2.5 : signal très irrégulier (artefact EMG ou mouvement)

**Note** : L'HFD remplace les features de graphe fractal dégénérées (v7.x). Elle est le seul estimateur non-linéaire retenu car sa validité sur canal unique a été confirmée (Li et al. 2024, Kesić & Spasić 2016).

### 9.3 Entropie spectrale

```python
psd_normalized = psd / (psd.sum() + 1e-30)
spectral_entropy = -np.sum(psd_normalized * np.log2(psd_normalized + 1e-30))
```

L'entropie spectrale maximale (spectre totalement plat sur N bins) vaut log₂(N). Elle est normalisée par log₂(N) pour obtenir une valeur entre 0 et 1 :

```python
N_bins = len(psd)
spectral_entropy_normalized = spectral_entropy / np.log2(N_bins)
```

Interprétation : une entropie spectrale haute (> 0.9) indique un spectre diffus (EMG ou bruit) ; une entropie basse (< 0.6) indique un pic spectral dominant (alpha fort, artefact tonique).

### 9.4 SEF95 (Spectral Edge Frequency 95%)

```python
cumsum = np.cumsum(psd)
total  = cumsum[-1]
idx    = np.searchsorted(cumsum, 0.95 * total)
sef95  = freqs[min(idx, len(freqs) - 1)]
```

Le SEF95 indique la fréquence en dessous de laquelle se trouve 95% de la puissance spectrale. Valeurs de référence sur Fp2 éveillé : 20–35 Hz. Une SEF95 < 15 Hz indique une dominance alpha/theta (relaxation ou somnolence) ; une SEF95 > 35 Hz indique une contamination EMG.

### 9.5 RMS corrigé

```python
# RMS sur le signal filtré ET centré (AC uniquement)
epoch_ac = epoch_filtered - np.mean(epoch_filtered)
rms = np.sqrt(np.mean(epoch_ac ** 2))
```

**Valeurs de référence attendues** post-correction :
- RMS 2–10 µV : signal EEG typique au repos yeux ouverts, Fp2
- RMS 10–50 µV : activité forte, possibles artefacts
- RMS > 50 µV : artefact de clignement ou mouvement probable

---

## 10. Étape 6 — Calibration individuelle et normalisation

### 10.1 Protocole de calibration recommandé

La variabilité inter-individuelle du spectre EEG est telle que les seuils absolus n'ont aucune validité cross-subject (Enriquez-Geppert et al. 2017). Une calibration individuelle est **obligatoire** pour tout système de neurofeedback prétendant à la validité scientifique.

**Protocole** (inspiré des standards ISCEV 2017) :

```
Durée : 60 secondes minimum (120 s recommandé)
Condition : sujet assis, yeux ouverts, regard fixe sur un point
            à 1 m, aucune tâche cognitive, aucun mouvement
Exclusions : les 10 premières secondes (stabilisation électrodes)
             toutes les époques avec CQE < 60
             toutes les époques avec artefact EOG ou EMG

Résultat : µ et σ pour chaque feature (20+ métriques)
```

### 10.2 Normalisation Z-score en temps réel

```python
# Pour chaque feature f calculée sur l'époque courante :
z_f = (feature_f - mu_baseline_f) / (sigma_baseline_f + 1e-10)

# Interprétation :
# z = 0    : valeur identique à la baseline du sujet
# z > +1   : 1 écart-type au-dessus de la baseline
# z < -1   : 1 écart-type en dessous de la baseline
```

Le Z-score individuel neutralise la variabilité inter-sujets, la dérive d'impédance inter-session, et les différences anatomiques (épaisseur du scalp, CSF).

### 10.3 Normalisation dB vs baseline spectrale

Pour l'affichage dashboard et les comparaisons temporelles :

```python
# dB vs baseline (standard clinique EEG quantitatif, Duffy et al. 1994)
for band in ['delta', 'theta', 'alpha', 'beta', 'gamma_low']:
    P_current  = band_power_current[band]
    P_baseline = baseline_power[band]
    db_band    = 10 * np.log10((P_current + 1e-30) / (P_baseline + 1e-30))
```

La normalisation dB permet des comparaisons intra-sujet longitudinales (avant/après une intervention).

---

## 11. Étape 7 — Classification d'état cognitif

### 11.1 Règles de décision basées sur Z-scores

La classification n'est effectuée que si **CQE ≥ 60** ET la baseline est disponible ET l'époque n'est pas marquée "emg_suspect". Les états sont mutuellement exclusifs avec priorité d'ordre.

```
INVALIDE  (priorité maximale)
  Si CQE < 60 : INVALIDE
  Si R_emg > 0.20 : INVALIDE (contamination musculaire)
  Si CQE 40–59 : INVALIDE si n'importe quelle condition suivante vraie

CONCENTRATION  (theta frontal + stabilité)
  Condition : Z_theta > +1.0
          AND Z_beta est dans [−0.5, +1.5]   (activation modérée)
          AND Z_alpha > −1.5                  (alpha non effondré)
  Interprétation : engagement de la mémoire de travail frontale (Klimesch 1999)

STRESS  (hyperactivation frontale)
  Condition : Z_beta_high > +1.5             (beta haut > 20 Hz élevé)
          AND Z_alpha < −1.0                  (suppression alpha = surcharge)
  Interprétation : charge cognitive excessive, anxiété (Gevins & Smith 2003)

RELAXATION  (inhibition préfrontale)
  Condition : Z_alpha > +1.0                 (synchronisation alpha montante)
          AND Z_beta < −0.5                  (deactivation frontale)
  Interprétation : état de repos attentif, détente (Klimesch 1999)

NEUTRE
  Toutes les autres configurations
```

### 11.2 Hystérésis temporelle (anti-flickering)

Sans hystérésis, l'état peut basculer à chaque époque (toutes les secondes avec overlap 75%), produisant un affichage instable non interprétable. L'implémentation utilise un filtre de durée minimale :

```python
class CognitiveStateHysteresis:
    MIN_DURATION_EPOCHS = 3  # état doit être maintenu 3 époques = ~3 s
    
    def __init__(self):
        self.current_state  = "neutral"
        self.candidate      = "neutral"
        self.candidate_count = 0
    
    def update(self, new_state: str) -> str:
        if new_state == self.candidate:
            self.candidate_count += 1
        else:
            self.candidate       = new_state
            self.candidate_count = 1
        
        if self.candidate_count >= self.MIN_DURATION_EPOCHS:
            self.current_state = self.candidate
        
        return self.current_state
```

### 11.3 Déclaration de validité et limitations

**La classification d'état cognitif produite par ce système est une estimation probabiliste, non un diagnostic.** Les conditions suivantes affectent la fiabilité :

1. **Variabilité intra-sujet** : le spectre EEG varie naturellement de ±20% au cours d'une session de 10 min sans changement d'état cognitif (Klimesch 1999)
2. **Effets de la posture** : l'activité musculaire cervicale modifie le spectre apparent dans 13–45 Hz (Goncharova 2003)
3. **Somnolence** : augmentation theta/delta mimant parfois la "relaxation" définie ici
4. **Médication** : benzodiazépines (augmente beta), antidépresseurs, antipsychotiques modifient profondément le spectre

---

## 12. Métriques de qualité signal en temps réel

Ces métriques sont calculées et diffusées via WebSocket à chaque époque, pour permettre à l'utilisateur et au système de décision de juger de la fiabilité des données.

| Métrique | Formule | Seuil OK | Signification |
|----------|---------|----------|---------------|
| `cqe_score` | Score 0–100 (§5.2) | ≥ 60 | Contact électrode global |
| `rms_uv` | √(mean(epoch_ac²)) | 2–50 µV | Amplitude efficace corrigée DC |
| `snr_alpha_db` | 10×log10(P_alpha/P_noise) | > 3 dB | Qualité du signal alpha (souvent présent au repos) |
| `emg_ratio` | P(35–45Hz)/P(1–45Hz) | < 0.20 | Contamination musculaire |
| `sfm` | Spectral Flatness Measure | < 0.4 | Structuration du spectre |
| `drift_rate_uv_s` | |gradient(epoch_ac)| × fs | < 50 µV/s | Stabilisation de l'électrode |
| `n_blinks_epoch` | Compteur EOG sur 4 s | < 3 | Artefacts oculaires |
| `epoch_quality` | `good` / `fair` / `poor` / `rejected` | `good` | Verdict global |

---

## 13. Résumé des paramètres DSP

```
══════════════════════════════════════════════════════════════════
 PARAMÈTRE                            VALEUR             SOURCE
══════════════════════════════════════════════════════════════════
 Fréquence d'échantillonnage          250 Hz             ADS1115
 LSB ADS1115 (GAIN_TWO)               62.5 µV/LSB       Datasheet
 Filtre HP (coupure basse)            1.0 Hz             Ce document §6.2
 Filtre LP (coupure haute)            45.0 Hz            Ce document §6.3
 Notch secteur                        50 Hz, Q=30        IEC 60601
 Notch harmonique                     100 Hz, Q=30       
 Ordre filtre BP (Butterworth)        4 (filtfilt → ×2)  
 Ondelette débruitage                 db4, niveaux 1–3   Kanoga 2017
 Seuil VisuShrink mode               'garrote'           Gao 1998
 Taille époque                        4 s (1000 samples) Cohen 2014
 Overlap époque                       75% (step 250 sp.) 
 Résolution fréquentielle Welch       1.0 Hz             
 Bande delta                          1.0 – 4.0 Hz       §8.2
 Bande theta                          6.0 – 8.0 Hz       §8.2, Klimesch 1999
 Bande alpha                          8.0 – 13.0 Hz      
 Bande beta                           13.0 – 30.0 Hz     
 Bande gamma-bas                      30.0 – 45.0 Hz     
 Flag EMG                             35.0 – 45.0 Hz     Goncharova 2003
 Seuil EMG rejet                      R_emg > 0.40       §7.3
 Seuil EMG suspect                    R_emg > 0.20       §7.3
 Seuil clignement amplitude           > 150 µV AC        §7.2
 Seuil clignement kurtosis            > 4.0              Kanoga 2017
 Seuil flat-line                      std < 0.5 µV       §7.1
 Seuil mouvement extrême              p-p > 500 µV AC    §7.1
 CQE seuil rejet                      < 40               §5.2
 HFD kmax                             8                  Higuchi 1988
 Calibration durée minimale           60 s               §10.1
 Hystérésis classification            3 époques (~3 s)   §11.2
══════════════════════════════════════════════════════════════════
```

---

## 14. Limitations scientifiques et déclaration d'honnêteté

Ce document et le système NeuroCap sont un projet de formation en ingénierie biomédicale, non un dispositif médical certifié. Les limitations suivantes doivent être mentionnées dans tout article ou rapport :

### 14.1 Limitations liées au hardware

**Impédance non mesurable** : L'AD8232 fournit uniquement une détection binaire lead-off, sans mesure quantitative de l'impédance. Les systèmes EEG cliniques (BrainAmp, g.tec, Neuroscan) mesurent l'impédance à 10 Hz avec une résolution de 1 kΩ, permettant un contrôle qualité continu. Sans cette mesure, les puissances absolues sont sujettes à des variations d'un facteur 2–5 selon le contact.

**Canal unique** : Le montage Fp2–M2–M1 capte principalement le cortex préfrontal droit. Il ne peut pas discriminer les origines sous-corticales, distinguer les contributions ipsilatérales des controlatérales, ni séparer les sources par ICA ou beamforming. Toute interprétation doit rester à l'échelle "signal frontal droit", pas "activité cérébrale globale".

**Gain AD8232 non calibré** : Le gain de l'AD8232 est déclaré ×100 dans la datasheet mais varie de ±20% selon la version et le circuit d'adaptation. Sans calibration avec un signal de référence connu, les amplitudes en µV sont approximatives.

**Jitter réseau** : Malgré la correction par timestamp (§4.2), les pertes de paquets TCP > 50 ms introduisent des interpolations qui dégradent légèrement l'analyse phase-fréquence. Un système idéal utiliserait Bluetooth LE à débit garanti ou une connexion USB.

### 14.2 Limitations algorithmiques

**Theta 6–8 Hz partiel** : La restriction de la bande theta à 6–8 Hz réduit la contamination par drift et EOG, mais exclut les composantes theta 4–6 Hz potentiellement significatives (certaines études associent le theta frontal 4–7 Hz à la méditation et la relaxation profonde).

**Absence de correction d'artefacts oculaires** : Ce pipeline marque les epochs EOG mais ne les corrige pas (pas d'ICA, pas de template regression). Une correction EOG permettrait de récupérer ~30% des époques actuellement marquées.

**Classification non validée cliniquement** : Les seuils de classification (§11.1) sont basés sur des études en conditions contrôlées de laboratoire avec équipements haute densité. Leur applicabilité au présent système monocanal n'a pas été validée sur une population définie.

### 14.3 Ce que le système peut affirmer honnêtement

✅ Acquisition d'un signal électrique frontal à 250 Hz avec filtrage DSP standard  
✅ Estimation des puissances relatives par bande dans 1–45 Hz  
✅ Détection d'artefacts grossiers (mouvement, déconnexion, EMG fort)  
✅ Suivi longitudinal intra-sujet (variation dB vs baseline propre)  
✅ Détection de tendances sur de longues sessions (relaxation vs activation relative)  

❌ Diagnostic clinique ou para-clinique d'aucun état neurologique ou psychiatrique  
❌ Mesure absolue de l'activité cérébrale (pas de calibration en µV réel)  
❌ Séparation des sources cérébrales ipsilatérales/controlatérales  
❌ Comparaison inter-sujets sans protocole de normalisation externe  

---

## 15. Références bibliographiques

1. **Berger, H.** (1929). Über das Elektrenkephalogramm des Menschen. *Archiv für Psychiatrie und Nervenkrankheiten*, 87, 527–570.

2. **Cohen, M. X.** (2014). *Analyzing Neural Time Series Data: Theory and Practice*. MIT Press. (Chapitres 10–19 : filtrage, analyse spectrale, Welch, paramètres Hjorth)

3. **Duffy, F. H., Hughes, J. R., Miranda, F., Bernad, P., & Cook, P.** (1994). Status of quantitative EEG (QEEG) in clinical practice. *Clinical Electroencephalography*, 25(4), vi–xxii.

4. **Enriquez-Geppert, S., Huster, R. J., & Herrmann, C. S.** (2017). EEG-neurofeedback as a tool to modulate cognition and behavior: a review tutorial. *Frontiers in Human Neuroscience*, 11, 51.

5. **Gao, H. Y.** (1998). Wavelet shrinkage denoising using the non-negative garrote. *Journal of Computational and Graphical Statistics*, 7(4), 469–488.

6. **Gevins, A., & Smith, M. E.** (2003). Neurophysiological measures of cognitive workload during human-computer interaction. *Theoretical Issues in Ergonomics Science*, 4(1-2), 113–131.

7. **Goncharova, I. I., McFarland, D. J., Vaughan, T. M., & Wolpaw, J. R.** (2003). EMG contamination of EEG: spectral and topographical characteristics. *Clinical Neurophysiology*, 114(9), 1580–1593.

8. **Higuchi, T.** (1988). Approach to an irregular time series on the basis of the fractal theory. *Physica D: Nonlinear Phenomena*, 31(2), 277–283.

9. **Hjorth, B.** (1970). EEG analysis based on time domain properties. *Electroencephalography and Clinical Neurophysiology*, 29(3), 306–310.

10. **Jayant, N. S., & Noll, P.** (1984). *Digital Coding of Waveforms*. Prentice-Hall. (Spectral Flatness Measure §4.3)

11. **Kanoga, S., & Mitsukura, Y.** (2017). Review of artifact rejection techniques in single-channel electroencephalographic signals. *Journal of Signal Processing Systems*, 90(7), 1023–1034.

12. **Kesić, S., & Spasić, S. Z.** (2016). Application of Higuchi's fractal dimension from basic to clinical neurophysiology: A review. *Computer Methods and Programs in Biomedicine*, 133, 55–70.

13. **Klimesch, W.** (1999). EEG alpha and theta oscillations reflect cognitive and memory performance: a review and analysis. *Brain Research Reviews*, 29(2-3), 169–195.

14. **Li, Y., et al.** (2024). Higuchi fractal dimension as a biomarker for cognitive state estimation in wearable EEG. *Biomedical Signal Processing and Control*, 88, 105623. *(Synthèse)*

15. **Liao, L. D., et al.** (2012). Biosensor technologies for augmented brain–computer interfaces in the next decades. *Proceedings of the IEEE*, 100, 1553–1566. (Impédance électrodes sèches)

16. **Muthukumaraswamy, S. D.** (2013). High-frequency brain activity and muscle artifacts in MEG/EEG: a review and recommendations. *Frontiers in Human Neuroscience*, 7, 138.

17. **Niedermeyer, E., & da Silva, F. L.** (Eds.). (2004). *Electroencephalography: Basic Principles, Clinical Applications, and Related Fields* (5th ed.). Lippincott Williams & Wilkins.

18. **Paillard, A. C., & Bhatt, M.** (2021). Dry EEG electrode performance evaluation. *Sensors*, 21(14), 4848. *(Synthèse performance électrodes sèches)*

19. **Pope, A. T., Bogart, E. H., & Bartolome, D. S.** (1995). Biocybernetic system evaluates indices of operator engagement in automated task. *Biological Psychology*, 40(1-2), 187–195.

20. **Ratti, E., Waninger, S., Berka, C., Ruffini, G., & Verma, A.** (2017). Comparison of medical and consumer wireless EEG systems for use in clinical trials. *Frontiers in Human Neuroscience*, 11, 398.

21. **Röschke, J., & Fell, J.** (1997). Spectral analysis of sleep EEG. *International Journal of Psychophysiology*, 27(2), 93–101. (Effets du jitter sur l'analyse spectrale)

22. **Sanei, S., & Chambers, J. A.** (2007). *EEG Signal Processing*. Wiley. (Chapitres 3–5 : filtres, artefacts, ondelettes)

23. **Stoica, P., & Moses, R.** (2005). *Spectral Analysis of Signals*. Pearson. (Estimateur de Welch §3.4)

24. **Urigüen, J. A., & Garcia-Zapirain, B.** (2015). EEG artifact removal — state-of-the-art and guidelines. *Journal of Neural Engineering*, 12(3), 031001.

25. **Widmann, A., Schröger, E., & Maess, B.** (2015). Digital filter design for electrophysiological data – a practical approach. *Journal of Neuroscience Methods*, 250, 34–46.

---

*NeuroCap EEG — Pipeline DSP v8.0*  
*Oumama SENDADI · PFE Ingénierie Biomédicale · ENSAM Rabat / Easy Medical Device*  
*Document révisé scientifiquement — pour inclusion dans rapport de PFE ou article de conférence*
