"""
Phase 1 – Re-validation on channel Fp2 — SAM40 Stress dataset.

Hardware configuration: Fp2 (active) – M2 (reference) – M1 (ground)

Dataset layout:
  Dataset/Stress_dataset/
      raw_data/ → {Arithmetic,Stroop}_sub_{1..40}_trial{1..3}.mat
      scales.xls → self-reported stress scores (1–10)

Fp2 in SAM40:
  The 32-channel Emotiv Epoc Flex layout contains Fp2 as the LAST channel.
  List: CZ,FZ,Fp1,F7,F3,FC1,C3,FC5,FT9,T7,CP5,CP1,P3,P7,PO9,O1,
        PZ,OZ,O2,PO10,P8,P4,CP2,CP6,T8,FT10,FC6,C4,FC2,F4,F8,Fp2
  Fp2 is at index 31 (0-based).

Extraction strategy (3 levels):
  1. Search for 'FP2' / 'Fp2' in channel names from file
  2. Fallback to known Emotiv layout index 31
  3. Last resort: channel 0 with warning

Usage:
  python validate_data/validate_stress_fp2.py
Outputs saved to: outputs_stress_fp2/
"""

import sys
from pathlib import Path
import numpy as np


import traceback
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.Validate_datasets.utils.eeg_utils import (
    FS_STRESS,
    FS_TARGET,
    ACTIVE_CHANNEL,
    EMOTIV_32_CHANNELS,
    FP2_IDX_STRESS_FALLBACK,
    load_stress_file,
    load_scales,
    get_fp2_channel_stress,
    check_artifacts,
    compute_psd,
    compute_band_powers,
    resample_signal,
    plot_time_series,
    plot_psd_comparison,
    plot_amplitude_histogram,
    plot_all_channels,
)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ─── Paths & settings ─────────────────────────────────────────────────────────

STRESS_ROOT = PROJECT_ROOT / '..' / '..'/ '..'/ 'data' /'Dataset' / 'Stress_dataset'
RAW_DIR     = STRESS_ROOT / 'raw_data'
SCALES_FILE = STRESS_ROOT / 'scales.xls'
OUT_DIR     = PROJECT_ROOT / '..' / '..'/ '..'/ 'data' / 'Validate_datasets' / 'outputs_stress_fp2'
OUT_DIR.mkdir(exist_ok=True)

TASKS    = ['Arithmetic', 'Stroop']
SUBJECT  = 1
TRIAL    = 1
N_CROSS  = 5
CH_LABEL = ACTIVE_CHANNEL  # 'Fp2'


# ─── Step 1 – .mat file structure ────────────────────────────────────────────

def explore_mat_structure():
    """Print every key and shape for one file per task."""
    import scipy.io as sio

    print(f"\n{'='*64}")
    print(f"  STEP 1 — .mat file structure exploration ({CH_LABEL})")
    print(f"{'='*64}")

    for task in TASKS:
        fp = RAW_DIR / f"{task}_sub_{SUBJECT}_trial{TRIAL}.mat"
        print(f"\n  [{task}]  {fp.name}")

        if not fp.exists():
            print("    ❌  File not found!")
            continue

        try:
            mat = sio.loadmat(str(fp), squeeze_me=True)
        except Exception as e:
            print(f"    ❌  Load error: {e}")
            continue

        data_keys = [k for k in mat.keys() if not k.startswith('__')]
        print(f"    Keys: {data_keys}")

        for key in data_keys:
            val = mat[key]
            try:
                arr = np.array(val, dtype=float)
                if arr.size == 0:
                    print(f"    [{key:<18}] empty")
                elif arr.ndim <= 1:
                    print(f"    [{key:<18}] scalar/1D  value={arr.flat[0]:.4g}")
                else:
                    print(f"    [{key:<18}] shape={arr.shape}  "
                          f"range=[{arr.min():.4g}, {arr.max():.4g}]")
            except Exception:
                print(f"    [{key:<18}] type={type(val).__name__}  {str(val)[:80]}")


# ─── Step 2 – Load & validate ────────────────────────────────────────────────

