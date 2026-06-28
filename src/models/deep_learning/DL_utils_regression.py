"""
DL_utils_regression.py
======================
Utilitaires DL pour régression de score EEG (0-10).
Miroir de DL_utils.py, adapté au paradigme scoring/régression.

Pour chaque architecture, lance :
  - 5 expériences (A/B/C/D/FULL) × 2 cibles (conc, stress)
  - LOSO sur expérience A
  - Métriques via metrics_professional.py (MAE, RMSE, R², AUC, bootstrap…)
  - Rapports sous reports/Regression/DL/{model}/{target}/{exp}/
"""

import sys, json, time, warnings, copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
from torch.amp import autocast, GradScaler
from sklearn.metrics import roc_curve as sk_roc_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

warnings.filterwarnings('ignore')

_HERE        = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "models"))

from metrics_professional import (
    compute_full_metrics, bootstrap_ci, permutation_test,
    calibration_analysis, bland_altman_analysis, icc,
    stability_analysis, decision_curve_analysis,
    generate_professional_report,
    plot_reliability_diagram, plot_bland_altman,
    plot_bootstrap_ci_bars, plot_full_confusion_matrix,
    plot_per_subject_heatmap, plot_decision_curve,
)

# ─── Constantes ───────────────────────────────────────────────────────────────
DEVICE    = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
USE_AMP   = torch.cuda.is_available()

EPOCH_SAMPLES   = 1000
N_OUT           = 1               # sortie scalaire (score continu 0-10)
LR              = 3e-3
WD              = 1e-4
MAX_EPOCHS      = 50
PATIENCE        = 10
BATCH_SIZE      = 32
GRAD_CLIP       = 1.0
NUM_WORKERS     = 0   # 0 requis sur Windows (shared memory DataLoader incompatible)
SCORE_THRESHOLD = 5.0             # seuil Low/High pour métriques binaires

REGRESSION_DATA = PROJECT_ROOT / "data"    / "Regression" / "augmented"
OUTPUT_BASE     = PROJECT_ROOT / "reports" / "Regression" / "DL"
MODEL_BASE      = PROJECT_ROOT / "models"  / "Regression" / "DL"

TARGETS     = ['conc', 'stress']
EXPERIMENTS = ['A', 'B', 'C', 'D', 'FULL']
N_CLASSES   = N_OUT     # alias pour les fichiers d'architecture


# ─── Modules partagés (réexportés pour les architectures) ─────────────────────
class CNNPreEncoder(nn.Module):
    """Compresse (batch,1,1000) → (batch,seq,feat) avant RNN."""
    def __init__(self, out_features=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=25, stride=4, padding=12),
            nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.1),
            nn.Conv1d(32, 64, kernel_size=11, stride=4, padding=5),
            nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.1),
            nn.Conv1d(64, out_features, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(out_features), nn.ReLU(),
        )
    def forward(self, x):
        return self.encoder(x).permute(0, 2, 1)


class BahdanauAttention(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_size, min(64, hidden_size)), nn.Tanh(),
            nn.Linear(min(64, hidden_size), 1),
        )
    def forward(self, rnn_output):
        weights = torch.softmax(self.attn(rnn_output), dim=1)
        return (weights * rnn_output).sum(dim=1), weights


# ─── Utilitaires déséquilibre & seuil ────────────────────────────────────────

def find_youden_threshold(y_true, y_pred_continuous, default=SCORE_THRESHOLD):
    """
    Seuil optimal via l'index de Youden J = argmax(Sensitivity + Specificity - 1).
    Ref : Youden (1950) Cancer 3(1):32-35.
    Corrige le biais du seuil fixe 5.0 quand la distribution est déséquilibrée.
    """
    y_bin = (np.asarray(y_true, float) >= default).astype(int)
    if len(np.unique(y_bin)) < 2:
        return default
    try:
        fpr, tpr, thresholds = sk_roc_curve(y_bin, np.asarray(y_pred_continuous, float))
        j_idx = int(np.argmax(tpr - fpr))
        return float(np.clip(thresholds[j_idx], 1.0, 9.0))
    except Exception:
        return default


