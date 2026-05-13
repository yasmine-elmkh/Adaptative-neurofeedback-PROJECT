# Dossier `Preprocessing` – Pipeline de prétraitement EEG monocanal pour NeuroCap

Ce dossier contient le pipeline complet de prétraitement du signal EEG pour le canal **Fp2** (frontale droite) avec référence mastoïde (M1/M2), adapté au **hardware NeuroCap** (AD8232 + ESP32).  
Il transforme le signal brut (synthétique ou réel) en **époques normalisées** et **features** exploitables par les classifieurs (baseline et deep learning).

---

## Table des matières

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Arborescence du dossier](#2-arborescence-du-dossier)
3. [Paramètres matériels intégrés](#3-paramètres-matériels-intégrés)
4. [Script principal : `pipeline_fp2.py`](#4-script-principal--pipeline_fp2py)
   - 4.1 [Génération d’un signal synthétique (`make_signal`)](#41-génération-dun-signal-synthétique-make_signal)
   - 4.2 [Étapes du prétraitement (filtres, DWT, segmentation, z‑score, features)](#42-étapes-du-prétraitement-filtres-dwt-segmentation-zscore-features)
   - 4.3 [Fonctions de visualisation (8 figures)](#43-fonctions-de-visualisation-8-figures)
5. [Utilisation](#5-utilisation)
   - 5.1 [Test sur signal synthétique](#51-test-sur-signal-synthétique)
   - 5.2 [Traitement de données réelles (CSV hardware)](#52-traitement-de-données-réelles-csv-hardware)
6. [Description détaillée des figures générées](#6-description-détaillée-des-figures-générées)
   - Figure 0 – Signal brut Fp2
   - Figure 1 – Filtrage complet (HP, LP, notch)
   - Figure 2 – Suppression d’artéfacts par DWT
   - Figure 3 – Segmentation (epochs et rejet)
   - Figure 4 – Normalisation z‑score par époque
   - Figure 5 – Extraction des features
   - Figure 6 – Comparaison des états cognitifs
   - Figure 7 – Diagramme du pipeline
7. [Compatibilité avec le hardware NeuroCap](#7-compatibilité-avec-le-hardware-neurocap)
8. [Justifications scientifiques et références](#8-justifications-scientifiques-et-références)
9. [Sorties générées et réutilisation](#9-sorties-générées-et-réutilisation)
10. [Dépendances](#10-dépendances)

---

## 1. Contexte et objectifs

NeuroCap utilise un casque EEG à **une seule électrode active Fp2** (référence M1/M2). Le signal acquis par l’ESP32 à 250 Hz subit un filtrage temps réel (HP 0,5 Hz, LP 40 Hz, notch 50 Hz).  
Ce pipeline **offline** effectue un prétraitement plus poussé pour l’entraînement des modèles :

- Applique les mêmes filtres que le hardware (pour cohérence).
- Supprime les artéfacts résiduels par **transformée en ondelettes discrète (DWT)** – alternative à l’ICA (impossible sur un seul canal).
- Segmente le signal en époques de **4 s** avec **75 % d’overlap** (pas = 1 s) → flux temps réel.
- Rejette les époques dont l’amplitude crête‑à‑crête dépasse **500 µV** (seuil adapté au bruit AD8232).
- Normalise chaque époque par **z‑score** (µ=0, σ=1) pour effacer les variations inter‑sessions.
- Extrait **15 features** (spectrales, ratios, Hjorth, features légères) prêtes pour la classification.

Le pipeline respecte le budget de latence du cahier des charges : prétraitement <150 ms, extraction <40 ms.

---

## 2. Arborescence du dossier

Preprocessing/
├── pipeline_fp2.py # Script principal (toutes les étapes)
├── outputs_hardware_compatible/ # Dossier créé automatiquement
│ ├── 00_signal_brut_fp2.png
│ ├── 01_filtrage_complet.png
│ ├── 02_DWT_artefacts.png
│ ├── 03_segmentation.png
│ ├── 04_zscore_normalisation.png
│ ├── 05_features_extraites.png
│ ├── 06_comparaison_etats.png
│ └── 07_pipeline_diagram.png
└── README.md # Ce fichier


---

## 3. Paramètres matériels intégrés

| Paramètre | Valeur | Justification |
|-----------|--------|----------------|
| Fréquence d’échantillonnage | 250 Hz | Identique à l’ESP32 |
| Durée d’epoch | 4 s | Fenêtre d’analyse hardware |
| Overlap | 75 % (step = 250 éch.) | Flux 1 epoch/seconde |
| Seuil de rejet | 500 µV | Adapté au bruit AD8232 (10‑20 µV RMS) |
| Filtre HP | 0,5 Hz, Butterworth ordre 4, zéro‑phase | Élimine la dérive continue |
| Filtre LP | 40 Hz, Butterworth ordre 4, zéro‑phase | Supprime EMG (>40 Hz) |
| Notch | 50 Hz, Q=30 | Élimine le bruit du réseau marocain |
| DWT | db4 (Daubechies 4), niveau 4, seuillage doux | Alternative à l’ICA (monocanal) |

---

## 4. Script principal : `pipeline_fp2.py`

### 4.1 Génération d’un signal synthétique (`make_signal`)

Pour tester et visualiser sans casque réel, la fonction `make_signal(state, dur=20)` produit un signal EEG réaliste contenant :

- Sinusoïdes aux fréquences caractéristiques (δ, θ, α, β, γ) avec amplitudes dépendant de l’état (`concentration`, `stress`, `relaxation`).
- Bruit blanc (capteur AD8232).
- Artefacts EMG (impulsions brèves de 35 µV).
- Clignements oculaires (fenêtre de Hanning, amplitude 120‑200 µV) – typiques sur Fp2.
- Bruit secteur 50 Hz.

### 4.2 Étapes du prétraitement (filtres, DWT, segmentation, z‑score, features)

Les fonctions implémentent chaque étape :

- `step2_highpass` / `step3_lowpass` / `step4_notch` : filtres Butterworth zéro‑phase (identique hardware).
- `step5_dwt` : suppression d’artéfacts par ondelettes (seuillage doux de Donoho‑Johnstone).
- `step6_reject` : marque les échantillons dépassant le seuil.
- `step7_segment` : découpage en fenêtres glissantes (4 s, 75 % overlap, fenêtre de Hann).
- `step8_zscore` : normalisation (µ=0, σ=1) par époque.
- `step9_features` : extraction des 15 features :
  - Puissances spectrales : δ, θ, α, β, γ (par PSD Welch, nperseg=256, fenêtre Hann).
  - Ratios : TBR (θ/β), ABR (α/β), EI (β/(α+θ)), TAR (θ/α).
  - Hjorth : Activité, Mobilité, Complexité.
  - Features légères : Power, MeanAmp, RelEnergy (β/total).

La fonction `preprocess_signal(sig, apply_dwt=True)` applique la chaîne complète à un tableau numpy et retourne `(epochs_norm, statuses, features_list)`.

### 4.3 Fonctions de visualisation (8 figures)

Chaque figure est une validation visuelle d’une étape clé. Elles sont sauvegardées dans `outputs_hardware_compatible/`.

---

## 5. Utilisation

### 5.1 Test sur signal synthétique

Lancez simplement le script pour générer les 8 figures (état concentration par défaut) :

```bash
python Preprocessing/pipeline_fp2.py

Vous pouvez changer l’état :
from pipeline_fp2 import run_pipeline
run_pipeline(state='stress')          # 'stress' ou 'relaxation'
```


## 6. Description détaillée des figures générées
**Figure 0 – 00_signal_brut_fp2.png**
Contenu : signal brut (avec artefacts : clignements, EMG, 50 Hz) et sa PSD. Le seuil de rejet ±500 µV est matérialisé.

Utilité : visualise la pollution initiale et vérifie la présence du pic 50 Hz.

**Figure 1 – 01_filtrage_complet.png**
Contenu : 4 lignes (brut, HP 0,5 Hz, LP 40 Hz, notch 50 Hz) ; chaque ligne montre le signal temporel et la PSD.

Utilité : vérifie que les filtres suppriment la dérive, l’EMG et le secteur sans distorsion de phase.

**Figure 2 – 02_DWT_artefacts.png**
Contenu : signal avant/après DWT, PSD superposées, coefficients de l’ondelette, différence = artefacts supprimés.

Utilité : prouve que la DWT élimine les pics de clignements et EMG tout en préservant le contenu spectral.

**Figure 3 – 03_segmentation.png**
Contenu : signal avec superposition des fenêtres d’epoch (vert = valide, rouge = rejeté), superposition des 8 premières époques, histogramme des amplitudes maximales, statistiques.

Utilité : valide les paramètres de segmentation (4 s, overlap 75 %) et le seuil de rejet (500 µV).

**Figure 4 – 04_zscore_normalisation.png**
Contenu : époques brutes vs normalisées, distributions des moyennes / écarts‑types, SNR par époque, tableau récapitulatif.

Utilité : montre que la normalisation ramène chaque époque à µ=0, σ=1 sans modifier le SNR.

**Figure 5 – 05_features_extraites.png**
Contenu : puissances par bande, ratios (TBR, EI, TAR), évolution temporelle de TBR/EI, paramètres Hjorth, features légères, tableau récapitulatif.

Utilité : vérifie que les features correspondent aux signatures EEG théoriques (ex : concentration → TBR<0,8, EI>0,7).

**Figure 6 – 06_comparaison_etats.png**
Contenu : comparaison des 3 états (concentration, stress, relaxation) : signaux temporels, PSD superposées, puissances par bande, ratios, tableau des signatures.

Utilité : démontre que le pipeline discrimine bien les états cognitifs conformément au cahier des charges.

**Figure 7 – 07_pipeline_diagram.png**
Contenu : schéma bloc des 12 étapes, avec références bibliographiques et budget de latence.

Utilité : documentation visuelle pour les rapports et présentations.

## 7. Compatibilité avec le hardware NeuroCap
Tous les paramètres critiques (filtres, durée d’epoch, overlap, seuil de rejet) sont alignés sur le firmware ESP32.
La DWT est optionnelle (non présente en temps réel) mais améliore la qualité pour l’entraînement offline.
Lors de l’inférence en temps réel, on appliquera seulement les filtres + segmentation + z‑score + features (pas de DWT pour respecter la latence).


## 8. Justifications scientifiques et références
Chaque étape est appuyée par des articles récents :

Étape	Référence
Filtre HP 0,5 Hz	Chaudhary 2025 (PREP-1)
Filtre LP 40 Hz	Acharya 2021 (PREP-2) ; Gaikwad 2017
Notch 50 Hz Q=30	Cahier des charges NeuroCap ; Gaikwad 2017
DWT db4 + seuillage	Gaikwad & Paithane 2017 (N°3) – validée sur Fp1/Fp2/Fpz
Overlap 75 %	Acharya 2021 (flux continu)
Z‑score par époque	Chaudhary 2025 ; Mynoddin 2025 (Brain2Vec)
Features (TBR, EI, etc.)	Cahier des charges Sec. 2.3 ; Samsa 2026 ; Salam 2026
ICA non applicable	Matrice sous‑déterminée sur monocanal (nécessite ≥4 canaux)
## 9. Sorties générées et réutilisation
Époques normalisées (epochs_norm) : peuvent être sauvegardées sous forme de tableau numpy pour l’entraînement des réseaux de neurones (EEGNet, TCN).

Features : directement utilisables pour les classifieurs classiques (SVM, Random Forest, XGBoost). Le script extract_features_for_baseline.py (dossier baselines) lit d’ailleurs les époques brutes et calcule ces mêmes features.

Figures : intégrables dans les rapports techniques.


## Mainteneur : Yasmine El Mkhantar – Easy Medical Device (2025-2026)
### Encadrement : Monir El Azzouzi, Loubna El Rhali, Yassir Matrane
## Version : 1.0 – conforme au cahier des charges NeuroCap (sections 2.1, 2.2, 2.3, 5.5)