"""
NeuroCap — EEGNet Transfer Learning (stress → conc)
====================================================
Stratégie :
  1. Charge les poids EEGNet pré-entraîné sur stress (Exp A — 40 sujets)
  2. Gèle toutes les couches conv (feature extractor partagé)
  3. Ré-initialise et fine-tune uniquement la couche FC finale sur conc
  4. LR = 1e-4 (×30 plus faible) — patience = 15

Référence :
  Kostas et al. (2022) — BENDR: Using Transformers and Contrastive
  Self-Supervised Learning to Learn from Massive Amounts of EEG Data.
  Frontiers in Human Neuroscience, 16. doi:10.3389/fnhum.2022.710900

  He & Wu (2019) — Transfer Learning for Brain-Computer Interfaces:
  A Euclidean Space Data Alignment Approach. IEEE TBME, 67(2).

Sortie :
  reports/Regression/DL/EEGNet_finetune/{conc}/{exp}/metrics.json
  models/Regression/DL/EEGNet_finetune/{conc}/EEGNet_finetune_conc_{exp}_best.pt
"""

import sys, copy, json, time, warnings
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

warnings.filterwarnings('ignore')

_HERE        = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[4]
sys.path.insert(0, str(PROJECT_ROOT / 'src' / 'models'))
sys.path.insert(0, str(PROJECT_ROOT / 'src' / 'models' / 'deep_learning'))

from DL_utils_regression import (
    DEVICE, EPOCH_SAMPLES, N_CLASSES, SCORE_THRESHOLD,
    prepare_data, predict_scores, train_model,
    _load_split, _save_scatter, _save_learning_curves,
    OUTPUT_BASE, MODEL_BASE,
    _make_weighted_sampler, find_youden_threshold,
)
from metrics_professional import (
    compute_full_metrics, bootstrap_ci, generate_professional_report,
)

# ── Paramètres fine-tuning ────────────────────────────────────────────────────
LR_FINETUNE  = 1e-4      # LR beaucoup plus faible que l'entraînement from scratch
PATIENCE_FT  = 15
MAX_EPOCHS_FT= 40
PRETRAIN_EXP = 'A'       # expérience stress utilisée pour le pré-entraînement


# ── Architecture EEGNet (identique à EEGNet.py) ───────────────────────────────
class EEGNet(nn.Module):
    def __init__(self, n_classes=N_CLASSES, F1=8, D=2, F2=16, dropout=0.5):
        super().__init__()
        self.conv1   = nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False)
        self.bn1     = nn.BatchNorm2d(F1)
        self.dw      = nn.Conv2d(F1, F1*D, (1, 1), groups=F1, bias=False)
        self.bn2     = nn.BatchNorm2d(F1*D)
        self.elu     = nn.ELU()
        self.pool1   = nn.AvgPool2d((1, 4))
        self.drop1   = nn.Dropout(dropout)
        self.sep_dw  = nn.Conv2d(F1*D, F1*D, (1, 16), padding=(0, 8),
                                 groups=F1*D, bias=False)
        self.sep_pw  = nn.Conv2d(F1*D, F2, (1, 1), bias=False)
        self.bn3     = nn.BatchNorm2d(F2)
        self.pool2   = nn.AvgPool2d((1, 8))
        self.drop2   = nn.Dropout(dropout)
        self._n_feat = self._get_features()
        self.fc      = nn.Linear(self._n_feat, n_classes)

    def _get_features(self):
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
        return self.fc(self._fwd_feat(x))