def validate_files():
    """Load one raw file per task and print validation report."""
    print(f"\n{'='*64}")
    print(f"  STEP 2 — File validation (raw_data, channel: {CH_LABEL})")
    print(f"{'='*64}")

    results = {}

    for task in TASKS:
        fp = RAW_DIR / f"{task}_sub_{SUBJECT}_trial{TRIAL}.mat"
        print(f"\n  [{task}]")

        if not fp.exists():
            print("    ❌  Not found")
            continue

        eeg, fs, ch_names, mat_keys = load_stress_file(fp)

        if eeg is None:
            print(f"    ❌  Could not extract EEG array. Keys: {mat_keys}")
            continue

        n_samples, n_ch = eeg.shape
        duration        = n_samples / fs
        expected_samp   = int(25 * fs)

        print(f"    Shape          : {n_samples} × {n_ch}  (samples × channels)")
        print(f"    Sampling rate  : {fs:.1f} Hz"
              f"  {'✅' if abs(fs - 128) < 5 else '⚠️ expected 128'}")
        print(f"    Duration       : {duration:.1f} s"
              f"  {'✅' if abs(n_samples - expected_samp) < expected_samp * 0.15 else '⚠️'}")
        print(f"    n_channels     : {n_ch}"
              f"  {'✅' if n_ch == 32 else '⚠️ expected 32'}")
        print(f"    Channel names  : {ch_names if ch_names else '(not in file)'}")

        amp_max = float(np.abs(eeg).max())
        print(f"    Amplitude range: [{eeg.min():.4g}, {eeg.max():.4g}]")

        if amp_max > 5000:
            unit_note = "⚠️  possibly raw ADC counts"
        elif amp_max < 0.01:
            unit_note = "⚠️  possibly in Volts"
        else:
            unit_note = "✅ likely µV"
        print(f"    Unit estimate  : {unit_note}")

        results[task] = (eeg, fs, ch_names)

    return results


# ─── Helper – extract Fp2 ─────────────────────────────────────────────────────

def extract_fp2(eeg, ch_names, task_name):
    """
    Return (fp2_signal, channel_index).

    Strategy:
    1. Search 'FP2' / 'Fp2' in ch_names
    2. Fallback to Emotiv layout index 31
    3. Last resort: channel 0
    """
    fp2, idx = get_fp2_channel_stress(eeg, ch_names)
    if fp2 is not None:
        print(f"    {CH_LABEL} found at index {idx}")
        return fp2, idx

    # Explicit search in provided names
    if ch_names is not None:
        for i, name in enumerate(ch_names):
            if str(name).strip().upper() in ('FP2',):
                print(f"    {CH_LABEL} found at index {i} (name search)")
                return eeg[:, i], i

    # Fallback to known Emotiv layout
    if eeg.shape[1] == 32:
        idx = FP2_IDX_STRESS_FALLBACK
        print(f"    {CH_LABEL} estimated at index {idx} (Emotiv 32-ch layout fallback)")
        return eeg[:, idx], idx

    print(f"    ⚠️  [{task_name}] {CH_LABEL} not identified — using channel 0 as fallback")
    return eeg[:, 0], 0


# ─── Step 3 – Extract Fp2 ────────────────────────────────────────────────────

def extract_all_fp2(file_results):
    """Build {task: (fp2, fs)} from validated file results."""
    print(f"\n{'='*64}")
    print(f"  STEP 3 — Extracting {CH_LABEL} channel")
    print(f"{'='*64}")

    fp2_signals = {}
    for task, (eeg, fs, ch_names) in file_results.items():
        print(f"\n  [{task}]")
        fp2, _ = extract_fp2(eeg, ch_names, task)
        fp2_signals[task] = (fp2, fs)
        print(f"    {CH_LABEL}: {len(fp2)} samples  ({len(fp2)/fs:.1f} s)  "
              f"range=[{fp2.min():.4g}, {fp2.max():.4g}]")
    return fp2_signals


# ─── Step 4 – Scales ─────────────────────────────────────────────────────────

