# dsp/file_processor.py
"""
Traitement batch de fichiers EEG — EDF / CSV / TXT
Pipeline : lecture → adaptation (fs, durée) → Golden Filter → FeatEng → LightGBM

Robustesse :
  - Rééchantillonnage automatique vers 250 Hz (128, 160, 200, 256 Hz...)
  - Padding miroir si signal < 4 s
  - Détection fs depuis colonne 'time', nom fichier, métadonnées EDF
  - Séparateurs auto : virgule, point-virgule, tabulation, espace
  - Rejet souple des artefacts (amplitude relative, pas de seuil fixe µV)
  - Catch des erreurs de filtre par époque
"""

import sys
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger("NeuroCap")

# ── Racine projet (pour feature_eng) ─────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_extract_feateng = None
try:
    from src.data.feature_eng import extract_all_features as _extract_feateng
    logger.info("[FileProcessor] feature_eng chargé")
except Exception as _e:
    logger.warning(f"[FileProcessor] feature_eng non disponible : {_e}")

_ml_clf = None
try:
    from .ml_classifier import MLClassifier
    _ml_clf = MLClassifier()
    logger.info("[FileProcessor] MLClassifier chargé")
except Exception as _e:
    logger.warning(f"[FileProcessor] MLClassifier non disponible : {_e}")

# ── Constantes ────────────────────────────────────────────────────────────────
TARGET_FS     = 250    # Hz cible (requis par le classifieur)
EPOCH_SAMPLES = 1000   # 4 s @ 250 Hz
STEP_SAMPLES  = 250    # overlap 75 %

# Mots-clés colonne signal (ordre de priorité)
_SIGNAL_KEYWORDS = ["fp2", "fp1", "raw", "eeg", "uv", "voltage",
                    "signal", "value", "amplitude", "data", "mv", "ch"]
# Mots-clés colonne temps
_TIME_KEYWORDS   = ["time", "timestamp", "t", "second", "sec", "ms"]
# Mots-clés colonne fs
_FS_KEYWORDS     = ["fs", "freq", "sampling", "rate", "hz", "srate"]
# Canaux EDF préférés
_PREFERRED_CH    = ["FP2", "FP 2", "FP1", "FP 1", "AF3", "AF4",
                    "AFZ", "FZ", "F3", "F4", "EEG"]


# ═════════════════════════════════════════════════════════════════════════════
# LECTURE — EDF
# ═════════════════════════════════════════════════════════════════════════════

def read_edf(content: bytes) -> tuple:
    """
    Lit un fichier EDF. Retourne (signal: ndarray, fs: int).
    Priorité canal : Fp2 > Fp1 > AF3 > premier canal EEG > premier canal.
    """
    import tempfile, os
    try:
        import pyedflib
    except ImportError:
        raise RuntimeError("pyedflib non installé — lancez : pip install pyedflib")

    with tempfile.NamedTemporaryFile(suffix=".edf", delete=False) as f:
        f.write(content)
        tmp = f.name

    try:
        with pyedflib.EdfReader(tmp) as edf:
            labels = edf.getSignalLabels()
            ch_idx = _pick_edf_channel(labels)
            fs     = int(edf.getSampleFrequency(ch_idx))
            sig    = edf.readSignal(ch_idx).astype(np.float64)
            logger.info(f"[FileProcessor] EDF — canal '{labels[ch_idx]}', {fs} Hz, {len(sig)} samples")
            return sig, fs
    finally:
        os.unlink(tmp)


def _pick_edf_channel(labels: list) -> int:
    upper = [str(l).strip().upper() for l in labels]
    for pref in _PREFERRED_CH:
        for i, u in enumerate(upper):
            if pref in u:
                return i
    return 0


# ═════════════════════════════════════════════════════════════════════════════
# LECTURE — CSV / TXT
# ═════════════════════════════════════════════════════════════════════════════

