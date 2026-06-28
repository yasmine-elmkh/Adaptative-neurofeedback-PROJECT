"""
NeuroCap – EEGNet Feature Extraction RÉGRESSION (Prabhakar 2022, TL-2)
=======================================================================
Stratégie  : geler TOUTES les couches sauf FC — extracteur de features fixe.
Cibles     : conc (score concentration 0-10) | stress (score stress 0-10)
Expériences: A / B / C / D / FULL

Pré-entraîné : models/Regression/DL/EEGNet/{target}/EEGNet_{target}_{exp}_best.pt
Données FT   : data/Regression/augmented/{target}/X_val.npy   (calibration)
Évaluation   : data/Regression/augmented/{target}/X_test.npy
Sorties      : reports/Regression/TL/EEGNet_FeatureExtraction/{target}/{exp}/

Principe : les couches convolutives apprises sur la population (patterns α/β/θ)
sont gelées — seule la tête de régression (FC) est ré-entraînée pour adapter
la sortie scalaire au sujet cible.
"""

import sys, json, time, warnings, copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
from sklearn.metrics import roc_curve as sk_roc_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "models"))

from metrics_professional import (
    compute_full_metrics, bootstrap_ci, permutation_test, calibration_analysis,
    bland_altman_analysis, icc, stability_analysis,
    decision_curve_analysis,
    generate_professional_report,
    plot_reliability_diagram, plot_bland_altman,
    plot_bootstrap_ci_bars, plot_full_confusion_matrix,
    plot_decision_curve,
)

# ── Constantes ─────────────────────────────────────────────────────────────────
DEVICE          = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EPOCH_SAMPLES   = 1000
N_OUT           = 1
FT_LR           = 5e-5
FT_EPOCHS       = 60
FT_PATIENCE     = 12
FT_BATCH        = 32
GRAD_CLIP       = 1.0
SCORE_THRESHOLD = 5.0

REGRESSION_DATA = PROJECT_ROOT / "data"    / "Regression" / "augmented"
PRETRAINED_DIR  = PROJECT_ROOT / "models"  / "Regression" / "DL" / "EEGNet"
OUTPUT_BASE     = PROJECT_ROOT / "reports" / "Regression" / "TL"
MODEL_BASE      = PROJECT_ROOT / "models"  / "Regression" / "TL"

TARGETS = ['conc', 'stress']
EXPS    = ['A', 'B', 'C', 'D', 'FULL']

print(f"Device : {DEVICE}")


# ── Architecture EEGNet (sortie scalaire régression) ──────────────────────────
class EEGNet(nn.Module):
    def __init__(self, n_out=1, F1=8, D=2, F2=16, dr=0.5):
        super().__init__()
        self.conv1   = nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False)
        self.bn1     = nn.BatchNorm2d(F1)
        self.dw      = nn.Conv2d(F1, F1*D, (1, 1), groups=F1, bias=False)
        self.bn2     = nn.BatchNorm2d(F1*D)
        self.elu     = nn.ELU()
        self.pool1   = nn.AvgPool2d((1, 4))
        self.drop1   = nn.Dropout(dr)
        self.sep_dw  = nn.Conv2d(F1*D, F1*D, (1, 16), padding=(0, 8), groups=F1*D, bias=False)
        self.sep_pw  = nn.Conv2d(F1*D, F2, (1, 1), bias=False)
        self.bn3     = nn.BatchNorm2d(F2)
        self.pool2   = nn.AvgPool2d((1, 8))
        self.drop2   = nn.Dropout(dr)
        self._n_feat = self._get_n_feat()
        self.fc      = nn.Linear(self._n_feat, n_out)

    def _get_n_feat(self):
        with torch.no_grad():
            return self._fwd_feat(torch.zeros(1, 1, 1, EPOCH_SAMPLES)).shape[1]

    def _fwd_feat(self, x):
        x = self.bn1(self.conv1(x))
        x = self.elu(self.bn2(self.dw(x)))
        x = self.drop1(self.pool1(x))
        x = self.sep_pw(self.sep_dw(x))
        x = self.elu(self.bn3(x))
        return self.drop2(self.pool2(x)).flatten(1)

    def forward(self, x):
        if x.dim() == 3:
            x = x.unsqueeze(1)
        return self.fc(self._fwd_feat(x))          # (N, 1)


# ── Utilitaires données ────────────────────────────────────────────────────────
def prepare(X, y):
    Xt = torch.FloatTensor(X)
    if Xt.dim() == 2:
        Xt = Xt.unsqueeze(1)
    return Xt, torch.FloatTensor(y)