def _make_weighted_sampler(y_tensor: torch.Tensor, threshold: float = SCORE_THRESHOLD):
    """
    WeightedRandomSampler : sur-échantillonne la classe High pour batches équilibrés.
    High reçoit poids n_Low/n_High — He & Garcia (2009) IEEE TKDE 21(9):1263-1284.
    """
    y_bin  = (y_tensor >= threshold).float()
    n_low  = max((y_bin == 0).sum().item(), 1)
    n_high = max((y_bin == 1).sum().item(), 1)
    weights = torch.where(y_bin == 1,
                          torch.tensor(float(n_low) / n_high),
                          torch.ones(len(y_tensor)))
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


# ─── Données ──────────────────────────────────────────────────────────────────
def _load_split(target: str, exp: str):
    d = REGRESSION_DATA / target
    X_train = np.load(d / f"X_train_{exp}.npy")
    y_train = np.load(d / f"y_train_{exp}.npy").astype(np.float32)
    X_val   = np.load(d / "X_val.npy")
    y_val   = np.load(d / "y_val.npy").astype(np.float32)
    X_test  = np.load(d / "X_test.npy")
    y_test  = np.load(d / "y_test.npy").astype(np.float32)

    sid_train = sid_val = sid_test = None
    for name in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        p = d / name
        if p.exists():
            sid_train = np.load(p); break
    for name in ["subject_ids_val.npy"]:
        p = d / name
        if p.exists(): sid_val = np.load(p)
    for name in ["subject_ids_test.npy"]:
        p = d / name
        if p.exists(): sid_test = np.load(p)

    return X_train, y_train, X_val, y_val, X_test, y_test, sid_train, sid_val, sid_test


def prepare_data(X: np.ndarray, y: np.ndarray):
    X_t = torch.FloatTensor(X)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)       # (N, 1, 1000)
    return X_t, torch.FloatTensor(y)


# ─── Entraînement ─────────────────────────────────────────────────────────────
def train_model(model, X_train, y_train, X_val, y_val,
                epochs=MAX_EPOCHS, patience=PATIENCE, class_weighted=True):
    """
    Régression avec Huber loss + WeightedRandomSampler (class_weighted=True)
    + early stopping sur val_loss.
    class_weighted=True : sur-échantillonne la classe High → corrige always-Low.
    Ref : He & Garcia (2009) IEEE TKDE 21(9):1263-1284.
    """
    model = model.to(DEVICE)
    criterion = nn.HuberLoss(delta=1.0)
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, min_lr=LR * 0.01)

    X_tr, y_tr = prepare_data(X_train, y_train)
    X_vl, y_vl = prepare_data(X_val,   y_val)

    if class_weighted:
        sampler = _make_weighted_sampler(y_tr, SCORE_THRESHOLD)
        loader = DataLoader(
            TensorDataset(X_tr, y_tr),
            batch_size=BATCH_SIZE, sampler=sampler,
            num_workers=NUM_WORKERS, pin_memory=(DEVICE.type == 'cuda'),
            persistent_workers=(NUM_WORKERS > 0),
        )
    else:
        loader = DataLoader(
            TensorDataset(X_tr, y_tr),
            batch_size=BATCH_SIZE, shuffle=True,
            num_workers=NUM_WORKERS, pin_memory=(DEVICE.type == 'cuda'),
            persistent_workers=(NUM_WORKERS > 0),
        )
    scaler = GradScaler('cuda') if USE_AMP else None

    history = {
        'train_loss': [], 'val_loss': [],
        'train_mae':  [], 'val_mae':  [],
        'epochs': [], 'best_epoch': 0, 'total_epochs': 0, 'early_stopped': False,
    }
    best_vl, best_st, pc, best_epoch = float('inf'), None, 0, 0

    for epoch in range(epochs):
        model.train()
        tl_sum = tmae_sum = n_tr = 0

        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)
            if USE_AMP:
                with autocast('cuda'):
                    pred = model(xb).squeeze(1)
                    loss = criterion(pred, yb)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                scaler.step(optimizer); scaler.update()
            else:
                pred = model(xb).squeeze(1)
                loss = criterion(pred, yb)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                optimizer.step()
            tl_sum   += loss.item() * len(yb)
            tmae_sum += torch.abs(pred.detach() - yb).sum().item()
            n_tr     += len(yb)

        train_loss = tl_sum   / max(n_tr, 1)
        train_mae  = tmae_sum / max(n_tr, 1)

        model.eval()
        with torch.no_grad():
            vp       = model(X_vl.to(DEVICE)).squeeze(1)
            val_loss = criterion(vp, y_vl.to(DEVICE)).item()
            val_mae  = float(torch.abs(vp - y_vl.to(DEVICE)).mean())

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_mae'].append(train_mae)
        history['val_mae'].append(val_mae)
        history['epochs'].append(epoch + 1)

        scheduler.step(val_loss)

        if val_loss < best_vl:
            best_vl = val_loss
            best_st = copy.deepcopy(model.state_dict())
            pc = 0; best_epoch = epoch + 1
        else:
            pc += 1
            if pc >= patience:
                history['early_stopped'] = True
                break

    if best_st:
        model.load_state_dict(best_st)
    history['best_epoch']   = best_epoch
    history['total_epochs'] = len(history['epochs'])
    return model, history


