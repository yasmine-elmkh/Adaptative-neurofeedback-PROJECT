"""
Phase 1 – Re-validation on channel Fp2 — Cognitive Load (Concentration) dataset.

Hardware configuration: Fp2 (active) – M2 (reference) – M1 (ground)

Dataset layout:
  Dataset/Cognitive Load Assessment Concentration/raw_data/
      Arithmetic_Data/ → {natural,lowlevel,midlevel,highlevel}-{1..15}.txt
      Stroop_Data/     → {natural,lowlevel,midlevel,highlevel}-{1..15}.txt

.txt format (25 comma-separated columns, NO header):
  Col  0   : sample index
  Cols 1–8 : EEG [Fp1, Fp2, F7, F3, FZ, F4, F8, C2] in ADC counts
  Col  22  : Unix timestamp (seconds)

Fp2 is at: overall col index 2 → EEG sub-array index 1 (FP2_IDX_CONCENTRATION = 1)
ADC → µV:  value × OPENBCI_SCALE (≈ 0.02235 µV/count)

Note on Fp2 vs Fz:
  Fp2 (frontal polar right) is more sensitive to ocular artifacts than Fz.
  The same artifact thresholds are applied but more epochs may be flagged.
  Alpha on Fp2 is often more ample; beta slightly less discriminant for
  pure concentration compared to Fz.

Usage:
  python validate_data/validate_concentration_fp2.py
Outputs saved to: outputs_concentration_fp2/
"""

import sys
from pathlib import Path
import numpy as np


import traceback
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.Validate_datasets.utils.eeg_utils import (
    CONCENTRATION_CHANNELS,
    FP2_IDX_CONCENTRATION,
    FS_CONCENTRATION,
    OPENBCI_SCALE,
    LABEL_COLORS,
    ACTIVE_CHANNEL,
    load_concentration_file,
    check_artifacts,
    compute_psd,
    compute_band_powers,
    plot_time_series,
    plot_psd_comparison,
    plot_amplitude_histogram,
    plot_all_channels,
)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ─── Paths & settings ─────────────────────────────────────────────────────────

DATA_ROOT  = (PROJECT_ROOT / '..' / '..'/ '..'/ 'data' / 'Dataset'
              / 'Cognitive Load Assessment Concentration' / 'raw_data')
ARITH_DIR  = DATA_ROOT / 'Arithmetic_Data'
STROOP_DIR = DATA_ROOT / 'Stroop_Data'
OUT_DIR    = PROJECT_ROOT / '..' / '..'/ '..'/ 'data' / 'Validate_datasets' / 'outputs_concentration_fp2'
OUT_DIR.mkdir(exist_ok=True)

LABELS   = ['natural', 'lowlevel', 'midlevel', 'highlevel']
SUBJECT  = 1
N_CROSS  = 5

CH_IDX   = FP2_IDX_CONCENTRATION   # 1
CH_LABEL = ACTIVE_CHANNEL          # 'Fp2'


# ─── Step 1 – File structure ──────────────────────────────────────────────────

def validate_file_structure():
    """Verify file format and check Fp2 amplitude plausibility."""
    import pandas as pd

    print(f"\n{'='*64}")
    print(f"  STEP 1 — File structure validation (channel: {CH_LABEL})")
    print(f"{'='*64}")

    all_ok = True
    for label in LABELS:
        fp = ARITH_DIR / f"{label}-{SUBJECT}.txt"
        print(f"\n  [{label.upper():<10}]  {fp.name}")

        if not fp.exists():
            print("    ❌  File not found!")
            all_ok = False
            continue

        try:
            df = pd.read_csv(fp, header=None, skipinitialspace=True,
                             on_bad_lines='skip')
        except Exception as e:
            print(f"    ❌  Load error: {e}")
            all_ok = False
            continue

        n_rows, n_cols = df.shape
        print(f"    Shape            : {n_rows} rows × {n_cols} cols"
              f"  {'✅' if n_cols == 25 else '⚠️ expected 25'}")

        eeg_cols = list(range(1, 9))
        eeg_data = df[eeg_cols].iloc[1:].values.astype(float)

        n_samples = eeg_data.shape[0]
        duration  = n_samples / FS_CONCENTRATION
        print(f"    EEG samples      : {n_samples}  ({duration:.1f} s @ 250 Hz)")

        fp2_raw = eeg_data[:, CH_IDX]
        fp2_uv  = fp2_raw * OPENBCI_SCALE
        print(f"    {CH_LABEL} (col 2) range : ADC [{fp2_raw.min():.0f}, {fp2_raw.max():.0f}]"
              f"  →  µV [{fp2_uv.min():.1f}, {fp2_uv.max():.1f}]")

        uv_ok = abs(fp2_uv).max() < 5000
        print(f"    Amplitude check  : {'✅ plausible' if uv_ok else '⚠️ very large – check scale'}")

        # Estimate real fs from timestamps
        try:
            ts = df[22].values.astype(float)
            ts_valid = ts[ts > 0]
            if len(ts_valid) > 2:
                dts = np.diff(ts_valid)
                dts = dts[(dts > 0) & (dts < 1)]
                if len(dts):
                    est_fs = 1.0 / np.median(dts)
                    print(f"    Estimated fs     : {est_fs:.1f} Hz  "
                          f"{'✅' if abs(est_fs - 250) < 10 else '⚠️'}")
        except Exception:
            pass

    return all_ok


