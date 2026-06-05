"""
NeuroCap – DANN_utils.py
========================
Pipeline d'entraînement DANN, miroir de DL_utils.py.

Réutilise de DL_utils :
  - Toutes les constantes (LR, WD, BATCH_SIZE, ...)
  - CNNPreEncoder, BahdanauAttention
  - prepare_data, check_data_leakage
  - detect_overfitting, format_overfitting_report
  - evaluate_model, save_plots, plot_learning_curves, format_rates_output
  - plot_rates_distribution, plot_test_accuracy

Ajoute :
  - DomainEEGDataset  — dataset avec labels de domaine
  - get_lambda_grl    — scheduler progressif du paramètre GRL
  - train_dann_model  — boucle DANN (2 pertes + GRL)
  - evaluate_dann_model — évaluation DANN (lambda_grl=0)
  - run_dann_experiment / run_dann_loso_validation / dann_main

Note sur les domaines :
  Dans NeuroCap, les données Concentration viennent d'OpenBCI (domaine 0)
  et les données Stress d'EMOTIV (domaine 1). Le label de domaine est donc
  identique au label cognitif — c'est précisément le biais inter-dataset que
  DANN cherche à réduire en apprenant des représentations domain-invariantes.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.amp import autocast, GradScaler
from torch.autograd import Function
import copy, time, json, os
from pathlib import Path

from sklearn.metrics import accuracy_score

from DL_utils import (
    DEVICE, USE_AMP,
    N_CLASSES, LR, WD, MAX_EPOCHS, PATIENCE, BATCH_SIZE, GRAD_CLIP, NUM_WORKERS,
    AUGMENTED_DIR, OUTPUT_BASE, MODEL_BASE,
    OVERFIT_PERFECT_SCORE,
    prepare_data,
    detect_overfitting, format_overfitting_report,
    check_data_leakage,
    evaluate_model,
    save_plots, plot_learning_curves, plot_rates_distribution,
    format_rates_output, plot_test_accuracy,
)

DANN_OUTPUT_BASE = OUTPUT_BASE.parent / "DANN_outputs"
DANN_MODEL_BASE  = MODEL_BASE.parent  / "DANN_models"


# ============================================================================
# COMPOSANTS DANN PARTAGÉS  (importés par chaque fichier architectures_DANN/)
# ============================================================================
class GradientReversalLayer(Function):
    """
    Forward : identité.
    Backward : multiplie le gradient par -lambda_grl.
    Permet à l'extracteur de features de CONFONDRE le classifieur de domaine.
    """
    @staticmethod
    def forward(ctx, x, lambda_grl):
        ctx.lambda_grl = lambda_grl
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.lambda_grl, None


class DomainClassifier(nn.Module):
    """
    Classifieur de domaine : OpenBCI (0) vs EMOTIV (1).
    Le GRL est appliqué en amont.
    """
    def __init__(self, in_dim, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 2),
        )

    def forward(self, x, lambda_grl=1.0):
        x = GradientReversalLayer.apply(x, lambda_grl)
        return self.net(x)


# ============================================================================
# DATASET AVEC LABELS DE DOMAINE
# ============================================================================
class DomainEEGDataset(Dataset):
    """
    Dataset EEG avec labels de domaine.
      X      : (N, 1000) ou (N, 1, 1000)
      y      : (N,) labels cognitifs  [0=Concentration, 1=Stress]
      domain : (N,) labels de domaine [0=OpenBCI,      1=EMOTIV ]
    """
    def __init__(self, X, y, domain):
        X_t = torch.FloatTensor(X)
        if X_t.dim() == 2:
            X_t = X_t.unsqueeze(1)   # (N, 1, 1000)
        self.X = X_t
        self.y = torch.LongTensor(y)
        self.domain = torch.LongTensor(domain)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx], self.domain[idx]


# ============================================================================
# SCHEDULER LAMBDA GRL
# ============================================================================
def get_lambda_grl(epoch, total_epochs, lambda_max=1.0):
    """
    Augmentation progressive de lambda via une sigmoïde inversée.
    Epoch 0   → lambda ≈ 0   (pas d'adversaire au début)
    Epoch T-1 → lambda ≈ lambda_max  (plein adversaire)
    """
    p = epoch / max(total_epochs - 1, 1)
    return lambda_max * (2.0 / (1.0 + np.exp(-10.0 * p)) - 1.0)


# ============================================================================
# WRAPPER POUR ÉVALUATION  (rend un modèle DANN compatible avec evaluate_model)
# ============================================================================
class _DANNLabelOnly(nn.Module):
    """Wrap un modèle DANN pour qu'il retourne uniquement les label_logits."""
    def __init__(self, dann_model):
        super().__init__()
        self.m = dann_model

    def forward(self, x):
        label_out, _ = self.m(x, lambda_grl=0.0)
        return label_out


# ============================================================================
# ENTRAÎNEMENT DANN
# ============================================================================
def train_dann_model(model, X_train, y_train, X_val, y_val,
                     epochs=MAX_EPOCHS, patience=PATIENCE, lambda_max=1.0):
    """
    Entraîne un modèle DANN avec GRL progressif.

    Perte totale = L_label + L_domain
      - L_label  : CrossEntropy sur les labels cognitifs
      - L_domain : CrossEntropy sur les labels de domaine (OpenBCI / EMOTIV)
      Le GRL dans le modèle inverse le gradient de L_domain → l'extracteur
      apprend des features domain-invariantes.

    Domain labels = y (OpenBCI=Concentration=0, EMOTIV=Stress=1).

    Retourne : (model, history)
    """
    model = model.to(DEVICE)

    # Class weights sur le label cognitif
    cc = np.bincount(y_train.astype(int))
    cw = (torch.FloatTensor(len(y_train) / (2 * cc)).to(DEVICE)
          if len(cc) >= 2 and min(cc) > 0 else None)

    criterion_label  = nn.CrossEntropyLoss(weight=cw)
    criterion_domain = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=epochs, eta_min=LR * 0.01)

    # Dans NeuroCap : domain == label cognitif
    domain_train = y_train.copy()

    train_dataset = DomainEEGDataset(X_train, y_train, domain_train)
    loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=NUM_WORKERS, pin_memory=(DEVICE.type == 'cuda'),
        persistent_workers=(NUM_WORKERS > 0),
    )

    X_vl, y_vl = prepare_data(X_val, y_val)
    scaler = GradScaler('cuda') if USE_AMP else None

    history = {
        'train_loss': [], 'val_loss': [],
        'train_acc':  [], 'val_acc':  [],
        'label_loss': [], 'domain_loss': [], 'lambda_grl': [],
        'epochs': [],
        'best_epoch': 0, 'total_epochs': 0, 'early_stopped': False,
    }

    best_vl   = float('inf')
    best_st   = None
    pc        = 0
    best_epoch = 0

    for epoch in range(epochs):
        model.train()
        lam = get_lambda_grl(epoch, epochs, lambda_max)

        total_loss_sum  = 0.0
        label_loss_sum  = 0.0
        domain_loss_sum = 0.0
        train_correct   = 0
        train_total     = 0

        for xb, yb, db in loader:
            xb = xb.to(DEVICE)
            yb = yb.to(DEVICE)
            db = db.to(DEVICE)

            optimizer.zero_grad(set_to_none=True)

            if USE_AMP:
                with autocast('cuda'):
                    lbl_out, dom_out = model(xb, lam)
                    loss_lbl = criterion_label(lbl_out, yb)
                    loss_dom = criterion_domain(dom_out, db)
                    loss = loss_lbl + loss_dom
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                scaler.step(optimizer)
                scaler.update()
            else:
                lbl_out, dom_out = model(xb, lam)
                loss_lbl = criterion_label(lbl_out, yb)
                loss_dom = criterion_domain(dom_out, db)
                loss = loss_lbl + loss_dom
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                optimizer.step()

            n = len(yb)
            total_loss_sum  += loss.item()     * n
            label_loss_sum  += loss_lbl.item() * n
            domain_loss_sum += loss_dom.item() * n

            with torch.no_grad():
                train_correct += (lbl_out.argmax(1) == yb).sum().item()
                train_total   += n

        scheduler.step()

        # train_loss = label_loss seul (comparable à DL_utils, sans domain loss)
        train_loss = label_loss_sum  / max(train_total, 1)
        train_acc  = train_correct   / max(train_total, 1)

        # ── Validation (GRL désactivé : perte label seule, identique à DL_utils) ──
        model.eval()
        with torch.no_grad():
            val_out, _ = model(X_vl.to(DEVICE), lambda_grl=0.0)
            val_loss   = criterion_label(val_out, y_vl.to(DEVICE)).item()
            val_preds  = val_out.argmax(1).cpu().numpy()
            val_acc    = accuracy_score(y_val, val_preds)

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['label_loss'].append(label_loss_sum  / max(train_total, 1))
        history['domain_loss'].append(domain_loss_sum / max(train_total, 1))
        history['lambda_grl'].append(float(lam))
        history['epochs'].append(epoch + 1)

        if val_loss < best_vl:
            best_vl  = val_loss
            best_st  = copy.deepcopy(model.state_dict())
            pc       = 0
            best_epoch = epoch + 1
        else:
            pc += 1
            if pc >= patience:
                print(f"         Early stopping à l'époque {epoch + 1}")
                history['early_stopped'] = True
                break

    if best_st:
        model.load_state_dict(best_st)

    history['best_epoch']   = best_epoch
    history['total_epochs'] = len(history['epochs'])
    return model, history