# ─── Inférence ────────────────────────────────────────────────────────────────
def predict_scores(model, X: np.ndarray) -> np.ndarray:
    """Retourne y_pred continu (N,) — scores clippés dans [0, 10]."""
    model.eval()
    X_t, _ = prepare_data(X, np.zeros(len(X)))
    preds = []
    with torch.no_grad():
        for i in range(0, len(X_t), 256):
            out = model(X_t[i:i+256].to(DEVICE)).squeeze(1).cpu().numpy()
            preds.append(out)
    return np.clip(np.concatenate(preds), 0.0, 10.0)


# ─── Graphiques ───────────────────────────────────────────────────────────────
def _save_scatter(y_true, y_pred, outdir, model_name, target, exp):
    yt, yp = np.array(y_true), np.array(y_pred)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(yt, yp, alpha=0.4, s=18, color='#2980B9')
    mn = min(yt.min(), yp.min()) - 0.2
    mx = max(yt.max(), yp.max()) + 0.2
    ax.plot([mn, mx], [mn, mx], 'r--', lw=1.5, label='Idéal')
    ax.set_xlabel('Score réel'); ax.set_ylabel('Score prédit')
    ax.set_title(f'{model_name} – {target.upper()} – Exp. {exp}')
    ax.legend(); plt.tight_layout()
    plt.savefig(outdir / 'scatter_pred_true.png', dpi=150); plt.close()


def _save_residuals(y_true, y_pred, outdir):
    res = np.array(y_pred) - np.array(y_true)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(res, bins=30, color='#27AE60', alpha=0.8, edgecolor='white')
    ax.axvline(0, color='red', ls='--', lw=1.5)
    ax.set_xlabel('Résidu (prédit − réel)'); ax.set_ylabel('Fréquence')
    ax.set_title('Distribution des résidus')
    plt.tight_layout()
    plt.savefig(outdir / 'residuals_distribution.png', dpi=150); plt.close()


def _save_learning_curves(history, outdir, model_name, target, exp):
    if not history['epochs']:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(f'{model_name} – {target.upper()} – Courbes (Exp. {exp})', fontsize=12)
    ep = history['epochs']; be = history['best_epoch']
    for ax, k_tr, k_vl, title in [
        (ax1, 'train_loss', 'val_loss', 'Huber Loss'),
        (ax2, 'train_mae',  'val_mae',  'MAE'),
    ]:
        ax.plot(ep, history[k_tr], 'b-', label='Train')
        ax.plot(ep, history[k_vl], 'r-', label='Val')
        ax.axvline(be, color='green', ls='--', lw=1.5, label=f'Best ({be})')
        ax.set_title(title); ax.set_xlabel('Époque')
        ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / 'learning_curves.png', dpi=150); plt.close()


