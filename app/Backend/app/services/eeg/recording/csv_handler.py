# backend/recording/csv_handler.py
"""
Gestionnaire d'enregistrement CSV pour NeuroCap EEG.
"""

import csv
import os
from datetime import datetime
from ..utils.constants import REC_DIR

# Variables globales d'enregistrement
rec_active           = False
csv_signal_file      = None
csv_signal_writer    = None
csv_epochs_file      = None
csv_epochs_writer    = None
last_rec_signal_path = ""

def start_recording():
    """Démarre l'enregistrement CSV."""
    global rec_active, csv_signal_file, csv_signal_writer
    global csv_epochs_file, csv_epochs_writer, last_rec_signal_path

    rec_active = True
    ts_str     = datetime.now().strftime("%Y%m%d_%H%M%S")

    sig_path          = f"{REC_DIR}/signal_{ts_str}.csv"
    csv_signal_file   = open(sig_path, "w", newline="")
    csv_signal_writer = csv.writer(csv_signal_file)
    csv_signal_writer.writerow([
        "timestamp_us", "raw_uV", "filtered_uV", "batt_V",
        "lo_plus_raw", "lo_minus_raw", "pkt_id", "electrode_ok"
    ])
    last_rec_signal_path = sig_path

    ep_path           = f"{REC_DIR}/epochs_{ts_str}.csv"
    csv_epochs_file   = open(ep_path, "w", newline="")
    csv_epochs_writer = csv.writer(csv_epochs_file)
    csv_epochs_writer.writerow([
        "epoch_idx", "timestamp",
        "fractal_dim", "fd_degree_dist_mean", "fd_clustering_coeff", "fd_jaccard_mean",
        "rel_alpha", "rel_beta", "theta_beta", "engagement", "stress_idx",
        "pac_theta_gamma", "sef95", "hjorth_complexity", "spectral_entropy",
    ])

    return sig_path

def stop_recording():
    """Arrête l'enregistrement CSV."""
    global rec_active, csv_signal_file, csv_signal_writer, csv_epochs_file, csv_epochs_writer
    rec_active = False
    if csv_signal_file:
        csv_signal_file.close()
        csv_signal_file   = None
        csv_signal_writer = None
    if csv_epochs_file:
        csv_epochs_file.close()
        csv_epochs_file   = None
        csv_epochs_writer = None

def write_signal_sample(ts, raw_uv, filtered_uv, batt_v, lo_plus, lo_minus, pkt_id, electrode_ok):
    """Écrit un échantillon signal dans le CSV."""
    if rec_active and csv_signal_writer:
        csv_signal_writer.writerow([
            ts, raw_uv, round(filtered_uv, 3), batt_v,
            lo_plus, lo_minus, pkt_id, int(electrode_ok)
        ])

def write_epoch(epoch_idx, timestamp, features, graph):
    """Écrit une époque dans le CSV."""
    if rec_active and csv_epochs_writer:
        feat = features
        grf  = graph or {}
        csv_epochs_writer.writerow([
            epoch_idx, timestamp,
            feat.get("fractal_dim",          0),
            grf.get("degree_dist_mean",      0),
            grf.get("clustering_coeff",      0),
            grf.get("jaccard_mean",          0),
            feat.get("rel_alpha",            0),
            feat.get("rel_beta",             0),
            feat.get("theta_beta",           0),
            feat.get("engagement",           0),
            feat.get("stress_idx",           0),
            feat.get("pac_theta_gamma",      0),
            feat.get("sef95",                0),
            feat.get("hjorth_complexity",    0),
            feat.get("spectral_entropy",     0),
        ])

def get_last_signal_path():
    """Retourne le chemin du dernier fichier signal enregistré."""
    return last_rec_signal_path if last_rec_signal_path and os.path.exists(last_rec_signal_path) else None