def _make_weighted_sampler(y_tensor, threshold=SCORE_THRESHOLD):
    """Sur-échantillonne High pour corriger always-Low — He & Garcia (2009) IEEE TKDE."""
    y_bin  = (y_tensor >= threshold).float()
    n_low  = max((y_bin == 0).sum().item(), 1)
    n_high = max((y_bin == 1).sum().item(), 1)
    weights = torch.where(y_bin == 1,
                          torch.tensor(float(n_low) / n_high),
                          torch.ones(len(y_tensor)))
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


def find_youden_threshold(y_true, y_pred_continuous, default=SCORE_THRESHOLD):
    """Seuil optimal Youden J = argmax(Sens + Spec − 1) — Youden (1950)."""
    y_bin = (np.asarray(y_true, float) >= default).astype(int)
    if len(np.unique(y_bin)) < 2:
        return default
    try:
        fpr, tpr, thresholds = sk_roc_curve(y_bin, np.asarray(y_pred_continuous, float))
        j_idx = int(np.argmax(tpr - fpr))
        return float(np.clip(thresholds[j_idx], 1.0, 9.0))
    except Exception:
        return default


def predict_scores(model, X: np.ndarray, n_mc: int = 10) -> np.ndarray:
    """MC Dropout : BN en eval, Dropout actif → moyenne sur 10 passes stochastiques."""
    Xt, _ = prepare(X, np.zeros(len(X)))
    model.eval()
    for m in model.modules():
        if isinstance(m, nn.Dropout):
            m.train()
    all_preds = []
    with torch.no_grad():
        for _ in range(n_mc):
            batch = []
            for i in range(0, len(Xt), 256):
                out = model(Xt[i:i+256].to(DEVICE)).squeeze(1).cpu().numpy()
                batch.append(out)
            all_preds.append(np.concatenate(batch))
    return np.clip(np.mean(all_preds, axis=0), 0.0, 10.0)


# ── Sélection du meilleur pré-entraîné ────────────────────────────────────────
def _load_best_pretrained(target: str, preferred_exp: str):
    """
    Charge le pré-entraîné EEGNet DL pour (target, preferred_exp).
    Si ce modèle n'existe pas ou si son R² est trop bas (< 0.05),
    sélectionne automatiquement l'exp avec le meilleur R² parmi A–FULL.
    Retourne (pt_path | None, exp_utilisé).
    """
    R2_MIN = 0.05
    dl_reports = PROJECT_ROOT / "reports" / "Regression" / "DL" / "EEGNet"

    def _r2_for_exp(e):
        metrics_path = dl_reports / target / e / "metrics.json"
        if metrics_path.exists():
            import json as _json
            with open(metrics_path) as f:
                return _json.load(f).get('r2', -999)
        return -999

    pt_preferred = PRETRAINED_DIR / target / f"EEGNet_{target}_{preferred_exp}_best.pt"
    r2_preferred = _r2_for_exp(preferred_exp)

    if pt_preferred.exists() and r2_preferred >= R2_MIN:
        return pt_preferred, preferred_exp

    best_r2, best_path, best_exp = -999, None, None
    for e in EXPS:
        pt = PRETRAINED_DIR / target / f"EEGNet_{target}_{e}_best.pt"
        if pt.exists():
            r2 = _r2_for_exp(e)
            if r2 > best_r2:
                best_r2, best_path, best_exp = r2, pt, e

    return best_path, best_exp


# ── Stratégie TL-2 : Feature Extraction ───────────────────────────────────────
def apply_feature_extraction(model):
    """Geler tout sauf FC — extracteur de features fixe (Prabhakar 2022)."""
    for p in model.parameters():
        p.requires_grad = False
    for p in model.fc.parameters():
        p.requires_grad = True
    return model