def _save_fold_boxplot(fold_metrics, outdir, model_name, target):
    """Boxplot MAE / R² par fold LOSO."""
    maes = [f['mae'] for f in fold_metrics]
    r2s  = [f['r2']  for f in fold_metrics]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.boxplot(maes, vert=True, patch_artist=True)
    ax1.set_title(f'MAE par fold – {target.upper()}')
    ax1.set_ylabel('MAE'); ax1.grid(True, alpha=0.3)
    ax2.boxplot(r2s, vert=True, patch_artist=True)
    ax2.set_title(f'R² par fold – {target.upper()}')
    ax2.set_ylabel('R²'); ax2.grid(True, alpha=0.3)
    plt.suptitle(f'{model_name} – LOSO {target.upper()}', fontsize=12)
    plt.tight_layout()
    plt.savefig(outdir / 'fold_metrics_boxplot.png', dpi=150); plt.close()


# ─── Expérience standard ──────────────────────────────────────────────────────
def run_experiment(model_name: str, model_class, target: str, exp: str):
    """
    Entraîne + évalue + sauvegarde une expérience (target × exp).
    Retourne full_metrics dict, ou None si les données sont absentes.
    """
    print(f"\n{'='*65}")
    print(f"  {model_name} | {target.upper()} | Exp. {exp} | {DEVICE}")
    print(f"{'='*65}")

    try:
        X_train, y_train, X_val, y_val, X_test, y_test, _, _, _ = \
            _load_split(target, exp)
    except FileNotFoundError as e:
        print(f"  Données absentes — ignoré : {e}")
        return None

    print(f"  Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}")

    outdir = OUTPUT_BASE / model_name / target / exp
    moddir = MODEL_BASE  / model_name / target
    outdir.mkdir(parents=True, exist_ok=True)
    moddir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    model = model_class()
    model, history = train_model(model, X_train, y_train, X_val, y_val)
    tt = time.time() - t0

    y_pred = predict_scores(model, X_test)

    # Seuil Youden optimal (Youden 1950) — corrige biais fixed threshold 5.0
    youden = find_youden_threshold(y_test, y_pred)

    # Métriques professionnelles (niveaux 1–5)
    full_m    = compute_full_metrics(y_test, y_pred, youden)
    full_m['youden_threshold'] = youden
    boot      = bootstrap_ci(y_test, y_pred)
    perm      = permutation_test(y_test, y_pred)
    calib     = calibration_analysis(y_test, y_pred)
    ba        = bland_altman_analysis(y_test, y_pred)
    icc_val   = icc(y_test, y_pred)
    dca       = decision_curve_analysis(y_test, y_pred)
    stability = stability_analysis([full_m])
    report_md = generate_professional_report(
        target=target, model_name=model_name, exp=exp,
        full_metrics=full_m, bootstrap_results=boot,
        permutation_results=perm, stability_result=stability,
        calibration_result=calib, bland_altman_result=ba,
        icc_result=icc_val,
    )

    print(f"  MAE={full_m['mae']:.3f}  RMSE={full_m['rmse']:.3f}  "
          f"R²={full_m['r2']:.3f}  AUC={full_m['auc_roc']:.3f}  t={tt:.1f}s")

    # Graphiques — out_path = fichier, model_name = string
    _save_scatter(y_test, y_pred, outdir, model_name, target, exp)
    _save_residuals(y_test, y_pred, outdir)
    _save_learning_curves(history, outdir, model_name, target, exp)
    for fn, args in [
        (plot_reliability_diagram,  (y_test, y_pred, model_name, outdir / 'reliability_diagram.png')),
        (plot_bland_altman,          (y_test, y_pred, model_name, outdir / 'bland_altman.png')),
        (plot_bootstrap_ci_bars,     (boot,   model_name, outdir / 'bootstrap_ci_bars.png')),
        (plot_full_confusion_matrix, (y_test, y_pred, model_name, outdir / 'confusion_matrix.png', youden)),
        (plot_decision_curve,        (dca,    model_name, outdir / 'decision_curve.png')),
    ]:
        try:
            fn(*args)
        except Exception as e:
            print(f"  ⚠ {fn.__name__}: {e}")

    # Sauvegarde
    out_dict = {
        **full_m,
        'train_time_sec': tt, 'exp': exp, 'target': target, 'model': model_name,
        'bootstrap': boot, 'permutation': perm,
        'calibration': calib, 'bland_altman': ba, 'icc': icc_val,
        'stability': stability,
        'history': {k: history[k] for k in
                    ('best_epoch', 'total_epochs', 'early_stopped')},
    }
    with open(outdir / 'metrics.json', 'w') as f:
        json.dump(out_dict, f, indent=2, default=str)
    with open(outdir / 'report.md', 'w', encoding='utf-8') as f:
        f.write(report_md)
    torch.save(model.state_dict(), moddir / f"{model_name}_{target}_{exp}_best.pt")
    print(f"  → {outdir}")
    return full_m