# ─── Step 2 – Load Fp2 for all labels ────────────────────────────────────────

def load_all_labels(task='Arithmetic'):
    """Load the Fp2 channel for every label (one subject)."""
    task_dir = ARITH_DIR if task == 'Arithmetic' else STROOP_DIR
    signals  = {}

    for label in LABELS:
        fp = task_dir / f"{label}-{SUBJECT}.txt"
        if not fp.exists():
            print(f"  [Warning] Missing: {fp.name}")
            continue

        eeg_uv, _, fs = load_concentration_file(fp)
        ch = eeg_uv[:, CH_IDX]   # Fp2
        signals[label] = ch
        print(f"  [{label:>10}]  {len(ch):>6} samples  "
              f"({len(ch)/fs:>5.1f} s)  "
              f"{CH_LABEL}: [{ch.min():>8.1f}, {ch.max():>8.1f}] µV")

    return signals


# ─── Step 3 – Artifact audit ──────────────────────────────────────────────────

def run_artifact_checks(signals, task_label=''):
    """Artifact report for each label's Fp2 signal."""
    print(f"\n  --- {task_label} ({CH_LABEL}) ---")
    for label, sig in signals.items():
        r = check_artifacts(sig, FS_CONCENTRATION, label=label)
        ok_ptp  = '✅' if not r['artifact_ptp']  else '⚠️ ARTIFACT (ocular?)'
        ok_hf   = '✅' if r['hf_ratio'] < 0.7    else '⚠️ NOISY'
        ok_flat = '✅' if not r['artifact_flat'] else '⚠️ FLAT'
        ok_sat  = '✅' if not r['saturated']     else '⚠️ SATURATED'
        print(f"\n  [{label}]")
        print(f"    Duration   : {r['duration_s']:.1f} s")
        print(f"    Mean ± std : {r['mean_uv']:.2f} ± {r['std_uv']:.2f} µV")
        print(f"    Min / Max  : {r['min_uv']:.2f} / {r['max_uv']:.2f} µV")
        print(f"    PTP        : {r['ptp_uv']:.2f} µV   {ok_ptp}")
        print(f"    HF ratio   : {r['hf_ratio']:.3f}       {ok_hf}")
        print(f"    Flat chan   :                  {ok_flat}")
        print(f"    Saturation :                  {ok_sat}")


# ─── Step 4 – Visualisations ─────────────────────────────────────────────────