def read_csv_txt(content: bytes, filename: str = "signal.csv") -> tuple:
    """
    Lit un CSV ou TXT contenant un signal EEG brut.
    Retourne (signal: ndarray, fs: int).

    Détection automatique :
      - Séparateur : virgule, point-virgule, tabulation, espace
      - Colonne signal : fp2, raw, uv, voltage, eeg, signal, value…
      - Colonne temps  : time, timestamp, t, second…
      - Fréquence d'échantillonnage depuis colonne temps ou nom fichier
    """
    text = content.decode("utf-8", errors="replace").strip()

    # Supprimer les lignes commentaires
    lines = [l for l in text.splitlines()
             if l.strip() and not l.strip().startswith(("#", "%", "//"))]
    if not lines:
        raise ValueError("Fichier vide ou non lisible")

    # ── Détection séparateur ─────────────────────────────────────
    sep = _detect_sep(lines[0])

    # ── Détection header ─────────────────────────────────────────
    has_header, header_cols = _detect_header(lines[0], sep)
    data_lines = lines[1:] if has_header else lines

    # ── Parse numérique ──────────────────────────────────────────
    rows = []
    for line in data_lines:
        parts = line.split(sep)
        try:
            row = [float(p.strip().replace(",", ".")) for p in parts if p.strip()]
            if row:
                rows.append(row)
        except ValueError:
            continue

    if not rows:
        raise ValueError(
            f"Aucune donnée numérique trouvée ({len(data_lines)} lignes lues)."
            " Vérifiez le format du fichier."
        )

    # Homogénéiser la longueur des lignes
    max_cols = max(len(r) for r in rows)
    arr = np.array(
        [r + [np.nan] * (max_cols - len(r)) for r in rows],
        dtype=np.float64
    )

    # ── Sélection colonne signal ─────────────────────────────────
    sig_col = _pick_signal_col(arr, header_cols, has_header)
    sig     = arr[:, sig_col]
    sig     = sig[~np.isnan(sig)]   # retirer NaN résiduels

    if len(sig) == 0:
        raise ValueError("La colonne signal ne contient que des valeurs invalides")

    # ── Détection fs ─────────────────────────────────────────────
    fs = _detect_fs(arr, header_cols, has_header, filename)

    logger.info(
        f"[FileProcessor] CSV — {len(sig)} samples, "
        f"fs={fs} Hz (estimé), colonne={header_cols[sig_col] if has_header else sig_col}"
    )
    return sig, fs


def _detect_sep(line: str) -> str:
    """Retourne le séparateur le plus probable."""
    counts = {
        ";": line.count(";"),
        ",": line.count(","),
        "\t": line.count("\t"),
    }
    best = max(counts, key=counts.get)
    if counts[best] == 0:
        return " "
    return best


def _detect_header(line: str, sep: str) -> tuple:
    """Retourne (has_header: bool, cols: list[str])."""
    parts = [p.strip() for p in line.split(sep) if p.strip()]
    has_header = False
    for p in parts:
        try:
            float(p.replace(",", "."))
        except ValueError:
            has_header = True
            break
    cols = [p.lower() for p in parts] if has_header else list(range(len(parts)))
    return has_header, cols


def _pick_signal_col(arr: np.ndarray, header_cols: list, has_header: bool) -> int:
    """Trouve la colonne contenant le signal EEG."""
    if arr.shape[1] == 1:
        return 0

    # Chercher par nom de colonne
    if has_header:
        for kw in _SIGNAL_KEYWORDS:
            for i, col in enumerate(header_cols):
                if kw in str(col):
                    return i

        # Éviter les colonnes 'time' / 'timestamp'
        time_idxs = set()
        for i, col in enumerate(header_cols):
            if any(kw in str(col) for kw in _TIME_KEYWORDS):
                time_idxs.add(i)

        # Prendre la première colonne non-temps
        for i in range(arr.shape[1]):
            if i not in time_idxs:
                return i

    # Heuristique sans header : colonne avec la plus grande variance
    # (exclut les timestamps monotones et colonnes constantes)
    variances = []
    for i in range(arr.shape[1]):
        col = arr[:, i]
        col = col[~np.isnan(col)]
        if len(col) == 0:
            variances.append(0.0)
            continue
        # Pénaliser les colonnes monotones (timestamps)
        diffs = np.diff(col)
        monotone_score = np.sum(diffs > 0) / max(len(diffs), 1)
        variance = float(np.var(col))
        if monotone_score > 0.95:   # Colonne quasi-monotone = timestamp
            variance *= 0.01
        variances.append(variance)

    return int(np.argmax(variances))


