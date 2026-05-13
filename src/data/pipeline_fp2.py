"""
=============================================================================
NeuroCap — Pipeline de Prétraitement EEG Monocanal Fp2 (AD8232 + ESP32)
=============================================================================
fait par    : Yasmine El Mkhantar
Encadrement : Monir El Azzouzi | Loubna El Rhali | Yassir Matrane
Structure   : Easy Medical Device — 2025-2026

Compatibilité matérielle (hardware) :
  - Électrode active : Fp2 (frontale droite)
  - Référence : mastoïde (M1/M2 combinés) – câblée en différentiel sur l'AD8232
  - Amplificateur : AD8232 (bruit de fond typique 10–20 µV RMS)
  - Convertisseur : ESP32 ADC 12 bits, 250 Hz
  - Filtrage temps réel sur ESP32 : HP 0.5 Hz + LP 40 Hz + notch 50 Hz (Butterworth ordre 4, zéro-phase)
  - Segmentation en ligne : fenêtres de 4 s, overlap 75 % (step = 250 éch.) → flux à 1 époque/seconde
  - Rejet d'epochs : amplitude crête-à-crête (PTP) > 500 µV (adapté au bruit AD8232)

Ce script réalise le prétraitement OFFLINE (post‑enregistrement) pour l'entraînement des modèles.
Il est compatible avec les fichiers CSV produits par le serveur WebSocket du hardware.
Il applique les mêmes filtres que le hardware, puis ajoute une DWT optionnelle pour un nettoyage
plus poussé, segmente selon les paramètres hardware (4s, 75%), rejette les époques de mauvaise
qualité (seuil 500 µV), normalise par z‑score par époque, extrait les features spectrales et
temporelles définies dans le cahier des charges NeuroCap.

Justification de chaque étape (état de l'art) :
  - HP 0.5 Hz : Chaudhary 2025, Acharya 2021 – élimine la dérive DC.
  - LP 40 Hz : Acharya 2021, Gaikwad 2017 – supprime l'EMG (>40 Hz) tout en conservant le gamma (30-40 Hz).
  - Notch 50 Hz Q=30 : Gaikwad 2017, CdC NeuroCap – élimine le bruit du secteur marocain.
  - DWT db4 + seuillage doux : Gaikwad 2017 (remplace ICA, impossible sur 1 canal).
  - Fenêtre de Hann : réduit les fuites spectrales avant calcul PSD.
  - Overlap 75 % : crée un flux quasi‑continu (1 mise à jour par seconde) pour le temps réel.
  - Seuil de rejet 500 µV : adapté au bruit de fond de l'AD8232 (contre 150 µV pour des datasets propres).
  - Z‑score par époque : Chaudhary 2025, Lawhern 2018 – compense la variabilité inter‑sujets.
  - Features : CdC Sec. 2.3, Samsa 2026, Salam 2026.
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from scipy import signal
import pywt
import os
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path


# ============================================================================
# CONSTANTES – Paramètres alignés sur le hardware NeuroCap (AD8232 + ESP32)
# ============================================================================

FS         = 250          # Fréquence d'échantillonnage (Hz) – identique hardware
EPOCH_S    = 4.0          # Durée de la fenêtre d'analyse (secondes) – conforme hardware (4 s)
OVERLAP    = 0.75         # Taux de recouvrement (75 %) → step = 250 éch. = 1 s
AMP_THR    = 500.0        # Seuil de rejet d'époque (µV) – adapté au bruit AD8232 (10‑20 µV RMS)
HP_FREQ    = 0.5          # Fréquence de coupure du filtre passe‑haut (Hz)
LP_FREQ    = 40.0         # Fréquence de coupure du filtre passe‑bas (Hz)
NOTCH_F    = 50.0         # Fréquence du filtre notch (réseau marocain)
WAVELET    = 'db4'        # Ondelette de Daubechies 4 (Gaikwad 2017)
DWT_LEV    = 4            # Niveau de décomposition DWT (à 250 Hz)

# Constantes dérivées (ne pas modifier)
EPOCH_SAMPLES = int(EPOCH_S * FS)               # = 1000 échantillons par époque
STEP = int(EPOCH_SAMPLES * (1 - OVERLAP))       # = 250 échantillons (1 seconde)

# Définition des bandes EEG et couleurs associées (pour les figures)
BAND_DEF = {
    'δ (0.5-4)':  (0.5, 4.0),
    'θ (4-8)':    (4.0, 8.0),
    'α (8-13)':   (8.0, 13.0),
    'β (13-30)':  (13.0, 30.0),
    'γ (30-40)':  (30.0, 40.0),
}
BAND_COLS = ['#9B59B6', '#3498DB', '#27AE60', '#E67E22', '#E74C3C']

# Palette de couleurs pour les graphiques
COL = dict(
    raw='#2C3E50', hp='#2980B9', lp='#1ABC9C', notch='#8E44AD',
    dwt='#27AE60', epoch='#E67E22', norm='#E74C3C',
    conc='#2980B9', stress='#E74C3C', relax='#27AE60',
    delta='#9B59B6', theta='#3498DB', alpha='#27AE60',
    beta='#E67E22', gamma='#E74C3C',
    dark='#1A2E5A', mid='#2E4D7B', light='#EEF3FA',
)


# ============================================================================
# FONCTIONS UTILITAIRES (helpers) – inchangées
# ============================================================================

def _psd(x, fs=FS, nperseg=256):
    """
    Calcule la densité spectrale de puissance (Welch) avec fenêtre de Hann.
    Pour une époque de 1000 points, nperseg=256 offre un bon compromis résolution/variance.
    """
    return signal.welch(x, fs, nperseg=nperseg, window='hann')

def _band_power(freqs, psd, flo, fhi):
    """Intègre la PSD sur une bande de fréquence donnée (méthode trapézoïdale)."""
    idx = (freqs >= flo) & (freqs <= fhi)
    return float(np.trapezoid(psd[idx], freqs[idx])) if idx.any() else 0.0

def _style(ax, title='', xlabel='', ylabel='', grid=True):
    """Applique un style standard aux axes matplotlib."""
    ax.set_facecolor('#FAFAFA')
    ax.grid(grid, alpha=0.25, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if title:
        ax.set_title(title, fontsize=9, fontweight='bold', color=COL['dark'], pad=5)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8, color='#555')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8, color='#555')
    ax.tick_params(labelsize=7, colors='#555')

def _shade_bands(ax, freqs_max=45):
    """Colore l'arrière‑plan avec les bandes EEG (δ, θ, α, β, γ)."""
    colors = ['#9B59B6','#3498DB','#27AE60','#E67E22','#E74C3C']
    limits = [(0.5,4),(4,8),(8,13),(13,30),(30,min(40,freqs_max))]
    for (f1,f2), c in zip(limits, colors):
        if f2 > freqs_max:
            f2 = freqs_max
        if f1 >= freqs_max:
            break
        ax.axvspan(f1, f2, alpha=0.06, color=c, zorder=0)

def _add_ref_tag(ax, text, color='#666', fs=7):
    """Ajoute une référence bibliographique en bas à droite du graphique."""
    ax.text(0.99, 0.02, text, transform=ax.transAxes, fontsize=fs,
            ha='right', va='bottom', color=color, style='italic',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))


# ============================================================================
# GÉNÉRATION D'UN SIGNAL SYNTHÉTIQUE (pour tests et démonstration)
# ============================================================================