def visualize_all(sig_arith, sig_stroop):
    """Generate and save all validation figures for Fp2."""
    print(f"\n{'='*64}")
    print(f"  STEP 4 — Generating visualisations ({CH_LABEL})")
    print(f"{'='*64}\n")

    plot_time_series(
        sig_arith, FS_CONCENTRATION, n_seconds=10,
        title=f"EEG {CH_LABEL} — Cognitive Load · Arithmetic — Subject {SUBJECT}",
        save_path=OUT_DIR / f"01_timeseries_arithmetic_{CH_LABEL.lower()}_s{SUBJECT}.png",
    )

    plot_time_series(
        sig_stroop, FS_CONCENTRATION, n_seconds=10,
        title=f"EEG {CH_LABEL} — Cognitive Load · Stroop — Subject {SUBJECT}",
        save_path=OUT_DIR / f"02_timeseries_stroop_{CH_LABEL.lower()}_s{SUBJECT}.png",
    )

    plot_psd_comparison(
        sig_arith, FS_CONCENTRATION, fmax=60,
        title=f"PSD Comparison ({CH_LABEL}) — Arithmetic — Subject {SUBJECT}",
        save_path=OUT_DIR / f"03_psd_arithmetic_{CH_LABEL.lower()}_s{SUBJECT}.png",
    )

    plot_psd_comparison(
        sig_stroop, FS_CONCENTRATION, fmax=60,
        title=f"PSD Comparison ({CH_LABEL}) — Stroop — Subject {SUBJECT}",
        save_path=OUT_DIR / f"04_psd_stroop_{CH_LABEL.lower()}_s{SUBJECT}.png",
    )

    plot_amplitude_histogram(
        sig_arith,
        title=f"Amplitude Distribution ({CH_LABEL}) — Arithmetic — Subject {SUBJECT}",
        save_path=OUT_DIR / f"05_histogram_arithmetic_{CH_LABEL.lower()}_s{SUBJECT}.png",
    )

    plot_amplitude_histogram(
        sig_stroop,
        title=f"Amplitude Distribution ({CH_LABEL}) — Stroop — Subject {SUBJECT}",
        save_path=OUT_DIR / f"06_histogram_stroop_{CH_LABEL.lower()}_s{SUBJECT}.png",
    )

    # Natural vs Highlevel — key figure
    combined = {}
    for task_name, sigs in [('Arith', sig_arith), ('Stroop', sig_stroop)]:
        for lbl in ['natural', 'highlevel']:
            if lbl in sigs:
                combined[f"{task_name}-{lbl}"] = sigs[lbl]
    if combined:
        plot_psd_comparison(
            combined, FS_CONCENTRATION, fmax=60,
            title=f"PSD — Natural vs High · Arith & Stroop ({CH_LABEL}) — Subject {SUBJECT}",
            save_path=OUT_DIR / f"07_psd_natural_vs_high_{CH_LABEL.lower()}_s{SUBJECT}.png",
        )

    # All 8 channels — Fp2 highlighted in red
    fp_natural = ARITH_DIR / f"natural-{SUBJECT}.txt"
    if fp_natural.exists():
        eeg_uv, _, _ = load_concentration_file(fp_natural)
        plot_all_channels(
            eeg_uv, CONCENTRATION_CHANNELS, FS_CONCENTRATION, n_seconds=5,
            title=f"All Channels — Arithmetic natural — Subject {SUBJECT} ({CH_LABEL} in red)",
            save_path=OUT_DIR / f"08_all_channels_natural_{CH_LABEL.lower()}_s{SUBJECT}.png",
        )

    _plot_band_power(sig_arith, 'Arithmetic')
    _plot_band_power(sig_stroop, 'Stroop')


print("Test de tracé simple...")
plt.figure()
plt.plot([0,1], [0,1])
plt.savefig(OUT_DIR / "test.png")
print("test.png créé, taille:", (OUT_DIR / "test.png").stat().st_size)



