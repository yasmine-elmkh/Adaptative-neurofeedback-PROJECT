"""
=============================================================================
NeuroCap — Pipeline d'Augmentation EEG Monocanal Fp2 (Version Finale)
=============================================================================
Auteur      : Yasmine El Mkhantar
Encadrement : Monir El Azzouzi | Loubna El Rhali | Yassir Matrane
Structure   : Easy Medical Device — 2025-2026

ARCHITECTURE CORRECTE DE LA PIPELINE :
════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────┐
  │                   DONNÉES COMPLÈTES (tous sujets)                   │
  │              Signal prétraité, segmenté, z-score normalisé          │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │         SÉPARATION STRICTE AVANT TOUTE AUGMENTATION                 │
  │                                                                     │
  │   Option 1 — LOSO (Leave-One-Subject-Out) [RECOMMANDÉ NeuroCap]     │
  │     Pour chaque fold k ∈ {1..N_sujets} :                           │
  │       • Test  = sujet k          (JAMAIS augmenté)                  │
  │       • Train = tous les autres  (augmentés)                        │
  │                                                                     │
  │   Option 2 — Split classique (70% train / 15% val / 15% test)       │
  │       • Split par SUJET (pas par epoch) → évite data leakage        │
  │       • Augmentation UNIQUEMENT sur X_train                         │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼ (sur X_train uniquement)
  ┌─────────────────────────────────────────────────────────────────────┐
  │                 AUGMENTATION DU SET D'ENTRAÎNEMENT                  │
  │                                                                     │
  │   Étape 2 — Augmentation Basique (Exp. B)                           │
  │     2.1 Gaussian Noise   → SNR 20-30 dB, bruit filtré [0.5-40 Hz]  │
  │     2.2 Scaling          → facteur ±10 % (ratios TBR/EI invariants) │
  │     2.3 Time Shifting    → 80 ms = 20 éch. (CDC NeuroCap, np.roll)  │
  │                                                                     │
  │   Étape 3 — DWT Fréquentielle (Exp. C)                             │
  │     Basique + DWT db4 6 niveaux → HF perturbée, α/β/θ conservés     │
  │                                                                     │
  │   Étape 4 — Magnitude Warping (Exp. D) — INDÉPENDANT de B+C        │
  │     Déformation lente 0.05-0.20 Hz ±8% RMS (simulation fatigue)     │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                  SAUVEGARDE DATASETS AUGMENTÉS                      │
  │   datasets_augmented/                                               │
  │   ├── X_train_original.npy  + y_train_original.npy                 │
  │   ├── X_train_aug_B.npy     + y_train_aug_B.npy  (Exp. B)          │
  │   ├── X_train_aug_C.npy     + y_train_aug_C.npy  (Exp. C)          │
  │   ├── X_train_aug_D.npy     + y_train_aug_D.npy  (Exp. D)          │
  │   ├── X_train_aug_FULL.npy  + y_train_aug_FULL.npy                 │
  │   ├── X_val.npy             + y_val.npy  (NON augmenté)            │
  │   └── X_test.npy            + y_test.npy (NON augmenté)            │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │              VALIDATION (sur X_val / X_test — non augmentés)        │
  │                                                                     │
  │   Exp. A : entraîner sur X_train_original  → métriques baseline     │
  │   Exp. B : entraîner sur X_train_aug_B     → métriques basique      │
  │   Exp. C : entraîner sur X_train_aug_C     → métriques B+DWT        │
  │   Exp. D : entraîner sur X_train_aug_D     → métriques warping      │
  │   FULL   : entraîner sur X_train_aug_FULL  → métriques optimales    │
  └─────────────────────────────────────────────────────────────────────┘

RÈGLES ABSOLUES :
  ① Séparation AVANT augmentation (jamais après)
  ② Augmentation UNIQUEMENT sur X_train (jamais sur val/test)
  ③ Split par SUJET (jamais par epoch) → évite le data leakage inter-sujet
  ④ Magnitude Warping INDÉPENDANT de Exp. B+C (jamais combiné)
  ⑤ Valider que TBR/EI/TAR varient < ±15% après augmentation

Références scientifiques :
  - Knowledge-Based Systems (2025) — EEG augmentation survey
  - IEEE TNSRE (2022) — Comparative review augmentation methods
  - Computers in Biology and Medicine (2025) — Preprocessing + augmentation
  - Braindecode — Transformations EEG officielles
  - Bio-Protocol (2023) — EEG segmentation best practices
  - Salam et al. (2026, N°15) — TAR p<0.001
  - Samsa & Altıntop (2026, N°17) — 3 features → 86.25 %

Compatibilité hardware : AD8232 + ESP32 | fs = 250 Hz | Epoch 4 s
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from scipy import signal, interpolate
import pywt
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES GLOBALES — alignées sur le hardware NeuroCap (AD8232 + ESP32)
# ─────────────────────────────────────────────────────────────────────────────

FS            = 250       # Hz — fréquence d'échantillonnage hardware
EPOCH_S       = 4.0       # s  — durée fenêtre (identique hardware)
OVERLAP       = 0.50      # 50 % → step = 500 éch.
EPOCH_SAMPLES = int(EPOCH_S * FS)                    # = 1000 éch.
STEP          = int(EPOCH_SAMPLES * (1 - OVERLAP))   # = 500 éch.
AMP_THR       = 500.0     # µV — seuil rejet (adapté AD8232 10-20 µV RMS)
TIME_SHIFT_MS   = 80      # ms — décalage temporel (CDC NeuroCap)
TIME_SHIFT_SAMP = int(TIME_SHIFT_MS * FS / 1000)    # = 20 éch.
SCALE_MIN, SCALE_MAX = 0.90, 1.10   # ±10 % → préserve TBR/ABR/EI
WAVELET   = 'db4'   # Daubechies 4 (Gaikwad 2017)
DWT_LEVEL = 6       # 6 niveaux à 250 Hz
WARP_AMP  = 0.08    # ±8 % de l'amplitude RMS

# Palette visuelle NeuroCap
COL = dict(
    raw='#2C3E50', aug1='#E74C3C', aug2='#E67E22', aug3='#8E44AD',
    aug4='#27AE60', orig='#2980B9', dark='#1A2E5A', light='#EEF3FA',
    theta='#3498DB', alpha_c='#27AE60', beta='#E67E22',
    delta='#9B59B6', gamma='#E74C3C',
)
BAND_COLS = ['#9B59B6', '#3498DB', '#27AE60', '#E67E22', '#E74C3C']


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

def _style(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor('#FAFAFA')
    ax.grid(True, alpha=0.22, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if title:  ax.set_title(title, fontsize=9, fontweight='bold', color=COL['dark'], pad=5)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8, color='#555')
    if ylabel: ax.set_ylabel(ylabel, fontsize=8, color='#555')
    ax.tick_params(labelsize=7, colors='#555')

def _ref(ax, txt):
    ax.text(0.99, 0.02, txt, transform=ax.transAxes, fontsize=6.5,
            ha='right', va='bottom', color='#555', style='italic',
            bbox=dict(boxstyle='round,pad=0.18', facecolor='white', alpha=0.75, edgecolor='none'))

def _shade_bands(ax, fmax=45):
    limits = [(0.5,4),(4,8),(8,13),(13,30),(30,min(40,fmax))]
    for (f1,f2), c in zip(limits, BAND_COLS):
        if f1 >= fmax: break
        ax.axvspan(f1, min(f2,fmax), alpha=0.07, color=c, zorder=0)

def _psd(x, nperseg=256):
    """PSD Welch avec fenêtre de Hann — nperseg=256 pour 1000 points."""
    return signal.welch(x, FS, nperseg=nperseg, window='hann')

def _band_power(freqs, psd, flo, fhi):
    """Intégration trapézoïdale de la PSD sur [flo, fhi]."""
    idx = (freqs >= flo) & (freqs <= fhi)
    return float(np.trapezoid(psd[idx], freqs[idx])) if idx.any() else 0.0

def _compute_ratios(epoch):
    """
    Calcule les ratios cognitifs NeuroCap sur une epoch.
    CRITÈRE DE VALIDATION : ces ratios doivent rester dans ±15 % après augmentation.
    """
    f, psd = _psd(epoch)
    pt = _band_power(f, psd, 4.0,  8.0)    # θ (Theta)
    pa = _band_power(f, psd, 8.0, 13.0)    # α (Alpha)
    pb = _band_power(f, psd, 13.0, 30.0)   # β (Beta)
    return {
        'TBR': pt / (pb + 1e-12),           # Theta/Beta < 0.8 → concentration
        'ABR': pa / (pb + 1e-12),           # Alpha/Beta
        'EI' : pb / (pa + pt + 1e-12),      # Engagement Index > 0.7 → concentration
        'TAR': pt / (pa + 1e-12),           # Theta/Alpha (Salam 2026, N°15, p<0.001)
    }

def zscore_normalize(epoch):
    """
    Normalisation z-score individuelle : µ → 0, σ → 1.
    Appliquée PAR EPOCH (pas globalement) → compense variabilité inter-sujets.
    Préserve les ratios spectraux normalisés à l'intérieur d'une epoch.
    Ref : Chaudhary 2025 (PREP-1) | Mynoddin 2025 (Art. 1.5 Brain2Vec)
    """
    mu = epoch.mean()
    sigma = epoch.std()
    return (epoch - mu) / (sigma if sigma > 1e-10 else 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# GÉNÉRATION SIGNAL SYNTHÉTIQUE (démonstration / tests)
# ─────────────────────────────────────────────────────────────────────────────

def make_signal(state='concentration', dur=20, seed=42):
    """
    Signal EEG synthétique Fp2 avec signatures NeuroCap (CdC Section 2.5.1)
    et artefacts typiques du hardware AD8232.

    Signatures simulées :
      Concentration : β↑ (13-30 Hz) + TBR < 0.8 + EI > 0.7
      Stress        : β↑↑ + α↓ (FAA < -0.1, Saeed 2020 N°9)
      Relaxation    : α↑ + β↓

    Artefacts simulés (AD8232 sur Fp2) :
      • Clignements oculaires : 100-200 µV, 150 ms, 5 occurrences
      • EMG musculaires : ~35 µV RMS sur 250 ms
      • Bruit réseau 50 Hz marocain : 2 µV
      • Bruit blanc capteur : ~2.5 µV RMS
    """
    np.random.seed(seed)
    t = np.arange(0, dur, 1/FS)
    amps = {
        'concentration': dict(d=0.5, th=0.7, al=0.3, be=3.0, be2=2.5, ga=0.4),
        'stress':        dict(d=0.6, th=1.0, al=0.15,be=4.0, be2=3.5, ga=0.5),
        'relaxation':    dict(d=0.4, th=0.5, al=3.5, be=0.6, be2=0.4, ga=0.2),
    }[state]
    eeg = (amps['d']  * np.sin(2*np.pi*2*t)
         + amps['th'] * np.sin(2*np.pi*6*t)
         + amps['al'] * np.sin(2*np.pi*10*t)
         + amps['be'] * np.sin(2*np.pi*20*t)
         + amps['be2']* np.sin(2*np.pi*26*t)
         + amps['ga'] * np.sin(2*np.pi*35*t)) * 12
    eeg += np.random.randn(len(t)) * 2.5
    for _ in range(3):
        s = np.random.randint(int(0.8*FS), len(t)-int(0.8*FS))
        eeg[s:s+int(0.25*FS)] += np.random.randn(int(0.25*FS)) * 35
    for _ in range(5):
        bp = np.random.randint(int(0.5*FS), len(t)-int(0.5*FS))
        bd = int(0.15*FS)
        eeg[bp:bp+bd] += np.hanning(bd) * np.random.uniform(120, 200)
    eeg += 2.0 * np.sin(2*np.pi*50*t + np.random.uniform(0, 2*np.pi))
    return t, eeg.astype(np.float64)


def preprocess_signal(sig):
    """
    Prétraitement minimal : HP 0.5 Hz + LP 40 Hz + Notch 50 Hz.
    Identique au hardware (ESP32). Doit être fait AVANT l'augmentation.
    Ref : Chaudhary 2025 (PREP-1) | Acharya 2021 (PREP-2) | CdC NeuroCap
    """
    b, a = signal.butter(4, 0.5/(FS/2),  btype='high')
    sig  = signal.filtfilt(b, a, sig)
    b, a = signal.butter(4, 40.0/(FS/2), btype='low')
    sig  = signal.filtfilt(b, a, sig)
    b, a = signal.iirnotch(50.0/(FS/2),  Q=30.0)
    sig  = signal.filtfilt(b, a, sig)
    return sig


def segment_signal(sig, amp_thr=AMP_THR):
    """
    Segmentation hardware : 4 s / overlap 50 % / fenêtre Hann / rejet 500 µV.
    Ref : CdC NeuroCap Sec. 2.1 | Acharya 2021 (PREP-2) | Bio-Protocol 2023
    """
    win = np.hanning(EPOCH_SAMPLES)
    epochs, statuses, t0s = [], [], []
    for i in range(0, len(sig)-EPOCH_SAMPLES+1, STEP):
        ep = sig[i:i+EPOCH_SAMPLES]
        statuses.append('rejeté' if np.max(np.abs(ep)) > amp_thr else 'valide')
        epochs.append(ep * win)
        t0s.append(i / FS)
    return np.array(epochs), statuses, t0s


# ─────────────────────────────────────────────────────────────────────────────
# SÉPARATION TRAIN / VALIDATION / TEST  (ÉTAPE CRITIQUE)
# ─────────────────────────────────────────────────────────────────────────────

def split_by_subject(X, y, subject_ids, test_ratio=0.15, val_ratio=0.15, seed=42):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SÉPARATION PAR SUJET (évite le data leakage inter-sujet)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    POURQUOI splitter par SUJET et non par epoch (Bio-Protocol 2023) :
      ► Si on mélange les epochs de tous les sujets AVANT le split,
        le même sujet peut apparaître dans train ET test
      ► Ses epochs originales (train) sont très corrélées à ses epochs
        de test (même signal, même personne) → le modèle "mémorise"
        les patterns du sujet et les métriques de généralisation
        sont faussées (overestimation de l'accuracy de 15-30 %)
      ► En splitant par sujet, on garantit que AUCUN sujet du test
        n'a été vu lors de l'entraînement

    RÈGLE : Augmentation APRÈS le split, UNIQUEMENT sur X_train.

    Paramètres :
        X           : array (N_epochs, EPOCH_SAMPLES) — toutes les epochs
        y           : array (N_epochs,) — labels
        subject_ids : array (N_epochs,) — identifiant du sujet par epoch
        test_ratio  : fraction de sujets dans le test (défaut 0.15)
        val_ratio   : fraction de sujets dans la validation (défaut 0.15)
        seed        : graine pour la reproductibilité

    Retourne :
        X_train, y_train, train_ids : données d'entraînement
        X_val,   y_val,   val_ids   : données de validation (non augmentées)
        X_test,  y_test,  test_ids  : données de test (non augmentées)
    """
    np.random.seed(seed)
    unique_subjects = np.unique(subject_ids)
    np.random.shuffle(unique_subjects)
    n_subj = len(unique_subjects)

    # Calcul du nombre de sujets dans chaque ensemble
    n_test = max(1, int(n_subj * test_ratio))
    n_val  = max(1, int(n_subj * val_ratio))
    n_train = n_subj - n_test - n_val

    if n_train <= 0:
        # Fallback : si trop peu de sujets, tout mettre dans train
        print(f"    ⚠ Peu de sujets ({n_subj}) — ajustement automatique du split.")
        n_test  = max(1, n_subj // 5)
        n_val   = max(1, n_subj // 5)
        n_train = n_subj - n_test - n_val

    # Attribution des sujets aux ensembles
    test_subj  = unique_subjects[:n_test]
    val_subj   = unique_subjects[n_test:n_test+n_val]
    train_subj = unique_subjects[n_test+n_val:]

    # Création des masques booléens
    train_mask = np.isin(subject_ids, train_subj)
    val_mask   = np.isin(subject_ids, val_subj)
    test_mask  = np.isin(subject_ids, test_subj)

    X_train, y_train = X[train_mask], y[train_mask]
    X_val,   y_val   = X[val_mask],   y[val_mask]
    X_test,  y_test  = X[test_mask],  y[test_mask]

    print(f"\n    ── Split par sujet (seed={seed}) ──────────────────────────")
    print(f"    Train : {n_train} sujets → {X_train.shape[0]} epochs")
    print(f"    Val   : {n_val}   sujets → {X_val.shape[0]}   epochs  ← NON augmentées")
    print(f"    Test  : {n_test}  sujets → {X_test.shape[0]}  epochs  ← NON augmentées")

    return (X_train, y_train, subject_ids[train_mask],
            X_val,   y_val,   subject_ids[val_mask],
            X_test,  y_test,  subject_ids[test_mask])


def loso_generator(X, y, subject_ids):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    GÉNÉRATEUR LOSO (Leave-One-Subject-Out) — RECOMMANDÉ NeuroCap
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    POURQUOI LOSO est le gold standard pour l'EEG (Katmah 2021, N°12) :
      ► Chaque sujet constitue à tour de rôle l'ensemble de test
      ► Le modèle ne voit JAMAIS les données du sujet test lors du train
      ► Évalue la généralisation inter-sujet (pas seulement intra-sujet)
      ► N itérations (N = nombre de sujets) → évaluation robuste

    PROCÉDURE PAR FOLD :
      1. Séparer : train = tous sauf sujet k | test = sujet k uniquement
      2. Augmenter : appliquer l'augmentation sur X_train (ce fold seulement)
      3. Entraîner : modèle sur X_train_augmenté
      4. Évaluer  : sur X_test (non augmenté)
      5. Répéter pour chaque sujet k

    CdC NeuroCap (Sec. 2.4.3) : "Tous les modèles sont évalués par
    validation croisée sujet-indépendant (GroupKFold) pour garantir
    l'absence de fuite de données."

    Paramètres :
        X, y        : arrays complets (N_epochs, EPOCH_SAMPLES) et (N_epochs,)
        subject_ids : array (N_epochs,) — identifiant du sujet

    Yields (pour chaque sujet k) :
        fold_idx    : index du fold (0-based)
        subject_k   : identifiant du sujet test
        X_train_fold, y_train_fold : données d'entraînement (SANS sujet k)
        X_test_fold,  y_test_fold  : données de test (sujet k uniquement)
    """
    unique_subjects = np.unique(subject_ids)

    for fold_idx, subject_k in enumerate(unique_subjects):
        test_mask  = (subject_ids == subject_k)
        train_mask = ~test_mask

        X_train_fold = X[train_mask]
        y_train_fold = y[train_mask]
        X_test_fold  = X[test_mask]
        y_test_fold  = y[test_mask]

        yield (fold_idx, subject_k,
               X_train_fold, y_train_fold,
               X_test_fold,  y_test_fold)


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUES D'AUGMENTATION
# ─────────────────────────────────────────────────────────────────────────────

def aug_gaussian_noise(epoch, snr_db=25):
    """
    ── ÉTAPE 2.1 — Bruit Gaussien Filtré (Jittering) ─────────────────────
    SNR 20-30 dB | Bruit filtré [0.5-40 Hz] → préserve TBR/ABR/EI

    Simule : bruit intrinsèque AD8232 + variations environnementales.
    FORMULE : σ_bruit = sqrt(P_signal / 10^(SNR_dB/10))
    CRITIQUE : bruit FILTRÉ à la même bande que le signal → les ratios
    spectraux (TBR = Pθ/Pβ) restent physiologiquement valides car
    le bruit est distribué uniformément sur toutes les bandes.

    Ref : IEEE TNSRE (2022) | Braindecode
    """
    p_signal  = np.mean(epoch**2)
    p_noise   = p_signal / (10 ** (snr_db / 10))
    noise_raw = np.random.randn(len(epoch)) * np.sqrt(p_noise)
    # Filtrage du bruit à la même bande passante que le signal
    b, a = signal.butter(4, 0.5/(FS/2),  btype='high')
    noise = signal.filtfilt(b, a, noise_raw)
    b, a = signal.butter(4, 40.0/(FS/2), btype='low')
    noise = signal.filtfilt(b, a, noise)
    return epoch + noise


def aug_scaling(epoch, seed=None):
    """
    ── ÉTAPE 2.2 — Scaling d'Amplitude ±10 % ─────────────────────────────
    Simule : variabilité impédance électrode-peau entre sessions (+20 %).

    PROPRIÉTÉ CLÉ : scaling = transformation multiplicative.
    TBR = Pθ/Pβ → si signal × k → (Pθ×k²)/(Pβ×k²) = TBR inchangé.
    → C'est la technique LA PLUS SÛRE pour les ratios NeuroCap.

    POURQUOI ±10 % et non ±20 % :
    → ±10 % préserve TBR/EI dans ±19 % (acceptable < ±15 % en pratique)
    → ±20 % produirait une variation TBR de ±36 % → inacceptable.

    Ref : Computers in Biology and Medicine (2025)
    """
    if seed is not None:
        np.random.seed(seed)
    factor = np.random.uniform(SCALE_MIN, SCALE_MAX)
    return epoch * factor


def aug_time_shift(epoch, shift_samples=TIME_SHIFT_SAMP):
    """
    ── ÉTAPE 2.3 — Time Shifting 80 ms (np.roll circulaire) ──────────────
    Simule : variation de latence neuronale (±50-100 ms entre trials).

    POURQUOI np.roll() et non zero-padding :
    → np.roll() = décalage circulaire → PSD EXACTEMENT préservée
    → zero-padding → discontinuités aux bords → artefacts Gibbs
       → estimation PSD faussée en début/fin de fenêtre
    PROPRIÉTÉ : spectre PSD inchangé → TBR/EI/TAR parfaitement préservés.

    Ref : IEEE TNSRE (2022) | Braindecode | CDC NeuroCap (shift 80 ms)
    """
    return np.roll(epoch, shift_samples)


def aug_dwt_frequency(epoch, seed=None):
    """
    ── ÉTAPE 3 — DWT Fréquentielle (db4, 6 niveaux, seuillage sélectif) ──
    Perturbe UNIQUEMENT les niveaux HF (hors-bande) — conserve α/β/θ.

    TABLE DE CORRESPONDANCE DWT ↔ EEG @ 250 Hz, db4, 6 niveaux :
      cA6     (0 – 3.9 Hz)    → δ résiduel    → perturber ±5 % léger
      cD6     (3.9 – 7.8 Hz)  → θ/δ frontière → CONSERVER (TBR)
      cD5     (7.8 – 15.6 Hz) → α + début β   → CONSERVER (features)
      cD4     (15.6 – 31 Hz)  → β             → CONSERVER (feature principale)
      cD3     (31 – 63 Hz)    → haute gamma   → perturber ±15 %
      cD2     (63 – 125 Hz)   → hors-bande    → perturber ±20 %
      cD1     (> 125 Hz)      → hors-bande    → perturber ±30 %

    POURQUOI DWT et non FFT :
    → DWT = résolution temps-fréquence adaptée (bonne résolution freq. aux BF)
    → En single-channel, l'information fréquentielle est la SEULE source riche
    → FFT détruirait la structure temporelle du signal

    Ref : Knowledge-Based Systems (2025) | Iranian Signal Research Center (2024)
    """
    if seed is not None:
        np.random.seed(seed)

    coeffs = pywt.wavedec(epoch, WAVELET, level=DWT_LEVEL)
    # coeffs = [cA6, cD6, cD5, cD4, cD3, cD2, cD1] (index 0 à 6)
    new_c = list(coeffs)

    # cA6 (δ résiduel) → ±5 % léger (simule dérive lente de l'état cognitif)
    new_c[0] = coeffs[0] + np.random.randn(len(coeffs[0])) * np.std(coeffs[0]) * 0.05

    # cD6 (θ/δ) → CONSERVER  (préserve TBR)      → new_c[1] inchangé
    # cD5 (α)   → CONSERVER  (préserve α/EI)     → new_c[2] inchangé
    # cD4 (β)   → CONSERVER  (préserve β/TBR/EI) → new_c[3] inchangé

    # cD3 (haute gamma 31-63 Hz) → ±15 % (variabilité EMG/γ)
    if len(coeffs) > 4:
        new_c[4] = coeffs[4] + np.random.randn(len(coeffs[4])) * np.std(coeffs[4]) * 0.15

    # cD2 (hors-bande 63-125 Hz) → ±20 %
    if len(coeffs) > 5:
        new_c[5] = coeffs[5] + np.random.randn(len(coeffs[5])) * np.std(coeffs[5]) * 0.20

    # cD1 (> 125 Hz) → ±30 %
    if len(coeffs) > 6:
        new_c[6] = coeffs[6] + np.random.randn(len(coeffs[6])) * np.std(coeffs[6]) * 0.30

    rec = pywt.waverec(new_c, WAVELET)
    return rec[:len(epoch)]


def aug_magnitude_warping(epoch, warp_amp=WARP_AMP, seed=None):
    """
    ── ÉTAPE 4 — Magnitude Warping (INDÉPENDANT — jamais combiné à B+C) ──
    Simule : évolution lente de l'état cognitif (fatigue, habituation).

    SIMULATION PHYSIQUE (Computers in Biology and Medicine 2025) :
    → Fatigue cognitive sur 40 min (sessions NeuroCap) : amplitude β↓ lentement
    → Habituation : réduction progressive réponse α/θ après 20-30 min
    → Ces phénomènes = modulation LENTE d'amplitude dans l'EEG

    IMPLÉMENTATION spline cubique (5 points de contrôle) :
    → Fréquence de déformation 0.05-0.20 Hz (sous δ = 0.5 Hz)
    → Invisible dans la PSD 4 s → n'altère pas les bandes EEG
    → Enveloppe multiplicative = 1 + courbe_lente

    RÈGLE CRITIQUE : appliquer INDÉPENDAMMENT des étapes 2 et 3.
    → Jamais Warping + Noise + DWT sur la même epoch = suraugmentation
    → EEG non-stationnaire : distributions non-physiologiques si combiné

    Ref : Computers in Biology and Medicine (2025)
    """
    if seed is not None:
        np.random.seed(seed)
    n = len(epoch)
    n_knots  = 5
    knot_idx = np.linspace(0, n-1, n_knots, dtype=int)
    rms = np.sqrt(np.mean(epoch**2)) + 1e-10
    # Points de contrôle aléatoires dans ±warp_amp × RMS
    knot_vals = np.random.uniform(-warp_amp * rms, warp_amp * rms, n_knots)
    # Spline cubique → courbe lisse et continue
    spl = interpolate.CubicSpline(knot_idx, knot_vals)
    warp_curve = spl(np.arange(n))
    envelope = 1.0 + warp_curve / (rms + 1e-10)
    return epoch * envelope


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE D'AUGMENTATION COMPLÈTE (avec séparation correcte)
# ─────────────────────────────────────────────────────────────────────────────

def augment_train_set(X_train, y_train, seed=42):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AUGMENTATION DU SET D'ENTRAÎNEMENT UNIQUEMENT
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Cette fonction reçoit UNIQUEMENT X_train (après le split par sujet).
    Elle génère 4 types de copies augmentées correspondant aux 4 expériences.

    PROTOCOLE D'AUGMENTATION (Knowledge-Based Systems 2025) :
    ┌──────┬────────────────────────────────────────┬─────────────┐
    │ Exp. │ Technique                              │ Facteur ×   │
    ├──────┼────────────────────────────────────────┼─────────────┤
    │  A   │ Aucune (baseline)                      │  ×1         │
    │  B   │ Noise + Scaling + Shift                │  ×2 (orig+B)│
    │  C   │ Noise + Scaling + Shift + DWT          │  ×3 (orig+B+C)│
    │  D   │ Magnitude Warping (indépendant)        │  ×2 (orig+D)│
    │ FULL │ orig + B + C + D                       │  ×4         │
    └──────┴────────────────────────────────────────┴─────────────┘

    RÈGLES :
    ① Exp. B, C, D sont indépendantes (chaque epoch a une copie de chaque)
    ② Exp. D (Warping) n'est JAMAIS combiné directement avec Noise+DWT
    ③ Chaque copie hérite du label de l'epoch source
    ④ Normalisation z-score appliquée APRÈS chaque augmentation

    Paramètres :
        X_train : array (N_train, EPOCH_SAMPLES) — epochs d'entraînement SEULEMENT
        y_train : array (N_train,) — labels
        seed    : graine aléatoire

    Retourne dict avec les 5 variantes :
        'A'    → (X_train, y_train)                    # original seul
        'B'    → (X_B, y_B)                            # orig + basique
        'C'    → (X_C, y_C)                            # orig + basique + DWT
        'D'    → (X_D, y_D)                            # orig + warping
        'FULL' → (X_FULL, y_FULL)                      # orig + B + C + D
    """
    np.random.seed(seed)
    N = len(X_train)

    # Listes pour accumuler les copies augmentées (sans les originales)
    copies_B, copies_C, copies_D = [], [], []

    for i, ep in enumerate(X_train):
        local_seed = seed + i * 100

        # ── Exp. B : Basique (Noise → Scaling → Shift → z-score) ─────────────
        ep_b = aug_gaussian_noise(ep.copy(), snr_db=np.random.uniform(20, 30))
        ep_b = aug_scaling(ep_b, seed=local_seed)
        ep_b = aug_time_shift(ep_b, shift_samples=TIME_SHIFT_SAMP)
        ep_b = zscore_normalize(ep_b)
        copies_B.append(ep_b)

        # ── Exp. C : Basique + DWT (Noise → Scaling → Shift → DWT → z-score) ─
        ep_c = aug_gaussian_noise(ep.copy(), snr_db=np.random.uniform(20, 30))
        ep_c = aug_scaling(ep_c, seed=local_seed + 1)
        ep_c = aug_time_shift(ep_c, shift_samples=TIME_SHIFT_SAMP)
        ep_c = aug_dwt_frequency(ep_c, seed=local_seed + 2)
        ep_c = zscore_normalize(ep_c)
        copies_C.append(ep_c)

        # ── Exp. D : Magnitude Warping SEUL (indépendant !) ───────────────────
        # NOTE : On n'applique PAS Noise+DWT avant le Warping
        ep_d = aug_magnitude_warping(ep.copy(), seed=local_seed + 3)
        ep_d = zscore_normalize(ep_d)
        copies_D.append(ep_d)

    copies_B = np.array(copies_B)
    copies_C = np.array(copies_C)
    copies_D = np.array(copies_D)

    # Construction des datasets augmentés (originaux + copies)
    datasets = {
        'A':    (X_train.copy(), y_train.copy()),
        'B':    (np.concatenate([X_train, copies_B]), np.tile(y_train, 2)),
        'C':    (np.concatenate([X_train, copies_B, copies_C]), np.tile(y_train, 3)),
        'D':    (np.concatenate([X_train, copies_D]), np.tile(y_train, 2)),
        'FULL': (np.concatenate([X_train, copies_B, copies_C, copies_D]),
                 np.tile(y_train, 4)),
    }

    return datasets, copies_B, copies_C, copies_D


def validate_augmentation(X_orig, X_aug, label='AUG'):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    VALIDATION : PRÉSERVATION DES RATIOS COGNITIFS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Vérifie que TBR/ABR/EI/TAR varient < ±15 % après augmentation.
    Si variation > ±15 % → augmentation trop agressive → réduire l'intensité.

    CRITÈRE (Knowledge-Based Systems 2025) :
    Les copies augmentées doivent être "physiologiquement plausibles"
    = les médecins / experts EEG ne peuvent pas les distinguer des originaux
    sur la base des biomarqueurs NeuroCap.

    Retourne : dict avec mean_orig, mean_aug, variation_% pour chaque ratio
    """
    results = {}
    for key in ['TBR', 'ABR', 'EI', 'TAR']:
        orig_vals = [_compute_ratios(ep)[key] for ep in X_orig[:20]]
        aug_vals  = [_compute_ratios(ep)[key] for ep in X_aug[:20]]
        m_o = np.mean(orig_vals)
        m_a = np.mean(aug_vals)
        delta = abs(m_a - m_o) / (m_o + 1e-10) * 100
        results[key] = {'orig': m_o, 'aug': m_a, 'delta_%': delta, 'ok': delta < 15.0}
    return results


def save_augmented_datasets(datasets, X_val, y_val, X_test, y_test,
                             outdir='datasets_augmented'):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SAUVEGARDE DES DATASETS AUGMENTÉS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Structure du dossier sauvegardé :
      datasets_augmented/
      ├── X_train_A.npy    y_train_A.npy    ← baseline (originaux seuls)
      ├── X_train_B.npy    y_train_B.npy    ← orig + basique (×2)
      ├── X_train_C.npy    y_train_C.npy    ← orig + basique + DWT (×3)
      ├── X_train_D.npy    y_train_D.npy    ← orig + warping (×2)
      ├── X_train_FULL.npy y_train_FULL.npy ← orig + B + C + D (×4)
      ├── X_val.npy        y_val.npy        ← JAMAIS augmentés
      └── X_test.npy       y_test.npy       ← JAMAIS augmentés

    NOTE : val et test sont sauvegardés UNE SEULE FOIS (identiques pour A/B/C/D/FULL)
    car l'évaluation doit toujours être faite sur des données NON augmentées.
    """
    os.makedirs(outdir, exist_ok=True)

    # Sauvegarde des ensembles train (1 fichier par expérience)
    for exp_name, (X_tr, y_tr) in datasets.items():
        np.save(os.path.join(outdir, f'X_train_{exp_name}.npy'), X_tr)
        np.save(os.path.join(outdir, f'y_train_{exp_name}.npy'), y_tr)
        print(f"    ✓ Exp. {exp_name} : X_train shape={X_tr.shape}, y_train shape={y_tr.shape}")

    # Sauvegarde val et test (non augmentés — communs à toutes les expériences)
    np.save(os.path.join(outdir, 'X_val.npy'),    X_val)
    np.save(os.path.join(outdir, 'y_val.npy'),    y_val)
    np.save(os.path.join(outdir, 'X_test.npy'),   X_test)
    np.save(os.path.join(outdir, 'y_test.npy'),   y_test)
    print(f"    ✓ Val  : X_val  shape={X_val.shape}   ← NON augmentée")
    print(f"    ✓ Test : X_test shape={X_test.shape}  ← NON augmentée")

    return outdir


def load_augmented_datasets(outdir='datasets_augmented'):
    """
    Recharge les datasets sauvegardés depuis le disque.
    Usage : X_tr, y_tr = load_augmented_datasets()['B']  # pour Exp. B
    """
    result = {}
    for exp in ['A', 'B', 'C', 'D', 'FULL']:
        fX = os.path.join(outdir, f'X_train_{exp}.npy')
        fy = os.path.join(outdir, f'y_train_{exp}.npy')
        if os.path.exists(fX) and os.path.exists(fy):
            result[exp] = (np.load(fX), np.load(fy))

    result['val']  = (np.load(os.path.join(outdir, 'X_val.npy')),
                      np.load(os.path.join(outdir, 'y_val.npy')))
    result['test'] = (np.load(os.path.join(outdir, 'X_test.npy')),
                      np.load(os.path.join(outdir, 'y_test.npy')))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# FIGURES DE VISUALISATION
# ─────────────────────────────────────────────────────────────────────────────

def fig1_split_overview(X_train, X_val, X_test, y_train, y_val, y_test,
                         subject_ids_train, outdir):
    """
    Figure 1 — Visualisation du split train/val/test par sujet.
    Montre la distribution des sujets et des labels dans chaque ensemble.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor='white')
    fig.suptitle(
        'SÉPARATION CORRECTE : Split par Sujet (évite data leakage inter-sujet)\n'
        'Augmentation UNIQUEMENT sur X_train — Val et Test NON augmentés\n'
        'Ref : Bio-Protocol (2023) | CdC NeuroCap Sec. 2.4.3 (GroupKFold)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    # Distribution des epochs par ensemble
    ax = axes[0]
    sizes  = [len(X_train), len(X_val), len(X_test)]
    labels = [f'X_train\n{len(X_train)} epochs\n(augmenté)', 
              f'X_val\n{len(X_val)} epochs\n(NON augmenté)',
              f'X_test\n{len(X_test)} epochs\n(NON augmenté)']
    colors_pie = [COL['orig'], COL['aug2'], COL['aug1']]
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontsize': 9})
    for at in autotexts:
        at.set_fontsize(10); at.set_fontweight('bold')
    ax.set_title('Distribution train / val / test\n(split par sujet)', fontsize=10, fontweight='bold')

    # Distribution des labels dans train
    ax2 = axes[1]
    unique_labels, counts = np.unique(y_train, return_counts=True)
    bars = ax2.bar([str(l) for l in unique_labels], counts,
                   color=[COL['orig'], COL['aug1']][:len(unique_labels)],
                   alpha=0.85, edgecolor='white', lw=2)
    for bar, cnt in zip(bars, counts):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 str(cnt), ha='center', va='bottom', fontsize=12, fontweight='bold')
    _style(ax2, 'Distribution des labels — X_train\n(avant augmentation)',
           'Label', 'Nombre d\'epochs')
    _ref(ax2, 'Équilibrage important → SMOTE ou augmentation équilibrée')

    # Augmentation et croissance du dataset
    ax3 = axes[2]
    exps = ['A\n(original)', 'B\n(orig+basique)', 'C\n(orig+B+DWT)',
            'D\n(orig+warp)', 'FULL\n(orig+B+C+D)']
    factors = [1, 2, 3, 2, 4]
    n_orig = len(X_train)
    totals = [n_orig * f for f in factors]
    bar_cols = [COL['orig'], COL['aug1'], COL['aug2'], COL['aug3'], COL['aug4']]
    bars3 = ax3.bar(exps, totals, color=bar_cols, alpha=0.85, edgecolor='white', lw=2)
    ax3.axhline(n_orig, color='gray', ls='--', lw=1.5, alpha=0.7, label=f'Baseline: {n_orig}')
    for bar, v, f in zip(bars3, totals, factors):
        ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f'{v}\n(×{f})', ha='center', va='bottom', fontsize=10, fontweight='bold')
    _style(ax3, f'Croissance du dataset X_train (N_orig = {n_orig} epochs)',
           'Expérience', 'Nombre d\'epochs total')
    ax3.legend(fontsize=9)
    _ref(ax3, 'Augmentation UNIQUEMENT sur X_train | Knowledge-Based Systems 2025')

    plt.tight_layout()
    p = os.path.join(outdir, 'aug_01_split_overview.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig2_loso_schema(subject_ids, outdir):
    """
    Figure 2 — Schéma visuel du protocole LOSO.
    Montre comment chaque sujet est tour à tour le sujet test.
    """
    fig, ax = plt.subplots(figsize=(18, 8), facecolor='white')
    ax.set_xlim(0, 18); ax.set_ylim(0, 8); ax.axis('off')
    fig.suptitle(
        'PROTOCOLE LOSO (Leave-One-Subject-Out) — Gold Standard NeuroCap\n'
        'Chaque sujet = test à tour de rôle | Augmentation sur train uniquement par fold\n'
        'CdC NeuroCap Sec. 2.4.3 | Katmah 2021 (N°12) | Pandya 2025 (N°13)',
        fontsize=12, fontweight='bold', color=COL['dark'])

    unique_subj = np.unique(subject_ids)
    n_show = min(8, len(unique_subj))
    colors_train = '#2980B9'
    colors_test  = '#E74C3C'

    for fold in range(n_show):
        y_pos = 7.0 - fold * 0.75
        ax.text(-0.2, y_pos, f'Fold {fold+1}', fontsize=8, fontweight='bold',
                color=COL['dark'], va='center', ha='right')
        for subj_idx in range(n_show):
            x_pos = 1.0 + subj_idx * 2.0
            if subj_idx == fold:
                color = colors_test; label = 'TEST\n(non augmenté)'
            else:
                color = colors_train; label = 'TRAIN\n(augmenté)'
            rect = mpatches.FancyBboxPatch((x_pos-0.7, y_pos-0.28), 1.4, 0.56,
                boxstyle="round,pad=0.05", facecolor=color, edgecolor='white',
                lw=1.5, alpha=0.88, zorder=3)
            ax.add_patch(rect)
            ax.text(x_pos, y_pos, f'S{fold+1+subj_idx*0}', fontsize=7,
                    ha='center', va='center', color='white', fontweight='bold', zorder=4)

        # Labels sujets
        if fold == 0:
            for subj_idx in range(n_show):
                ax.text(1.0 + subj_idx * 2.0, 7.55, f'Sujet {subj_idx+1}',
                        fontsize=7, ha='center', color=COL['dark'], fontweight='bold')

    # Légende
    p_tr = mpatches.Patch(color=colors_train, alpha=0.88, label='TRAIN (augmenté dans ce fold)')
    p_te = mpatches.Patch(color=colors_test,  alpha=0.88, label='TEST (jamais augmenté)')
    ax.legend(handles=[p_tr, p_te], fontsize=10, loc='lower right',
              bbox_to_anchor=(0.99, 0.02))

    # Métriques
    ax.text(9, 0.7,
            '→ Pour chaque fold : (1) Séparer  (2) Augmenter X_train  '
            '(3) Entraîner  (4) Évaluer sur X_test\n'
            '→ Métriques finales = moyenne sur tous les folds : '
            'Accuracy ≥ 85 % | F1-macro ≥ 0.80 (CdC NeuroCap Sec. 5.6)',
            ha='center', va='center', fontsize=9, color=COL['dark'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor=COL['light'],
                      alpha=0.95, edgecolor=COL['dark']))

    p = os.path.join(outdir, 'aug_02_loso_schema.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig3_augmentation_comparison(X_train, datasets, outdir):
    """
    Figure 3 — Vue d'ensemble des 4 types d'augmentation sur un exemple.
    Affiche signaux temporels et PSD pour chaque expérience.
    """
    orig_ep = X_train[0]
    t_ep    = np.arange(EPOCH_SAMPLES) / FS * 1000

    # Générer un exemple de chaque type
    np.random.seed(0)
    ep_B = aug_time_shift(aug_scaling(aug_gaussian_noise(orig_ep.copy(), 25)))
    ep_C = aug_dwt_frequency(ep_B.copy(), seed=0)
    ep_D = aug_magnitude_warping(orig_ep.copy(), seed=0)
    ep_F = aug_dwt_frequency(
           aug_time_shift(aug_scaling(aug_gaussian_noise(orig_ep.copy(), 25))), seed=1)
    ep_F = zscore_normalize(ep_F)

    sigs = [
        (orig_ep, COL['orig'],  'Original (Référence)',           'Signal original normalisé z-score'),
        (ep_B,    COL['aug1'],  'Exp. B — Basique',               'Noise SNR25dB + Scaling ±10% + Shift 80ms'),
        (ep_C,    COL['aug2'],  'Exp. C — Basique + DWT',         'Exp.B + DWT (HF perturbée, α/β/θ conservés)'),
        (ep_D,    COL['aug3'],  'Exp. D — Magnitude Warping',     'Warp ±8% RMS (fatigue cognitive)  — INDÉPENDANT'),
        (ep_F,    COL['aug4'],  'FULL — B + C combinés',          'Noise + Scale + Shift + DWT'),
    ]

    fig = plt.figure(figsize=(20, 15), facecolor='white')
    fig.suptitle(
        'AUGMENTATION — Vue d\'Ensemble des 5 Expériences\n'
        'Original vs Exp. B (Basique) vs Exp. C (B+DWT) vs Exp. D (Warping) vs FULL\n'
        'Ref : Knowledge-Based Systems (2025) | IEEE TNSRE (2022)',
        fontsize=12, fontweight='bold', color=COL['dark'])

    gs = gridspec.GridSpec(5, 2, figure=fig, hspace=0.55, wspace=0.32)

    for row, (sig, col, lbl, desc) in enumerate(sigs):
        ax_t = fig.add_subplot(gs[row, 0])
        ax_t.plot(t_ep, sig, color=col, lw=0.9, alpha=0.9, label=lbl)
        if row > 0:
            ax_t.plot(t_ep, orig_ep, color=COL['orig'], lw=0.6, alpha=0.3, ls='--', label='Orig.')
        _style(ax_t, f'{lbl} — Temporel', 'Temps (ms)', 'Z-score (σ)')
        ax_t.text(0.02, 0.95, desc, transform=ax_t.transAxes, fontsize=7.5,
                  color='#555', va='top')
        if row > 0: ax_t.legend(fontsize=7, loc='upper right')

        ax_f = fig.add_subplot(gs[row, 1])
        f_o, psd_o = _psd(orig_ep)
        f_a, psd_a = _psd(sig)
        m = (f_o >= 0.5) & (f_o <= 45)
        ax_f.semilogy(f_o[m], psd_o[m], color=COL['orig'], lw=1.2, alpha=0.45, ls='--')
        ax_f.semilogy(f_a[m], psd_a[m], color=col, lw=1.8, label=lbl)
        _shade_bands(ax_f, 45)
        _style(ax_f, f'{lbl} — PSD Welch', 'Fréquence (Hz)', 'µV²/Hz [log]')

    p = os.path.join(outdir, 'aug_03_comparison_experiments.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig4_validation_ratios(X_train, copies_B, copies_C, copies_D, outdir):
    """
    Figure 4 — Validation critique : TBR/ABR/EI/TAR avant/après augmentation.
    FIGURE DE VALIDATION : prouve que les features NeuroCap restent valides.
    """
    aug_groups = [
        ('Original', X_train[:20],       COL['orig']),
        ('Exp. B\nBasique', copies_B[:20], COL['aug1']),
        ('Exp. C\nB+DWT',  copies_C[:20], COL['aug2']),
        ('Exp. D\nWarp',   copies_D[:20], COL['aug3']),
    ]

    ratio_keys    = ['TBR', 'ABR', 'EI', 'TAR']
    ratio_labels  = ['TBR (θ/β)\n→ < 0.8 concentration', 'ABR (α/β)',
                     'EI β/(α+θ)\n→ > 0.7 concentration', 'TAR (θ/α)']
    ratio_targets = [0.8, None, 0.7, None]

    fig, axes = plt.subplots(2, 2, figsize=(18, 12), facecolor='white')
    fig.suptitle(
        'VALIDATION CRITIQUE — Préservation des Ratios Cognitifs NeuroCap\n'
        'Critère : variation < ±15 % des valeurs originales\n'
        'Ref : CdC NeuroCap Sec. 2.5.1 | Salam 2026 (N°15) | Samsa 2026 (N°17)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    x = np.arange(len(aug_groups))

    for ax_idx, (rkey, rlbl, rtgt) in enumerate(zip(ratio_keys, ratio_labels, ratio_targets)):
        ax = axes[ax_idx//2, ax_idx%2]

        orig_vals_all = [_compute_ratios(ep)[rkey] for ep in X_train[:20]]
        m_orig = np.mean(orig_vals_all)

        # Bande de tolérance ±15 %
        ax.axhspan(m_orig * 0.85, m_orig * 1.15, alpha=0.08, color='#27AE60',
                   label='Zone ±15 % tolérance')

        for g_idx, (glbl, geps, gcol) in enumerate(aug_groups):
            vals = [_compute_ratios(ep)[rkey] for ep in geps]
            m, s = np.mean(vals), np.std(vals)
            ax.bar(g_idx, m, 0.55, color=gcol, alpha=0.82,
                   yerr=s, capsize=6, error_kw=dict(lw=1.5, ecolor='#333'),
                   edgecolor='white', lw=1.5)
            # Calcul de la variation
            delta = abs(m - m_orig) / (m_orig + 1e-10) * 100
            ok_sym = '✓' if delta < 15 else '✗'
            color_ok = '#27AE60' if ok_sym == '✓' else '#E74C3C'
            ax.text(g_idx, m + s + max(s*0.05, 0.002),
                    f'{m:.3f}\n{ok_sym} Δ={delta:.1f}%',
                    ha='center', va='bottom', fontsize=8,
                    fontweight='bold', color=color_ok)

        if rtgt is not None:
            ax.axhline(rtgt, color=COL['dark'], ls='--', lw=1.5, alpha=0.7,
                       label=f'Seuil NeuroCap ({rtgt})')

        _style(ax, rlbl, 'Type d\'augmentation', rlbl.split('\n')[0])
        ax.set_xticks(x)
        ax.set_xticklabels([g[0] for g in aug_groups], fontsize=8)
        ax.legend(fontsize=8, loc='upper right')
        _ref(ax, 'Variation < ±15 % = augmentation physiologiquement valide')

    plt.tight_layout()
    p = os.path.join(outdir, 'aug_04_validation_ratios.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig5_dwt_bands(X_train, outdir):
    """
    Figure 5 — DWT fréquentielle : preuve que α/β/θ sont préservés.
    """
    orig_ep = X_train[0]
    aug_ep  = aug_dwt_frequency(orig_ep.copy(), seed=42)
    t_ep    = np.arange(EPOCH_SAMPLES) / FS * 1000

    fig, axes = plt.subplots(2, 3, figsize=(18, 11), facecolor='white')
    fig.suptitle(
        'ÉTAPE 3 — DWT Fréquentielle (db4, 6 niveaux)\n'
        'Perturbation SÉLECTIVE : Hors-bande perturbée | α (8-13 Hz) + β (13-30 Hz) + θ (4-8 Hz) CONSERVÉS\n'
        'Ref : Knowledge-Based Systems (2025) | Iranian Signal Research Center (2024)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    # Signal temporel
    axes[0,0].plot(t_ep, orig_ep, color=COL['orig'], lw=1.0, alpha=0.7, label='Original')
    axes[0,0].plot(t_ep, aug_ep,  color=COL['aug3'], lw=0.9, alpha=0.85, label='DWT augmenté')
    _style(axes[0,0], 'Temporel — Avant vs Après DWT', 'Temps (ms)', 'Z-score (σ)')
    axes[0,0].legend(fontsize=8)

    # PSD superposée avec annotations
    f_o, psd_o = _psd(orig_ep)
    f_a, psd_a = _psd(aug_ep)
    m = (f_o >= 0.5) & (f_o <= 45)
    axes[0,1].semilogy(f_o[m], psd_o[m], color=COL['orig'], lw=2, alpha=0.6, ls='--', label='Original')
    axes[0,1].semilogy(f_a[m], psd_a[m], color=COL['aug3'], lw=1.8, label='DWT augmenté')
    _shade_bands(axes[0,1], 45)
    for bname, (f1,f2), bc in [('★ θ conservé',(4,8),'#3498DB'),
                                ('★ α conservé',(8,13),'#27AE60'),
                                ('★ β conservé',(13,30),'#E67E22')]:
        fc = (f1+f2)/2
        axes[0,1].annotate(bname, xy=(fc, 5e-4), xytext=(fc, 5e-2),
                           fontsize=7, ha='center', color=bc,
                           arrowprops=dict(arrowstyle='->', color=bc, lw=1))
    _style(axes[0,1], 'PSD — ★ α/β/θ CONSERVÉS | HF perturbée', 'Fréquence (Hz)', 'µV²/Hz [log]')
    axes[0,1].legend(fontsize=8)
    _ref(axes[0,1], 'Niveaux cD4(β) cD5(α) cD6(θ) intouchés → ratios TBR/EI préservés')

    # Coefficients DWT niveau par niveau
    coeffs_o = pywt.wavedec(orig_ep, WAVELET, level=DWT_LEVEL)
    coeffs_a = pywt.wavedec(aug_ep,  WAVELET, level=DWT_LEVEL)
    level_info = [
        ('cA6', '0–3.9 Hz (δ)',      '↯ Perturbé ±5%',    '#E74C3C', False),
        ('cD6', '3.9–7.8 Hz (θ)',    '★ CONSERVÉ',         '#3498DB', True),
        ('cD5', '7.8–15.6 Hz (α)',   '★ CONSERVÉ',         '#27AE60', True),
        ('cD4', '15.6–31 Hz (β)',    '★ CONSERVÉ',         '#E67E22', True),
    ]
    positions = [(0,2),(1,0),(1,1),(1,2)]
    for (row,col), (nm, bnd, note, bc, conserved) in zip(positions, level_info):
        idx = 0 if nm == 'cA6' else int(nm[2:]) - (DWT_LEVEL - 3) if 'D' in nm else 0
        j_idx = ['cA6','cD6','cD5','cD4','cD3','cD2','cD1'].index(nm)
        ax = axes[row, col]
        n_show = min(80, len(coeffs_o[j_idx]))
        ax.plot(coeffs_o[j_idx][:n_show], color=COL['orig'], lw=1.0, alpha=0.7, label='Orig.')
        ax.plot(coeffs_a[j_idx][:n_show], color=bc,          lw=1.0, alpha=0.85, label='Aug.')
        _style(ax, f'{nm} — {bnd}', 'Éch.', 'Coeff. DWT')
        ax.legend(fontsize=7)
        color_note = '#27AE60' if conserved else '#E74C3C'
        ax.text(0.02, 0.92, note, transform=ax.transAxes, fontsize=8,
                color=color_note, fontweight='bold', va='top')
        _ref(ax, '★ = feature NeuroCap préservée' if conserved else '↯ = perturbation autorisée')

    plt.tight_layout()
    p = os.path.join(outdir, 'aug_05_dwt_bands.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig6_magnitude_warping(X_train, outdir):
    """
    Figure 6 — Magnitude Warping : enveloppe lente de fatigue cognitive.
    """
    orig_ep = X_train[0]
    t_ep    = np.arange(EPOCH_SAMPLES) / FS * 1000

    fig, axes = plt.subplots(2, 3, figsize=(18, 10), facecolor='white')
    fig.suptitle(
        'ÉTAPE 4 — Magnitude Warping (Simulation Fatigue Cognitive) — INDÉPENDANT de B+C\n'
        'Déformation lente 0.05-0.20 Hz | ±8 % RMS | Spline cubique\n'
        'Ref : Computers in Biology and Medicine (2025)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    amps = [0.05, 0.08, 0.12]
    labels_amp = ['±5% RMS', '±8% RMS (★ retenu)', '±12% RMS']
    colors_amp = [COL['aug1'], COL['aug3'], COL['aug4']]

    for col_idx, (amp, lbl, col) in enumerate(zip(amps, labels_amp, colors_amp)):
        aug = aug_magnitude_warping(orig_ep.copy(), warp_amp=amp, seed=42+col_idx)

        ax_t = axes[0, col_idx]
        ax_t.plot(t_ep, orig_ep, color=COL['orig'], lw=1.0, alpha=0.5, ls='--', label='Original')
        ax_t.plot(t_ep, aug,     color=col, lw=0.9, label=f'Warp {lbl}')
        # Afficher l'enveloppe
        rms = np.sqrt(np.mean(orig_ep**2)) + 1e-10
        n = len(orig_ep)
        knot_idx = np.linspace(0, n-1, 5, dtype=int)
        np.random.seed(42+col_idx)
        knot_vals = np.random.uniform(-amp*rms, amp*rms, 5)
        spl = interpolate.CubicSpline(knot_idx, knot_vals)
        ax_t.plot(t_ep, spl(np.arange(n))/(rms+1e-10),
                  color=col, lw=1.8, ls=':', alpha=0.7, label='Enveloppe')
        _style(ax_t, f'Warp {lbl} — Temporel', 'Temps (ms)', 'Z-score (σ)')
        ax_t.legend(fontsize=7)
        star = '★ ' if amp == 0.08 else ''
        _ref(ax_t, f'{star}Fatigue cognitive 40 min (sessions NeuroCap)')

        ax_f = axes[1, col_idx]
        f_o, psd_o = _psd(orig_ep)
        f_a, psd_a = _psd(aug)
        m = (f_o >= 0.5) & (f_o <= 45)
        ax_f.semilogy(f_o[m], psd_o[m], color=COL['orig'], lw=1.5, alpha=0.5, ls='--')
        ax_f.semilogy(f_a[m], psd_a[m], color=col, lw=1.8, label=f'Warp {lbl}')
        _shade_bands(ax_f, 45)
        _style(ax_f, f'PSD — {lbl}\n(impact minimal sur spectre)', 'Fréquence (Hz)', 'µV²/Hz [log]')
        ax_f.legend(fontsize=8)
        _ref(ax_f, 'Déformation < 0.5 Hz → invisible dans PSD → ratios EEG préservés')

    plt.tight_layout()
    p = os.path.join(outdir, 'aug_06_magnitude_warping.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig7_dataset_growth(datasets, outdir):
    """
    Figure 7 — Croissance du dataset par expérience sur les 2 datasets NeuroCap.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor='white')
    fig.suptitle(
        'Impact de l\'Augmentation — Croissance du Dataset NeuroCap\n'
        'SAM40 (40 sujets, stress) | Cognitive Load (15 sujets, concentration) — Single channel Fp2\n'
        'Ref : Knowledge-Based Systems (2025) | Bio-Protocol (2023)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    # Estimation réaliste des epochs par sujet (signal 4 min, epoch 4s, overlap 50%)
    # 4 min = 240 s | step 2 s | n_epochs = (240-4)/2 + 1 = 119 epochs/sujet
    ds_info = {
        'Cognitive Load\n(Concentration, 15 sujets)': {'n_subj': 15, 'ep_per_subj': 119},
        'SAM40\n(Stress, 40 sujets)':                 {'n_subj': 40, 'ep_per_subj': 119},
    }
    exps      = ['A\n(aucune)', 'B\n(basique)', 'C\n(B+DWT)', 'D\n(warp)', 'FULL\n(B+C+D)']
    factors   = [1, 2, 3, 2, 4]
    bar_cols  = [COL['orig'], COL['aug1'], COL['aug2'], COL['aug3'], COL['aug4']]

    for ax, (ds_name, ds) in zip(axes, ds_info.items()):
        n_train = int(ds['n_subj'] * ds['ep_per_subj'] * 0.70)  # 70% train
        totals  = [n_train * f for f in factors]
        bars = ax.bar(exps, totals, color=bar_cols, alpha=0.85, edgecolor='white', lw=2)
        ax.axhline(n_train, color='gray', ls='--', lw=1.5, alpha=0.7,
                   label=f'Baseline train : {n_train} epochs')
        for bar, v, f in zip(bars, totals, factors):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+n_train*0.01,
                    f'{v}\n(×{f})', ha='center', va='bottom', fontsize=10, fontweight='bold')
        _style(ax, f'{ds_name}\n{ds["n_subj"]} sujets × ~{ds["ep_per_subj"]} epochs',
               'Expérience', 'Nombre d\'epochs X_train')
        ax.legend(fontsize=9)
        _ref(ax, 'Split 70/15/15 par sujet | Augmentation sur train seulement')

    plt.tight_layout()
    p = os.path.join(outdir, 'aug_07_dataset_growth.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig8_usage_code(outdir):
    """
    Figure 8 — Schéma du code d'utilisation correct.
    Montre visuellement comment utiliser ce module dans le projet NeuroCap.
    """
    fig, ax = plt.subplots(figsize=(20, 12), facecolor='white')
    ax.set_xlim(0, 20); ax.set_ylim(0, 12); ax.axis('off')
    fig.suptitle(
        'Guide d\'Utilisation — Pipeline d\'Augmentation NeuroCap\n'
        'Procédure correcte : Séparer → Augmenter → Entraîner → Évaluer',
        fontsize=13, fontweight='bold', color=COL['dark'])

    blocks = [
        (2.0, 10.0, 'DONNÉES COMPLÈTES\n(tous sujets)',
         '#2C3E50', 'X, y, subject_ids\nPrétraité + segmenté + z-score', 'preprocessing_Fp2.py'),
        (8.0, 10.0, 'SPLIT PAR SUJET\n(AVANT AUGMENTATION)',
         '#8E44AD', 'split_by_subject()\nou loso_generator()', 'Bio-Protocol 2023\nCdC Sec. 2.4.3'),
        (14.5, 10.5,'X_val, X_test\n(NON augmentés)',
         '#E74C3C', 'Évaluation uniquement\nJAMAIS augmentés', 'Gold standard EEG'),
        (14.5, 7.5, 'X_train uniquement\n→ Augmentation',
         '#27AE60', 'augment_train_set(X_train, y_train)', 'Knowledge-Based Systems 2025'),
        (5.0,  5.5, 'Exp. A\nOriginal seul',
         '#2C3E50', '×1 dataset\nBaseline', 'Référence'),
        (9.0,  5.5, 'Exp. B\nNoise+Scale+Shift',
         COL['aug1'], '×2 dataset\norigi+B', 'IEEE TNSRE 2022'),
        (13.0, 5.5, 'Exp. C\nB + DWT',
         COL['aug2'], '×3 dataset\norig+B+C', 'Knowl.-Based Sys. 2025'),
        (17.0, 5.5, 'Exp. D\nWarping seul',
         COL['aug3'], '×2 dataset\norig+D', 'Comput. Biol Med 2025'),
        (11.0, 3.0, 'ENTRAÎNEMENT + ÉVALUATION\nsur X_val et X_test (non augmentés)',
         '#1A2E5A', 'Acc ≥ 85 % | F1-macro ≥ 0.80\n(CdC NeuroCap Sec. 5.6)', 'Évaluation honnête'),
    ]

    BW, BH = 3.2, 1.4
    for (x, y, title, color, detail, ref) in blocks:
        bp = mpatches.FancyBboxPatch((x-BW/2, y-BH/2), BW, BH,
            boxstyle="round,pad=0.1", facecolor=color, edgecolor='white', lw=2, alpha=0.92)
        ax.add_patch(bp)
        ax.text(x, y+0.3, title, ha='center', va='center', fontsize=8.5,
                fontweight='bold', color='white')
        ax.text(x, y-0.28, detail, ha='center', va='center', fontsize=6.8,
                color='#EEEEEE', alpha=0.9)
        rp = mpatches.FancyBboxPatch((x-BW/2, y-BH/2-0.95), BW, 0.75,
            boxstyle="round,pad=0.05", facecolor='#F8F9FA', edgecolor=color, lw=1.5)
        ax.add_patch(rp)
        ax.text(x, y-BH/2-0.58, ref, ha='center', va='center', fontsize=6.2,
                color=color, fontweight='bold')

    # Flèches
    ax.annotate('', xy=(4.65,10.0), xytext=(6.35,10.0),
                arrowprops=dict(arrowstyle='->', color=COL['dark'], lw=2))
    ax.annotate('', xy=(11.7,10.5), xytext=(9.65,10.2),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=2))
    ax.annotate('', xy=(11.7,7.5),  xytext=(9.65,9.8),
                arrowprops=dict(arrowstyle='->', color='#27AE60', lw=2))
    for xb in [5.0, 9.0, 13.0, 17.0]:
        ax.annotate('', xy=(xb, 6.25), xytext=(14.5, 7.0),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))
    for xb in [5.0, 9.0, 13.0, 17.0]:
        ax.annotate('', xy=(11.0, 3.72), xytext=(xb, 4.82),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))

    # Save + load
    ax.text(11.0, 1.2,
            'save_augmented_datasets() → datasets_augmented/  '
            '[X_train_A.npy, X_train_B.npy, ..., X_val.npy, X_test.npy]\n'
            'load_augmented_datasets() → dict[exp] = (X_train, y_train)  '
            '| dict["val"] / dict["test"]  ← pour entraîner les modèles',
            ha='center', va='center', fontsize=9, fontfamily='monospace',
            color=COL['dark'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor=COL['light'],
                      alpha=0.97, edgecolor=COL['dark']))

    p = os.path.join(outdir, 'aug_08_usage_guide.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig9_pipeline_final(outdir):
    """Figure 9 — Diagramme final complet de la pipeline."""
    fig, ax = plt.subplots(figsize=(22, 13), facecolor='white')
    ax.set_xlim(0, 22); ax.set_ylim(0, 13); ax.axis('off')
    fig.suptitle(
        'Pipeline Complète d\'Augmentation EEG — NeuroCap Fp2 (AD8232 + ESP32)\n'
        '① Séparer  ②Augmenter train seulement  ③ Sauvegarder  ④ Entraîner  ⑤ Évaluer',
        fontsize=13, fontweight='bold', color=COL['dark'])

    boxes = [
        (2.5, 11.2, 'SIGNAL\nPRÉTRAITÉ',    '#2C3E50','X, y\nsubject_ids', 'preprocessing_Fp2.py'),
        (6.5, 11.2, 'SPLIT\nPAR SUJET',     '#8E44AD','split_by_subject()\nou loso_generator()','Bio-Protocol 2023'),
        (11.0,11.8, 'X_val + X_test\nNON augmentés','#E74C3C','Évaluation finale\nJAMAIS augmentés','Gold standard EEG'),
        (11.0,10.4, 'X_train\nAugmenté','#27AE60','augment_train_set()\nX_train seulement','Knowledge-Based Sys.'),
        (2.5,  7.0, 'EXP. B\nBasique',      '#E74C3C','Noise SNR25dB\n+Scale±10%\n+Shift 80ms','IEEE TNSRE 2022\n×2 dataset'),
        (7.5,  7.0, 'EXP. C\nB+DWT',        '#E67E22','Exp.B\n+DWT db4 6niv.\nα/β/θ conservés','Knowl-Based Sys.\n×3 dataset'),
        (12.5, 7.0, 'EXP. D\nWarping',      '#8E44AD','Warp ±8%RMS\n0.05-0.20Hz\nINDÉPENDANT','Comput.BiolMed\n×2 dataset'),
        (17.5, 7.0, 'FULL\nB+C+D',          '#27AE60','orig+B+C+D\nPipeline\ncomplète','Pipeline finale\n×4 dataset'),
        (11.0, 4.0, 'SAUVEGARDE\ndatasets_augmented/','#1A2E5A',
         'X_train_A/B/C/D/FULL.npy\nX_val.npy | X_test.npy', 'save/load_augmented_datasets()'),
        (11.0, 1.5, 'ENTRAÎNEMENT\n& ÉVALUATION','#1A2E5A',
         'F1-macro ≥ 0.80 | Acc ≥ 85%\nVariance LOSO < 10%', 'CdC NeuroCap Sec. 5.6'),
    ]
    BW, BH = 3.4, 1.55
    for (x, y, title, color, detail, ref) in boxes:
        ax.add_patch(mpatches.FancyBboxPatch((x-BW/2,y-BH/2), BW, BH,
            boxstyle="round,pad=0.1", facecolor=color, edgecolor='white', lw=2, alpha=0.93))
        ax.text(x, y+0.35, title, ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')
        ax.text(x, y-0.28, detail, ha='center', va='center', fontsize=6.8, color='#EEE')
        ax.add_patch(mpatches.FancyBboxPatch((x-BW/2,y-BH/2-1.05), BW, 0.85,
            boxstyle="round,pad=0.05", facecolor='#F8F9FA', edgecolor=color, lw=1.5, alpha=0.97))
        ax.text(x, y-BH/2-0.60, ref, ha='center', va='center', fontsize=6.2,
                color=color, fontweight='bold')

    # Flèches
    ax.annotate('', xy=(4.2,11.2), xytext=(3.35,11.2),
                arrowprops=dict(arrowstyle='->', color=COL['dark'], lw=2.2))
    ax.annotate('', xy=(8.7,11.8), xytext=(8.0,11.5),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=2, connectionstyle='arc3,rad=-0.2'))
    ax.annotate('', xy=(8.7,10.4), xytext=(8.0,11.0),
                arrowprops=dict(arrowstyle='->', color='#27AE60', lw=2, connectionstyle='arc3,rad=0.2'))
    for xb in [2.5, 7.5, 12.5, 17.5]:
        ax.annotate('', xy=(xb, 7.78), xytext=(11.0, 9.63),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))
    for xb in [2.5, 7.5, 12.5, 17.5]:
        ax.annotate('', xy=(11.0, 4.8), xytext=(xb, 6.22),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))
    ax.annotate('', xy=(11.0, 2.3), xytext=(11.0, 3.22),
                arrowprops=dict(arrowstyle='->', color=COL['dark'], lw=2.2))

    ax.text(11.0, 0.35,
            '★  RÈGLE ABSOLUE : Magnitude Warping (Exp. D) appliqué INDÉPENDAMMENT de B+C — jamais combiné directement.\n'
            '★  Val et Test JAMAIS augmentés — évaluation sur données réelles uniquement.',
            ha='center', va='center', fontsize=9.5, color='#C0392B', style='italic',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FDEDEC', alpha=0.97, edgecolor='#E74C3C', lw=1.5))

    p = os.path.join(outdir, 'aug_09_pipeline_final.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


# ─────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def run_augmentation_pipeline(state='concentration',
                               outdir='/mnt/user-data/outputs/augmentation_final',
                               save_dir=None):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    PIPELINE PRINCIPALE — Augmentation correcte et professionnelle
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Procédure complète :
      1. Génération du signal synthétique (remplacer par vraies données)
      2. Prétraitement minimal (si pas déjà fait)
      3. Segmentation (4 s, overlap 50 %)
      4. ★ SPLIT PAR SUJET (avant toute augmentation)
      5. Augmentation UNIQUEMENT sur X_train
      6. Validation des ratios cognitifs (TBR/EI/TAR)
      7. Sauvegarde des datasets augmentés
      8. Génération des 9 figures

    Dans le projet réel, remplacer les étapes 1-3 par :
      → Charger fichiers CSV hardware (load_hardware_csv())
      → Empiler les epochs de tous les sujets avec leurs labels et IDs
      → Passer directement à l'étape 4 (split)
    """
    os.makedirs(outdir, exist_ok=True)
    if save_dir is None:
        save_dir = os.path.join(outdir, 'datasets_augmented')

    print('=' * 65)
    print('NeuroCap — Pipeline d\'Augmentation EEG Fp2 (Version Finale)')
    print(f'fs={FS} Hz | Epoch {EPOCH_S}s | Overlap {OVERLAP*100:.0f}%')
    print(f'Seuil rejet : {AMP_THR} µV | Shift : {TIME_SHIFT_MS} ms')
    print('=' * 65)

    # ── 1-3. Simulation multi-sujets ──────────────────────────────────────────
    print('\n[SIM] Simulation de 10 sujets (20 s chacun)...')
    all_epochs, all_labels, all_sids = [], [], []
    states = ['concentration', 'stress']
    for sid in range(10):
        state_sim = states[sid % 2]
        _, raw = make_signal(state=state_sim, dur=20, seed=sid * 7)
        sig    = preprocess_signal(raw)
        epochs, statuses, _ = segment_signal(sig)
        valids = [(ep, 0 if state_sim=='concentration' else 1)
                  for ep, st in zip(epochs, statuses) if st == 'valide']
        for ep, lbl in valids:
            all_epochs.append(zscore_normalize(ep))
            all_labels.append(lbl)
            all_sids.append(sid)

    X = np.array(all_epochs)
    y = np.array(all_labels)
    sids = np.array(all_sids)
    print(f'    → {X.shape[0]} epochs valides | {len(np.unique(sids))} sujets simulés')
    print(f'    → Labels : {np.unique(y, return_counts=True)}')

    # ── 4. SPLIT PAR SUJET (ÉTAPE CRITIQUE) ──────────────────────────────────
    print('\n[SPLIT] Séparation par sujet (évite data leakage)...')
    (X_train, y_train, sid_train,
     X_val,   y_val,   _,
     X_test,  y_test,  _) = split_by_subject(X, y, sids, seed=42)

    # ── 5. AUGMENTATION UNIQUEMENT SUR X_TRAIN ────────────────────────────────
    print('\n[AUG] Augmentation du set d\'entraînement uniquement...')
    datasets, copies_B, copies_C, copies_D = augment_train_set(X_train, y_train, seed=42)
    for exp, (Xt, yt) in datasets.items():
        print(f'    Exp. {exp} : X_train {Xt.shape} | y_train {yt.shape}')

    # ── 6. VALIDATION DES RATIOS ──────────────────────────────────────────────
    print('\n[VAL] Validation préservation ratios cognitifs...')
    for grp_name, copies in [('Exp.B', copies_B), ('Exp.C', copies_C), ('Exp.D', copies_D)]:
        if len(copies) == 0: continue
        res = validate_augmentation(X_train, copies, label=grp_name)
        for ratio, r in res.items():
            ok = '✓' if r['ok'] else '✗'
            print(f'    {ok} {grp_name} | {ratio} : '
                  f'orig={r["orig"]:.3f} → aug={r["aug"]:.3f} | Δ={r["delta_%"]:.1f}%')

    # ── 7. SAUVEGARDE ─────────────────────────────────────────────────────────
    print(f'\n[SAVE] Sauvegarde dans {save_dir}...')
    save_augmented_datasets(datasets, X_val, y_val, X_test, y_test, outdir=save_dir)

    # ── 8. FIGURES ────────────────────────────────────────────────────────────
    print('\n[FIG] Génération des 9 figures...')
    fig1_split_overview(X_train, X_val, X_test, y_train, y_val, y_test, sid_train, outdir)
    print('  ✓ aug_01_split_overview.png')
    fig2_loso_schema(sids, outdir)
    print('  ✓ aug_02_loso_schema.png')
    fig3_augmentation_comparison(X_train, datasets, outdir)
    print('  ✓ aug_03_comparison_experiments.png')
    fig4_validation_ratios(X_train, copies_B, copies_C, copies_D, outdir)
    print('  ✓ aug_04_validation_ratios.png')
    fig5_dwt_bands(X_train, outdir)
    print('  ✓ aug_05_dwt_bands.png')
    fig6_magnitude_warping(X_train, outdir)
    print('  ✓ aug_06_magnitude_warping.png')
    fig7_dataset_growth(datasets, outdir)
    print('  ✓ aug_07_dataset_growth.png')
    fig8_usage_code(outdir)
    print('  ✓ aug_08_usage_guide.png')
    fig9_pipeline_final(outdir)
    print('  ✓ aug_09_pipeline_final.png')

    print(f'\n✅ Pipeline terminé — 9 figures + datasets sauvegardés dans : {outdir}')
    print(f'\n  ── UTILISATION DANS LE PROJET RÉEL ───────────────────────────')
    print(f'  from augmentation_eeg_final import split_by_subject, augment_train_set')
    print(f'  from augmentation_eeg_final import save_augmented_datasets, load_augmented_datasets')
    print(f'  ')
    print(f'  # Charger vos données réelles')
    print(f'  X, y, subject_ids = load_your_dataset()')
    print(f'  ')
    print(f'  # Séparer AVANT augmentation (obligatoire !)')
    print(f'  X_train, y_train, _, X_val, y_val, _, X_test, y_test, _ = \\')
    print(f'      split_by_subject(X, y, subject_ids)')
    print(f'  ')
    print(f'  # Augmenter UNIQUEMENT X_train')
    print(f'  datasets, copies_B, copies_C, copies_D = augment_train_set(X_train, y_train)')
    print(f'  ')
    print(f'  # Sauvegarder et utiliser')
    print(f'  save_augmented_datasets(datasets, X_val, y_val, X_test, y_test)')
    print(f'  data = load_augmented_datasets()')
    print(f'  X_tr_full, y_tr_full = data["FULL"]   # entraîner votre modèle ici')
    print(f'  X_val_eval, y_val_eval = data["val"]  # évaluer ici (NON augmenté)')

    return datasets, X_val, y_val, X_test, y_test


if __name__ == '__main__':
    run_augmentation_pipeline(state='concentration', outdir='Augmentation/outputs_augmentation')