# ─── Validation LOSO ─────────────────────────────────────────────────────────
def run_loso(model_name: str, model_class, target: str):
    """Leave-One-Subject-Out sur expérience A."""
    exp = 'A'
    print(f"\n{'='*65}")
    print(f"  LOSO – {model_name} | {target.upper()}")
    print(f"{'='*65}")

    d = REGRESSION_DATA / target
    X_path = d / f"X_train_{exp}.npy"
    if not X_path.exists():
        print(f"  {X_path.name} introuvable — LOSO ignorée")
        return None

    X = np.load(X_path)
    y = np.load(d / f"y_train_{exp}.npy").astype(np.float32)
    sids = None
    for name in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        p = d / name
        if p.exists(): sids = np.load(p); break
    if sids is None:
        print("  subject_ids introuvable — LOSO ignorée")
        return None

    unique_subj = np.unique(sids)
    print(f"  {len(X)} epochs | {len(unique_subj)} sujets")

    all_yt, all_yp, fold_metrics = [], [], []
    t0 = time.time()

    for subj in unique_subj:
        mask_te  = sids == subj
        X_tr_full, y_tr_full = X[~mask_te], y[~mask_te]
        X_te,      y_te      = X[mask_te],  y[mask_te]
        if len(X_te) == 0:
            continue

        n_val = max(1, int(len(X_tr_full) * 0.1))
        idx   = np.random.permutation(len(X_tr_full))
        X_v,  y_v  = X_tr_full[idx[:n_val]],  y_tr_full[idx[:n_val]]
        X_tr, y_tr = X_tr_full[idx[n_val:]], y_tr_full[idx[n_val:]]

        model = model_class()
        model, _ = train_model(model, X_tr, y_tr, X_v, y_v,
                               epochs=20, patience=5, class_weighted=True)

        y_pred_fold = predict_scores(model, X_te)
        youden_fold = find_youden_threshold(y_te, y_pred_fold)
        fold_m = compute_full_metrics(y_te, y_pred_fold, youden_fold)
        fold_m['youden_threshold'] = youden_fold
        fold_metrics.append({**fold_m, 'subject': int(subj), 'n_samples': len(y_te)})
        all_yt.extend(y_te.tolist())
        all_yp.extend(y_pred_fold.tolist())

        print(f"    Fold {int(subj):2d}: MAE={fold_m['mae']:.3f}  "
              f"R²={fold_m['r2']:.3f}  AUC={fold_m['auc_roc']:.3f}  "
              f"(n={len(y_te)})")

    elapsed = time.time() - t0
    if not all_yt:
        print("  LOSO échouée — aucun fold valide")
        return None

    yt_arr = np.array(all_yt)
    yp_arr = np.array(all_yp)

    global_youden = float(np.mean([m.get('youden_threshold', SCORE_THRESHOLD)
                                    for m in fold_metrics]))
    global_m  = compute_full_metrics(yt_arr, yp_arr, global_youden)
    global_m['youden_mean'] = global_youden
    global_m['youden_std']  = float(np.std([m.get('youden_threshold', SCORE_THRESHOLD)
                                             for m in fold_metrics]))
    boot      = bootstrap_ci(yt_arr, yp_arr)
    perm      = permutation_test(yt_arr, yp_arr)
    calib     = calibration_analysis(yt_arr, yp_arr)
    ba        = bland_altman_analysis(yt_arr, yp_arr)
    icc_val   = icc(yt_arr, yp_arr)
    dca       = decision_curve_analysis(yt_arr, yp_arr)
    stability = stability_analysis(fold_metrics)
    report_md = generate_professional_report(
        target=target, model_name=model_name, exp='LOSO',
        full_metrics=global_m, bootstrap_results=boot,
        permutation_results=perm, stability_result=stability,
        calibration_result=calib, bland_altman_result=ba, icc_result=icc_val,
    )

    print(f"\n  LOSO: MAE={global_m['mae']:.3f}  R²={global_m['r2']:.3f}  "
          f"AUC={global_m['auc_roc']:.3f}  ({elapsed:.1f}s)")

    outdir = OUTPUT_BASE / model_name / target / "LOSO"
    outdir.mkdir(parents=True, exist_ok=True)
    _save_scatter(all_yt, all_yp, outdir, model_name, target, 'LOSO')
    _save_residuals(all_yt, all_yp, outdir)
    _save_fold_boxplot(fold_metrics, outdir, model_name, target)
    # Convertit fold_metrics (liste) → format attendu par plot_per_subject_heatmap
    per_subj_data = {'per_subject': {str(fm['subject']): fm for fm in fold_metrics}}
    for fn, args in [
        (plot_reliability_diagram, (yt_arr, yp_arr, model_name, outdir / 'reliability_diagram.png')),
        (plot_bland_altman,         (yt_arr, yp_arr, model_name, outdir / 'bland_altman.png')),
        (plot_bootstrap_ci_bars,    (boot,   model_name, outdir / 'bootstrap_ci_bars.png')),
        (plot_per_subject_heatmap,  (per_subj_data, target,      outdir / 'per_subject_heatmap.png')),
        (plot_decision_curve,       (dca,    model_name,          outdir / 'decision_curve.png')),
    ]:
        try:
            fn(*args)
        except Exception as e:
            print(f"  ⚠ {fn.__name__}: {e}")

    loso_out = {
        **global_m,
        'train_time_sec': elapsed, 'target': target, 'model': model_name,
        'validation': 'LOSO', 'n_folds': len(fold_metrics),
        'bootstrap': boot, 'permutation': perm,
        'calibration': calib, 'bland_altman': ba, 'icc': icc_val,
        'stability': stability,
        'fold_metrics': fold_metrics,
    }
    with open(outdir / 'metrics.json', 'w') as f:
        json.dump(loso_out, f, indent=2, default=str)
    with open(outdir / 'fold_metrics.json', 'w') as f:
        json.dump(fold_metrics, f, indent=2, default=str)
    with open(outdir / 'report.md', 'w', encoding='utf-8') as f:
        f.write(report_md)

    return global_m