def finetune_model(model, X_train, y_train, X_val, y_val):
    """
    Fine-tune uniquement la couche fc avec LR faible.
    Toutes les couches conv sont gelées (gradients désactivés).
    """
    # Geler toutes les couches sauf fc
    for name, param in model.named_parameters():
        param.requires_grad = (name.startswith('fc'))

    model = model.to(DEVICE)
    criterion = nn.HuberLoss(delta=1.0)
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LR_FINETUNE, weight_decay=1e-4,
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, min_lr=LR_FINETUNE * 0.01)

    X_tr, y_tr = prepare_data(X_train, y_train)
    X_vl, y_vl = prepare_data(X_val, y_val)
    from torch.utils.data import DataLoader, TensorDataset
    # WeightedRandomSampler : sur-échantillonne High pour corriger always-Low
    sampler = _make_weighted_sampler(y_tr, SCORE_THRESHOLD)
    loader  = DataLoader(TensorDataset(X_tr, y_tr), batch_size=32, sampler=sampler)

    history = {'train_loss': [], 'val_loss': [], 'train_mae': [], 'val_mae': [],
               'epochs': [], 'best_epoch': 0, 'total_epochs': 0, 'early_stopped': False}
    best_vl, best_st, pc, best_epoch = float('inf'), None, 0, 0

    for epoch in range(MAX_EPOCHS_FT):
        model.train()
        tl, tmae, n = 0., 0., 0
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)
            pred = model(xb).squeeze(1)
            loss = criterion(pred, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            tl += loss.item() * len(yb); tmae += torch.abs(pred.detach() - yb).sum().item(); n += len(yb)

        model.eval()
        with torch.no_grad():
            vp     = model(X_vl.to(DEVICE)).squeeze(1)
            vl     = criterion(vp, y_vl.to(DEVICE)).item()
            vmae   = float(torch.abs(vp - y_vl.to(DEVICE)).mean())

        history['train_loss'].append(tl/max(n,1)); history['val_loss'].append(vl)
        history['train_mae'].append(tmae/max(n,1)); history['val_mae'].append(vmae)
        history['epochs'].append(epoch+1)
        scheduler.step(vl)

        if vl < best_vl:
            best_vl = vl; best_st = copy.deepcopy(model.state_dict())
            pc = 0; best_epoch = epoch + 1
        else:
            pc += 1
            if pc >= PATIENCE_FT:
                history['early_stopped'] = True; break

    if best_st:
        model.load_state_dict(best_st)
    history['best_epoch'] = best_epoch; history['total_epochs'] = len(history['epochs'])
    return model, history


def run_finetune(exp: str = 'A'):
    target     = 'conc'
    model_name = 'EEGNet_finetune'

    pretrain_path = (MODEL_BASE / 'EEGNet' / 'stress'
                     / f'EEGNet_stress_{PRETRAIN_EXP}_best.pt')
    if not pretrain_path.exists():
        print(f'  Poids pré-entraînés introuvables : {pretrain_path}')
        print('  → Lancez d\'abord : python EEGNet.py (target=stress)')
        return None

    print(f'\n{"="*65}')
    print(f'  EEGNet FINE-TUNING  stress→conc | Exp. {exp}')
    print(f'  Poids source : {pretrain_path.name}')
    print(f'{"="*65}')

    try:
        X_train, y_train, X_val, y_val, X_test, y_test, _, _, _ = \
            _load_split(target, exp)
    except FileNotFoundError as e:
        print(f'  Données absentes : {e}'); return None

    print(f'  Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}')

    # Charger les poids stress
    model = EEGNet()
    state = torch.load(pretrain_path, map_location=DEVICE, weights_only=True)
    model.load_state_dict(state)
    print(f'  Poids chargés depuis stress/{PRETRAIN_EXP}')
    print(f'  Couches gelées : conv1, dw, sep_dw, sep_pw, bn1-3, pool1-2')
    print(f'  Couche fine-tunée : fc ({model._n_feat} → 1)')

    outdir = OUTPUT_BASE / model_name / target / exp
    moddir = MODEL_BASE  / model_name / target
    outdir.mkdir(parents=True, exist_ok=True)
    moddir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    model, history = finetune_model(model, X_train, y_train, X_val, y_val)
    tt = time.time() - t0

    y_pred  = predict_scores(model, X_test)
    youden  = find_youden_threshold(y_test, y_pred)
    full_m  = compute_full_metrics(y_test, y_pred, youden)
    full_m['youden_threshold'] = youden
    boot    = bootstrap_ci(y_test, y_pred)

    print(f'  MAE={full_m["mae"]:.3f}  R²={full_m["r2"]:.3f}  '
          f'AUC={full_m["auc_roc"]:.3f}  t={tt:.1f}s  '
          f'best_epoch={history["best_epoch"]}')

    _save_scatter(y_test, y_pred, outdir, model_name, target, exp)
    _save_learning_curves(history, outdir, model_name, target, exp)

    out = {**full_m, 'train_time_sec': tt, 'exp': exp, 'target': target,
           'model': model_name, 'pretrain': f'stress_{PRETRAIN_EXP}',
           'bootstrap': boot,
           'history': {k: history[k] for k in
                       ('best_epoch', 'total_epochs', 'early_stopped')}}
    with open(outdir / 'metrics.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)
    torch.save(model.state_dict(), moddir / f'{model_name}_{target}_{exp}_best.pt')
    print(f'  → {outdir}')
    return full_m


if __name__ == '__main__':
    print('NeuroCap — EEGNet Transfer Learning (stress → conc)')
    print('='*65)
    results = {}
    for exp in ['A', 'B', 'C', 'D', 'FULL']:
        m = run_finetune(exp)
        if m:
            results[exp] = {'r2': m['r2'], 'auc': m['auc_roc'], 'mae': m['mae']}

    if results:
        print('\n' + '='*65)
        print('RÉSUMÉ EEGNet Fine-tuning (stress → conc)')
        print('='*65)
        print(f"{'Exp':<6} {'R²':>8} {'AUC':>8} {'MAE':>8}")
        for exp, m in results.items():
            print(f"{exp:<6} {m['r2']:>8.4f} {m['auc']:>8.4f} {m['mae']:>8.4f}")