def _plot_band_power(signals, task_name):
    """Grouped bar chart of EEG band power per label."""
    label_list = list(signals.keys())
    if not label_list:
        return

    band_names = None
    powers = {}
    for label, sig in signals.items():
        bp = compute_band_powers(sig, FS_CONCENTRATION)
        powers[label] = list(bp.values())
        if band_names is None:
            band_names = list(bp.keys())

    n_bands  = len(band_names)
    n_labels = len(label_list)
    x        = np.arange(n_bands)
    width    = 0.80 / n_labels

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, label in enumerate(label_list):
        offset = (i - n_labels / 2 + 0.5) * width
        color  = LABEL_COLORS.get(label, '#546E7A')
        ax.bar(x + offset, powers[label], width,
               label=label, color=color, alpha=0.85, edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(band_names, fontsize=10)
    ax.set_ylabel('Band Power (µV²)', fontsize=10)
    ax.set_title(f'EEG Band Power ({CH_LABEL}) — {task_name} — Subject {SUBJECT}',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.25, axis='y')
    plt.tight_layout()

    idx   = 9 if task_name == 'Arithmetic' else 10
    fname = OUT_DIR / f"0{idx}_band_power_{task_name.lower()}_{CH_LABEL.lower()}_s{SUBJECT}.png"
    plt.savefig(str(fname), dpi=150, bbox_inches='tight')
    print(f"  Saved: {fname}")
    plt.close(fig)


# ─── Step 5 – Cross-subject statistics ────────────────────────────────────────

def cross_subject_stats(task='Arithmetic', n_subjects=N_CROSS):
    """Duration, std, ptp for Fp2 across several subjects."""
    print(f"\n{'='*64}")
    print(f"  STEP 5 — Cross-subject check ({CH_LABEL}, {task}, {n_subjects} subjects)")
    print(f"{'='*64}")

    task_dir = ARITH_DIR if task == 'Arithmetic' else STROOP_DIR
    stats    = {lbl: {'dur': [], 'std': [], 'ptp': []} for lbl in LABELS}

    for subj in range(1, n_subjects + 1):
        for label in LABELS:
            fp = task_dir / f"{label}-{subj}.txt"
            if not fp.exists():
                continue
            try:
                eeg_uv, _, fs = load_concentration_file(fp)
                ch = eeg_uv[:, CH_IDX]
                stats[label]['dur'].append(len(ch) / fs)
                stats[label]['std'].append(float(np.std(ch)))
                stats[label]['ptp'].append(float(np.ptp(ch)))
            except Exception as e:
                print(f"  [Warning] Subj {subj} {label}: {e}")

    hdr = f"  {'Label':<12} {'n':<4} {'Dur (s)':<12} {'Std (µV)':<15} {'PTP (µV)'}"
    print(f"\n{hdr}")
    print(f"  {'-'*60}")
    for label in LABELS:
        d = stats[label]
        n = len(d['dur'])
        if n:
            print(f"  {label:<12} {n:<4} "
                  f"{np.mean(d['dur']):<12.1f} "
                  f"{np.mean(d['std']):<15.2f} "
                  f"{np.mean(d['ptp']):.2f}")
        else:
            print(f"  {label:<12} {'N/A'}")

    _plot_cross_subject_psd(task_dir, task, n_subjects)


def _plot_cross_subject_psd(task_dir, task_name, n_subjects):
    """Overlay PSD of Fp2-natural across multiple subjects."""
    fig, ax = plt.subplots(figsize=(12, 5))
    cmap = plt.cm.Blues(np.linspace(0.4, 0.9, n_subjects))

    for i, subj in enumerate(range(1, n_subjects + 1)):
        fp = task_dir / f"natural-{subj}.txt"
        if not fp.exists():
            continue
        try:
            eeg_uv, _, fs = load_concentration_file(fp)
            ch = eeg_uv[:, CH_IDX]
            freqs, psd = compute_psd(ch, fs)
            mask = freqs <= 60
            ax.semilogy(freqs[mask], psd[mask], color=cmap[i],
                        linewidth=1.0, alpha=0.8, label=f'S{subj}')
        except Exception:
            pass

    ax.set_xlabel('Frequency (Hz)', fontsize=10)
    ax.set_ylabel('PSD [µV²/Hz] — log', fontsize=10)
    ax.set_title(f'Cross-subject PSD ({CH_LABEL}, natural) — {task_name}',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=7, ncol=2)
    ax.set_xlim(0, 60)
    ax.grid(True, alpha=0.25)
    plt.tight_layout()

    fname = OUT_DIR / f"11_cross_subject_psd_{CH_LABEL.lower()}_{task_name.lower()}.png"
    plt.savefig(str(fname), dpi=150, bbox_inches='tight')
    print(f"  Saved: {fname}")
    plt.close(fig)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*64}")
    print(f"  Cognitive Load — Re-validation on channel {CH_LABEL}")
    print(f"  Hardware: {CH_LABEL} (active) – M2 (ref) – M1 (gnd)")
    print(f"{'='*64}")
    print(f"  Dataset : {DATA_ROOT}")
    print(f"  Output  : {OUT_DIR}")
    print(f"  Channel : {CH_LABEL} (index {CH_IDX})")
    print(f"  Subject : {SUBJECT}")

    validate_file_structure()

    print(f"\n{'='*64}")
    print(f"  STEP 2 — Loading {CH_LABEL} channel")
    print(f"{'='*64}")
    print(f"\n  [Arithmetic]")
    sig_arith  = load_all_labels('Arithmetic')
    print(f"\n  [Stroop]")
    sig_stroop = load_all_labels('Stroop')

    print(f"\n{'='*64}")
    print(f"  STEP 3 — Artifact audit ({CH_LABEL} channel)")
    print(f"{'='*64}")
    run_artifact_checks(sig_arith,  task_label='Arithmetic')
    run_artifact_checks(sig_stroop, task_label='Stroop')

    visualize_all(sig_arith, sig_stroop)
    cross_subject_stats('Arithmetic', n_subjects=N_CROSS)

    print(f"\n{'='*64}")
    print(f"  ✅ Re-validation on {CH_LABEL} complete.")
    print(f"  Figures saved to: {OUT_DIR}")
    print(f"{'='*64}\n")


if __name__ == '__main__':
    main()