def _detect_fs(arr: np.ndarray, header_cols: list, has_header: bool,
               filename: str) -> int:
    """
    Estime la fréquence d'échantillonnage.

    Ordre de priorité :
    1. Colonne fs / sampling_rate dans le CSV
    2. Colonne temps (dt = 1/fs)
    3. Nom du fichier (ex: "subject1_250hz.csv")
    4. Défaut : 250 Hz
    """
    # 1. Colonne fs explicite
    if has_header:
        for i, col in enumerate(header_cols):
            if any(kw in str(col) for kw in _FS_KEYWORDS):
                try:
                    val = float(arr[0, i])
                    if 10 <= val <= 10000:
                        return int(val)
                except Exception:
                    pass

    # 2. Colonne temps → dt
    if has_header:
        for i, col in enumerate(header_cols):
            if any(kw in str(col) for kw in _TIME_KEYWORDS):
                try:
                    times = arr[:, i]
                    times = times[~np.isnan(times)]
                    if len(times) > 2:
                        dt = np.median(np.diff(times))
                        if dt > 0:
                            # Détecter l'unité : secondes ou millisecondes ?
                            if "ms" in str(col) or dt > 0.5:
                                fs_est = 1000.0 / dt  # ms → Hz
                            else:
                                fs_est = 1.0 / dt     # s → Hz
                            if 10 <= fs_est <= 10000:
                                return int(round(fs_est))
                except Exception:
                    pass

    # 3. Nom de fichier
    fname = Path(filename).stem.lower()
    for hint in ["10000", "5000", "2048", "1024", "1000", "512",
                 "500", "256", "250", "200", "160", "128", "64"]:
        if hint in fname:
            return int(hint)

    # 4. Défaut
    return 250


# ═════════════════════════════════════════════════════════════════════════════
# ADAPTATION : rééchantillonnage + padding
# ═════════════════════════════════════════════════════════════════════════════

def _adapt_signal(signal_uv: np.ndarray, fs: int) -> tuple:
    """
    Normalise le signal vers TARGET_FS Hz, garantit ≥ EPOCH_SAMPLES samples.

    1. Rééchantillonnage scipy.signal.resample si fs ≠ 250 Hz
    2. Padding miroir si durée < 4 s

    Retourne (signal_adapted, warnings: list[str])
    """
    warnings = []

    # ── Rééchantillonnage ────────────────────────────────────────
    if fs != TARGET_FS and fs > 0:
        from scipy.signal import resample as scipy_resample
        new_len = int(round(len(signal_uv) * TARGET_FS / fs))
        if new_len < 2:
            raise ValueError(f"Signal trop court après rééchantillonnage ({new_len} samples)")
        signal_uv = scipy_resample(signal_uv, new_len).astype(np.float64)
        warnings.append(f"Rééchantillonné {fs} Hz → {TARGET_FS} Hz")
        fs = TARGET_FS

    # ── Normalisation amplitude (si valeurs hors µV raisonnable) ─
    # Certains EDF stockent en µV avec DC offset énorme, d'autres en mV
    rms = float(np.sqrt(np.mean(signal_uv ** 2)))
    if rms > 1e5:           # Probablement en µV brut avec offset
        signal_uv = signal_uv - np.median(signal_uv)
    elif rms < 1e-3 and rms > 0:   # Probablement en V → convertir en µV
        signal_uv = signal_uv * 1e6
        warnings.append("Signal converti V → µV")

    # ── Padding miroir si trop court ─────────────────────────────
    if len(signal_uv) < EPOCH_SAMPLES:
        needed  = EPOCH_SAMPLES - len(signal_uv)
        orig_n  = len(signal_uv)
        # Padding par miroir (plus naturel que zéro-padding pour l'EEG)
        mirror  = signal_uv[::-1]
        tile_n  = int(np.ceil(needed / max(len(mirror), 1)))
        padding = np.tile(mirror, tile_n)[:needed]
        signal_uv = np.concatenate([signal_uv, padding])
        warnings.append(
            f"Signal trop court ({orig_n} samples / {orig_n/TARGET_FS:.2f} s) "
            f"→ padding miroir à {len(signal_uv)} samples"
        )

    return signal_uv, warnings


# ═════════════════════════════════════════════════════════════════════════════
# TRAITEMENT BATCH
# ═════════════════════════════════════════════════════════════════════════════