# ============================================================================
# ÉVALUATION DANN
# ============================================================================
def evaluate_dann_model(model, X, y):
    """
    Évalue un modèle DANN en mode inférence (lambda_grl=0).
    Réutilise evaluate_model de DL_utils via _DANNLabelOnly.
    """
    return evaluate_model(_DANNLabelOnly(model), X, y)


# ============================================================================
# GRAPHIQUE DANN-SPÉCIFIQUE : évolution lambda + pertes séparées
# ============================================================================
def plot_dann_training(history, outdir, model_name, exp_name):
    """Courbes label_loss / domain_loss / lambda_grl au fil des époques."""
    if not history['epochs']:
        return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'{model_name} – Entraînement DANN (Exp. {exp_name})',
                 fontsize=13, fontweight='bold')

    ep = history['epochs']
    ax1.plot(ep, history['label_loss'],  'b-o', ms=3, lw=1.5, label='Label Loss')
    ax1.plot(ep, history['domain_loss'], 'r-s', ms=3, lw=1.5, label='Domain Loss')
    ax1.set_xlabel('Époque')
    ax1.set_ylabel('Loss')
    ax1.set_title('Pertes séparées (Label + Domain)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(ep, history['lambda_grl'], 'g-^', ms=3, lw=1.5, label='λ GRL')
    ax2.set_xlabel('Époque')
    ax2.set_ylabel('λ')
    ax2.set_title('Progression du paramètre GRL')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(outdir / 'dann_training_curves.png', dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# EXPÉRIENCE DANN
# ============================================================================
def run_dann_experiment(model_name, model_class, exp, lambda_max=1.0):
    """
    Lance une expérience d'augmentation DANN (A / B / C / D / FULL).
    Reproduit run_experiment de DL_utils avec la boucle DANN.
    """
    print("=" * 70)
    print(f"NeuroCap DANN – {model_name} – Expérience {exp}")
    print(f"Device : {DEVICE} | AMP : {USE_AMP} | λ_max : {lambda_max}")
    print("=" * 70)

    X_train = np.load(AUGMENTED_DIR / f"X_train_{exp}.npy")
    y_train = np.load(AUGMENTED_DIR / f"y_train_{exp}.npy")
    X_val   = np.load(AUGMENTED_DIR / "X_val.npy")
    y_val   = np.load(AUGMENTED_DIR / "y_val.npy")
    X_test  = np.load(AUGMENTED_DIR / "X_test.npy")
    y_test  = np.load(AUGMENTED_DIR / "y_test.npy")

    print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
    print(f"Train – Concentration: {np.sum(y_train==0)}, Stress: {np.sum(y_train==1)}")

    # ── Vérification fuite de données ────────────────────────────────────────
    sid_train = sid_val = sid_test = None
    for sn in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists():
            sid_train = np.load(sp); break
    for sn in ["subject_ids_val.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists(): sid_val = np.load(sp)
    for sn in ["subject_ids_test.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists(): sid_test = np.load(sp)

    leak_report = check_data_leakage(sid_train, sid_val, sid_test)
    print(f"\n  Vérification fuite de données : {leak_report['message']}")

    # ── Répertoires de sortie ────────────────────────────────────────────────
    od = DANN_OUTPUT_BASE / model_name / f"exp_{exp}"
    md = DANN_MODEL_BASE  / model_name
    try:
        od.mkdir(parents=True, exist_ok=True)
        md.mkdir(parents=True, exist_ok=True)
    except Exception:
        os.makedirs(str(od), exist_ok=True)
        os.makedirs(str(md), exist_ok=True)

    # ── Entraînement DANN ─────────────────────────────────────────────────────
    print(f"\n▶ Entraînement DANN {model_name} – Exp. {exp}...")
    t0 = time.time()
    model = model_class()
    model, history = train_dann_model(
        model, X_train, y_train, X_val, y_val, lambda_max=lambda_max)
    tt = time.time() - t0

    # ── Détection overfitting ────────────────────────────────────────────────
    overfit_report = detect_overfitting(history)

    # ── Évaluation ───────────────────────────────────────────────────────────
    train_metrics = evaluate_dann_model(model, X_train, y_train)
    metrics       = evaluate_dann_model(model, X_test,  y_test)
    metrics['train_time_sec']  = tt
    metrics['exp_name']        = exp
    metrics['model']           = model_name
    metrics['lambda_max']      = lambda_max
    metrics['train_accuracy']  = train_metrics['accuracy']
    metrics['train_test_gap']  = abs(train_metrics['accuracy'] - metrics['accuracy'])
    metrics['overfitting_report'] = overfit_report
    metrics['data_leak_report']   = leak_report

    # ── Affichage identique à DL_utils.run_experiment ────────────────────────
    print(f"\n   ✅ Résultats DANN {model_name} – Exp. {exp} :")
    print(f"      Accuracy    = {metrics['accuracy']:.4f}")
    print(f"      F1 (stress) = {metrics['f1']:.4f}")
    print(f"      Recall      = {metrics['recall']:.4f}")
    print(f"      Precision   = {metrics['precision']:.4f}")
    print(f"      F1-macro    = {metrics['f1_macro']:.4f}")
    print(f"      F1-weighted = {metrics['f1_weighted']:.4f}")
    print(f"      AUC         = {metrics['auc']:.4f}")
    print(f"      Spécificité = {metrics['specificity']:.4f}")
    print(f"      Incertitude = {metrics['pct_uncertain']:.1f}%")
    print(f"      Temps       = {tt:.1f}s")
    print(f"      Train Acc   = {train_metrics['accuracy']:.4f}")
    print(f"      Gap Train-Test = {metrics['train_test_gap']:.4f}")
    print(f"\n{format_rates_output(metrics)}")
    print(f"\n{format_overfitting_report(overfit_report)}")

    if metrics['accuracy'] >= OVERFIT_PERFECT_SCORE:
        print(f"\n   🚨🚨🚨  ALERTE : SCORE PARFAIT ({metrics['accuracy']:.4f})  🚨🚨🚨")
        print(f"   Un score parfait en EEG est QUASIMENT JAMAIS légitime.")
        print(f"   → Vérifiez impérativement le split par sujet !")

    # ── Graphiques ────────────────────────────────────────────────────────────
    save_plots(metrics['y_true'], metrics['y_pred'],
               metrics['y_proba'], od, model_name, exp)
    plot_learning_curves(history, od, model_name, exp)
    plot_dann_training(history, od, model_name, exp)
    plot_rates_distribution(
        metrics['y_true'], metrics['y_proba_concentration'],
        metrics['y_proba'], od, model_name, exp)

    # ── Sauvegarde métriques ──────────────────────────────────────────────────
    metrics_save = {k: v for k, v in metrics.items()
                    if k not in ('y_true', 'y_pred', 'y_proba',
                                 'y_proba_concentration',
                                 'overfitting_report', 'data_leak_report')}
    metrics_save['overfitting'] = {
        'is_overfitting': overfit_report['is_overfitting'],
        'severity':       overfit_report['severity'],
        'generalization_gap': overfit_report['generalization_gap'],
        'val_loss_trend': overfit_report['val_loss_trend'],
        'perfect_score':  overfit_report['perfect_score'],
        'warnings':       overfit_report['warnings'],
    }
    metrics_save['data_leak'] = {
        'has_leakage': leak_report['has_leakage'],
        'message':     leak_report['message'],
    }
    metrics_save['dann_history'] = {
        'label_loss':  history['label_loss'],
        'domain_loss': history['domain_loss'],
        'lambda_grl':  history['lambda_grl'],
    }

    with open(od / 'metrics.json', 'w') as f:
        json.dump(metrics_save, f, indent=2, default=str)

    # ── metrics.txt (identique à DL_utils) ───────────────────────────────────
    with open(od / 'metrics.txt', 'w') as f:
        f.write(f"{model_name} – Expérience DANN {exp}\n")
        f.write(f"{'='*50}\n")
        f.write(f"Accuracy      : {metrics['accuracy']:.4f}\n")
        f.write(f"F1 (stress)   : {metrics['f1']:.4f}\n")
        f.write(f"F1-macro      : {metrics['f1_macro']:.4f}\n")
        f.write(f"Recall        : {metrics['recall']:.4f}\n")
        f.write(f"Precision     : {metrics['precision']:.4f}\n")
        f.write(f"F1-weighted   : {metrics['f1_weighted']:.4f}\n")
        f.write(f"AUC           : {metrics['auc']:.4f}\n")
        f.write(f"Spécificité   : {metrics['specificity']:.4f}\n")
        f.write(f"Incertitude   : {metrics['pct_uncertain']:.1f}%\n")
        f.write(f"Temps         : {tt:.1f}s\n")
        f.write(f"Taille train  : {len(X_train)}\n")
        f.write(f"Taille test   : {len(y_test)}\n")
        f.write(f"Train Acc     : {train_metrics['accuracy']:.4f}\n")
        f.write(f"Gap Train-Test: {metrics['train_test_gap']:.4f}\n")
        f.write(f"Lambda max    : {lambda_max}\n")
        f.write(f"\n{'='*50}\n")
        f.write(f"TAUX CONCENTRATION / STRESS\n")
        f.write(f"{'='*50}\n")
        r = metrics['rates']
        f.write(f"Taux Concentration moyen : {r['avg_concentration_rate']:.1f}%\n")
        f.write(f"Taux Stress moyen        : {r['avg_stress_rate']:.1f}%\n")
        f.write(f"Concentration sur Concentration : {r['concentration_on_concentration']:.1f}%\n")
        f.write(f"Stress sur Concentration        : {r['stress_on_concentration']:.1f}%\n")
        f.write(f"Concentration sur Stress        : {r['concentration_on_stress']:.1f}%\n")
        f.write(f"Stress sur Stress               : {r['stress_on_stress']:.1f}%\n")
        f.write(f"\n{'='*50}\n")
        f.write(f"VALIDATION ANTI-OVERFITTING\n")
        f.write(f"{'='*50}\n")
        f.write(f"Overfitting détecté : {overfit_report['is_overfitting']}\n")
        f.write(f"Sévérité            : {overfit_report['severity']}\n")
        f.write(f"Gap généralisation  : {overfit_report['generalization_gap']:.1%}\n")
        f.write(f"Tendance val_loss   : {overfit_report['val_loss_trend']}\n")
        f.write(f"Score parfait       : {overfit_report['perfect_score']}\n")
        if overfit_report['warnings']:
            f.write(f"\nAvertissements :\n")
            for w in overfit_report['warnings']:
                f.write(f"  - {w}\n")
        if overfit_report['recommendations']:
            f.write(f"\nRecommandations :\n")
            for rec in overfit_report['recommendations']:
                f.write(f"  {rec}\n")
        f.write(f"\nFuite de données : {leak_report['message']}\n")

    # ── Sauvegarde modèle ─────────────────────────────────────────────────────
    model_path = md / f"{model_name}_{exp}_best.pt"
    try:
        md.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), model_path)
        print(f"   Modèle sauvegardé : {model_path}")
    except Exception as e:
        fallback = od / f"{model_name}_{exp}_best.pt"
        try:
            torch.save(model.state_dict(), fallback)
            print(f"   Modèle sauvegardé (fallback) : {fallback}")
        except Exception as e2:
            print(f"   Impossible de sauvegarder le modèle : {e2}")

    print(f"\n Terminé pour l'expérience DANN {exp}.\n")
    return metrics['accuracy']


# ============================================================================
# LOSO DANN
# ============================================================================
def run_dann_loso_validation(model_name, model_class, lambda_max=1.0):
    """Validation LOSO DANN sur l'expérience A."""
    from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                                  recall_score, confusion_matrix, roc_auc_score)

    exp = 'A'
    print("\n" + "=" * 70)
    print(f"NeuroCap DANN – {model_name} – Validation LOSO (Exp. {exp})")
    print("=" * 70)

    X_path = AUGMENTED_DIR / f"X_train_{exp}.npy"
    y_path = AUGMENTED_DIR / f"y_train_{exp}.npy"
    if not X_path.exists():
        print(f"  Fichier X_train_{exp}.npy manquant, LOSO ignorée")
        return

    X = np.load(X_path)
    y = np.load(y_path)

    sids = None
    for sn in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists():
            sids = np.load(sp); break
    if sids is None:
        print("  subject_ids introuvable, LOSO ignorée")
        return

    if len(sids) != len(X):
        ml = min(len(sids), len(X))
        sids, X, y = sids[:ml], X[:ml], y[:ml]

    unique_subjects = np.unique(sids)
    print(f"  {len(X)} epochs, {len(unique_subjects)} sujets")
    if len(unique_subjects) < 2:
        print("  Moins de 2 sujets, LOSO ignorée")
        return

    all_yt, all_yp, all_yprob = [], [], []
    fold_metrics = []
    t0 = time.time()

    for test_subj in unique_subjects:
        test_mask  = (sids == test_subj)
        train_mask = ~test_mask
        X_tr_full, y_tr_full = X[train_mask], y[train_mask]
        X_te, y_te            = X[test_mask],  y[test_mask]

        if len(np.unique(y_tr_full)) < 2 or len(X_te) == 0:
            continue

        n_val = max(1, int(len(X_tr_full) * 0.1))
        idx   = np.random.permutation(len(X_tr_full))
        X_tr, y_tr   = X_tr_full[idx[n_val:]], y_tr_full[idx[n_val:]]
        X_val_l, y_val_l = X_tr_full[idx[:n_val]], y_tr_full[idx[:n_val]]

        model = model_class()
        model, hist = train_dann_model(
            model, X_tr, y_tr, X_val_l, y_val_l,
            epochs=20, patience=5, lambda_max=lambda_max)

        of  = detect_overfitting(hist)
        met = evaluate_dann_model(model, X_te, y_te)
        train_acc_fold = evaluate_dann_model(model, X_tr, y_tr)['accuracy']
        gap_fold = train_acc_fold - met['accuracy']

        fold_metrics.append({
            'subject':              int(test_subj),
            'accuracy':             met['accuracy'],
            'f1_macro':             met['f1_macro'],
            'auc':                  met['auc'],
            'n_samples':            len(y_te),
            'overfitting':          of['is_overfitting'],
            'overfitting_severity': of['severity'],
            'concentration_rate':   met['rates']['avg_concentration_rate'],
            'stress_rate':          met['rates']['avg_stress_rate'],
            'train_test_gap':       gap_fold,
        })
        all_yt.extend(y_te.tolist())
        all_yp.extend(met['y_pred'])
        all_yprob.extend(met['y_proba'])

        of_icon = 'x' if of['is_overfitting'] else 'ok'
        print(f"    Fold sujet {int(test_subj):2d}: "
              f"Acc={met['accuracy']:.3f} Gap={gap_fold:.3f} "
              f"F1m={met['f1_macro']:.3f} [{of_icon}] ({len(y_te)} samples)")

    elapsed = time.time() - t0
    if not all_yt:
        print("  LOSO DANN échouée")
        return

    # ── Métriques globales ────────────────────────────────────────────────────
    global_metrics = {
        'accuracy':    accuracy_score(all_yt, all_yp),
        'f1_macro':    f1_score(all_yt, all_yp, average='macro', zero_division=0),
        'f1_weighted': f1_score(all_yt, all_yp, average='weighted', zero_division=0),
        'f1':          f1_score(all_yt, all_yp, zero_division=0),
        'precision':   precision_score(all_yt, all_yp, zero_division=0),
        'recall':      recall_score(all_yt, all_yp, zero_division=0),
        'specificity': 0.0, 'auc': 0.5,
        'n_folds':     len(fold_metrics),
        'train_time_sec': elapsed,
        'model':       model_name,
        'validation':  'LOSO',
        'exp':         exp,
        'fold_metrics': fold_metrics,
    }
    global_metrics['train_test_gap'] = float(
        np.mean([f['train_test_gap'] for f in fold_metrics]))

    cm = confusion_matrix(all_yt, all_yp)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        global_metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    if len(np.unique(all_yt)) > 1:
        try:
            global_metrics['auc'] = roc_auc_score(all_yt, all_yprob)
        except Exception:
            pass

    y_arr      = np.array(all_yt)
    prob_stress = np.array(all_yprob)
    prob_conc   = 1 - prob_stress
    loso_rates = {
        'avg_concentration_rate':         float(np.mean(prob_conc) * 100),
        'avg_stress_rate':                float(np.mean(prob_stress) * 100),
        'concentration_on_concentration': float(np.mean(prob_conc[y_arr == 0]) * 100) if (y_arr==0).any() else 0.0,
        'stress_on_concentration':        float(np.mean(prob_stress[y_arr == 0]) * 100) if (y_arr==0).any() else 0.0,
        'concentration_on_stress':        float(np.mean(prob_conc[y_arr == 1]) * 100) if (y_arr==1).any() else 0.0,
        'stress_on_stress':               float(np.mean(prob_stress[y_arr == 1]) * 100) if (y_arr==1).any() else 0.0,
    }
    global_metrics['rates'] = loso_rates

    print(f"\n  LOSO DANN exp {exp}: "
          f"Acc={global_metrics['accuracy']:.4f} "
          f"F1m={global_metrics['f1_macro']:.4f} "
          f"AUC={global_metrics['auc']:.4f} "
          f"Gap={global_metrics['train_test_gap']:.3f} "
          f"({global_metrics['n_folds']} folds, {elapsed:.1f}s)")

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    out_dir = DANN_OUTPUT_BASE / model_name / f"LOSO_exp_{exp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_plots(all_yt, all_yp, all_yprob, out_dir, model_name, f"LOSO_{exp}")
    plot_rates_distribution(
        all_yt, (1 - np.array(all_yprob)).tolist(), all_yprob,
        out_dir, model_name, f"LOSO_{exp}")

    metrics_save = {k: v for k, v in global_metrics.items()
                    if k != 'fold_metrics'}
    metrics_save['fold_metrics'] = fold_metrics
    with open(out_dir / 'metrics.json', 'w') as f:
        json.dump(metrics_save, f, indent=2, default=str)


# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================
def dann_main(model_name, model_class, lambda_max=1.0):
    """
    Lance 5 expériences DANN (A, B, C, D, FULL) + LOSO,
    miroir de dl_main dans DL_utils.
    """
    print(f"\n{'='*70}")
    print(f"NeuroCap DANN – {model_name}  (λ_max={lambda_max})")
    print(f"Device : {DEVICE} | AMP : {USE_AMP}")
    print(f"{'='*70}\n")

    exp_names      = ['A', 'B', 'C', 'D', 'FULL']
    test_accuracies = []

    for exp in exp_names:
        acc = run_dann_experiment(model_name, model_class, exp, lambda_max)
        test_accuracies.append(acc)

    out_dir = DANN_OUTPUT_BASE / model_name
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_test_accuracy(exp_names, test_accuracies, model_name, out_dir)

    run_dann_loso_validation(model_name, model_class, lambda_max)

    print(f"\n{'='*70}")
    print(f"DANN {model_name} — TERMINÉ (5 expériences + LOSO)")
    print(f"{'='*70}")
    print("\nTest accuracies DANN par expérience :")
    for exp, acc in zip(exp_names, test_accuracies):
        print(f"   {exp}: {acc:.4f}")
