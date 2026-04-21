# Validation des Datasets EEG – Canal Fp2 (NeuroCap)
# EEG Datasets Validation – Fp2 Channel (NeuroCap)

---

## version english

### Overview

This folder contains the **validation pipeline** for the two EEG datasets used in the NeuroCap project. The goal is to verify the integrity, signal quality, and compatibility of the raw data with the final hardware (single active electrode Fp2, reference M2, ground M1). Validation includes extracting the Fp2 channel, detecting artifacts, computing spectral metrics, and generating diagnostic figures.

### Datasets Validated

| Dataset | Reference | Subjects | Channels (incl. Fp2) | Sample Rate | Tasks |
|---------|-----------|----------|----------------------|-------------|-------|
| **Concentration** (Cognitive Load) | Nirabi et al., 2024 | 15 | 8 | 250 Hz | Arithmetic / Stroop (4 load levels) |
| **Stress** (SAM40) | Ghosh et al., 2021 | 40 | 32 | 128 Hz | Arithmetic / Stroop / Mirror image (3 trials) |

### Features

- **Fp2 channel extraction** from multi‑channel recordings (`.txt` for concentration, `.mat` for stress)
- **ADC → µV conversion** (OpenBCI scale factor)
- **Artifact audit** – peak‑to‑peak, HF ratio, flat channel, saturation
- **Resampling** (128 Hz → 250 Hz) for SAM40
- **Visualisation suite** – time series, PSD (log/linear), histograms, band powers, cross‑subject PSD
- **Stress label loading** from `scales.xls` (self‑reported scores 1‑10)

### Project Structure
Validate_datasets/
├── outputs_concentration_fp2/ # Generated figures for concentration dataset
├── outputs_stress_fp2/ # Generated figures for stress dataset
├── utils/ # Shared utility functions (eeg_utils.py)
├── validate_data/ # Validation scripts
│ ├── validate_concentration.py
│ └── validate_stress.py
├── init.py
└── README.md # This file

text

### Installation & Dependencies

Make sure you are in the project root (where `requirements.txt` is located). Then:

```bash 
pip install -r requirements.txt
The datasets must be placed in the following relative paths:

text
../Dataset/Cognitive Load Assessment Concentration/raw_data/
../Dataset/Stress_dataset/raw_data/
../Dataset/Stress_dataset/scales.xls
Running the Validation
1. Validate Concentration Dataset
bash
python -m validate_data.validate_concentration
2. Validate Stress Dataset
bash
python -m validate_data.validate_stress
Both scripts print artifact metrics to the console and save figures into the respective outputs_* folders.

Output Figures – Interpretation
Concentration (11 figures)
File	Content	Utility
01_timeseries_arithmetic_fp2_s1.png	Fp2 time series (Arithmetic, 10 s)	Visual artifact check
02_timeseries_stroop_fp2_s1.png	Same for Stroop	Cross‑task comparison
03_psd_arithmetic_fp2_s1.png	PSD per load level (Arithmetic)	Spectral discrimination (alpha ↓ with load)
04_psd_stroop_fp2_s1.png	PSD per load level (Stroop)	Reproducibility
05_histogram_arithmetic_fp2_s1.png	Amplitude histogram (Arithmetic)	Detects non‑stationarity
06_histogram_stroop_fp2_s1.png	Amplitude histogram (Stroop)	Symmetry, saturation
07_psd_natural_vs_high_fp2_s1.png	Natural vs highload PSD overlay	Alpha biomarker visualisation
08_all_channels_natural_fp2_s1.png	All 8 channels (Fp2 in red)	Justifies Fp2 choice
09_band_power_arithmetic_fp2_s1.png	Band powers δ,θ,α,β,γ (Arithmetic)	Spectral quantification
010_band_power_stroop_fp2_s1.png	Same for Stroop	Reproducibility
11_cross_subject_psd_fp2_arithmetic.png	PSD of 5 subjects (natural)	Inter‑subject variability → need fine‑tuning
Stress (10 figures)
File	Content	Utility
01_timeseries_raw_fp2_s1_t1.png	Raw 128 Hz signal	Ocular artifacts detection (large peaks)
02_timeseries_resampled_fp2_s1_t1.png	After resampling 250 Hz	Signal preservation check
03_psd_raw_fp2_s1_t1.png	PSD raw 128 Hz	Mains 50 Hz noise identification
04_psd_resampled_fp2_s1_t1.png	PSD after resampling	No spectral distortion
05_histogram_fp2_s1_t1.png	Amplitude histogram (raw)	Asymmetry due to DC offset
06_all_channels_arithmetic_fp2_s1.png	All 32 channels (Fp2 in red)	Spatial comparison
07_resample_check_fp2_s1_t1.png	PSD overlay 128 vs 250 Hz	Resampling validation
08_band_power_128Hz_raw_fp2_s1.png	Band powers (raw)	Baseline before filtering
09_band_power_250Hz_resampled_fp2_s1.png	Band powers (resampled)	Robustness check
10_cross_subject_psd_fp2.png	PSD of 5 subjects (Arithmetic)	Inter‑subject variability
Key Conclusions from Validation
Fp2 is usable – contains expected EEG rhythms (alpha, beta, theta).

Ocular artifacts present on SAM40 → requires DWT soft‑thresholding (ICA not possible on single channel).

DC offset on SAM40 → will be removed by 0.5 Hz high‑pass filter.

High inter‑subject variability → justifies individual fine‑tuning after calibration.

500 ms window compatible with <500 ms latency required by the specification.

Integration with the Rest of the Project
The validation outputs guide the preprocessing pipeline (Preprocessing/) and the augmentation pipeline (Augmentation/). Figures serve as traceable reference for reproducibility.

Authors
Scripts & analysis: Yasmine El Mkhantar
Supervisors: Monir El AZZOUZI, Loubna EL RHALI, Yassir MATRANE
Project: NeuroCap – Easy Medical Device (2025–2026)

License
Code and documentation: MIT License.
Datasets are subject to their own licenses (CC BY 4.0 for SAM40, specific terms for Cognitive Load dataset).

version francais
Vue d'ensemble
Ce dossier contient la pipeline de validation des deux jeux de données EEG utilisés dans le projet NeuroCap. L’objectif est de vérifier l’intégrité, la qualité du signal et la compatibilité avec le matériel final (électrode active unique Fp2, référence M2, masse M1). La validation comprend l’extraction du canal Fp2, la détection d’artefacts, le calcul de métriques spectrales et la génération de figures de diagnostic.

Datasets validés
Dataset	Référence	Sujets	Canaux (dont Fp2)	Fréquence	Tâches
Concentration (Cognitive Load)	Nirabi et al., 2024	15	8	250 Hz	Arithmétique / Stroop (4 niveaux)
Stress (SAM40)	Ghosh et al., 2021	40	32	128 Hz	Arithmétique / Stroop / Miroir (3 essais)
Fonctionnalités
Extraction du canal Fp2 depuis des enregistrements multi‑canaux (.txt pour concentration, .mat pour stress)

Conversion ADC → µV (facteur OpenBCI)

Audit d’artefacts – amplitude crête‑à‑crête, ratio haute fréquence, canal plat, saturation

Rééchantillonnage (128 Hz → 250 Hz) pour SAM40

Suite de visualisation – séries temporelles, PSD (log/linéaire), histogrammes, puissances par bande, PSD inter‑sujets

Chargement des labels de stress depuis scales.xls (scores auto‑rapportés de 1 à 10)

Structure du dossier
text
Validate_datasets/
├── outputs_concentration_fp2/      # Figures générées pour le dataset Concentration
├── outputs_stress_fp2/             # Figures générées pour le dataset Stress
├── utils/                          # Fonctions partagées (eeg_utils.py)
├── validate_data/                  # Scripts de validation
│   ├── validate_concentration.py
│   └── validate_stress.py
├── __init__.py
└── README.md                       # Ce fichier
Installation et dépendances
Assurez‑vous d’être à la racine du projet (où se trouve requirements.txt). Ensuite :

bash
pip install -r requirements.txt
Les datasets doivent être placés dans les chemins relatifs suivants :

text
../Dataset/Cognitive Load Assessment Concentration/raw_data/
../Dataset/Stress_dataset/raw_data/
../Dataset/Stress_dataset/scales.xls
Exécution de la validation
1. Valider le dataset Concentration
bash
python -m validate_data.validate_concentration
2. Valider le dataset Stress
bash
python -m validate_data.validate_stress
Les deux scripts affichent les métriques d’artefacts dans la console et enregistrent les figures dans les dossiers outputs_* respectifs.

Figures de sortie – Interprétation
Concentration (11 fichiers)
Fichier	Contenu	Utilité
01_timeseries_arithmetic_fp2_s1.png	Série temporelle Fp2 (Arithmetic, 10 s)	Contrôle visuel des artefacts
02_timeseries_stroop_fp2_s1.png	Idem pour Stroop	Comparaison inter‑tâches
03_psd_arithmetic_fp2_s1.png	PSD par niveau (Arithmetic)	Discrimination spectrale (alpha ↓ avec charge)
04_psd_stroop_fp2_s1.png	PSD par niveau (Stroop)	Reproductibilité
05_histogram_arithmetic_fp2_s1.png	Histogramme d’amplitude (Arithmetic)	Détection de non‑stationnarité
06_histogram_stroop_fp2_s1.png	Histogramme (Stroop)	Symétrie, saturation
07_psd_natural_vs_high_fp2_s1.png	Superposition natural vs highlevel	Visualisation du biomarqueur alpha
08_all_channels_natural_fp2_s1.png	Tous les 8 canaux (Fp2 en rouge)	Justification du choix Fp2
09_band_power_arithmetic_fp2_s1.png	Puissances δ,θ,α,β,γ (Arithmetic)	Quantification spectrale
010_band_power_stroop_fp2_s1.png	Idem pour Stroop	Reproductibilité
11_cross_subject_psd_fp2_arithmetic.png	PSD de 5 sujets (natural)	Variabilité inter‑individuelle → nécessité fine‑tuning
Stress (10 fichiers)
Fichier	Contenu	Utilité
01_timeseries_raw_fp2_s1_t1.png	Signal brut 128 Hz	Détection des artefacts oculaires (pics amples)
02_timeseries_resampled_fp2_s1_t1.png	Après rééchantillonnage 250 Hz	Vérification de la conservation du signal
03_psd_raw_fp2_s1_t1.png	PSD brut 128 Hz	Identification du bruit secteur 50 Hz
04_psd_resampled_fp2_s1_t1.png	PSD après rééchantillonnage	Absence de distorsion spectrale
05_histogram_fp2_s1_t1.png	Histogramme d’amplitude (brut)	Asymétrie due à l’offset continu
06_all_channels_arithmetic_fp2_s1.png	Tous les 32 canaux (Fp2 en rouge)	Comparaison spatiale
07_resample_check_fp2_s1_t1.png	Superposition PSD 128 vs 250 Hz	Validation du rééchantillonnage
08_band_power_128Hz_raw_fp2_s1.png	Puissances par bande (brut)	Baseline avant filtrage
09_band_power_250Hz_resampled_fp2_s1.png	Puissances après rééchantillonnage	Robustesse
10_cross_subject_psd_fp2.png	PSD de 5 sujets (Arithmetic)	Variabilité inter‑individuelle
Conclusions clés de la validation
Fp2 est utilisable – les signaux contiennent les rythmes EEG attendus (alpha, beta, theta).

Artefacts oculaires importants sur SAM40 → nécessite un seuillage doux par DWT (ICA impossible en mono‑canal).

Offset continu sur SAM40 → sera supprimé par un filtre passe‑haut 0,5 Hz.

Forte variabilité inter‑sujets → justifie un fine‑tuning individuel après calibration.

Fenêtre de 500 ms compatible avec la latence < 500 ms imposée par le cahier des charges.

Intégration dans le reste du projet
Les résultats de la validation guident la pipeline de prétraitement (Preprocessing/) et la pipeline d’augmentation (Augmentation/). Les figures servent de référence traçable pour la reproductibilité.

Auteurs
Scripts et analyses : Yasmine El Mkhantar
Encadrement : Monir El AZZOUZI, Loubna EL RHALI, Yassir MATRANE
Projet : NeuroCap – Easy Medical Device (2025–2026)

Licence
Code et documentation : Licence MIT.
Les datasets sont soumis à leurs propres licences (CC BY 4.0 pour SAM40, conditions spécifiques pour Cognitive Load).
