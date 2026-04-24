# Dossier `Augmentation` – Pipeline d’augmentation de données EEG pour NeuroCap

Ce dossier contient le pipeline complet d’**augmentation de données** pour le signal EEG monocanal **Fp2** (frontale droite, référence M1/M2), conforme au hardware NeuroCap (AD8232 + ESP32).  
L’augmentation est appliquée **uniquement sur l’ensemble d’entraînement** après une **séparation stricte par sujet**, afin d’éviter toute fuite de données inter‑sujet.

---

## Table des matières

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Architecture correcte de la pipeline](#2-architecture-correcte-de-la-pipeline)
3. [Fichier principal : `augmentation_eeg.py`](#3-fichier-principal--augmentation_eegpy)
   - 3.1 [Séparation par sujet (split_by_subject)](#31-séparation-par-sujet-split_by_subject)
   - 3.2 [Générateur LOSO (loso_generator)](#32-générateur-loso-loso_generator)
   - 3.3 [Techniques d’augmentation](#33-techniques-daugmentation)
   - 3.4 [Pipeline d’augmentation du train (`augment_train_set`)](#34-pipeline-daugmentation-du-train-augment_train_set)
   - 3.5 [Validation des ratios cognitifs](#35-validation-des-ratios-cognitifs)
   - 3.6 [Sauvegarde / chargement des datasets](#36-sauvegarde--chargement-des-datasets)
4. [Utilisation dans le projet réel](#4-utilisation-dans-le-projet-réel)
5. [Figures générées (9 schémas de validation)](#5-figures-générées-9-schémas-de-validation)
6. [Références scientifiques](#6-références-scientifiques)
7. [Dépendances](#7-dépendances)

---

## 1. Contexte et objectifs

Les jeux de données EEG (Cognitive Load Assessment : 15 sujets ; SAM40 : 40 sujets) sont de taille modeste. L’augmentation permet de :

- **Multiplier artificiellement** le nombre d’époques d’entraînement (facteurs ×2, ×3, ×4).
- **Améliorer la robustesse** aux variations naturelles (bruit capteur, impédance, fatigue cognitive).
- **Respecter la physiologie** : les transformations simulées doivent conserver les signatures EEG de concentration (TBR < 0,8, EI > 0,7) et de stress (β↑↑, α↓).

**Règles d’or** (validées par la littérature récente) :

1. **Séparer les sujets AVANT toute augmentation** – ne jamais mélanger les sujets entre train et test.
2. **Augmenter UNIQUEMENT l’ensemble d’entraînement** – validation et test restent bruts.
3. **Split par sujet** (et non par époque) pour éviter le data leakage.
4. **Magnitude warping (Exp. D) indépendant** – ne jamais le combiner avec les transformations B et C sur la même copie.

---

## 2. Architecture correcte de la pipeline

┌─────────────────────────────────────────────────────────────────────┐
│ DONNÉES COMPLÈTES (tous sujets) │
│ Signal prétraité, segmenté, z-score normalisé │
└──────────────────────────┬──────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ SÉPARATION STRICTE AVANT TOUTE AUGMENTATION │
│ • Option 1 – Split classique (70/15/15 par sujet) │
│ • Option 2 – LOSO (Leave‑One‑Subject‑Out) [recommandé] │
└──────────────────────────┬──────────────────────────────────────────┘
│
▼ (sur X_train uniquement)
┌─────────────────────────────────────────────────────────────────────┐
│ AUGMENTATION DU SET D'ENTRAÎNEMENT │
│ Exp. B : Gaussian Noise (SNR 20-30 dB) + Scaling ±10% + Time Shift│
│ Exp. C : B + DWT fréquentielle (db4, niveau 6) – α/β/θ conservés │
│ Exp. D : Magnitude Warping (déformation lente, indépendant) │
│ FULL : Orig + B + C + D │
└──────────────────────────┬──────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ SAUVEGARDE DATASETS AUGMENTÉS │
│ X_train_A.npy, X_train_B.npy, X_train_C.npy, X_train_D.npy, │
│ X_train_FULL.npy, X_val.npy, X_test.npy + labels │
└─────────────────────────────────────────────────────────────────────┘


---

## 3. Fichier principal : `augmentation_eeg.py`

Ce script contient toutes les fonctions nécessaires. Voici les plus importantes.

### 3.1 Séparation par sujet (`split_by_subject`)

```python
def split_by_subject(X, y, subject_ids, test_ratio=0.15, val_ratio=0.15, seed=42):
    """Sépare les données par sujet (évite le data leakage)."""
    # Les sujets sont assignés aléatoirement aux ensembles train/val/test.
    # Retourne X_train, y_train, X_val, y_val, X_test, y_test
```

### 3.2 Générateur LOSO (loso_generator)
def loso_generator(X, y, subject_ids):
    """Générateur pour validation Leave‑One‑Subject‑Out."""
    for fold_idx, subject_k in enumerate(unique_subjects):
        yield fold_idx, subject_k, X_train, y_train, X_test, y_test


### 3.3 Techniques d’augmentation
Fonction	Effet	Référence
aug_gaussian_noise(epoch, snr_db=25)	Ajoute bruit blanc filtré (20-30 dB), simule bruit AD8232.	IEEE TNSRE 2022
aug_scaling(epoch, factor=±10%)	Multiplie l’amplitude. Préserve TBR/EI (effet multiplicatif).	Comput. Biol. Med. 2025
aug_time_shift(epoch, shift=20 éch.)	Décalage circulaire de 80 ms.	CDC NeuroCap
aug_dwt_frequency(epoch)	DWT db4 niveau 6 ; perturbe les hautes fréquences (>31 Hz) mais conserve α, β, θ.	Knowledge‑Based Systems 2025
aug_magnitude_warping(epoch, warp_amp=0.08)	Déformation lente (0.05‑0.20 Hz) pour simuler fatigue cognitive.	Comput. Biol. Med. 2025


### 3.4 Pipeline d’augmentation du train (augment_train_set)

def augment_train_set(X_train, y_train, seed=42):
    """
    Génère les copies augmentées pour les expériences B, C, D et FULL.
    Retourne un dictionnaire datasets = {'A': (X,y), 'B': (X,y), ...}
    """

Facteurs multiplicateurs :

A : ×1 (original seul)

B : ×2 (original + basique)

C : ×3 (original + basique + DWT)

D : ×2 (original + warping)

FULL : ×4 (original + B + C + D)

3.5 Validation des ratios cognitifs (validate_augmentation)
Vérifie que les ratios TBR, ABR, EI, TAR varient de moins de ±15 % après augmentation.
Une variation >15 % indiquerait une déformation trop agressive.

3.6 Sauvegarde / chargement des datasets
save_augmented_datasets(...) : écrit les fichiers .npy dans datasets_augmented/.

load_augmented_datasets(...) : recharge ces fichiers dans un dictionnaire.

## 4. Utilisation dans le projet réel
python
from augmentation_eeg import split_by_subject, augment_train_set
from augmentation_eeg import save_augmented_datasets, load_augmented_datasets

### 1. Charger vos données réelles (ex. depuis CSV hardware ou depuis Preprocessing)
### X : shape (n_epochs, 1000), y : (n_epochs,), subject_ids : (n_epochs,)
X, y, subject_ids = load_your_data()

### 2. Séparer par sujet (OBLIGATOIRE avant augmentation)
X_train, y_train, _, X_val, y_val, _, X_test, y_test, _ = split_by_subject(
    X, y, subject_ids, test_ratio=0.15, val_ratio=0.15
)

### 3. Augmenter uniquement X_train
datasets, _, _, _ = augment_train_set(X_train, y_train)

### 4. Sauvegarder pour une utilisation ultérieure
save_augmented_datasets(datasets, X_val, y_val, X_test, y_test,
                        outdir='datasets_augmented')


## 5. Figures générées (9 schémas de validation)
Le script run_augmentation_pipeline() produit 9 figures dans Augmentation/outputs_augmentation/ :

**Figure Contenu Utilité**
**aug_01_split_overview.png**	Distribution train/val/test par sujet	Vérifie l’absence de leakage
**aug_02_loso_schema.png**	Schéma du protocole LOSO	Justification du gold standard
**aug_03_comparison_experiments.png**	Signaux temporels et PSD pour A/B/C/D/FULL	Compare visuellement chaque augmentation
**aug_04_validation_ratios.png**	TBR/EI/TAR avant/après augmentation	Vérifie que les ratios restent dans ±15%
**aug_05_dwt_bands.png**	Coefficients DWT – preuve que α/β/θ sont conservés	Validation de la DWT fréquentielle
**aug_06_magnitude_warping.png**	Effet de l’enveloppe lente (3 amplitudes)	Choix de l’amplitude ±8%
**aug_07_dataset_growth.png**	Croissance du nombre d’epochs par expérience	Facteurs multiplicatifs
**aug_08_usage_guide.png**	Schéma d’utilisation (code)	Guide visuel pour l’intégration
**aug_09_pipeline_final.png**	Diagramme complet de la pipeline Documentation pour rapports


## 6. Références scientifiques
Knowledge‑Based Systems (2025) – EEG augmentation survey (DWT, Noise, Scaling).

IEEE TNSRE (2022) – Comparative review of augmentation methods for BCI.

Computers in Biology and Medicine (2025) – Magnitude warping for fatigue simulation.

Braindecode – official transformations (Gaussian noise, time shift).

Bio‑Protocol (2023) – EEG segmentation best practices (split by subject).

CdC NeuroCap – Sections 2.4.2 (augmentation), 2.4.3 (LOSO), 2.5.1 (signatures).

Salam et al. (2026, N°15) – TAR as biomarker (p<0.001).

Samsa & Altıntop (2026, N°17) – 3 features → 86.25% accuracy.