def make_signal(state='concentration', dur=20, seed=42):
    """
    Génère un signal EEG synthétique Fp2 avec les signatures NeuroCap.
    Simule également les artefacts typiques (clignements oculaires, EMG, bruit 50 Hz)
    pour ressembler aux enregistrements réels du hardware.

    Paramètres :
        state : 'concentration', 'stress' ou 'relaxation'
        dur   : durée du signal en secondes (par défaut 20 s pour obtenir plusieurs époques de 4 s)
        seed  : graine aléatoire pour reproductibilité

    Retourne (t, signal) où t est le vecteur temps et signal le tableau des µV.
    """
    np.random.seed(seed)
    t = np.arange(0, dur, 1/FS)

    # Amplitudes des composantes sinusoïdales pour chaque état
    amps = {
        'concentration': dict(d=0.5, th=0.7, al=0.3, be=3.0, be2=2.5, ga=0.4),
        'stress':        dict(d=0.6, th=1.0, al=0.15, be=4.0, be2=3.5, ga=0.5),
        'relaxation':    dict(d=0.4, th=0.5, al=3.5, be=0.6, be2=0.4, ga=0.2),
    }[state]

    # Génération du signal propre (somme de sinusoïdes)
    eeg = (amps['d']  * np.sin(2*np.pi*2*t)
         + amps['th'] * np.sin(2*np.pi*6*t)
         + amps['al'] * np.sin(2*np.pi*10*t)
         + amps['be'] * np.sin(2*np.pi*20*t)
         + amps['be2']* np.sin(2*np.pi*26*t)
         + amps['ga'] * np.sin(2*np.pi*35*t)) * 12

    # Bruit blanc (bruit de fond du capteur)
    eeg += np.random.randn(len(t)) * 2.5

    # Artefacts musculaires (EMG) – brèves impulsions de haute amplitude
    for _ in range(3):
        s = np.random.randint(int(0.8*FS), len(t)-int(0.8*FS))
        emg = np.random.randn(int(0.25*FS)) * 35
        eeg[s:s+len(emg)] += emg

    # Artefacts de clignement oculaire (très sensibles sur Fp2, amplitude ~100-200 µV)
    for _ in range(5):
        bp = np.random.randint(int(0.5*FS), len(t)-int(0.5*FS))
        bd = int(0.15*FS)
        eeg[bp:bp+bd] += np.hanning(bd) * np.random.uniform(120, 200)

    # Bruit secteur 50 Hz (réseau marocain)
    eeg += 2.0 * np.sin(2*np.pi*50*t + np.random.uniform(0, 2*np.pi))

    return t, eeg.astype(np.float64)


# ============================================================================
# ÉTAPES DU PIPELINE DE PRÉTRAITEMENT (compatibles hardware)
# ============================================================================

def step2_highpass(sig, fc=HP_FREQ, order=4):
    """
    Filtre passe‑haut Butterworth, zéro‑phase (filtfilt).
    Élimine la dérive continue et les mouvements lents (<0.5 Hz).
    Justifié par Chaudhary (2025) et Acharya (2021).
    Paramètres identiques à ceux implémentés sur l'ESP32.
    """
    b, a = signal.butter(order, fc/(FS/2), btype='high')
    return signal.filtfilt(b, a, sig)

def step3_lowpass(sig, fc=LP_FREQ, order=4):
    """
    Filtre passe‑bas Butterworth, zéro‑phase.
    Supprime les artéfacts EMG (>40 Hz) tout en conservant la bande gamma (30-40 Hz).
    Justifié par Acharya (2021) et Gaikwad (2017).
    Paramètres identiques au hardware.
    """
    b, a = signal.butter(order, fc/(FS/2), btype='low')
    return signal.filtfilt(b, a, sig)

def step4_notch(sig, f0=NOTCH_F, q=30.0):
    """
    Filtre coupe‑bande (notch) à 50 Hz, facteur de qualité Q=30.
    Élimine le bruit du réseau électrique marocain.
    Justifié par le cahier des charges NeuroCap et Gaikwad (2017).
    Paramètres identiques au hardware.
    """
    b, a = signal.iirnotch(f0/(FS/2), q)
    return signal.filtfilt(b, a, sig)

