"""
Shared EEG utility functions for validation, visualization, and preprocessing.
Adapted for hardware configuration: Fp2 (active) – M2 (ref) – M1 (gnd)

Shared between:
  - validate_data/validate_concentration.py
  - validate_data/validate_stress.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path

import traceback
import sys


# ─── Constants ────────────────────────────────────────────────────────────────

# Cognitive Load (OpenBCI Cyton) channel order (cols 1-8 of .txt files)
# [Fp1, Fp2, F7, F3, FZ, F4, F8, C2]
CONCENTRATION_CHANNELS = ['Fp1', 'Fp2', 'F7', 'F3', 'FZ', 'F4', 'F8', 'C2']

# Fp2 is at index 1 in the EEG sub-array (col 2 overall in .txt file)
FP2_IDX_CONCENTRATION = 1

# Kept for reference / backward compatibility
FZ_IDX_CONCENTRATION = 4

# Active channel label used in all figure titles and logs
ACTIVE_CHANNEL = 'Fp2'

# OpenBCI Cyton ADC → µV: Vref=4.5V, gain=24, 24-bit signed
OPENBCI_SCALE = (4.5 / (2**23 - 1) / 24) * 1e6   # ≈ 0.02235 µV/count

# Sampling rates
FS_CONCENTRATION = 250   # Hz (Cognitive Load dataset)
FS_STRESS = 128          # Hz (SAM40 Emotiv)
FS_TARGET = 250          # Hz (common target after resampling)

# Artifact detection thresholds
# Note: Fp2 is more sensitive to eye blinks than Fz.
# PTP threshold remains 500 µV but expect more ocular artifacts.
ARTIFACT_PTP_UV = 500    # µV – peak-to-peak above this → artifact epoch
ARTIFACT_FLAT_UV = 1.0   # µV – std below this → flat/dead channel
ARTIFACT_SAT_UV = 3000   # µV – absolute value above this → saturation
HF_RATIO_THRESH = 0.70   # power fraction above 40 Hz → noisy channel

# Colour palette per label / task
LABEL_COLORS = {
    'natural':    '#2196F3',
    'lowlevel':   '#4CAF50',
    'midlevel':   '#FF9800',
    'highlevel':  '#F44336',
    'Arithmetic': '#9C27B0',
    'Stroop':     '#FF5722',
    'Relax':      '#00BCD4',
}

# SAM40 Emotiv Epoc Flex – 32-channel layout
# Fp2 is at index 31 (last channel)
EMOTIV_32_CHANNELS = [
    'CZ', 'FZ', 'Fp1', 'F7', 'F3', 'FC1', 'C3', 'FC5',
    'FT9', 'T7', 'CP5', 'CP1', 'P3', 'P7', 'PO9', 'O1',
    'PZ', 'OZ', 'O2', 'PO10', 'P8', 'P4', 'CP2', 'CP6',
    'T8', 'FT10', 'FC6', 'C4', 'FC2', 'F4', 'F8', 'Fp2',
]
FP2_IDX_STRESS_FALLBACK = 31  # Fp2 index in EMOTIV_32_CHANNELS


# ─── Loading utilities ────────────────────────────────────────────────────────

def load_concentration_file(filepath):
    """
    Load a Cognitive Load .txt file.

    File format (25 columns, comma-separated, no header row):
      Col  0   : sample index
      Cols 1-8 : EEG channels [Fp1,Fp2,F7,F3,FZ,F4,F8,C2] in ADC counts
      Cols 9-11: accelerometer X,Y,Z
      Col  12  : device status
      Cols 13-21: event markers
      Col  22  : Unix timestamp (seconds)
      Col  23  : event marker
      Col  24  : human-readable datetime string

    Returns
    -------
    eeg_uv : np.ndarray, shape (n_samples, 8)  – converted to µV
    timestamps : np.ndarray, shape (n_samples,) – Unix seconds (col 22)
    fs : float – nominal sampling rate (250 Hz)
    """
    import pandas as pd

    df = pd.read_csv(
        str(filepath),
        header=None,
        skipinitialspace=True,
        on_bad_lines='skip',
    )

    # Row 0 is an initialisation frame with all-zero EEG – skip it
    df = df.iloc[1:].copy()
    df.reset_index(drop=True, inplace=True)

    eeg_cols = list(range(1, 9))
    eeg_raw = df[eeg_cols].values.astype(float)
    eeg_uv  = eeg_raw * OPENBCI_SCALE

    try:
        timestamps = df[22].values.astype(float)
    except Exception:
        timestamps = np.arange(len(eeg_uv)) / FS_CONCENTRATION

    return eeg_uv, timestamps, FS_CONCENTRATION


def load_stress_file(filepath):
    """
    Load a SAM40 Stress .mat file.

    Returns
    -------
    eeg : np.ndarray, shape (n_samples, n_channels)
    fs : float – sampling rate in Hz
    ch_names : list[str] or None
    mat_keys : list[str]
    """
    import scipy.io as sio

    mat = sio.loadmat(str(filepath), squeeze_me=True)
    data_keys = [k for k in mat.keys() if not k.startswith('__')]

    eeg = None
    fs = FS_STRESS
    ch_names = None

    for key in ['data', 'EEG', 'eeg', 'raw_data', 'filtered_data', 'Data']:
        if key in mat:
            arr = np.array(mat[key], dtype=float)
            if arr.ndim == 2:
                eeg = arr
                break

    if eeg is None:
        for key in data_keys:
            try:
                arr = np.array(mat[key], dtype=float)
                if arr.ndim == 2 and min(arr.shape) > 1:
                    eeg = arr
                    break
            except Exception:
                continue

    # Ensure (n_samples, n_channels) orientation
    if eeg is not None and eeg.shape[0] < eeg.shape[1]:
        eeg = eeg.T

    for key in ['fs', 'Fs', 'srate', 'fs_Hz', 'SR']:
        if key in mat:
            try:
                fs = float(np.array(mat[key]).flat[0])
                break
            except Exception:
                pass

    for key in ['chanlocs', 'channels', 'ch_names', 'labels', 'channames']:
        if key in mat:
            try:
                raw = mat[key]
                if hasattr(raw, '__iter__') and not isinstance(raw, str):
                    ch_names = [str(c).strip() for c in raw]
                break
            except Exception:
                pass

    return eeg, fs, ch_names, data_keys


def load_scales(scales_path):
    """Load SAM40 scales.xls for stress self-report scores."""
    import pandas as pd
    try:
        df = pd.read_excel(str(scales_path))
        return df
    except Exception as e:
        print(f"  [Warning] Could not load scales: {e}")
        return None


# ─── Fp2 extraction ───────────────────────────────────────────────────────────

def get_fp2_channel_stress(eeg, ch_names=None):
    """
    Return the Fp2 channel from SAM40 data and its index.

    Search strategy:
    1. Look for 'Fp2' (case-insensitive) in ch_names from file
    2. Fallback to known Emotiv 32-channel layout (index 31)
    3. Last resort: return None

    Parameters
    ----------
    eeg : (n_samples, n_channels)
    ch_names : list[str] or None

    Returns
    -------
    fp2 : 1D array or None
    idx : int or None
    """
    if ch_names is not None:
        for i, name in enumerate(ch_names):
            if str(name).strip().upper() in ('FP2', 'FP2'):
                return eeg[:, i], i

    # Fallback: known Emotiv layout
    if eeg.shape[1] == 32:
        idx = FP2_IDX_STRESS_FALLBACK
        print(f"    Fp2 estimated at index {idx} (Emotiv 32-ch layout fallback)")
        return eeg[:, idx], idx

    return None, None


# Kept for backward compatibility (Fz validation)
def get_fz_channel_stress(eeg, ch_names=None):
    if ch_names is not None:
        for i, name in enumerate(ch_names):
            if str(name).strip().upper() == 'FZ':
                return eeg[:, i], i
    return None, None


# ─── Signal processing ────────────────────────────────────────────────────────

def compute_psd(sig, fs, nperseg=None):
    """Welch PSD estimate. Returns (freqs, psd) in µV²/Hz."""
    if nperseg is None:
        nperseg = min(len(sig), int(fs * 4))
    freqs, psd = signal.welch(sig, fs=fs, nperseg=nperseg,
                               noverlap=nperseg // 2, window='hann')
    return freqs, psd


def resample_signal(sig, fs_orig, fs_target):
    """Resample 1-D signal from fs_orig to fs_target Hz (FFT-based)."""
    n_target = int(len(sig) * fs_target / fs_orig)
    return signal.resample(sig, n_target)


def check_artifacts(sig, fs, label=""):
    """
    Basic artifact audit on a 1-D EEG signal.
    Note: Fp2 is more prone to ocular artifacts than Fz.
    PTP > 500 µV threshold is kept but expect more flagged epochs.
    """
    ptp  = float(np.ptp(sig))
    std  = float(np.std(sig))
    mn   = float(np.mean(sig))

    freqs, psd = compute_psd(sig, fs)
    hf_mask  = freqs > 40
    hf_ratio = float(np.sum(psd[hf_mask]) / np.sum(psd)) if psd.sum() > 0 else 0.0
    saturated = bool(np.any(np.abs(sig) > ARTIFACT_SAT_UV))

    return {
        'label':         label,
        'n_samples':     len(sig),
        'duration_s':    len(sig) / fs,
        'mean_uv':       mn,
        'std_uv':        std,
        'ptp_uv':        ptp,
        'min_uv':        float(np.min(sig)),
        'max_uv':        float(np.max(sig)),
        'hf_ratio':      hf_ratio,
        'saturated':     saturated,
        'artifact_ptp':  ptp  > ARTIFACT_PTP_UV,
        'artifact_flat': std  < ARTIFACT_FLAT_UV,
    }


# ─── Visualization helpers ────────────────────────────────────────────────────

def plot_time_series(signals_dict, fs, n_seconds=10,
                     title="EEG Time Series (Fp2)", save_path=None):
    """Stacked time-series plot for multiple labelled signals."""
    n = len(signals_dict)
    fig, axes = plt.subplots(n, 1, figsize=(14, 2.8 * n), sharex=False)
    if n == 1:
        axes = [axes]

    n_pts = int(n_seconds * fs)

    for ax, (label, sig) in zip(axes, signals_dict.items()):
        seg   = sig[:n_pts]
        t     = np.arange(len(seg)) / fs
        color = LABEL_COLORS.get(label, '#546E7A')
        ax.plot(t, seg, color=color, linewidth=0.7, alpha=0.9)
        ax.set_ylabel('µV', fontsize=9)
        ax.set_title(f'  {label}', loc='left', fontsize=10,
                     color=color, fontweight='bold')
        ax.axhline(0, color='gray', linewidth=0.4, linestyle='--')
        for thresh in (+ARTIFACT_PTP_UV / 2, -ARTIFACT_PTP_UV / 2):
            ax.axhline(thresh, color='red', linewidth=0.6,
                       linestyle=':', alpha=0.55, label='±250 µV')
        ax.grid(True, alpha=0.25)

    axes[-1].set_xlabel('Time (s)', fontsize=10)
    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    plt.close(fig)


def plot_psd_comparison(signals_dict, fs, fmax=60,
                        title="PSD Comparison (Fp2)", save_path=None):
    """Overlay PSD curves (log + linear) for multiple labelled signals."""
    fig, (ax_log, ax_lin) = plt.subplots(1, 2, figsize=(14, 5))

    bands = {
        'δ 1-4':   (1,  4,  '#E3F2FD'),
        'θ 4-8':   (4,  8,  '#F3E5F5'),
        'α 8-13':  (8,  13, '#E8F5E9'),
        'β 13-30': (13, 30, '#FFF3E0'),
        'γ 30-45': (30, 45, '#FCE4EC'),
    }

    for label, sig in signals_dict.items():
        freqs, psd = compute_psd(sig, fs)
        color = LABEL_COLORS.get(label, '#546E7A')
        mask  = freqs <= fmax
        for ax in (ax_log, ax_lin):
            ax.plot(freqs[mask], psd[mask], color=color,
                    linewidth=1.5, label=label, alpha=0.9)

    for ax in (ax_log, ax_lin):
        for bname, (f_lo, f_hi, bc) in bands.items():
            if f_hi <= fmax:
                ax.axvspan(f_lo, f_hi, alpha=0.12, color=bc)
        ax.axvline(50, color='red', linewidth=1, linestyle='--',
                   alpha=0.6, label='50 Hz (mains)')
        ax.set_xlabel('Frequency (Hz)', fontsize=10)
        ax.set_xlim(0, fmax)
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, loc='upper right')

    ax_log.set_yscale('log')
    ax_log.set_ylabel('PSD [µV²/Hz]  —  log scale', fontsize=10)
    ax_log.set_title('Log Scale', fontsize=11)
    ax_lin.set_ylabel('PSD [µV²/Hz]', fontsize=10)
    ax_lin.set_title('Linear Scale', fontsize=11)

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    plt.close(fig)


def plot_amplitude_histogram(signals_dict,
                              title="Amplitude Distribution (Fp2)",
                              save_path=None):
    """One histogram panel per label."""
    n = len(signals_dict)
    fig, axes = plt.subplots(1, n, figsize=(4.5 * n, 4), sharey=False)
    if n == 1:
        axes = [axes]

    for ax, (label, sig) in zip(axes, signals_dict.items()):
        color = LABEL_COLORS.get(label, '#546E7A')
        ax.hist(sig, bins=80, color=color, alpha=0.80,
                edgecolor='white', linewidth=0.3)
        mu, sd = np.mean(sig), np.std(sig)
        ax.axvline(mu, color='black', linewidth=1.5, linestyle='--',
                   label=f'μ={mu:.1f} µV')
        ax.axvline(mu + 2*sd, color='red', linewidth=1.0,
                   linestyle=':', alpha=0.7)
        ax.axvline(mu - 2*sd, color='red', linewidth=1.0,
                   linestyle=':', alpha=0.7, label='±2σ')
        ax.set_xlabel('Amplitude (µV)', fontsize=9)
        ax.set_ylabel('Count', fontsize=9)
        ax.set_title(label, fontsize=10, color=color, fontweight='bold')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.25)

    fig.suptitle(title, fontsize=12, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    plt.close(fig)


def plot_all_channels(eeg_uv, ch_names, fs, n_seconds=5,
                      title="All Channels", save_path=None):
    """
    Stacked butterfly plot of every channel.
    Fp2 is highlighted in red (previously Fz was highlighted).
    """
    n_ch  = eeg_uv.shape[1]
    n_pts = int(n_seconds * fs)
    seg   = eeg_uv[:n_pts, :]
    t     = np.arange(n_pts) / fs

    spacing = 2.5
    fig, ax = plt.subplots(figsize=(14, 1.6 * n_ch))

    for i, name in enumerate(ch_names):
        offset = (n_ch - 1 - i) * spacing
        s      = seg[:, i]
        norm_s = s / (np.ptp(s) / 2 + 1e-9)

        # Highlight Fp2 instead of Fz
        is_fp2 = str(name).strip().upper() in ('FP2',)
        color  = '#E53935' if is_fp2 else '#546E7A'
        lw     = 1.8       if is_fp2 else 0.7
        alpha  = 1.0       if is_fp2 else 0.7

        ax.plot(t, norm_s + offset, color=color, linewidth=lw, alpha=alpha)
        ax.text(-0.05 * t[-1], offset, name, ha='right', va='center',
                fontsize=8, color=color,
                fontweight='bold' if is_fp2 else 'normal')

    ax.set_xlabel('Time (s)', fontsize=10)
    ax.set_ylabel('Channels (normalised, offset)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlim(0, t[-1])
    ax.grid(True, alpha=0.15)

    plt.tight_layout()
    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    plt.close(fig)


def compute_band_powers(sig, fs):
    """Return EEG band power values (µV²) for standard bands."""
    bands = {
        'δ 1-4':   (1,  4),
        'θ 4-8':   (4,  8),
        'α 8-13':  (8,  13),
        'β 13-30': (13, 30),
        'γ 30-45': (30, 45),
    }
    freqs, psd = compute_psd(sig, fs)
    out = {}
    for name, (f_lo, f_hi) in bands.items():
        mask = (freqs >= f_lo) & (freqs <= f_hi)
        out[name] = float(np.trapezoid(psd[mask], freqs[mask]))
    return out