def process_signal(signal_uv: np.ndarray, fs: int = TARGET_FS) -> dict:
    """
    Pipeline batch complet :
      Adaptation (resample + pad) → découpage époques → Golden Filter
      → z-score → 63 features FeatEng → LightGBM predict_proba

    Robuste à tout fs et à tout signal ≥ 1 sample.
    """
    # ── Adaptation ───────────────────────────────────────────────
    signal_uv, adapt_warnings = _adapt_signal(signal_uv, fs)
    for w in adapt_warnings:
        logger.info(f"[FileProcessor] {w}")

    # Toujours 250 Hz après adaptation
    fs = TARGET_FS

    from .filters import FilterBank
    fb = FilterBank(fs)

    # ── Rejet artefact adaptatif ──────────────────────────────────
    # Seuils relatifs au signal entier (évite les valeurs absolues µV)
    global_rms = float(np.sqrt(np.mean(signal_uv ** 2)))
    max_amp    = max(global_rms * 20, 50.0)   # seuil = 20× RMS global
    min_amp    = max(global_rms * 0.01, 0.1)  # seuil = 1% RMS global

    n_samples     = len(signal_uv)
    n_total       = 0
    n_accepted    = 0
    n_filtered    = 0
    epochs_result = []

    start = 0
    while start + EPOCH_SAMPLES <= n_samples:
        raw_epoch = signal_uv[start : start + EPOCH_SAMPLES]
        n_total  += 1

        # ── Rejet amplitude ────────────────────────────────────────
        amp_range = float(np.ptp(raw_epoch))
        rms_ep    = float(np.sqrt(np.mean(raw_epoch ** 2)))

        if amp_range < min_amp or amp_range > max_amp:
            start += STEP_SAMPLES
            continue

        # ── Golden Filter (zero-phase) ────────────────────────────
        try:
            filtered = fb.filter_epoch(raw_epoch)
        except Exception as fe:
            logger.debug(f"[FileProcessor] Filtre epoch {n_total} ignorée : {fe}")
            n_filtered += 1
            start += STEP_SAMPLES
            continue

        # ── 63 features FeatEng (z-score) ────────────────────────
        ml_features: dict = {}
        std = float(np.std(filtered))
        if _extract_feateng is not None and std > 1e-10:
            try:
                epoch_z     = (filtered - np.mean(filtered)) / std
                ml_features = _extract_feateng(epoch_z)
            except Exception:
                pass

        # ── Prédiction LightGBM ───────────────────────────────────
        ml_prediction = None
        if ml_features and _ml_clf is not None:
            try:
                ml_prediction = _ml_clf.predict_from_dict(ml_features)
            except Exception:
                pass

        n_accepted += 1
        epochs_result.append({
            "epoch_idx":     n_accepted,
            "time_s":        round(start / fs, 2),
            "ml_prediction": ml_prediction,
            "amplitude_uv":  round(amp_range, 2),
            "rms_uv":        round(rms_ep,    2),
        })

        start += STEP_SAMPLES

    summary = _compute_summary(epochs_result)
    summary["adapt_warnings"] = adapt_warnings

    return {
        "n_samples":         n_samples,
        "duration_s":        round(n_samples / fs, 1),
        "fs":                fs,
        "n_epochs_total":    n_total,
        "n_epochs_accepted": n_accepted,
        "n_epochs_filtered": n_filtered,
        "epochs":            epochs_result,
        "summary":           summary,
    }


# ═════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ
# ═════════════════════════════════════════════════════════════════════════════

def _compute_summary(epochs: list) -> dict:
    preds = [e["ml_prediction"] for e in epochs if e.get("ml_prediction")]

    if not preds:
        return {
            "n_classified":      0,
            "concentration_pct": 0.0,
            "stress_pct":        0.0,
            "uncertain_pct":     0.0,
            "dominant_state":    "inconnu",
            "mean_confidence":   0.0,
            "adapt_warnings":    [],
        }

    n        = len(preds)
    n_conc   = sum(1 for p in preds if p["state"] == "concentration" and not p["uncertain"])
    n_stress = sum(1 for p in preds if p["state"] == "stress"        and not p["uncertain"])
    n_uncert = sum(1 for p in preds if p["uncertain"])
    mean_conf = round(float(np.mean([p["confidence"] for p in preds])), 4)

    dominant = (
        "concentration" if n_conc > n_stress else
        "stress"        if n_stress > n_conc  else
        "neutre"
    )

    return {
        "n_classified":      n,
        "concentration_pct": round(n_conc   / n * 100, 1),
        "stress_pct":        round(n_stress / n * 100, 1),
        "uncertain_pct":     round(n_uncert / n * 100, 1),
        "dominant_state":    dominant,
        "mean_confidence":   mean_conf,
        "adapt_warnings":    [],
    }