def step5_dwt(sig, wavelet=WAVELET, level=DWT_LEV):
    """
    Suppression des artéfacts résiduels par transformée en ondelettes discrète (DWT)
    avec seuillage doux (Donoho-Johnstone).
    Remplace l'ICA (impossible sur un seul canal). Validée sur Fp1/Fp2/Fpz par Gaikwad (2017).
    Cette étape n'est PAS présente dans le pipeline temps réel du hardware (pour des raisons
    de latence), mais elle est utile pour le post‑traitement offline (entraînement des modèles).
    """
    coeffs = pywt.wavedec(sig, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745   # estimateur robuste du bruit
    thr = sigma * np.sqrt(2 * np.log(len(sig)))       # seuil universel
    new_c = [coeffs[0]] + [pywt.threshold(c, thr, mode='soft') for c in coeffs[1:]]
    rec = pywt.waverec(new_c, wavelet)
    return rec[:len(sig)]   # rec peut être plus long d'un échantillon → troncature

def step6_reject(sig, thr=AMP_THR):
    """
    Marque les échantillons dont l'amplitude dépasse le seuil (PTP > thr).
    Pour le hardware, thr = 500 µV (tolérance au bruit AD8232).
    Retourne un masque booléen et le pourcentage d'échantillons contaminés.
    """
    mask = np.abs(sig) > thr
    return mask, float(mask.mean() * 100)

def step7_segment(sig, epoch_samples=EPOCH_SAMPLES, step=STEP, win_type='hann', amp_thr=AMP_THR):
    """
    Segmentation du signal en époques glissantes.
    Paramètres hardware : epoch_samples = 1000 (4 s), step = 250 (75 % d'overlap).
    Application d'une fenêtre de Hann (réduit les fuites spectrales avant FFT).
    Chaque époque est étiquetée 'valide' ou 'rejeté' selon que son amplitude maximale
    dépasse le seuil amp_thr.
    Justification : overlap 75 % donne un flux quasi‑continu (1 époque/seconde) pour
    le temps réel (Acharya 2021).
    """
    win = np.hanning(epoch_samples) if win_type == 'hann' else np.ones(epoch_samples)
    epochs, statuses, t0s = [], [], []
    for i in range(0, len(sig) - epoch_samples + 1, step):
        ep = sig[i:i+epoch_samples]
        epochs.append(ep * win)
        statuses.append('rejeté' if np.max(np.abs(ep)) > amp_thr else 'valide')
        t0s.append(i / FS)
    return np.array(epochs), statuses, t0s

def step8_zscore(epochs):
    """
    Normalisation z‑score par époque indépendante.
    Chaque époque est centrée réduite : (x - μ) / σ.
    Utilisée pour l'entraînement des modèles (EEGNet, SVM, etc.).
    Justification : Chaudhary (2025), Lawhern (2018).
    """
    out = np.zeros_like(epochs)
    for i, ep in enumerate(epochs):
        s = ep.std()
        out[i] = (ep - ep.mean()) / (s if s > 1e-10 else 1.0)
    return out

def step9_features(epochs, statuses):
    """
    Extraction des features sur les époques valides uniquement.
    Features calculées :
      - Puissances absolues des bandes δ, θ, α, β, γ (intégrale PSD)
      - Ratios cognitifs : TBR (θ/β), ABR (α/β), EI (β/(α+θ)), TAR (θ/α)
      - Paramètres Hjorth : Activity, Mobility, Complexity
      - Features légères : Power, MeanAmp, RelEnergy (β/total)
    Sources : CdC NeuroCap Sec. 2.3, Samsa & Altıntop 2026, Salam et al. 2026.
    """
    out = []
    for ep, st in zip(epochs, statuses):
        if st != 'valide':
            continue
        f, psd = _psd(ep)
        pd = _band_power(f, psd, 0.5, 4.0)
        pt = _band_power(f, psd, 4.0, 8.0)
        pa = _band_power(f, psd, 8.0, 13.0)
        pb = _band_power(f, psd, 13.0, 30.0)
        pg = _band_power(f, psd, 30.0, 40.0)
        tot = pd + pt + pa + pb + pg + 1e-12
        tbr = pt / (pb + 1e-12)
        abr = pa / (pb + 1e-12)
        ei = pb / (pa + pt + 1e-12)
        tar = pt / (pa + 1e-12)
        # Hjorth
        d1 = np.diff(ep)
        d2 = np.diff(d1)
        act = float(np.var(ep))
        mob = float(np.std(d1) / (np.std(ep) + 1e-12))
        cmp = float((np.std(d2) / (np.std(d1) + 1e-12)) / (mob + 1e-12))
        out.append(dict(
            Pd=pd, Pt=pt, Pa=pa, Pb=pb, Pg=pg,
            TBR=tbr, ABR=abr, EI=ei, TAR=tar,
            Act=act, Mob=mob, Cmp=cmp,
            Power=float(np.mean(ep**2)),
            MeanAmp=float(np.mean(np.abs(ep))),
            RelEnergy=pb/tot,
        ))
    return out


# ============================================================================
# CHARGEMENT DE DONNÉES RÉELLES PROVENANT DU HARDWARE (fichier CSV)
# ============================================================================

def load_hardware_csv(filepath):
    """
    Lit un fichier CSV produit par le serveur WebSocket du hardware NeuroCap.
    Format attendu : chaque ligne contient "timestamp,value" (ou "timestamp,value,quality").
    La valeur est supposée être en µV (déjà convertie par le firmware).
    Retourne (t, signal) où t est le temps relatif en secondes et signal le tableau des µV.
    """
    import pandas as pd
    df = pd.read_csv(filepath, header=None, names=['timestamp', 'value'], usecols=[0,1])
    t = df['timestamp'].values - df['timestamp'].iloc[0]   # temps relatif
    sig = df['value'].values.astype(np.float64)
    return t, sig


# ============================================================================
# PIPELINE COMPLET POUR UN SIGNAL (réel ou synthétique)
# ============================================================================

def preprocess_signal(sig, fs=FS, apply_dwt=True, amp_thr=AMP_THR):
    """
    Applique la chaîne de prétraitement complète (identique au hardware, plus DWT optionnelle).
    Étapes :
      1. Filtrage HP 0.5 Hz
      2. Filtrage LP 40 Hz
      3. Notch 50 Hz
      4. (Optionnel) DWT pour suppression d'artéfacts
      5. Segmentation en époques (4 s, overlap 75 %)
      6. Rejet des époques selon seuil d'amplitude
      7. Normalisation z‑score par époque
      8. Extraction des features

    Retourne (epochs_norm, statuses, features_list)
    """
    # Filtrage (identique hardware)
    sig_filt = step2_highpass(sig)
    sig_filt = step3_lowpass(sig_filt)
    sig_filt = step4_notch(sig_filt)

    # DWT optionnelle (offline seulement)
    if apply_dwt:
        sig_clean = step5_dwt(sig_filt)
    else:
        sig_clean = sig_filt

    # Segmentation (paramètres hardware)
    epochs, statuses, t0s = step7_segment(sig_clean, amp_thr=amp_thr)

    # Normalisation
    epochs_norm = step8_zscore(epochs)

    # Extraction des features
    features = step9_features(epochs_norm, statuses)

    return epochs_norm, statuses, features


# ============================================================================
# FONCTIONS DE VISUALISATION (mises à jour pour refléter les paramètres hardware)
# ============================================================================

def fig0_raw(t, raw, state, outdir):
    """Figure 0 : signal brut Fp2 (avant tout traitement) avec PSD."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), facecolor='white')
    fig.suptitle(
        f'ÉTAPE 0 — Signal EEG Brut Fp2  •  Référence M1/M2  •  État simulé : {state.upper()}\n'
        f'Signal non traité — artefacts visibles : clignements oculaires, EMG, bruit 50 Hz\n'
        f'Hardware : AD8232 + ESP32, fs={FS} Hz',
        fontsize=11, fontweight='bold', color=COL['dark'])

    ax1.plot(t, raw, color=COL['raw'], lw=0.7, alpha=0.9, label='Signal brut Fp2')
    for thr in [AMP_THR, -AMP_THR]:
        ax1.axhline(thr, color=COL['stress'], ls='--', lw=1.3, alpha=0.7,
                    label=f'± {AMP_THR} µV (seuil rejet hardware)' if thr > 0 else '')
    mask = np.abs(raw) > AMP_THR
    if mask.any():
        ax1.fill_between(t, raw.min()-5, raw.max()+5, where=mask,
                         color=COL['stress'], alpha=0.12, label=f'Artefacts > {AMP_THR} µV')
    _style(ax1, 'Domaine temporel — Signal brut Fp2 (avant tout prétraitement)', 'Temps (s)', 'Amplitude (µV)')
    ax1.legend(fontsize=8, loc='upper right')
    _add_ref_tag(ax1, f'Prototype NeuroCap | f_s = {FS} Hz | Seuil rejet = {AMP_THR} µV')

    f, psd = _psd(raw, nperseg=512)
    ax2.semilogy(f[f<=60], psd[f<=60], color=COL['raw'], lw=1.5, label='PSD brute')
    ax2.axvline(50, color=COL['stress'], ls='--', lw=1.5, alpha=0.8, label='50 Hz (réseau MAR)')
    _shade_bands(ax2, 60)
    for bname, (f1,f2), bc in zip(BAND_DEF, BAND_DEF.values(), BAND_COLS):
        ax2.text((f1+f2)/2, ax2.get_ylim()[0]*1.5 if ax2.get_ylim()[0]>0 else 1e-6,
                 bname.split()[0], ha='center', fontsize=7, color=bc)
    _style(ax2, 'PSD Welch — Signal brut (pic 50 Hz visible = bruit réseau marocain)',
           'Fréquence (Hz)', 'PSD (µV²/Hz) [log]')
    ax2.legend(fontsize=8)
    _add_ref_tag(ax2, 'Chaudhary 2025 (PREP-1)')
    plt.tight_layout()
    p = os.path.join(outdir, '00_signal_brut_fp2.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig1_filtering(t, raw, hp, lp, notch, outdir):
    """Figure 1 : étapes de filtrage (HP, LP, notch) avec signaux temporels et PSD."""
    fig = plt.figure(figsize=(18, 14), facecolor='white')
    fig.suptitle(
        'ÉTAPES 2-4 — Pipeline de Filtrage Hardware  ·  HP 0.5 Hz → LP 40 Hz → Notch 50 Hz\n'
        'Butterworth ordre 4, zéro-phase (filtfilt) — pas de distorsion de phase\n'
        'Ref : Kołodziej 2016 (PREP-4) | Chaudhary 2025 (PREP-1) | Acharya 2021 (PREP-2)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    sigs  = [(raw,   COL['raw'],   'Étape 0 — Brut (Fp2)',     'Signal brut + artefacts EMG + 50 Hz'),
             (hp,    COL['hp'],    'Étape 2 — HP 0.5 Hz',      'Dérive DC et δ<0.5 Hz supprimés'),
             (lp,    COL['lp'],    'Étape 3 — LP 40 Hz',       'EMG (>40 Hz) éliminé'),
             (notch, COL['notch'], 'Étape 4 — Notch 50 Hz',    'Bruit réseau marocain supprimé')]

    gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.52, wspace=0.32)

    for row, (sig, col, etape, desc) in enumerate(sigs):
        ax_t = fig.add_subplot(gs[row, 0])
        ax_t.plot(t, sig, color=col, lw=0.7, alpha=0.9)
        ax_t.axhline(AMP_THR,  color=COL['stress'], ls='--', lw=0.9, alpha=0.5)
        ax_t.axhline(-AMP_THR, color=COL['stress'], ls='--', lw=0.9, alpha=0.5)
        _style(ax_t, f'{etape} — Temporel', 'Temps (s)', 'µV')
        ax_t.text(0.02, 0.95, desc, transform=ax_t.transAxes,
                  fontsize=7.5, color='#555', va='top')

        ax_f = fig.add_subplot(gs[row, 1])
        fr, psd = _psd(sig, nperseg=512)
        mask = fr <= 60
        ax_f.semilogy(fr[mask], psd[mask], color=col, lw=1.5)
        ax_f.axvline(50,      color=COL['stress'], ls='--', lw=1.2, alpha=0.8)
        ax_f.axvline(LP_FREQ, color=COL['lp'],     ls=':',  lw=1.2, alpha=0.8)
        ax_f.axvline(HP_FREQ, color=COL['hp'],     ls=':',  lw=1.2, alpha=0.8)
        _shade_bands(ax_f, 60)
        _style(ax_f, f'{etape} — PSD Welch', 'Fréquence (Hz)', 'µV²/Hz [log]')

    refs = ['Kołodziej 2016 (PREP-4)',
            'Chaudhary 2025 (PREP-1) | Acharya 2021 (PREP-2)',
            'Acharya 2021 (PREP-2) | Gaikwad 2017 (N°3)',
            'CdC NeuroCap Sec.2.1 | Gaikwad 2017 (N°3)']
    for row, ref in enumerate(refs):
        _add_ref_tag(fig.add_subplot(gs[row, 1]), ref)

    p = os.path.join(outdir, '01_filtrage_complet.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig2_dwt(t, before, after, outdir):
    """Figure 2 : effet de la DWT (suppression d'artéfacts)."""
    fig, axes = plt.subplots(3, 2, figsize=(18, 13), facecolor='white')
    fig.suptitle(
        'ÉTAPE 5 — Suppression d\'Artefacts par DWT (Daubechies db4, Niveau 4, Seuillage Doux)\n'
        'Remplace l\'ICA — IMPOSSIBLE sur monocanal Fp2 (matrice de mélange non définie)\n'
        'Ref : Gaikwad & Paithane (2017, N°3) — validée Fp1/Fp2/Fpz  |  σ = MAD/0.6745 (Donoho-Johnstone)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    # Temporel avant/après
    axes[0,0].plot(t, before, color=COL['notch'], lw=0.7, alpha=0.9)
    axes[0,0].axhline( AMP_THR, color=COL['stress'], ls='--', lw=1, alpha=0.6)
    axes[0,0].axhline(-AMP_THR, color=COL['stress'], ls='--', lw=1, alpha=0.6)
    _style(axes[0,0], 'Avant DWT — artefacts résiduels visibles', 'Temps (s)', 'µV')
    _add_ref_tag(axes[0,0], 'Entrée DWT (après notch 50 Hz)')

    axes[0,1].plot(t, after, color=COL['dwt'], lw=0.7, alpha=0.9)
    axes[0,1].axhline( AMP_THR, color=COL['stress'], ls='--', lw=1, alpha=0.6)
    axes[0,1].axhline(-AMP_THR, color=COL['stress'], ls='--', lw=1, alpha=0.6)
    _style(axes[0,1], 'Après DWT — artefacts supprimés', 'Temps (s)', 'µV')
    _add_ref_tag(axes[0,1], 'Sortie DWT (db4, niveau 4, seuillage doux)')

    # PSD avant/après superposées
    for ax, sig, col, lbl in [(axes[1,0], before, COL['notch'], 'Avant DWT'),
                               (axes[1,1], after,  COL['dwt'],   'Après DWT')]:
        fr, psd = _psd(sig, nperseg=512)
        m = fr <= 60
        ax.semilogy(fr[m], psd[m], color=col, lw=1.5, label=lbl)
        _shade_bands(ax, 60)
        _style(ax, f'PSD — {lbl}', 'Fréquence (Hz)', 'µV²/Hz [log]')
        _add_ref_tag(ax, 'Gaikwad & Paithane 2017 (N°3)')

    # Coefficients DWT
    coeffs = pywt.wavedec(before, WAVELET, level=DWT_LEV)
    names  = [f'cA{DWT_LEV}'] + [f'cD{DWT_LEV-i}' for i in range(DWT_LEV)]
    cols_c = ['#2C3E50','#9B59B6','#3498DB','#27AE60','#E67E22']
    for j, (c, nm, col) in enumerate(zip(coeffs, names, cols_c)):
        axes[2,0].plot(c[:120] + j*15, color=col, lw=0.9, alpha=0.85, label=nm)
    _style(axes[2,0], 'Coefficients DWT db4 (avant seuillage)',
           'Échantillons', 'Valeur (décalés pour lisibilité)')
    axes[2,0].legend(fontsize=8, ncol=5, loc='upper right')
    _add_ref_tag(axes[2,0], 'Niveau 4 → artefacts clignements concentrés niv. 3-4')

    # Différence = artefacts supprimés
    diff = before - after
    axes[2,1].plot(t, diff, color=COL['stress'], lw=0.8, alpha=0.85)
    axes[2,1].fill_between(t, diff, 0, where=(np.abs(diff) > 5),
                           color=COL['stress'], alpha=0.12)
    _style(axes[2,1], 'Différence (Avant − Après DWT) = Artefacts supprimés',
           'Temps (s)', 'µV')
    _add_ref_tag(axes[2,1], 'Clignements + EMG résiduel éliminés')

    fig.text(0.5, 0.01,
             '★  Note ICA : L\'ICA nécessite ≥ 4 canaux — non applicable sur Fp2 monocanal. '
             'La DWT (db4) est l\'alternative validée (Gaikwad & Paithane, 2017, N°3).',
             ha='center', fontsize=9, color=COL['stress'], style='italic',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDEDEC', alpha=0.9, edgecolor=COL['stress']))
    plt.tight_layout(rect=[0,0.04,1,1])
    p = os.path.join(outdir, '02_DWT_artefacts.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig3_segmentation(t, sig, epochs, statuses, t0s, outdir):
    """Figure 3 : segmentation en époques (4 s, overlap 75 %, seuil 500 µV)."""
    ep_n = EPOCH_SAMPLES
    t_ep = np.arange(ep_n) / FS * 1000   # temps en ms pour l'affichage

    n_valid = sum(1 for s in statuses if s == 'valide')
    n_rej = len(statuses) - n_valid

    fig, axes = plt.subplots(2, 2, figsize=(18, 10), facecolor='white')
    fig.suptitle(
        f'ÉTAPES 6-7 — Rejet Amplitude > {AMP_THR} µV  +  Segmentation {EPOCH_S} s (Overlap {OVERLAP*100:.0f} %, Fenêtre Hann)\n'
        f'{len(statuses)} epochs total  |  {n_valid} valides  |  {n_rej} rejetés ({n_rej/len(statuses)*100:.1f} %)  |  {ep_n} éch./epoch @ {FS} Hz\n'
        'Ref : Chaudhary 2025 (PREP-1) | CdC NeuroCap Sec. 2.1 | Acharya 2021 (PREP-2)',
        fontsize=10, fontweight='bold', color=COL['dark'])

    # Signal avec zones colorées (epochs)
    ax = axes[0,0]
    ax.plot(t, sig, color=COL['dwt'], lw=0.7, alpha=0.8, label='Signal propre')
    ax.axhline( AMP_THR, color=COL['stress'], ls='--', lw=1.3, alpha=0.8, label=f'± {AMP_THR} µV')
    ax.axhline(-AMP_THR, color=COL['stress'], ls='--', lw=1.3, alpha=0.8)
    for t0, st in list(zip(t0s, statuses))[:20]:
        col = '#27AE60' if st == 'valide' else '#E74C3C'
        ax.axvspan(t0, t0+EPOCH_S, alpha=0.07, color=col)
    p_v = mpatches.Patch(color='#27AE60', alpha=0.4, label='Epoch valide')
    p_r = mpatches.Patch(color='#E74C3C', alpha=0.4, label='Epoch rejeté')
    ax.legend(handles=[p_v, p_r], fontsize=8)
    _style(ax, f'Signal avec epochs segmentés (fenêtres {EPOCH_S} s, overlap {OVERLAP*100:.0f} %)', 'Temps (s)', 'µV')
    _add_ref_tag(ax, f'Overlap {OVERLAP*100:.0f} % → flux continu (Acharya 2021)')

    # Superposition des époques valides
    ax2 = axes[0,1]
    valid_eps = [(epochs[i], t0s[i]) for i, s in enumerate(statuses) if s == 'valide'][:8]
    cmap = plt.cm.Blues(np.linspace(0.4, 0.95, len(valid_eps)))
    for (ep, _), col in zip(valid_eps, cmap):
        ax2.plot(t_ep, ep, color=col, lw=0.8, alpha=0.85)
    _style(ax2, f'Epochs valides (fenêtre de Hann)\n→ {ep_n} éch. = {EPOCH_S*1000:.0f} ms', 'Temps (ms)', 'µV')
    _add_ref_tag(ax2, f'Hardware : {EPOCH_S} s, step={STEP} éch.')

    # Distribution des amplitudes maximales
    ax3 = axes[1,0]
    max_a = [np.max(np.abs(epochs[i])) for i in range(len(epochs))]
    bar_c = ['#27AE60' if a <= AMP_THR else '#E74C3C' for a in max_a]
    ax3.bar(range(len(max_a)), max_a, color=bar_c, alpha=0.75, width=1.0, edgecolor='none')
    ax3.axhline(AMP_THR, color=COL['stress'], ls='--', lw=2, label=f'Seuil {AMP_THR} µV')
    ax3.legend(fontsize=9)
    _style(ax3, f'Amplitude maximale par epoch — critère de rejet > {AMP_THR} µV',
           'Numéro d\'epoch', 'Amplitude max (µV)')
    _add_ref_tag(ax3, 'Seuil adapté à l\'AD8232 (bruit 10‑20 µV RMS)')

    # Statistiques
    ax4 = axes[1,1]
    cats = ['Epochs\nvalides', 'Epochs\nrejetés', 'Taux de\nrejet (%)']
    vals = [n_valid, n_rej, round(n_rej/len(statuses)*100, 1)]
    bcols = ['#27AE60', '#E74C3C', '#E67E22']
    bars = ax4.bar(cats, vals, color=bcols, alpha=0.85, edgecolor='white', linewidth=2, width=0.5)
    for bar, v in zip(bars, vals):
        ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.4, str(v),
                 ha='center', va='bottom', fontsize=13, fontweight='bold')
    _style(ax4, 'Statistiques de segmentation', '', 'Nombre / Pourcentage')
    ax4.grid(False)
    _add_ref_tag(ax4, f'Hardware : {EPOCH_S} s, overlap {OVERLAP*100:.0f} %')

    plt.tight_layout()
    p = os.path.join(outdir, '03_segmentation.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p



def fig4_zscore(epochs, epochs_n, statuses, outdir):
    """Figure 4 : normalisation z‑score par époque."""
    ep_n = EPOCH_SAMPLES
    t_ep = np.arange(ep_n) / FS * 1000
    vidx = [i for i, s in enumerate(statuses) if s == 'valide']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10), facecolor='white')
    fig.suptitle(
        'ÉTAPE 8 — Normalisation Z-Score par Epoch\n'
        'µ → 0 | σ → 1  •  appliqué individuellement par epoch (compense variabilité inter-sujets)\n'
        'Ref : Chaudhary 2025 (PREP-1) | Mynoddin 2025 (Art. 1.5 Brain2Vec) | Salam 2026 (N°15)',
        fontsize=10, fontweight='bold', color=COL['dark'])

    # Avant normalisation
    for ep in [epochs[i] for i in vidx[:7]]:
        axes[0,0].plot(t_ep, ep, lw=0.7, alpha=0.7)
    _style(axes[0,0], 'Avant Z-score — epochs bruts (µV)', 'Temps (ms)', 'µV')
    _add_ref_tag(axes[0,0], 'Avant normalisation')

    # Après normalisation
    for ep in [epochs_n[i] for i in vidx[:7]]:
        axes[0,1].plot(t_ep, ep, lw=0.7, alpha=0.7)
    axes[0,1].axhline(0, color='#2C3E50', ls='--', lw=1, alpha=0.5)
    axes[0,1].axhline(2, color='#888', ls=':', lw=0.8, alpha=0.4)
    axes[0,1].axhline(-2, color='#888', ls=':', lw=0.8, alpha=0.4)
    _style(axes[0,1], 'Après Z-score — adimensionnel (σ)', 'Temps (ms)', 'Z-score (σ)')
    _add_ref_tag(axes[0,1], 'Après normalisation — µ=0, σ=1')

    # Distributions des moyennes et écarts-types
    mu_b = [epochs[i].mean() for i in vidx]
    mu_a = [epochs_n[i].mean() for i in vidx]
    sig_b = [epochs[i].std() for i in vidx]
    sig_a = [epochs_n[i].std() for i in vidx]

    def safe_hist(ax, data_b, data_a, xlabel, title):
        if len(data_b) == 0 or len(data_a) == 0:
            return
        # Déterminer les limites communes pour les bins
        all_data = np.concatenate([data_b, data_a])
        min_val = np.min(all_data)
        max_val = np.max(all_data)
        if min_val == max_val:
            min_val -= 0.5
            max_val += 0.5
        bins = np.linspace(min_val, max_val, 11)  # 10 bins
        ax.hist(data_b, bins=bins, color=COL['hp'], alpha=0.7, label='Avant')
        ax.hist(data_a, bins=bins, color=COL['stress'], alpha=0.7, label='Après')
        ax.axvline(0, color='black', ls='--', lw=1.5)
        _style(ax, title, xlabel, 'Fréquence')
        ax.legend(fontsize=9)

    safe_hist(axes[0,2], mu_b, mu_a, 'Moyenne (µV / σ)', 'Distribution des moyennes par epoch')

    axes[1,0].remove()
    axes[1,0] = fig.add_subplot(2,3,4)
    safe_hist(axes[1,0], sig_b, sig_a, 'Écart-type', 'Distribution des écarts-types par epoch')
    axes[1,0].axvline(1, color='black', ls='--', lw=1.5, label='σ=1')
    axes[1,0].legend(fontsize=9)

    # SNR avant/après
    snr_b = [10*np.log10(np.var(epochs[i])/(np.var(np.diff(epochs[i]))+1e-12)) for i in vidx]
    snr_a = [10*np.log10(np.var(epochs_n[i])/(np.var(np.diff(epochs_n[i]))+1e-12)) for i in vidx]
    axes[1,1].plot(snr_b, 'o-', ms=3, color=COL['hp'], lw=1, label='Avant Z-score')
    axes[1,1].plot(snr_a, 's-', ms=3, color=COL['stress'], lw=1, label='Après Z-score')
    _style(axes[1,1], 'SNR par epoch (avant vs après normalisation)', 'Epoch', 'SNR (dB)')
    axes[1,1].legend(fontsize=9)
    _add_ref_tag(axes[1,1], 'Z-score préserve le SNR relatif')

    # Tableau récapitulatif
    axes[1,2].axis('off')
    rows = [['Statistique', 'Avant', 'Après Z-score'],
            ['Moyenne moy.', f'{np.mean(mu_b):.2f} µV', f'{np.mean(mu_a):.5f} ≈ 0'],
            ['σ moyen', f'{np.mean(sig_b):.2f} µV', f'{np.mean(sig_a):.4f} ≈ 1'],
            ['Min / Max', f'{min(mu_b):.1f} / {max(mu_b):.1f}', f'{min(mu_a):.3f} / {max(mu_a):.3f}'],
            ['Objectif', 'Variable inter-sujets', 'µ=0, σ=1 (uniforme)']]
    tbl = axes[1,2].table(cellText=rows[1:], colLabels=rows[0], loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(9.5); tbl.scale(1.15, 2.0)
    for j in range(3):
        tbl[0,j].set_facecolor(COL['dark']); tbl[0,j].set_text_props(color='white', fontweight='bold')
    for i in range(1,5):
        for j in range(3):
            tbl[i,j].set_facecolor(COL['light'] if i%2==0 else 'white')
    axes[1,2].set_title('Résumé statistique Z-score', fontsize=9, fontweight='bold',
                        color=COL['dark'], pad=55)

    plt.tight_layout()
    p = os.path.join(outdir, '04_zscore_normalisation.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close()
    return p


def fig5_features(feats, state, outdir):
    """Figure 5 : extraction des features (puissances spectrales, ratios, Hjorth, etc.)."""
    if not feats:
        return None
    fig = plt.figure(figsize=(20, 14), facecolor='white')
    fig.suptitle(
        f'ÉTAPE 9 — Features EEG Extraites sur Fp2  •  État : {state.upper()}\n'
        'PSD Welch (δ θ α β γ)  ·  Ratios cognitifs NeuroCap (TBR, ABR, EI, TAR)  '
        '·  Hjorth (Act, Mob, Cmp)  ·  Power / MeanAmp / RelEnergy\n'
        'Ref : CdC NeuroCap Sec. 2.3 (Table 2.2) | Samsa 2026 (N°17) | Salam 2026 (N°15)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.52, wspace=0.38)

    # 1. Puissances de bande
    ax1 = fig.add_subplot(gs[0, :2])
    bkeys = ['Pd','Pt','Pa','Pb','Pg']
    blbls = ['δ (0.5-4 Hz)','θ (4-8 Hz)','α (8-13 Hz)','β (13-30 Hz)','γ (30-40 Hz)']
    bmeans = [np.mean([f[k] for f in feats]) for k in bkeys]
    bstds = [np.std([f[k] for f in feats]) for k in bkeys]
    bars = ax1.bar(blbls, bmeans, color=BAND_COLS, alpha=0.85,
                   yerr=bstds, capsize=6, error_kw=dict(lw=1.5), edgecolor='white', lw=2)
    for bar, v in zip(bars, bmeans):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(bstds)*0.1,
                 f'{v:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    _style(ax1, f'Puissance Spectrale par Bande (Welch PSD) — {state.upper()}',
           '', 'Puissance (µV²/Hz)')
    _add_ref_tag(ax1, 'CdC NeuroCap Sec. 2.3 | Katmah 2021 (N°12)')

    # 2. Ratios cognitifs
    ax2 = fig.add_subplot(gs[0, 2])
    rkeys = ['TBR','ABR','EI','TAR']
    rlbls = ['TBR\nθ/β','ABR\nα/β','EI\nβ/(α+θ)','TAR\nθ/α']
    rcols = [COL['theta'],COL['alpha'],COL['beta'],COL['delta']]
    rmeans = [np.mean([f[k] for f in feats]) for k in rkeys]
    rstds = [np.std([f[k] for f in feats]) for k in rkeys]
    ax2.bar(rlbls, rmeans, color=rcols, alpha=0.85, yerr=rstds, capsize=5,
            edgecolor='white', lw=2)
    ax2.axhline(0.8, color=COL['dark'], ls='--', lw=1.5, alpha=0.8, label='TBR<0.8 (conc.)')
    ax2.axhline(0.7, color=COL['stress'], ls=':', lw=1.5, alpha=0.8, label='EI>0.7 (conc.)')
    ax2.legend(fontsize=8)
    _style(ax2, 'Ratios Cognitifs\nSignatures CdC NeuroCap', '', 'Ratio')
    _add_ref_tag(ax2, 'CdC Sec.2.5.1 | Salam 2026 (N°15)')

    # 3. Évolution temporelle TBR & EI
    ax3 = fig.add_subplot(gs[1, :2])
    tbrs = [f['TBR'] for f in feats]
    eis = [f['EI'] for f in feats]
    tars = [f['TAR'] for f in feats]
    ax3b = ax3.twinx()
    l1, = ax3.plot(tbrs, color=COL['theta'], lw=1.8, marker='o', ms=3.5, label='TBR (θ/β)')
    l2, = ax3b.plot(eis, color=COL['beta'], lw=1.8, marker='s', ms=3.5, label='EI (β/(α+θ))')
    l3, = ax3.plot(tars, color=COL['delta'], lw=1.4, ls='--', alpha=0.7, label='TAR (θ/α)')
    ax3.axhline(0.8, color=COL['theta'], ls=':', lw=1, alpha=0.5)
    ax3b.axhline(0.7, color=COL['beta'], ls=':', lw=1, alpha=0.5)
    _style(ax3, f'Évolution temporelle TBR et EI — {state.upper()}\n'
                'Cible NeuroCap concentration : TBR < 0.8  ET  EI > 0.7',
           'Numéro d\'epoch', 'TBR / TAR')
    ax3b.set_ylabel('EI', fontsize=8, color=COL['beta'])
    ax3.legend(handles=[l1, l2, l3], fontsize=8, loc='upper right')
    _add_ref_tag(ax3, 'CdC NeuroCap Sec. 2.5.1 | Salam 2026 (N°15) TAR p<0.001')

    # 4. Paramètres Hjorth
    ax4 = fig.add_subplot(gs[1, 2])
    hkeys = ['Act','Mob','Cmp']
    hlbls = ['Activity\n(variance)', 'Mobility\nstd(diff)/std', 'Complexity']
    hcols = ['#1ABC9C','#F39C12','#C0392B']
    hmeans = [np.mean([f[k] for f in feats]) for k in hkeys]
    hstds = [np.std([f[k] for f in feats]) for k in hkeys]
    ax4.bar(hlbls, hmeans, color=hcols, alpha=0.85, yerr=hstds, capsize=5, edgecolor='white', lw=2)
    _style(ax4, 'Paramètres Hjorth\n(Activité, Mobilité, Complexité)', '', 'Valeur')
    _add_ref_tag(ax4, 'CdC NeuroCap Sec.2.3 Table 2.2')

    # 5. Features légères (Power, MeanAmp, RelEnergy)
    ax5 = fig.add_subplot(gs[2, :2])
    pows = [f['Power'] for f in feats]
    mamps = [f['MeanAmp'] for f in feats]
    rels = [f['RelEnergy'] for f in feats]
    ax5b = ax5.twinx()
    ax5.plot(pows, color='#2980B9', lw=1.6, marker='.', ms=3, label='Power (µV²)')
    ax5.plot(mamps, color='#27AE60', lw=1.6, marker='.', ms=3, label='MeanAmp (µV)')
    ax5b.plot(rels, color=COL['stress'], lw=1.6, ls='--', marker='.', ms=3, label='RelEnergy β')
    _style(ax5, '3 Features Clés Embarquées — Samsa & Altıntop (2026, N°17) : 3 features → 86.25 % accuracy\n'
                'Calcul < 5 ms — compatibles contrainte latence NeuroCap < 500 ms',
           'Numéro d\'epoch', 'Power / MeanAmp')
    ax5b.set_ylabel('RelEnergy β/total', fontsize=8, color=COL['stress'])
    ax5.legend(fontsize=8, loc='upper left')
    ax5b.legend(fontsize=8, loc='upper right')
    _add_ref_tag(ax5, 'Samsa & Altıntop 2026 (N°17) | Calcul < 5 ms')

    # 6. Tableau récapitulatif
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    rows = [['Feature','Valeur moy.','Référence'],
            ['TBR (θ/β)', f'{np.mean(tbrs):.3f}', 'CdC NeuroCap'],
            ['EI (β/(α+θ))', f'{np.mean(eis):.3f}', 'CdC NeuroCap'],
            ['TAR (θ/α)', f'{np.mean(tars):.3f}', 'Salam 2026 (N°15)'],
            ['Power', f'{np.mean(pows):.4f}', 'Samsa 2026 (N°17)'],
            ['MeanAmp', f'{np.mean(mamps):.4f}', 'Samsa 2026 (N°17)'],
            ['RelEnergy β', f'{np.mean(rels):.4f}', 'Samsa 2026 (N°17)'],
            ['Hjorth Act.', f'{np.mean([f["Act"] for f in feats]):.4f}', 'CdC Sec. 2.3']]
    tbl = ax6.table(cellText=rows[1:], colLabels=rows[0], loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1.1, 1.85)
    for j in range(3):
        tbl[0,j].set_facecolor(COL['dark']); tbl[0,j].set_text_props(color='white', fontweight='bold')
    for i in range(1, len(rows)):
        for j in range(3):
            tbl[i,j].set_facecolor(COL['light'] if i%2==0 else 'white')
    ax6.set_title('Features — Résumé', fontsize=9, fontweight='bold', color=COL['dark'], pad=60)

    plt.savefig(os.path.join(outdir, '05_features_extraites.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return os.path.join(outdir, '05_features_extraites.png')


def fig6_comparison(outdir):
    """Comparaison des 3 états cognitifs (concentration, stress, relaxation) sur signal synthétique."""
    results = {}
    for state, seed in [('concentration',42), ('stress',43), ('relaxation',44)]:
        t, raw = make_signal(state=state, dur=20, seed=seed)
        # Appliquer tout le pipeline (filtrage + DWT) pour obtenir un signal propre
        sig = step5_dwt(step4_notch(step3_lowpass(step2_highpass(raw))))
        eps, sts, _ = step7_segment(sig, amp_thr=AMP_THR)
        eps_n = step8_zscore(eps)
        feats = step9_features(eps_n, sts)
        results[state] = {'t': t, 'sig': sig, 'feats': feats, 'eps': eps, 'sts': sts}

    fig, axes = plt.subplots(3, 3, figsize=(20, 14), facecolor='white')
    fig.suptitle(
        'COMPARAISON DES ÉTATS COGNITIFS — Fp2 : Concentration vs Stress vs Relaxation\n'
        'Validation des signatures EEG du Cahier des Charges NeuroCap (Section 2.5.1)\n'
        'β↑+TBR<0.8+EI>0.7 (Concentration)  ·  β↑↑+α↓ (Stress)  ·  α↑+β↓ (Relaxation)',
        fontsize=11, fontweight='bold', color=COL['dark'])

    state_col = {'concentration': COL['conc'], 'stress': COL['stress'], 'relaxation': COL['relax']}
    state_lbl = {'concentration': 'Concentration', 'stress': 'Stress', 'relaxation': 'Relaxation'}

    # Colonne 0 : signaux temporels
    for row, state in enumerate(['concentration', 'stress', 'relaxation']):
        d = results[state]
        axes[row,0].plot(d['t'], d['sig'], color=state_col[state], lw=0.7, alpha=0.9)
        _style(axes[row,0], f'{state_lbl[state]} — Signal Fp2 propre', 'Temps (s)', 'µV')

    # Colonne 1 : PSD comparées
    ax_psd = axes[0,1]
    for state in ['concentration', 'stress', 'relaxation']:
        fr, psd = _psd(results[state]['sig'], nperseg=512)
        m = fr <= 45
        ax_psd.semilogy(fr[m], psd[m], color=state_col[state], lw=2, label=state_lbl[state])
    _shade_bands(ax_psd, 45)
    _style(ax_psd, 'PSD Welch comparée — 3 états', 'Fréquence (Hz)', 'µV²/Hz [log]')
    ax_psd.legend(fontsize=9)
    _add_ref_tag(ax_psd, 'Katmah 2021 (N°12) : α↓ et β↑ = biomarqueurs consensus')
    axes[1,1].axis('off'); axes[2,1].axis('off')

    # Colonne 2 : puissances de bande
    bkeys = ['Pd','Pt','Pa','Pb','Pg']
    blbls = ['δ','θ','α','β','γ']
    x = np.arange(5)
    w = 0.28
    ax_b = axes[0,2]
    for k, state in enumerate(['concentration', 'stress', 'relaxation']):
        fs_feats = results[state]['feats']
        if fs_feats:
            means = [np.mean([f[bk] for f in fs_feats]) for bk in bkeys]
            ax_b.bar(x + k*w, means, w, color=state_col[state], alpha=0.85,
                     label=state_lbl[state], edgecolor='white')
    ax_b.set_xticks(x + w); ax_b.set_xticklabels(blbls)
    _style(ax_b, 'Puissance par bande (3 états)', '', 'µV²/Hz')
    ax_b.legend(fontsize=8)
    _add_ref_tag(ax_b, 'Velnath 2021 (N°20) : Conc.=β↑ | Saeed 2015 (N°8) : Stress=β↑↑')

    # Ratios cognitifs comparés
    ax_r = axes[1,2]
    rkeys = ['TBR','EI','TAR']
    rlbls = ['TBR\nθ/β','EI\nβ/(α+θ)','TAR\nθ/α']
    x_r = np.arange(3)
    for k, state in enumerate(['concentration', 'stress', 'relaxation']):
        fs_feats = results[state]['feats']
        if fs_feats:
            means = [np.mean([f[rk] for f in fs_feats]) for rk in rkeys]
            ax_r.bar(x_r + k*0.28, means, 0.28, color=state_col[state],
                     alpha=0.85, label=state_lbl[state], edgecolor='white')
    ax_r.axhline(0.8, color=COL['dark'], ls='--', lw=1.5, alpha=0.7, label='TBR<0.8')
    ax_r.axhline(0.7, color=COL['stress'], ls=':', lw=1.5, alpha=0.7, label='EI>0.7')
    ax_r.set_xticks(x_r + 0.28); ax_r.set_xticklabels(rlbls)
    _style(ax_r, 'Ratios Cognitifs NeuroCap (3 états)', '', 'Ratio')
    ax_r.legend(fontsize=7, ncol=2)
    _add_ref_tag(ax_r, 'CdC NeuroCap Sec. 2.5.1 | Saeed 2020 (N°9) FAA p=0.0005')

    # Tableau récapitulatif des signatures
    ax_sig = axes[2,2]
    ax_sig.axis('off')
    txt = ("Signatures EEG — CdC NeuroCap Sec. 2.5.1\n\n"
           "CONCENTRATION (Fp2) :\n"
           "  β↑ + θ↓ + TBR < 0.8 + EI > 0.7\n"
           "  → Feedback récompense β↑ + EI↑\n\n"
           "STRESS (Fp2) :\n"
           "  β↑↑ + α↓ + Hi-β > 1.5× baseline\n"
           "  FAA < -0.1 (Saeed 2020, p=0.0005)\n\n"
           "RELAXATION (Fp2) :\n"
           "  α↑ + β↓ + TBR > 1.0\n\n"
           "Références État de l'Art :\n"
           "• Velnath 2021 (N°20) : β↑=concentration\n"
           "• Katmah 2021 (N°12) : α↓+β↑=stress\n"
           "• Saeed 2020 (N°9) : FAA p=0.0005\n"
           "• Salam 2026 (N°15) : TAR p<0.001")
    ax_sig.text(0.05, 0.97, txt, transform=ax_sig.transAxes, fontsize=8.8,
                va='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=COL['light'],
                          alpha=0.95, edgecolor=COL['dark']))

    plt.tight_layout()
    p = os.path.join(outdir, '06_comparaison_etats.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


def fig7_pipeline_diagram(outdir):
    """Diagramme visuel du pipeline complet (paramètres hardware)."""
    fig, ax = plt.subplots(figsize=(22, 12), facecolor='white')
    ax.set_xlim(0, 22); ax.set_ylim(0, 12); ax.axis('off')
    fig.suptitle(
        'Pipeline de Prétraitement NeuroCap — Canal Fp2 (AD8232 + ESP32)\n'
        'Chaque étape justifiée par l\'État de l\'Art — Contrainte latence < 500 ms (CdC Section 5.5)',
        fontsize=14, fontweight='bold', color=COL['dark'], y=0.99)

    steps = [
        # (x, y, titre, couleur, détail, référence)
        (1.7,  9.5, 'SIGNAL\nBRUT Fp2',     '#2C3E50', f'{FS} Hz\nFp2 (M1/M2)', 'Prototype\nNeuroCap'),
        (4.5,  9.5, 'HP 0.5 Hz\nButterworth','#2980B9','Zéro-phase\nfiltfilt', 'Chaudhary 2025\n(PREP-1)'),
        (7.5,  9.5, 'LP 40 Hz\nButterworth','#1ABC9C','Élimine EMG\n> 40 Hz', 'Acharya 2021\n(PREP-2)'),
        (10.5, 9.5, 'NOTCH 50 Hz\nQ=30',   '#F39C12','Réseau MAR\n50 Hz', 'CdC NeuroCap\nGaikwad 2017'),
        (13.5, 9.5, 'DWT db4\nSeuillage doux','#27AE60','Remplace ICA\n(1 canal)','Gaikwad 2017\n(N°3)'),
        (16.8, 9.5, 'REJET\n> 500 µV',     '#E74C3C', 'Epoch marqué\nfeedback OFF', 'Chaudhary 2025\n(adapté AD8232)'),
        (20.0, 9.5, 'SEGMENTATION\n4 s 75%','#E67E22','1000 éch./epoch\nHann window','CdC Sec.2.1\nAcharya 2021'),
        (4.5,  5.5, 'Z-SCORE\npar epoch',  '#16A085', 'µ=0, σ=1\ninter-sujets', 'Chaudhary 2025\nMynoddin 2025'),
        (8.5,  5.5, 'PSD WELCH\nδθαβγ',   '#2980B9', 'TBR, ABR\nEI, TAR', 'CdC Sec.2.3\nSalam 2026 (N°15)'),
        (12.5, 5.5, 'HJORTH\nAct/Mob/Cmp','#8E44AD', 'Power\nMeanAmp RelE', 'CdC Sec.2.3\nSamsa 2026 (N°17)'),
        (16.5, 5.5, 'VECTEUR\n~100-120 F', '#E74C3C', '< 40 ms\nEntrée classif.', 'CdC Sec.2.3\n< 40 ms budget'),
    ]

    BW, BH = 2.7, 1.55
    for (x, y, title, color, detail, ref) in steps:
        bp = mpatches.FancyBboxPatch((x-BW/2, y-BH/2), BW, BH,
            boxstyle="round,pad=0.12", facecolor=color, edgecolor='white', lw=2, alpha=0.93, zorder=3)
        ax.add_patch(bp)
        ax.text(x, y+0.32, title, ha='center', va='center', fontsize=8.5,
                fontweight='bold', color='white', zorder=4)
        ax.text(x, y-0.28, detail, ha='center', va='center', fontsize=6.8,
                color='#EEEEEE', zorder=4, alpha=0.95)
        rp = mpatches.FancyBboxPatch((x-BW/2, y-BH/2-1.05), BW, 0.85,
            boxstyle="round,pad=0.06", facecolor='#F8F9FA', edgecolor=color, lw=1.5, alpha=0.97, zorder=3)
        ax.add_patch(rp)
        ax.text(x, y-BH/2-0.60, ref, ha='center', va='center', fontsize=6.5,
                color=color, fontweight='bold', zorder=4)

    # Flèches rangée 1
    y1 = 9.5
    for xa, xb in [(3.05,3.5), (6.15,6.6), (9.15,9.6), (12.2,12.6), (15.2,15.6), (18.45,18.9)]:
        ax.annotate('', xy=(xb,y1), xytext=(xa,y1),
                    arrowprops=dict(arrowstyle='->', color=COL['dark'], lw=2.2), zorder=5)

    # Flèche de raccord
    ax.annotate('', xy=(4.5, 6.35), xytext=(20.0, 8.72),
                arrowprops=dict(arrowstyle='->', color=COL['dark'], lw=2.2,
                                connectionstyle='angle,angleA=0,angleB=90,rad=0'), zorder=5)

    # Flèches rangée 2
    y2 = 5.5
    for xa, xb in [(7.15,7.6), (11.15,11.6), (15.15,15.6), (18.15,18.6)]:
        ax.annotate('', xy=(xb,y2), xytext=(xa,y2),
                    arrowprops=dict(arrowstyle='->', color=COL['dark'], lw=2.2), zorder=5)

    # Budget latence
    lat_txt = ('BUDGET DE LATENCE — CdC NeuroCap Section 5.5\n'
               'Prétraitement 500 ms  <150 ms    Extraction features  <40 ms    '
               'Inférence classifieur  <50 ms    WebSocket  <10 ms\n'
               '──────────────────────  Latence end-to-end  <350 ms (cible) / <500 ms (max)  ──────────────────────')
    ax.text(11, 1.15, lat_txt, ha='center', va='center', fontsize=9, color=COL['dark'],
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.45', facecolor='#EEF3FA',
                      alpha=0.97, edgecolor=COL['dark'], lw=1.5))

    # Note ICA
    ax.text(11, 2.7,
            '★  ICA NON APPLICABLE sur monocanal Fp2 — matrice de mélange sous-déterminée (nécessite ≥ 4 canaux).\n'
            '   Remplacement : DWT Daubechies db4 (niveau 4, seuillage doux) — validée Fp1/Fp2/Fpz '
            '(Gaikwad & Paithane, IEEE ICCMC 2017, N°3).',
            ha='center', va='center', fontsize=9.5, color='#C0392B', style='italic',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FDEDEC',
                      alpha=0.97, edgecolor='#E74C3C', lw=1.5))

    p = os.path.join(outdir, '07_pipeline_diagram.png')
    fig.savefig(p, dpi=150, bbox_inches='tight'); plt.close(); return p


# ============================================================================
# FONCTION PRINCIPALE (run_pipeline)
# ============================================================================

def run_pipeline(state='concentration', outdir=None):
    """
    Exécute le pipeline complet sur un signal synthétique (pour test).
    Paramètres :
        state : 'concentration', 'stress' ou 'relaxation'
        outdir : dossier de sortie pour les figures (par défaut, Preprocessing/outputs_hardware_compatible)
    """
    if outdir is None:
        outdir = Path(__file__).resolve().parent.parent.parent / 'reports' / 'Preprocessing' / 'outputs_hardware_compatible'
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print('=' * 65)
    print('NeuroCap — Pipeline Prétraitement EEG Fp2 (compatible AD8232 + ESP32)')
    print(f'État : {state.upper()}  |  fs={FS} Hz  |  epoch={EPOCH_S} s  |  overlap={OVERLAP*100:.0f}%  |  seuil={AMP_THR} µV')
    print('=' * 65)

    print('\n[0] Génération signal synthétique Fp2...')
    # Durée de 20 s pour avoir plusieurs époques de 4 s
    t, raw = make_signal(state=state, dur=20)

    # Application des filtres (sans étape 1 car hardware déjà référencé)
    print('[2] Filtre HP 0.5 Hz     (Chaudhary 2025, PREP-1)')
    s2 = step2_highpass(raw)
    print('[3] Filtre LP 40 Hz      (Acharya 2021, PREP-2)')
    s3 = step3_lowpass(s2)
    print('[4] Notch 50 Hz          (CdC NeuroCap, Gaikwad 2017)')
    s4 = step4_notch(s3)

    print('[5] DWT db4 seuillage doux  (Gaikwad 2017 N°3 — offline)')
    s5 = step5_dwt(s4)

    print('[6] Marquage amplitude > seuil hardware')
    mask, pct = step6_reject(s5, thr=AMP_THR)
    print(f'    → {pct:.1f} % du signal contaminé')

    print(f'[7] Segmentation {EPOCH_S} s / overlap {OVERLAP*100:.0f} %  (paramètres hardware)')
    epochs, sts, t0s = step7_segment(s5, amp_thr=AMP_THR)
    nv = sum(1 for s in sts if s == 'valide')
    print(f'    → {len(epochs)} epochs | {nv} valides | {len(epochs)-nv} rejetés')

    print('[8] Normalisation Z-score par epoch  (Chaudhary 2025, PREP-1)')
    epochs_n = step8_zscore(epochs)

    print('[9] Extraction features (PSD, ratios, Hjorth, Power)')
    feats = step9_features(epochs_n, sts)
    if feats:
        print(f'    → {len(feats)} epochs × {len(feats[0])} features')
    else:
        print('    → Aucune epoch valide → extraction vide.')

    print('\n📊 Génération des figures...')
    fig0_raw(t, raw, state, outdir)
    # Pour fig1_filtering, on doit passer les signaux intermédiaires (raw, s2, s3, s4)
    fig1_filtering(t, raw, s2, s3, s4, outdir)
    fig2_dwt(t, s4, s5, outdir)
    fig3_segmentation(t, s5, epochs, sts, t0s, outdir)
    fig4_zscore(epochs, epochs_n, sts, outdir)
    fig5_features(feats, state, outdir)
    fig6_comparison(outdir)
    fig7_pipeline_diagram(outdir)
    print('\n✅ Pipeline terminé — 8 figures générées.')
    return epochs_n, sts, feats


if __name__ == '__main__':
    run_pipeline(state='concentration', outdir=None)