# ─── Point d'entrée principal ─────────────────────────────────────────────────
def dl_main_regression(model_name: str, model_class):
    """
    Lance 5 expériences + LOSO pour conc ET stress.
    Même structure que dl_main() de DL_utils.py, mais en régression.

    Usage dans chaque fichier architecture :
        from DL_utils_regression import N_OUT, dl_main_regression
        from architectures.CNN1D import CNN1D
        if __name__ == '__main__':
            dl_main_regression("CNN1D", lambda: CNN1D(n_classes=N_OUT))
    """
    print(f"\n{'='*65}")
    print(f"  NeuroCap DL Régression – {model_name}")
    print(f"  Device: {DEVICE} | AMP: {USE_AMP} | Seuil: {SCORE_THRESHOLD}")
    print(f"{'='*65}")

    summary: dict = {}

    for target in TARGETS:
        summary[target] = {}
        for exp in EXPERIMENTS:
            m = run_experiment(model_name, model_class, target, exp)
            if m:
                summary[target][exp] = {
                    'mae': m['mae'], 'r2': m['r2'], 'auc': m['auc_roc']}

        loso_m = run_loso(model_name, model_class, target)
        if loso_m:
            summary[target]['LOSO'] = {
                'mae': loso_m['mae'], 'r2': loso_m['r2'],
                'auc': loso_m['auc_roc']}

    print(f"\n{'='*65}")
    print(f"  Résumé {model_name}")
    print(f"{'='*65}")
    for target in TARGETS:
        print(f"\n  {target.upper()}:")
        for exp_key, vals in summary[target].items():
            print(f"    {exp_key:5s}: "
                  f"MAE={vals['mae']:.3f}  R²={vals['r2']:.3f}  AUC={vals['auc']:.3f}")

    print(f"\n  Résultats dans : {OUTPUT_BASE / model_name}")
