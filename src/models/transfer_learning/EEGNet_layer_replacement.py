"""
NeuroCap – EEGNet Layer Replacement (Olesen 2020, TL-3) ★ RECOMMANDÉ
Stratégie : remplacer conv1+bn1 (adaptation temporelle) + geler dw→spw + fine-tuner FC
Exécute automatiquement les 5 expériences (A, B, C, D, FULL).

Référence : Olesen, Jennum, Mignot & Sorensen (2020) — IEEE EMBC
  "Deep transfer learning for improving single-EEG arousal detection"
  F1=0.682 ≈ multivarié (F1=0.694) — perte minimale malgré contrainte monocanal

Principe :
  1. Charger le modèle EEGNet pré-entraîné (meilleur DL classique)
  2. GELER toutes les couches (patterns spectraux génériques)
  3. REMPLACER conv1 + bn1 (couches d'adaptation temporelle)
  4. DÉGELER la couche FC (classification)
  5. Fine-tuner sur les données du sujet cible (~180 époques calibration S1)

Avantage : conserve les patterns β/α/θ appris sur 55 sujets tout en
adaptant le filtrage temporel au profil neurophysiologique individuel.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (accuracy_score, f1_score, confusion_matrix,
                             roc_auc_score, roc_curve, auc)
import json, time, warnings, copy
from pathlib import Path

warnings.filterwarnings('ignore')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device : {DEVICE}")

# ============================================================================
# CONSTANTES
# ============================================================================
EPOCH_SAMPLES = 1000; N_CLASSES = 2
FT_LR = 1e-4; FT_EPOCHS = 30; FT_PATIENCE = 8
FT_BATCH = 16; GRAD_CLIP = 1.0; HOLDOUT = 0.20

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PRETRAINED_DIR = PROJECT_ROOT / "models/deep_learning/DL_models/EEGNet"
MERGED_DIR = PROJECT_ROOT / "data/Merge_datasets/datasets_merged"
OUTPUT_BASE = PROJECT_ROOT / "reports/transfer_learning/outputs_tl"
MODEL_BASE = PROJECT_ROOT / "models/transfer_learning/TL_models"
EXPS = ['A', 'B', 'C', 'D', 'FULL']

# ============================================================================
# EEGNet (identique au DL classique)
# ============================================================================
class EEGNet(nn.Module):
    def __init__(self, n_classes=2, F1=8, D=2, F2=16, dr=0.5):
        super().__init__()
        self.conv1 = nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False)
        self.bn1 = nn.BatchNorm2d(F1)
        self.dw = nn.Conv2d(F1, F1*D, (1, 1), groups=F1, bias=False)
        self.bn2 = nn.BatchNorm2d(F1*D)
        self.elu = nn.ELU()
        self.pool1 = nn.AvgPool2d((1, 4)); self.drop1 = nn.Dropout(dr)
        self.sep_dw = nn.Conv2d(F1*D, F1*D, (1, 16), padding=(0, 8), groups=F1*D, bias=False)
        self.sep_pw = nn.Conv2d(F1*D, F2, (1, 1), bias=False)
        self.bn3 = nn.BatchNorm2d(F2)
        self.pool2 = nn.AvgPool2d((1, 8)); self.drop2 = nn.Dropout(dr)
        self._n_features = self._get_final_features()
        self.fc = nn.Linear(self._n_features, n_classes)
    def _get_final_features(self):
        with torch.no_grad():
            return self._forward_features(torch.zeros(1, 1, 1, EPOCH_SAMPLES)).shape[1]
    def _forward_features(self, x):
        x = self.bn1(self.conv1(x))
        x = self.elu(self.bn2(self.dw(x)))
        x = self.drop1(self.pool1(x))
        x = self.sep_pw(self.sep_dw(x))
        x = self.elu(self.bn3(x))
        return self.drop2(self.pool2(x)).flatten(1)
    def forward(self, x):
        if x.dim() == 3: x = x.unsqueeze(1)
        return self.fc(self._forward_features(x))

# ============================================================================
# FONCTIONS
# ============================================================================
def prepare(X, y):
    Xt = torch.FloatTensor(X)
    if Xt.dim() == 2: Xt = Xt.unsqueeze(1)
    return Xt, torch.LongTensor(y)

def apply_layer_replacement(model):
    """Geler tout, remplacer conv1+bn1, dégeler FC."""
    for p in model.parameters(): p.requires_grad = False
    # Remplacer les premières couches (adaptation temporelle au sujet)
    model.conv1 = nn.Conv2d(1, 8, (1, 64), padding=(0, 32), bias=False)
    model.bn1 = nn.BatchNorm2d(8)
    # Dégeler FC (classification)
    for p in model.fc.parameters(): p.requires_grad = True
    return model

def train_ft(model, X_tr, y_tr, X_vl, y_vl):
    model = model.to(DEVICE)
    trainable = [p for p in model.parameters() if p.requires_grad]
    cc = np.bincount(y_tr.astype(int))
    cw = torch.FloatTensor(len(y_tr)/(2*cc)).to(DEVICE) if len(cc)>=2 and cc.min()>0 else None
    crit = nn.CrossEntropyLoss(weight=cw)
    opt = optim.AdamW(trainable, lr=FT_LR, weight_decay=1e-4)
    sch = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=FT_EPOCHS, eta_min=FT_LR*0.01)
    Xt, yt = prepare(X_tr, y_tr); Xv, yv = prepare(X_vl, y_vl)
    dl = DataLoader(TensorDataset(Xt, yt), batch_size=FT_BATCH, shuffle=True)
    best_vl = float('inf'); best_st = None; pc = 0
    for ep in range(FT_EPOCHS):
        model.train()
        for xb, yb in dl:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad(); loss = crit(model(xb), yb); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP); opt.step()
        sch.step()
        model.eval()
        with torch.no_grad():
            vl = crit(model(Xv.to(DEVICE)), yv.to(DEVICE)).item()
        if vl < best_vl: best_vl = vl; best_st = copy.deepcopy(model.state_dict()); pc = 0
        else:
            pc += 1
            if pc >= FT_PATIENCE:
                print(f"         Early stopping ep.{ep+1}"); break
    if best_st: model.load_state_dict(best_st)
    return model

def evaluate(model, X, y):
    model.eval()
    Xt, _ = prepare(X, y)
    with torch.no_grad():
        out = model(Xt.to(DEVICE))
        probs = torch.softmax(out, 1).cpu().numpy()
        preds = out.argmax(1).cpu().numpy()
    m = {'accuracy': accuracy_score(y, preds),
         'f1': f1_score(y, preds, zero_division=0),
         'f1_macro': f1_score(y, preds, average='macro', zero_division=0),
         'specificity': 0.0, 'auc': 0.5,
         'y_true': y.tolist(), 'y_pred': preds.tolist(), 'y_proba': probs[:,1].tolist(),
         'n_samples': len(y)}
    cm = confusion_matrix(y, preds)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        m['specificity'] = tn/(tn+fp) if (tn+fp)>0 else 0
    if len(np.unique(y)) > 1:
        try: m['auc'] = roc_auc_score(y, probs[:,1])
        except: pass
    m['pct_uncertain'] = float(np.sum(np.max(probs,1)<0.60)/len(y)*100)
    return m

def plot_confusion(yt, yp, outdir, exp):
    cm = confusion_matrix(yt, yp)
    if cm.shape == (1,1): cm = np.array([[cm[0,0],0],[0,0]])
    cmn = cm.astype(float)/(cm.sum(axis=1,keepdims=True)+1e-12)
    plt.figure(figsize=(5,4))
    sns.heatmap(cmn, annot=True, fmt='.1%', cmap='Blues',
                xticklabels=['Concentration','Stress'], yticklabels=['Concentration','Stress'])
    plt.title(f'EEGNet Layer Replacement – Exp. {exp}')
    plt.tight_layout(); plt.savefig(outdir/'confusion_matrix.png', dpi=150); plt.close()

def plot_roc(yt, yp, outdir, exp):
    if len(np.unique(yt)) < 2: return
    fpr, tpr, _ = roc_curve(yt, yp); ra = auc(fpr, tpr)
    plt.figure(figsize=(5,4))
    plt.plot(fpr, tpr, lw=2, label=f'AUC={ra:.3f}'); plt.plot([0,1],[0,1],'k--')
    plt.xlabel('FPR'); plt.ylabel('TPR')
    plt.title(f'EEGNet Layer Replacement – ROC (Exp.{exp})')
    plt.legend(); plt.tight_layout(); plt.savefig(outdir/'roc_curve.png', dpi=150); plt.close()

def plot_proba(yt, yp, outdir, exp):
    plt.figure(figsize=(6,4))
    yt, yp = np.array(yt), np.array(yp)
    plt.hist(yp[yt==0], bins=25, alpha=0.6, color='#2980B9', label='Concentration', density=True)
    plt.hist(yp[yt==1], bins=25, alpha=0.6, color='#E74C3C', label='Stress', density=True)
    plt.axvspan(0.40, 0.60, alpha=0.12, color='gray', label='Zone incertaine')
    plt.axvline(0.60, color='red', ls=':', lw=1.5, label='Seuil CdC 0.60')
    plt.xlabel('P(Stress)'); plt.ylabel('Densité')
    plt.title(f'EEGNet Layer Replacement – Probas (Exp.{exp})')
    plt.legend(); plt.tight_layout(); plt.savefig(outdir/'proba_distribution.png', dpi=150); plt.close()

# ============================================================================
# EXPÉRIENCE
# ============================================================================
def run_experiment(exp):
    print("="*70)
    print(f"NeuroCap – EEGNet Layer Replacement (Olesen 2020) – Exp. {exp}")
    print("="*70)

    # Charger données fusionnées
    X = np.load(MERGED_DIR / 'X_merged.npy')
    y = np.load(MERGED_DIR / 'y_merged.npy')
    sids = np.load(MERGED_DIR / 'subject_ids_merged.npy')

    # Charger modèle pré-entraîné de cette expérience
    pt_path = PRETRAINED_DIR / f"EEGNet_{exp}_best.pt"
    model = EEGNet()
    if pt_path.exists():
        model.load_state_dict(torch.load(pt_path, map_location=DEVICE, weights_only=True))
        print(f"  ✅ Pré-entraîné chargé : {pt_path.name}")
    else:
        print(f"  ⚠️ {pt_path.name} non trouvé – utilisation aléatoire")

    # Appliquer Layer Replacement
    model = apply_layer_replacement(model)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    print(f"  Params entraînés : {n_train}/{n_total} ({n_train/n_total*100:.0f}%)")

    # Sélectionner des sujets avec 2 classes pour le fine-tuning
    unique_sids = np.unique(sids)
    ft_sids = [s for s in unique_sids if len(np.unique(y[sids==s])) >= 2][:5]
    if not ft_sids:
        ft_sids = unique_sids[:5]

    # Fine-tuning par sujet puis évaluation sur les autres
    all_yt, all_yp, all_yprob = [], [], []
    t0 = time.time()

    for sid in ft_sids:
        mask = sids == sid
        X_subj, y_subj = X[mask], y[mask]
        if len(X_subj) > 180:
            idx = np.random.choice(len(X_subj), 180, replace=False)
            X_subj, y_subj = X_subj[idx], y_subj[idx]

        n_eval = max(1, int(len(X_subj) * HOLDOUT))
        idx = np.random.permutation(len(X_subj))
        X_tr, y_tr = X_subj[idx[n_eval:]], y_subj[idx[n_eval:]]
        X_ev, y_ev = X_subj[idx[:n_eval]], y_subj[idx[:n_eval]]

        # Copie fraîche du modèle pré-entraîné + layer replacement
        m = EEGNet()
        if pt_path.exists():
            m.load_state_dict(torch.load(pt_path, map_location=DEVICE, weights_only=True))
        m = apply_layer_replacement(m)
        m = train_ft(m, X_tr, y_tr, X_ev, y_ev)
        ev = evaluate(m, X_ev, y_ev)
        all_yt.extend(ev['y_true']); all_yp.extend(ev['y_pred']); all_yprob.extend(ev['y_proba'])

    train_time = time.time() - t0
    # Métriques globales
    metrics = {
        'accuracy': accuracy_score(all_yt, all_yp),
        'f1': f1_score(all_yt, all_yp, zero_division=0),
        'f1_macro': f1_score(all_yt, all_yp, average='macro', zero_division=0),
        'auc': 0.5, 'specificity': 0.0,
        'pct_uncertain': 0.0,
        'y_true': all_yt, 'y_pred': all_yp, 'y_proba': all_yprob,
        'n_samples': len(all_yt),
        'train_time_sec': train_time,
        'model': 'EEGNet_LayerReplacement', 'exp_name': exp,
        'n_trainable': n_train, 'n_total': n_total,
        'strategy': 'Layer Replacement (Olesen 2020)'
    }
    cm = confusion_matrix(all_yt, all_yp)
    if cm.size == 4:
        tn,fp,fn,tp = cm.ravel()
        metrics['specificity'] = tn/(tn+fp) if (tn+fp)>0 else 0
    if len(np.unique(all_yt)) > 1:
        try: metrics['auc'] = roc_auc_score(all_yt, all_yprob)
        except: pass
    metrics['pct_uncertain'] = float(np.sum(np.max(
        np.column_stack([1-np.array(all_yprob), all_yprob]), 1) < 0.60) / len(all_yt) * 100)

    print(f"\n  ✅ Résultats EEGNet Layer Replacement – Exp. {exp} :")
    print(f"     Accuracy    = {metrics['accuracy']:.4f}")
    print(f"     F1-macro    = {metrics['f1_macro']:.4f}")
    print(f"     AUC         = {metrics['auc']:.4f}")
    print(f"     Spécificité = {metrics['specificity']:.4f}")
    print(f"     Incertitude = {metrics['pct_uncertain']:.1f}%")
    print(f"     Temps       = {train_time:.1f}s")

    # Sauvegarde
    out_dir = OUTPUT_BASE / "EEGNet_LayerReplacement" / f"exp_{exp}"
    model_dir = MODEL_BASE / "EEGNet_LayerReplacement"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    plot_confusion(metrics['y_true'], metrics['y_pred'], out_dir, exp)
    plot_roc(metrics['y_true'], metrics['y_proba'], out_dir, exp)
    plot_proba(metrics['y_true'], metrics['y_proba'], out_dir, exp)

    with open(out_dir/'metrics.json', 'w') as f: json.dump(metrics, f, indent=2, default=str)
    with open(out_dir/'metrics.txt', 'w') as f:
        f.write(f"EEGNet Layer Replacement – Exp. {exp}\n")
        f.write(f"Accuracy      : {metrics['accuracy']:.4f}\n")
        f.write(f"F1-macro      : {metrics['f1_macro']:.4f}\n")
        f.write(f"AUC           : {metrics['auc']:.4f}\n")
        f.write(f"Spécificité   : {metrics['specificity']:.4f}\n")
        f.write(f"Incertitude   : {metrics['pct_uncertain']:.1f}%\n")
        f.write(f"Temps         : {train_time:.1f}s\n")
        f.write(f"Params entraînés : {n_train}/{n_total} ({n_train/n_total*100:.0f}%)\n")
    torch.save(m.state_dict(), model_dir/f"EEGNet_LR_{exp}_best.pt")
    print(f"  Modèle sauvegardé : EEGNet_LR_{exp}_best.pt\n✅ Terminé.\n")

def main():
    for exp in EXPS:
        run_experiment(exp)

if __name__ == '__main__': main()