def load_and_display_scales():
    """Load scales.xls and display stress labels."""
    print(f"\n{'='*64}")
    print("  STEP 4 — Stress labels (scales.xls)")
    print(f"{'='*64}")

    df = load_scales(SCALES_FILE)
    if df is None:
        print("  ❌  Could not load scales.xls")
        return None

    print(f"  Shape   : {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"  Columns : {list(df.columns)}\n")
    print(df.head(15).to_string())

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        print(f"\n  Numeric summary:")
        print(df[num_cols].describe().to_string())

    return df


# ─── Step 5 – Artifact audit ──────────────────────────────────────────────────

def run_artifact_checks(fp2_signals):
    """Artifact report for each task's Fp2 signal."""
    print(f"\n{'='*64}")
    print(f"  STEP 5 — Artifact audit ({CH_LABEL} channel)")
    print(f"  Note: Fp2 is more sensitive to ocular artifacts than Fz.")
    print(f"{'='*64}")

    for task, (fp2, fs) in fp2_signals.items():
        r = check_artifacts(fp2, float(fs), label=task)
        ok_ptp  = '✅' if not r['artifact_ptp']  else '⚠️ >500 µV (ocular?)'
        ok_hf   = '✅' if r['hf_ratio'] < 0.7    else '⚠️ NOISY'
        ok_flat = '✅' if not r['artifact_flat'] else '⚠️ FLAT'
        ok_sat  = '✅' if not r['saturated']     else '⚠️ SATURATED'
        print(f"\n  [{task}]")
        print(f"    Duration   : {r['duration_s']:.1f} s")
        print(f"    Mean ± std : {r['mean_uv']:.4g} ± {r['std_uv']:.4g}")
        print(f"    PTP        : {r['ptp_uv']:.4g}   {ok_ptp}")
        print(f"    HF ratio   : {r['hf_ratio']:.3f}     {ok_hf}")
        print(f"    Flat chan   :              {ok_flat}")
        print(f"    Saturation :              {ok_sat}")


# ─── Step 6 – Resampling 128 → 250 Hz ────────────────────────────────────────

def resample_all(fp2_signals):
    """Resample every Fp2 signal from 128 Hz to 250 Hz."""
    print(f"\n{'='*64}")
    print(f"  STEP 6 — Resampling {FS_STRESS} → {FS_TARGET} Hz ({CH_LABEL})")
    print(f"{'='*64}")

    fp2_250 = {}
    for task, (fp2, fs) in fp2_signals.items():
        resampled = resample_signal(fp2, int(fs), FS_TARGET)
        expected  = int(len(fp2) * FS_TARGET / fs)
        ok = '✅' if abs(len(resampled) - expected) <= 2 else '⚠️'
        print(f"\n  [{task}]")
        print(f"    Original  : {len(fp2)} samples @ {fs:.0f} Hz  ({len(fp2)/fs:.2f} s)")
        print(f"    Resampled : {len(resampled)} samples @ {FS_TARGET} Hz  {ok}")
        fp2_250[task] = resampled
    return fp2_250


# ─── Step 7 – Visualisations ─────────────────────────────────────────────────

def visualize_all(file_results, fp2_signals, fp2_250):
    """Generate all validation figures for Fp2."""
    print(f"\n{'='*64}")
    print(f"  STEP 7 — Generating visualisations ({CH_LABEL})")
    print(f"{'='*64}\n")

    ts_128 = {t: fp2 for t, (fp2, _) in fp2_signals.items()}
    ts_250 = dict(fp2_250)

    plot_time_series(
        ts_128, FS_STRESS, n_seconds=10,
        title=f"EEG {CH_LABEL} — SAM40 · Subject {SUBJECT} Trial {TRIAL}  (128 Hz raw)",
        save_path=OUT_DIR / f"01_timeseries_raw_{CH_LABEL.lower()}_s{SUBJECT}_t{TRIAL}.png",
    )

    plot_time_series(
        ts_250, FS_TARGET, n_seconds=10,
        title=f"EEG {CH_LABEL} — SAM40 · Subject {SUBJECT} Trial {TRIAL}  (250 Hz resampled)",
        save_path=OUT_DIR / f"02_timeseries_resampled_{CH_LABEL.lower()}_s{SUBJECT}_t{TRIAL}.png",
    )

    plot_psd_comparison(
        ts_128, FS_STRESS, fmax=60,
        title=f"PSD ({CH_LABEL}) — SAM40 · Subject {SUBJECT} Trial {TRIAL}  (128 Hz raw)",
        save_path=OUT_DIR / f"03_psd_raw_{CH_LABEL.lower()}_s{SUBJECT}_t{TRIAL}.png",
    )

    plot_psd_comparison(
        ts_250, FS_TARGET, fmax=60,
        title=f"PSD ({CH_LABEL}) — SAM40 · Subject {SUBJECT} Trial {TRIAL}  (250 Hz resampled)",
        save_path=OUT_DIR / f"04_psd_resampled_{CH_LABEL.lower()}_s{SUBJECT}_t{TRIAL}.png",
    )

    plot_amplitude_histogram(
        ts_128,
        title=f"Amplitude Distribution ({CH_LABEL}) — SAM40 · Subject {SUBJECT}",
        save_path=OUT_DIR / f"05_histogram_{CH_LABEL.lower()}_s{SUBJECT}_t{TRIAL}.png",
    )

    first_task = TASKS[0]
    if first_task in file_results:
        eeg, fs, ch_names = file_results[first_task]
        n_ch  = eeg.shape[1]
        names = ch_names if ch_names else [f'Ch{i:02d}' for i in range(n_ch)]
        plot_all_channels(
            eeg, names, float(fs), n_seconds=5,
            title=f"All Channels — {first_task} · Subject {SUBJECT} ({CH_LABEL} in red)",
            save_path=OUT_DIR / f"06_all_channels_{first_task.lower()}_{CH_LABEL.lower()}_s{SUBJECT}.png",
        )

    _plot_resample_check(ts_128, ts_250)
    _plot_band_power(ts_128, FS_STRESS, suffix=f'128Hz_raw_{CH_LABEL.lower()}')
    _plot_band_power(ts_250, FS_TARGET, suffix=f'250Hz_resampled_{CH_LABEL.lower()}')


print("Test de tracé simple...")
plt.figure()
plt.plot([0,1], [0,1])
plt.savefig(OUT_DIR / "test.png")
print("test.png créé, taille:", (OUT_DIR / "test.png").stat().st_size)


def _plot_resample_check(ts_128, ts_250):
    """Overlay PSD before and after resampling."""
    fig, axes = plt.subplots(1, len(TASKS), figsize=(14, 5))
    if len(TASKS) == 1:
        axes = [axes]

    for ax, task in zip(axes, TASKS):
        if task not in ts_128 or task not in ts_250:
            continue
        f1, p1 = compute_psd(ts_128[task], FS_STRESS)
        f2, p2 = compute_psd(ts_250[task], FS_TARGET)

        ax.semilogy(f1[f1 <= 60], p1[f1 <= 60],
                    color='#1976D2', linewidth=1.5, label='128 Hz (original)', alpha=0.9)
        ax.semilogy(f2[f2 <= 60], p2[f2 <= 60],
                    color='#E53935', linewidth=1.5, linestyle='--',
                    label='250 Hz (resampled)', alpha=0.9)
        ax.axvline(50, color='gray', linewidth=1.0, linestyle=':', alpha=0.6, label='50 Hz')
        ax.set_xlabel('Frequency (Hz)', fontsize=10)
        ax.set_ylabel('PSD [µV²/Hz] — log', fontsize=10)
        ax.set_title(f'{task} ({CH_LABEL}) — resampling quality', fontsize=11)
        ax.legend(fontsize=9)
        ax.set_xlim(0, 60)
        ax.grid(True, alpha=0.25)

    fig.suptitle(f'Resampling Verification ({CH_LABEL}) — Subject {SUBJECT} Trial {TRIAL}',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    fname = OUT_DIR / f"07_resample_check_{CH_LABEL.lower()}_s{SUBJECT}_t{TRIAL}.png"
    plt.savefig(str(fname), dpi=150, bbox_inches='tight')
    print(f"  Saved: {fname}")
    plt.close(fig)


def _plot_band_power(signals, fs, suffix):
    """Grouped bar chart of band power per task."""
    task_list = list(signals.keys())
    if not task_list:
        return

    band_names = None
    powers = {}
    for task, sig in signals.items():
        bp = compute_band_powers(sig, fs)
        powers[task] = list(bp.values())
        if band_names is None:
            band_names = list(bp.keys())

    n_bands = len(band_names)
    n_tasks = len(task_list)
    x       = np.arange(n_bands)
    width   = 0.80 / n_tasks

    task_colors = {'Arithmetic': '#9C27B0', 'Stroop': '#FF5722', 'Relax': '#00BCD4'}

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, task in enumerate(task_list):
        offset = (i - n_tasks / 2 + 0.5) * width
        color  = task_colors.get(task, '#546E7A')
        ax.bar(x + offset, powers[task], width,
               label=task, color=color, alpha=0.85, edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(band_names, fontsize=10)
    ax.set_ylabel('Band Power (µV²)', fontsize=10)
    ax.set_title(f'EEG Band Power ({CH_LABEL}) — SAM40  ({suffix}) — Subject {SUBJECT}',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.25, axis='y')
    plt.tight_layout()

    idx   = 8 if '128' in suffix else 9
    fname = OUT_DIR / f"0{idx}_band_power_{suffix}_s{SUBJECT}.png"
    plt.savefig(str(fname), dpi=150, bbox_inches='tight')
    print(f"  Saved: {fname}")
    plt.close(fig)


# ─── Step 8 – Cross-subject statistics ───────────────────────────────────────

def cross_subject_stats(n_subjects=N_CROSS):
    """Duration, std, ptp for Fp2 across subjects (trial 1)."""
    print(f"\n{'='*64}")
    print(f"  STEP 8 — Cross-subject check ({CH_LABEL}, {n_subjects} subjects)")
    print(f"{'='*64}")

    hdr = (f"  {'Task':<13} {'Subj':<6} {'Dur(s)':<9} "
           f"{'Std':<14} {'PTP':<14} {CH_LABEL} idx")
    print(f"\n{hdr}")
    print(f"  {'-'*65}")

    for task in TASKS:
        for subj in range(1, n_subjects + 1):
            fp = RAW_DIR / f"{task}_sub_{subj}_trial1.mat"
            if not fp.exists():
                continue
            try:
                eeg, fs, ch_names, _ = load_stress_file(fp)
                if eeg is None:
                    continue
                fp2, idx = extract_fp2(eeg, ch_names, task)
                dur = len(fp2) / fs
                print(f"  {task:<13} {subj:<6} {dur:<9.1f} "
                      f"{np.std(fp2):<14.4g} {np.ptp(fp2):<14.4g} {idx}")
            except Exception as e:
                print(f"  {task:<13} {subj:<6} ERROR: {e}")

    _plot_cross_subject_psd(n_subjects)


def _plot_cross_subject_psd(n_subjects):
    """Overlay Fp2 PSD for multiple subjects."""
    fig, axes = plt.subplots(1, len(TASKS), figsize=(14, 5))
    if len(TASKS) == 1:
        axes = [axes]

    for ax, task in zip(axes, TASKS):
        cmap = plt.cm.plasma(np.linspace(0.2, 0.85, n_subjects))
        for i, subj in enumerate(range(1, n_subjects + 1)):
            fp = RAW_DIR / f"{task}_sub_{subj}_trial1.mat"
            if not fp.exists():
                continue
            try:
                eeg, fs, ch_names, _ = load_stress_file(fp)
                if eeg is None:
                    continue
                fp2, _ = extract_fp2(eeg, ch_names, task)
                freqs, psd = compute_psd(fp2, float(fs))
                mask = freqs <= 60
                ax.semilogy(freqs[mask], psd[mask], color=cmap[i],
                            linewidth=1.0, alpha=0.8, label=f'S{subj}')
            except Exception:
                pass

        ax.set_xlabel('Frequency (Hz)', fontsize=10)
        ax.set_ylabel('PSD [µV²/Hz] — log', fontsize=10)
        ax.set_title(f'{task} ({CH_LABEL}) — cross-subject PSD', fontsize=11)
        ax.legend(fontsize=7, ncol=2)
        ax.set_xlim(0, 60)
        ax.grid(True, alpha=0.25)

    fig.suptitle(f'Cross-subject PSD ({CH_LABEL}, trial 1) — SAM40',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    fname = OUT_DIR / f"10_cross_subject_psd_{CH_LABEL.lower()}.png"
    plt.savefig(str(fname), dpi=150, bbox_inches='tight')
    print(f"  Saved: {fname}")
    plt.close(fig)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*64}")
    print(f"  SAM40 Stress — Re-validation on channel {CH_LABEL}")
    print(f"  Hardware: {CH_LABEL} (active) – M2 (ref) – M1 (gnd)")
    print(f"{'='*64}")
    print(f"  Dataset : {STRESS_ROOT}")
    print(f"  Output  : {OUT_DIR}")
    print(f"  Channel : {CH_LABEL} (index {FP2_IDX_STRESS_FALLBACK} in Emotiv 32-ch)")
    print(f"  Subject : {SUBJECT}  Trial : {TRIAL}")

    explore_mat_structure()

    file_results = validate_files()
    if not file_results:
        print("\n  ❌  No files could be loaded. Aborting.")
        return

    fp2_signals = extract_all_fp2(file_results)
    load_and_display_scales()
    run_artifact_checks(fp2_signals)
    fp2_250 = resample_all(fp2_signals)
    visualize_all(file_results, fp2_signals, fp2_250)
    cross_subject_stats(n_subjects=N_CROSS)

    print(f"\n{'='*64}")
    print(f"  ✅ Re-validation on {CH_LABEL} complete.")
    print(f"  Figures saved to: {OUT_DIR}")
    print(f"{'='*64}\n")


if __name__ == '__main__':
    main()