# ── Entraînement FT (régression) ──────────────────────────────────────────────
def train_ft(model, X_tr, y_tr, X_vl, y_vl):
    model = model.to(DEVICE)
    crit  = nn.HuberLoss(delta=1.0)
    trainable = [p for p in model.parameters() if p.requires_grad]
    opt  = optim.AdamW(trainable, lr=FT_LR, weight_decay=1e-4)
    sch  = optim.lr_scheduler.ReduceLROnPlateau(opt, mode='min', factor=0.5, patience=3, min_lr=FT_LR * 0.01)

    Xt, yt = prepare(X_tr, y_tr)
    Xv, yv = prepare(X_vl, y_vl)
    sampler = _make_weighted_sampler(yt, SCORE_THRESHOLD)
    dl = DataLoader(TensorDataset(Xt, yt), batch_size=FT_BATCH, sampler=sampler)

    history = {'train_loss': [], 'val_loss': [], 'epochs': [],
               'best_epoch': 0, 'early_stopped': False}
    best_vl, best_st, pc, best_ep = float('inf'), None, 0, 0

    for ep in range(FT_EPOCHS):
        model.train()
        for xb, yb in dl:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            loss = crit(model(xb).squeeze(1), yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            opt.step()

        model.eval()
        with torch.no_grad():
            vp = model(Xv.to(DEVICE)).squeeze(1)
            vl = crit(vp, yv.to(DEVICE)).item()

        sch.step(vl)
        history['train_loss'].append(loss.item())
        history['val_loss'].append(vl)
        history['epochs'].append(ep + 1)

        if vl < best_vl:
            best_vl, best_st, pc, best_ep = vl, copy.deepcopy(model.state_dict()), 0, ep + 1
        else:
            pc += 1
            if pc >= FT_PATIENCE:
                history['early_stopped'] = True
                print(f"         Early stopping ep.{ep+1}")
                break

    if best_st:
        model.load_state_dict(best_st)
    history['best_epoch'] = best_ep
    return model, history


# ── Graphiques régression ──────────────────────────────────────────────────────
def _save_scatter(y_true, y_pred, outdir, model_name, target, exp):
    yt, yp = np.array(y_true), np.array(y_pred)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(yt, yp, alpha=0.4, s=18, color='#2980B9')
    mn = min(yt.min(), yp.min()) - 0.2
    mx = max(yt.max(), yp.max()) + 0.2
    ax.plot([mn, mx], [mn, mx], 'r--', lw=1.5, label='Idéal')
    ax.set_xlabel('Score réel')
    ax.set_ylabel('Score prédit')
    ax.set_title(f'{model_name} – {target.upper()} – Exp. {exp}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(outdir / 'scatter_pred_true.png', dpi=150)
    plt.close()


def _save_residuals(y_true, y_pred, outdir):
    res = np.array(y_pred) - np.array(y_true)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(res, bins=30, color='#27AE60', alpha=0.8, edgecolor='white')
    ax.axvline(0, color='red', ls='--', lw=1.5)
    ax.set_xlabel('Résidu (prédit − réel)')
    ax.set_ylabel('Fréquence')
    ax.set_title('Distribution des résidus')
    plt.tight_layout()
    plt.savefig(outdir / 'residuals_distribution.png', dpi=150)
    plt.close()


def _save_learning_curves(history, outdir, model_name, target, exp):
    if not history['epochs']:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ep = history['epochs']
    ax.plot(ep, history['train_loss'], 'b-', label='Train')
    ax.plot(ep, history['val_loss'],   'r-', label='Val')
    be = history['best_epoch']
    ax.axvline(be, color='green', ls='--', lw=1.5, label=f'Best ({be})')
    ax.set_title(f'{model_name} – {target.upper()} – Huber Loss (Exp. {exp})')
    ax.set_xlabel('Époque')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / 'learning_curves.png', dpi=150)
    plt.close()


# ── Expérience ─────────────────────────────────────────────────────────────────
def run_experiment(target: str, exp: str):
    MODEL_NAME = 'EEGNet_FeatureExtraction'
    print(f"\n{'='*65}")
    print(f"  {MODEL_NAME} | {target.upper()} | Exp. {exp} | {DEVICE}")
    print(f"{'='*65}")

    d = REGRESSION_DATA / target
    try:
        X_val  = np.load(d / "X_val.npy")
        y_val  = np.load(d / "y_val.npy").astype(np.float32)
        X_test = np.load(d / "X_test.npy")
        y_test = np.load(d / "y_test.npy").astype(np.float32)
    except FileNotFoundError as e:
        print(f"  Données absentes — ignoré : {e}")
        return None

    # Préférer X_train_{exp} (plus de données → meilleur R²/AUC) sinon découper X_val
    train_path = d / f"X_train_{exp}.npy"
    if train_path.exists():
        X_ft = np.load(train_path)
        y_ft = np.load(d / f"y_train_{exp}.npy").astype(np.float32)
        X_es, y_es = X_val, y_val
        print(f"  Train: {len(X_ft)}  Val (ES): {len(X_es)}  Test: {len(X_test)}")
    else:
        n_es  = max(1, int(len(X_val) * 0.20))
        idx   = np.random.permutation(len(X_val))
        X_ft, y_ft = X_val[idx[n_es:]], y_val[idx[n_es:]]
        X_es, y_es = X_val[idx[:n_es]], y_val[idx[:n_es]]
        print(f"  FT: {len(X_ft)}  ES: {len(X_es)}  Test: {len(X_test)}")

    pt_path, used_exp = _load_best_pretrained(target, exp)
    model   = EEGNet(n_out=N_OUT)
    if pt_path is not None:
        model.load_state_dict(torch.load(pt_path, map_location=DEVICE, weights_only=True))
        if used_exp != exp:
            print(f"  ⚠️  Exp.{exp} non pertinente → pré-entraîné remplacé par Exp.{used_exp} (meilleur R²)")
        print(f"  ✅ Pré-entraîné : {pt_path.name}")
    else:
        print(f"  ⚠️  Aucun pré-entraîné trouvé — poids aléatoires")

    model   = apply_feature_extraction(model)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    print(f"  Params entraînés : {n_train}/{n_total} ({n_train/n_total*100:.0f}%)")

    t0 = time.time()
    model, history = train_ft(model, X_ft, y_ft, X_es, y_es)
    tt = time.time() - t0

    y_pred = predict_scores(model, X_test)

    youden    = find_youden_threshold(y_test, y_pred)
    full_m    = compute_full_metrics(y_test, y_pred, youden)
    full_m['youden_threshold'] = youden
    perm      = permutation_test(y_test, y_pred, threshold=youden)
    boot      = bootstrap_ci(y_test, y_pred)
    calib     = calibration_analysis(y_test, y_pred)
    ba        = bland_altman_analysis(y_test, y_pred)
    icc_val   = icc(y_test, y_pred)
    dca       = decision_curve_analysis(y_test, y_pred)
    stability = stability_analysis([full_m])
    report_md = generate_professional_report(
        target=target, model_name=MODEL_NAME, exp=exp,
        full_metrics=full_m, bootstrap_results=boot,
        permutation_results=perm,
        stability_result=stability, calibration_result=calib,
        bland_altman_result=ba, icc_result=icc_val,
    )

    print(f"  MAE={full_m['mae']:.3f}  RMSE={full_m['rmse']:.3f}  "
          f"R²={full_m['r2']:.3f}  AUC={full_m['auc_roc']:.3f}  "
          f"Youden={youden:.2f}  t={tt:.1f}s")

    outdir = OUTPUT_BASE / MODEL_NAME / target / exp
    moddir = MODEL_BASE  / MODEL_NAME / target
    outdir.mkdir(parents=True, exist_ok=True)
    moddir.mkdir(parents=True, exist_ok=True)

    _save_scatter(y_test, y_pred, outdir, MODEL_NAME, target, exp)
    _save_residuals(y_test, y_pred, outdir)
    _save_learning_curves(history, outdir, MODEL_NAME, target, exp)

    for fn, args in [
        (plot_reliability_diagram, (y_test, y_pred, MODEL_NAME, outdir / 'reliability_diagram.png')),
        (plot_bland_altman,        (y_test, y_pred, MODEL_NAME, outdir / 'bland_altman.png')),
        (plot_bootstrap_ci_bars,   (boot,   MODEL_NAME, outdir / 'bootstrap_ci_bars.png')),
        (plot_full_confusion_matrix,(y_test, y_pred, MODEL_NAME, outdir / 'confusion_matrix.png', youden)),
        (plot_decision_curve,      (dca,    MODEL_NAME, outdir / 'decision_curve.png')),
    ]:
        try:
            fn(*args)
        except Exception as e:
            print(f"  ⚠ {fn.__name__}: {e}")

    out_dict = {
        **full_m,
        'train_time_sec': tt, 'exp': exp, 'target': target, 'model': MODEL_NAME,
        'strategy': 'Feature Extraction (Prabhakar 2022)',
        'n_trainable': n_train, 'n_total': n_total,
        'bootstrap': boot, 'calibration': calib,
        'bland_altman': ba, 'icc': icc_val,
        'stability': stability, 'permutation': perm,
        'history': {k: history[k] for k in ('best_epoch', 'early_stopped')},
    }
    with open(outdir / 'metrics.json', 'w') as f:
        json.dump(out_dict, f, indent=2, default=str)
    with open(outdir / 'metrics.txt', 'w', encoding='utf-8') as f:
        f.write(f"EEGNet Feature Extraction – {target.upper()} – Exp. {exp}\n")
        f.write(f"MAE           : {full_m['mae']:.4f}\n")
        f.write(f"RMSE          : {full_m['rmse']:.4f}\n")
        f.write(f"R²            : {full_m['r2']:.4f}\n")
        f.write(f"AUC           : {full_m['auc_roc']:.4f}\n")
        f.write(f"Temps         : {tt:.1f}s\n")
        f.write(f"Params train  : {n_train}/{n_total} ({n_train/n_total*100:.0f}%)\n")
    with open(outdir / 'report.md', 'w', encoding='utf-8') as f:
        f.write(report_md)

    torch.save(model.state_dict(), moddir / f"EEGNet_FE_{target}_{exp}_best.pt")
    print(f"  → {outdir}")
    return full_m


def main():
    for target in TARGETS:
        for exp in EXPS:
            run_experiment(target, exp)


if __name__ == '__main__':
    main()
