"""
NeuroCap – DL_utils_v2.py (Version avec Validation Anti-Overfitting + Taux Concentration/Stress)
===================================================================================================
Module commun pour les 17 architectures Deep Learning.

NOUVEAUTÉS vs v2 précédente :
──────────────────────────────
1. DÉTECTION D'OVERFITTING automatique (gap généralisation, tendance val_loss, score parfait)
2. TAUX DE CONCENTRATION / STRESS en sortie (probabilités en %)
3. VÉRIFICATION DE FUITE DE DONNÉES (sujets partagés train/val/test)
4. COURBES D'APPRENTISSAGE (train vs val loss/accuracy)
5. PORTE DE VALIDATION avant le test (bloque si overfitting détecté)
6. CORRECTION BUG mkdir (vérification avant torch.save)

UTILISATION — Inchangée pour les scripts modèles :
    from DL_utils_v2 import N_CLASSES, CNNPreEncoder, BahdanauAttention, dl_main
    dl_main("CNN1D", CNN1D)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torch.amp import autocast, GradScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score,
                             confusion_matrix, roc_auc_score, roc_curve, auc)
import json, time, warnings, copy, os
from pathlib import Path

warnings.filterwarnings('ignore')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
USE_AMP = torch.cuda.is_available()

# ============================================================================
# CONSTANTES
# ============================================================================
FS = 250
EPOCH_SAMPLES = 1000
N_CLASSES = 2
LR = 1e-3
WD = 1e-4
MAX_EPOCHS = 50
PATIENCE = 10
BATCH_SIZE = 32
GRAD_CLIP = 1.0
NUM_WORKERS = 2

# Seuils anti-overfitting
OVERFIT_GAP_THRESHOLD = 0.10        # Gap généralisation max (10%)
OVERFIT_VAL_LOSS_TREND = 0.5        # Hausse val_loss max tolérée (50%)
OVERFIT_PERFECT_SCORE = 0.999       # Seuil score "parfait" suspect
OVERFIT_STOP_TRAINING = False       # Si True, bloque le test si overfitting

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUGMENTED_DIR = PROJECT_ROOT / "data/Augmentation/datasets_augmented"
OUTPUT_BASE = PROJECT_ROOT / "reports/deep_learning/DL_outputs"
MODEL_BASE = PROJECT_ROOT / "models/deep_learning/DL_models"


# ============================================================================
# PRÉ-ENCODEUR CNN (inchangé)
# ============================================================================
class CNNPreEncoder(nn.Module):
    """
    Compresse le signal EEG brut avant de le passer aux RNNs.
    Input:  (batch, 1, 1000) → Output: (batch, seq_len, features)
    """
    def __init__(self, out_features=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=25, stride=4, padding=12),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Conv1d(32, 64, kernel_size=11, stride=4, padding=5),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Conv1d(64, out_features, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(out_features),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.encoder(x).permute(0, 2, 1)


# ============================================================================
# MODULE ATTENTION (inchangé)
# ============================================================================
class BahdanauAttention(nn.Module):
    """Attention additive (Bahdanau) sur la dimension séquentielle."""
    def __init__(self, hidden_size):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_size, min(64, hidden_size)),
            nn.Tanh(),
            nn.Linear(min(64, hidden_size), 1)
        )

    def forward(self, rnn_output):
        weights = torch.softmax(self.attn(rnn_output), dim=1)
        context = (weights * rnn_output).sum(dim=1)
        return context, weights


# ============================================================================
# PRÉPARATION DES DONNÉES (inchangé)
# ============================================================================
def prepare_data(X, y):
    """Convertit numpy → tenseurs PyTorch avec shape (batch, 1, 1000)."""
    X_t = torch.FloatTensor(X)
    y_t = torch.LongTensor(y)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)
    return X_t, y_t


# ============================================================================
# ENTRAÎNEMENT AVEC SUIVI D'HISTORIQUE (MODIFIÉ)
# ============================================================================
def train_model(model, X_train, y_train, X_val, y_val,
                epochs=MAX_EPOCHS, patience=PATIENCE):
    """
    Entraîne un modèle avec early stopping, class weights, cosine LR, AMP.
    RETOURNE MAINTENANT : (model, history)
      history = dict avec train_loss, val_loss, train_acc, val_acc par époque
    """
    model = model.to(DEVICE)

    # Class weights
    cc = np.bincount(y_train.astype(int))
    cw = (torch.FloatTensor(len(y_train) / (2 * cc)).to(DEVICE)
          if len(cc) >= 2 and min(cc) > 0 else None)

    criterion = nn.CrossEntropyLoss(weight=cw)
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=epochs, eta_min=LR * 0.01)

    X_tr, y_tr = prepare_data(X_train, y_train)
    X_vl, y_vl = prepare_data(X_val, y_val)

    loader = DataLoader(
        TensorDataset(X_tr, y_tr),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE.type == 'cuda'),
        persistent_workers=(NUM_WORKERS > 0),
    )

    scaler = GradScaler('cuda') if USE_AMP else None

    # ─── Historique d'entraînement ───────────────────────────────────────────
    history = {
        'train_loss': [], 'val_loss': [],
        'train_acc': [],  'val_acc': [],
        'epochs': [],
        'best_epoch': 0, 'total_epochs': 0,
        'early_stopped': False,
    }

    best_vl = float('inf')
    best_st = None
    pc = 0
    best_epoch = 0

    for epoch in range(epochs):
        # ── Phase entraînement ─────────────────────────────────────────────
        model.train()
        train_loss_sum = 0.0
        train_correct = 0
        train_total = 0

        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)

            if USE_AMP:
                with autocast('cuda'):
                    loss = criterion(model(xb), yb)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                scaler.step(optimizer)
                scaler.update()
            else:
                loss = criterion(model(xb), yb)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                optimizer.step()

            train_loss_sum += loss.item() * len(yb)
            with torch.no_grad():
                preds = model(xb).argmax(1)
                train_correct += (preds == yb).sum().item()
                train_total += len(yb)

        scheduler.step()

        train_loss = train_loss_sum / max(train_total, 1)
        train_acc = train_correct / max(train_total, 1)

        # ── Phase validation ───────────────────────────────────────────────
        model.eval()
        with torch.no_grad():
            val_out = model(X_vl.to(DEVICE))
            val_loss = criterion(val_out, y_vl.to(DEVICE)).item()
            val_preds = val_out.argmax(1).cpu().numpy()
            val_acc = accuracy_score(y_val, val_preds)

        # ── Enregistrement historique ──────────────────────────────────────
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['epochs'].append(epoch + 1)

        if val_loss < best_vl:
            best_vl = val_loss
            best_st = copy.deepcopy(model.state_dict())
            pc = 0
            best_epoch = epoch + 1
        else:
            pc += 1
            if pc >= patience:
                print(f"         Early stopping à l'époque {epoch+1}")
                history['early_stopped'] = True
                break

    if best_st:
        model.load_state_dict(best_st)

    history['best_epoch'] = best_epoch
    history['total_epochs'] = len(history['epochs'])

    return model, history


# ============================================================================
# DÉTECTION D'OVERFITTING (NOUVEAU)
# ============================================================================
def detect_overfitting(history, gap_threshold=OVERFIT_GAP_THRESHOLD,
                       trend_threshold=OVERFIT_VAL_LOSS_TREND):
    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DÉTECTION AUTOMATIQUE D'OVERFITTING
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Analyse 4 critères :
      1. Gap de généralisation : |train_acc - val_acc| au meilleur epoch
      2. Tendance val_loss : augmentation récente = surapprentissage
      3. Score parfait : accuracy ≈ 1.0 = suspect
      4. Convergence rapide : meilleur modèle trop tôt

    Retourne : dict avec verdict détaillé
    """
    report = {
        'generalization_gap': 0.0,
        'gap_ok': True,
        'val_loss_trend': 'stable',
        'trend_ok': True,
        'perfect_score': False,
        'perfect_ok': True,
        'early_stop_info': '',
        'early_stop_ok': True,
        'is_overfitting': False,
        'severity': 'none',  # 'none', 'mild', 'moderate', 'severe'
        'warnings': [],
        'recommendations': [],
    }

    if not history['train_acc'] or not history['val_acc']:
        report['warnings'].append("Historique vide — impossible d'analyser")
        return report

    best_idx = history['val_loss'].index(min(history['val_loss']))

    # ─── 1. Gap de généralisation ────────────────────────────────────────────
    gap = abs(history['train_acc'][best_idx] - history['val_acc'][best_idx])
    report['generalization_gap'] = gap
    report['gap_ok'] = gap < gap_threshold
    if not report['gap_ok']:
        report['warnings'].append(
            f"Gap de généralisation élevé : {gap:.1%} (seuil : {gap_threshold:.0%})")
        report['recommendations'].append(
            "→ Augmenter le dropout (0.5→0.6) ou le weight decay (1e-4→5e-4)")

# ─── 2. Tendance val_loss (ignorer si val_acc très élevée) ────────────────
    best_val_acc = history['val_acc'][best_idx]
    if best_val_acc >= 0.98:
        report['val_loss_trend'] = 'stable (ignoré)'
        report['trend_ok'] = True
    else:
        n = len(history['val_loss'])
        min_val_loss = min(history['val_loss'])
        if n >= 5:
            last_5_avg = np.mean(history['val_loss'][-5:])
            increase = (last_5_avg - min_val_loss) / (min_val_loss + 1e-10)
            if increase > trend_threshold * 3:
                report['val_loss_trend'] = 'strongly_increasing'
                report['trend_ok'] = False
                report['warnings'].append(
                    f"Val_loss en forte hausse : +{increase:.1%} par rapport au minimum")
            elif increase > trend_threshold:
                report['val_loss_trend'] = 'increasing'
                report['trend_ok'] = False
                report['warnings'].append(
                    f"Val_loss en hausse : +{increase:.1%} par rapport au minimum")
                report['recommendations'].append(
                    "→ Réduire le learning rate ou augmenter la patience de l'early stopping")
        if n >= 3:
            last3 = history['val_loss'][-3:]
            if all(last3[i] > last3[i-1] for i in range(1, len(last3))):
                if report['trend_ok']:
                    report['val_loss_trend'] = 'increasing_recent'
                    report['trend_ok'] = False
                    report['warnings'].append("Val_loss augmente sur les 3 dernières époques")
                    report['recommendations'].append(
                        "→ Réduire le learning rate ou augmenter la patience de l'early stopping")

    # ─── 3. Score parfait (SUSPECT) ──────────────────────────────────────────
    best_train_acc = history['train_acc'][best_idx]
    best_val_acc = history['val_acc'][best_idx]

    if best_train_acc >= OVERFIT_PERFECT_SCORE and best_val_acc >= OVERFIT_PERFECT_SCORE:
        report['perfect_score'] = True
        report['perfect_ok'] = False
        report['warnings'].append(
            "SCORE PARFAIT (≈1.0) sur train ET val — TRÈS SUSPECT !")
        report['recommendations'].extend([
            "→ Vérifier la fuite de données : sujets partagés train/val/test ?",
            "→ Vérifier que le split est par SUJET et non par epoch",
            "→ Le z-score par epoch peut créer des patterns triviaux",
            "→ Essayer avec des données non normalisées (raw µV)",
            "→ Réduire drastiquement la taille du modèle",
        ])
    elif best_train_acc >= OVERFIT_PERFECT_SCORE:
        report['perfect_score'] = True
        report['perfect_ok'] = False
        report['warnings'].append(
            f"Score parfait sur train ({best_train_acc:.3f}) mais pas val ({best_val_acc:.3f}) — overfitting classique")
        report['recommendations'].extend([
            "→ Augmenter la régularisation (dropout, weight decay)",
            "→ Réduire le nombre de paramètres du modèle",
            "→ Ajouter du bruit ou de l'augmentation de données",
        ])

    # ─── 4. Information early stopping ───────────────────────────────────────
    ratio = history['best_epoch'] / max(history['total_epochs'], 1)
    report['early_stop_info'] = (
        f"Meilleur modèle à époque {history['best_epoch']}/{history['total_epochs']}"
        f" (ratio={ratio:.2f})")
    if ratio < 0.2 and history['total_epochs'] >= 10:
        report['warnings'].append(
            f"Convergence très rapide : meilleur à époque {history['best_epoch']}")
        report['recommendations'].append(
            "→ Convergence rapide + score élevé = possible fuite de données")

    # ─── Sévérité et verdict ─────────────────────────────────────────────────
    n_issues = sum([not report['gap_ok'], not report['trend_ok'],
                    not report['perfect_ok']])

    if n_issues == 0:
        report['severity'] = 'none'
        report['is_overfitting'] = False
    elif n_issues == 1 and not report['perfect_ok']:
        report['severity'] = 'severe'  # Score parfait = severe
        report['is_overfitting'] = True
    elif n_issues == 1:
        report['severity'] = 'mild'
        report['is_overfitting'] = True
    elif n_issues >= 2:
        report['severity'] = 'moderate' if not report['perfect_ok'] else 'severe'
        report['is_overfitting'] = True

    return report


def format_overfitting_report(report):
    """Formate le rapport d'overfitting en texte lisible avec encadrés."""
    lines = []

    # En-tête
    severity_icon = {'none': '✅', 'mild': '⚠️', 'moderate': '🔴', 'severe': '🚨'}
    icon = severity_icon.get(report['severity'], '❓')

    lines.append("  ┌─ VALIDATION ANTI-OVERFITTING ─────────────────────────┐")

    # Gap
    gap = report['generalization_gap']
    gap_ok = '✅' if report['gap_ok'] else '⚠️'
    lines.append(f"  │  Gap de généralisation : {gap:.1%}  {gap_ok}"
                 f"{'':>5}{'(seuil: ' + str(int(OVERFIT_GAP_THRESHOLD*100)) + '%)':>15} │")

    # Tendance val_loss
    trend_labels = {
        'stable': 'Stable ✅',
        'increasing': 'En hausse ⚠️',
        'strongly_increasing': 'Forte hausse 🔴',
        'increasing_recent': 'Hausse récente ⚠️',
    }
    trend_txt = trend_labels.get(report['val_loss_trend'], report['val_loss_trend'])
    lines.append(f"  │  Tendance val_loss     : {trend_txt:<25} │")

    # Score parfait
    if report['perfect_score']:
        lines.append(f"  │  Score parfait         : OUI 🚨 SUSPECT              │")
    else:
        lines.append(f"  │  Score parfait         : Non ✅                      │")

    # Early stopping info
    lines.append(f"  │  {report['early_stop_info']:<47} │")

    # Verdict
    if report['is_overfitting']:
        lines.append("  │                                                        │")
        lines.append(f"  │  VERDICT : {icon} OVERFITTING DÉTECTÉ ({report['severity']})"
                     f"{'':>15} │")
    else:
        lines.append("  │                                                        │")
        lines.append(f"  │  VERDICT : ✅ Pas d'overfitting détecté{'':>18} │")

    lines.append("  └────────────────────────────────────────────────────────┘")

    # Warnings
    if report['warnings']:
        lines.append("")
        for w in report['warnings']:
            lines.append(f"    ⚠️  {w}")

    # Recommendations
    if report['recommendations']:
        lines.append("")
        lines.append("    Recommandations :")
        for r in report['recommendations']:
            lines.append(f"    {r}")

    return '\n'.join(lines)


# ============================================================================
# VÉRIFICATION FUITE DE DONNÉES (NOUVEAU)
# ============================================================================
def check_data_leakage(sid_train, sid_val, sid_test):
    """
    Vérifie qu'aucun sujet n'est partagé entre train/val/test.
    C'est la cause #1 des scores parfaits en EEG.
    """
    if sid_train is None or sid_val is None or sid_test is None:
        return {'has_leakage': None, 'message': 'subject_ids non disponibles'}

    train_set = set(np.array(sid_train).flatten())
    val_set = set(np.array(sid_val).flatten())
    test_set = set(np.array(sid_test).flatten())

    train_val = train_set & val_set
    train_test = train_set & test_set
    val_test = val_set & test_set

    has_leak = bool(train_val or train_test or val_test)

    result = {
        'has_leakage': has_leak,
        'train_val_leak': train_val,
        'train_test_leak': train_test,
        'val_test_leak': val_test,
        'n_train_subjects': len(train_set),
        'n_val_subjects': len(val_set),
        'n_test_subjects': len(test_set),
        'message': ''
    }

    if has_leak:
        leaks = []
        if train_val:
            leaks.append(f"train↔val: sujets {sorted(train_val)}")
        if train_test:
            leaks.append(f"train↔test: sujets {sorted(train_test)}")
        if val_test:
            leaks.append(f"val↔test: sujets {sorted(val_test)}")
        result['message'] = f"FUITE DE DONNÉES détectée ! {', '.join(leaks)}"
    else:
        result['message'] = "Aucune fuite de données — sujets disjoints ✅"

    return result


# ============================================================================
# ÉVALUATION AVEC TAUX CONCENTRATION / STRESS (MODIFIÉ)
# ============================================================================
def evaluate_model(model, X, y):
    """
    Évalue un modèle et retourne un dict de métriques complètes.
    INCLUT MAINTENANT : taux de concentration et de stress.
    """
    model.eval()
    X_t, _ = prepare_data(X, y)

    with torch.no_grad():
        all_probs = []
        all_preds = []
        bs = 256
        for i in range(0, len(X_t), bs):
            batch = X_t[i:i+bs].to(DEVICE)
            out = model(batch)
            probs = torch.softmax(out, 1).cpu().numpy()
            preds = out.argmax(1).cpu().numpy()
            all_probs.append(probs)
            all_preds.append(preds)

        probs = np.concatenate(all_probs, axis=0)
        preds = np.concatenate(all_preds, axis=0)

    m = {
        'accuracy':  accuracy_score(y, preds),
        'f1':        f1_score(y, preds, zero_division=0),
        'f1_macro':  f1_score(y, preds, average='macro', zero_division=0),
        'f1_weighted': f1_score(y, preds, average='weighted', zero_division=0),
        'precision': precision_score(y, preds, zero_division=0),
        'recall':    recall_score(y, preds, zero_division=0),
        'specificity': 0.0,
        'auc':       0.5,
        'pct_uncertain': 0.0,
        'y_true':  y.tolist(),
        'y_pred':  preds.tolist(),
        'y_proba': probs[:, 1].tolist(),
        'y_proba_concentration': probs[:, 0].tolist(),
        'n_samples': len(y),
    }

    cm = confusion_matrix(y, preds)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        m['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    if len(np.unique(y)) > 1:
        try:
            m['auc'] = roc_auc_score(y, probs[:, 1])
        except Exception:
            pass
    m['pct_uncertain'] = float(np.sum(np.max(probs, 1) < 0.60) / len(y) * 100)

    # ─── Taux de concentration / stress ──────────────────────────────────────
    y_arr = np.array(y)
    prob_conc = probs[:, 0]   # P(Concentration)
    prob_stress = probs[:, 1]  # P(Stress)

    rates = {
        'avg_concentration_rate': float(np.mean(prob_conc) * 100),
        'avg_stress_rate': float(np.mean(prob_stress) * 100),
    }

    # Taux par classe réelle
    conc_mask = y_arr == 0
    stress_mask = y_arr == 1

    if conc_mask.any():
        rates['concentration_on_concentration'] = float(np.mean(prob_conc[conc_mask]) * 100)
        rates['stress_on_concentration'] = float(np.mean(prob_stress[conc_mask]) * 100)
    else:
        rates['concentration_on_concentration'] = 0.0
        rates['stress_on_concentration'] = 0.0

    if stress_mask.any():
        rates['concentration_on_stress'] = float(np.mean(prob_conc[stress_mask]) * 100)
        rates['stress_on_stress'] = float(np.mean(prob_stress[stress_mask]) * 100)
    else:
        rates['concentration_on_stress'] = 0.0
        rates['stress_on_stress'] = 0.0

    m['rates'] = rates

    return m


def format_rates_output(metrics):
    """
    Formate les taux de concentration/stress en affichage lisible.
    """
    r = metrics.get('rates', {})
    lines = []
    lines.append("  ┌─ TAUX DE CONCENTRATION / STRESS ─────────────────────┐")
    lines.append(f"  │  Taux Concentration moyen : {r.get('avg_concentration_rate', 0):>6.1f}%"
                 f"{'':>18}│")
    lines.append(f"  │  Taux Stress moyen        : {r.get('avg_stress_rate', 0):>6.1f}%"
                 f"{'':>18}│")
    lines.append("  │                                                       │")
    lines.append("  │  Sur epochs Concentration réels :                      │")
    lines.append(f"  │    → Taux Concentration prédit : "
                 f"{r.get('concentration_on_concentration', 0):>6.1f}%               │")
    lines.append(f"  │    → Taux Stress prédit        : "
                 f"{r.get('stress_on_concentration', 0):>6.1f}%               │")
    lines.append("  │                                                       │")
    lines.append("  │  Sur epochs Stress réels :                             │")
    lines.append(f"  │    → Taux Concentration prédit : "
                 f"{r.get('concentration_on_stress', 0):>6.1f}%               │")
    lines.append(f"  │    → Taux Stress prédit        : "
                 f"{r.get('stress_on_stress', 0):>6.1f}%               │")
    lines.append("  └───────────────────────────────────────────────────────┘")
    return '\n'.join(lines)


# ============================================================================
# GRAPHIQUES (existants + nouveaux)
# ============================================================================
def plot_confusion(y_true, y_pred, outdir, model_name, exp_name):
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (1, 1):
        cm = np.array([[cm[0, 0], 0], [0, 0]])
    cmn = cm.astype(float) / (cm.sum(1, keepdims=True) + 1e-12)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cmn, annot=True, fmt='.1%', cmap='Blues',
                xticklabels=['Concentration', 'Stress'],
                yticklabels=['Concentration', 'Stress'])
    plt.title(f'{model_name} – Exp. {exp_name}')
    plt.tight_layout()
    plt.savefig(outdir / 'confusion_matrix.png', dpi=150)
    plt.close()


def plot_roc(y_true, y_proba, outdir, model_name, exp_name):
    if len(np.unique(y_true)) < 2:
        return
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, lw=2, label=f'AUC = {roc_auc:.3f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.title(f'{model_name} – ROC (Exp. {exp_name})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / 'roc_curve.png', dpi=150)
    plt.close()


def plot_proba_dist(y_true, y_proba, outdir, model_name, exp_name):
    plt.figure(figsize=(6, 4))
    yt = np.array(y_true)
    yp = np.array(y_proba)
    plt.hist(yp[yt == 0], bins=25, alpha=0.6, color='#2980B9',
             label='Concentration', density=True)
    plt.hist(yp[yt == 1], bins=25, alpha=0.6, color='#E74C3C',
             label='Stress', density=True)
    plt.axvspan(0.40, 0.60, alpha=0.12, color='gray',
                label='Zone incertaine (40-60%)')
    plt.axvline(0.60, color='red', ls=':', lw=1.5,
                label='Seuil de confiance 0.60')
    plt.xlabel('P(Stress)')
    plt.ylabel('Densité')
    plt.title(f'{model_name} – Probas (Exp. {exp_name})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / 'proba_distribution.png', dpi=150)
    plt.close()


def save_plots(y_true, y_pred, y_proba, outdir, model_name, exp_name):
    """Génère les 3 graphiques standards."""
    plot_confusion(y_true, y_pred, outdir, model_name, exp_name)
    plot_roc(y_true, y_proba, outdir, model_name, exp_name)
    plot_proba_dist(y_true, y_proba, outdir, model_name, exp_name)


# ─── NOUVEAU : Courbes d'apprentissage (anti-overfitting) ────────────────────

def plot_learning_curves(history, outdir, model_name, exp_name):
    """
    Trace les courbes train/val loss et accuracy.
    Permet de visualiser l'overfitting (val_loss remonte).
    """
    if not history['epochs']:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'{model_name} – Courbes d\'apprentissage (Exp. {exp_name})',
                 fontsize=13, fontweight='bold')

    epochs = history['epochs']

    # Loss
    ax1.plot(epochs, history['train_loss'], 'b-o', ms=3, lw=1.5, label='Train Loss')
    ax1.plot(epochs, history['val_loss'], 'r-s', ms=3, lw=1.5, label='Val Loss')
    best_ep = history['best_epoch']
    if best_ep in epochs:
        best_idx = epochs.index(best_ep)
        ax1.axvline(best_ep, color='green', ls='--', lw=1.5, alpha=0.7,
                    label=f'Best epoch ({best_ep})')
    ax1.set_xlabel('Époque')
    ax1.set_ylabel('Loss')
    ax1.set_title('Loss (Cross-Entropy)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Accuracy
    ax2.plot(epochs, history['train_acc'], 'b-o', ms=3, lw=1.5, label='Train Acc')
    ax2.plot(epochs, history['val_acc'], 'r-s', ms=3, lw=1.5, label='Val Acc')
    if best_ep in epochs:
        ax2.axvline(best_ep, color='green', ls='--', lw=1.5, alpha=0.7,
                    label=f'Best epoch ({best_ep})')
    ax2.set_xlabel('Époque')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Accuracy')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(outdir / 'learning_curves.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_rates_distribution(y_true, y_proba_conc, y_proba_stress, outdir, model_name, exp_name):
    """
    Nouveau graphique : distribution des taux de concentration/stress.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'{model_name} – Distribution des Taux Concentration/Stress (Exp. {exp_name})',
                 fontsize=12, fontweight='bold')

    y_arr = np.array(y_true)
    prob_c = np.array(y_proba_conc) * 100
    prob_s = np.array(y_proba_stress) * 100

    # Taux de concentration
    ax = axes[0]
    if (y_arr == 0).any():
        ax.hist(prob_c[y_arr == 0], bins=25, alpha=0.7, color='#2980B9',
                label='Vrai Concentration', density=True)
    if (y_arr == 1).any():
        ax.hist(prob_c[y_arr == 1], bins=25, alpha=0.7, color='#E74C3C',
                label='Vrai Stress', density=True)
    ax.axvline(50, color='gray', ls='--', lw=1.5, alpha=0.7, label='Seuil 50%')
    ax.set_xlabel('Taux de Concentration prédit (%)')
    ax.set_ylabel('Densité')
    ax.set_title('Distribution du Taux de Concentration')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    # Taux de stress
    ax2 = axes[1]
    if (y_arr == 0).any():
        ax2.hist(prob_s[y_arr == 0], bins=25, alpha=0.7, color='#2980B9',
                label='Vrai Concentration', density=True)
    if (y_arr == 1).any():
        ax2.hist(prob_s[y_arr == 1], bins=25, alpha=0.7, color='#E74C3C',
                label='Vrai Stress', density=True)
    ax2.axvline(50, color='gray', ls='--', lw=1.5, alpha=0.7, label='Seuil 50%')
    ax2.set_xlabel('Taux de Stress prédit (%)')
    ax2.set_ylabel('Densité')
    ax2.set_title('Distribution du Taux de Stress')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(outdir / 'rates_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# EXPÉRIENCE STANDARD (MODIFIÉE : overfitting + rates + bugfix)
# ============================================================================
def run_experiment(model_name, model_class, exp):
    """
    Lance une expérience d'augmentation (A/B/C/D/FULL).

    NOUVEAU FLUX :
      1. Charger données
      2. Vérifier fuite de données
      3. Créer répertoires (CORRIGÉ)
      4. Entraîner avec historique
      5. Détecter overfitting
      6. Afficher rapport anti-overfitting
      7. Évaluer sur test avec TAUX concentration/stress
      8. Sauvegarder tout (métriques, courbes, rapport overfitting)
    """
    print("=" * 70)
    print(f"NeuroCap – {model_name} – Expérience {exp}")
    print(f"Device : {DEVICE} | AMP : {USE_AMP}")
    print("=" * 70)

    X_train = np.load(AUGMENTED_DIR / f"X_train_{exp}.npy")
    y_train = np.load(AUGMENTED_DIR / f"y_train_{exp}.npy")
    X_val   = np.load(AUGMENTED_DIR / "X_val.npy")
    y_val   = np.load(AUGMENTED_DIR / "y_val.npy")
    X_test  = np.load(AUGMENTED_DIR / "X_test.npy")
    y_test  = np.load(AUGMENTED_DIR / "y_test.npy")

    print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
    print(f"Train – Concentration: {np.sum(y_train==0)}, Stress: {np.sum(y_train==1)}")

    # ─── Vérification fuite de données ───────────────────────────────────────
    sid_train = sid_val = sid_test = None
    for sn in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists():
            sid_train = np.load(sp)
            break
    for sn in ["subject_ids_val.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists():
            sid_val = np.load(sp)
    for sn in ["subject_ids_test.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists():
            sid_test = np.load(sp)

    leak_report = check_data_leakage(sid_train, sid_val, sid_test)
    print(f"\n  🔍 Vérification fuite de données : {leak_report['message']}")
    if leak_report['has_leakage']:
        print(f"  🚨 ATTENTION : {leak_report['message']}")
        print(f"  🚨 Les scores parfaits peuvent être causés par cette fuite !")

    # ─── Création répertoires (CORRIGÉ — vérification explicite) ────────────
    od = OUTPUT_BASE / model_name / f"exp_{exp}"
    md = MODEL_BASE / model_name

    try:
        od.mkdir(parents=True, exist_ok=True)
        md.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"  ❌ Erreur création répertoire : {e}")
        # Fallback : essayer de créer manuellement
        os.makedirs(str(od), exist_ok=True)
        os.makedirs(str(md), exist_ok=True)

    # Vérification que les répertoires existent
    if not od.exists() or not md.exists():
        print(f"  ❌ Impossible de créer les répertoires !")
        return

    # ─── Entraînement avec historique ───────────────────────────────────────
    print(f"\n▶ Entraînement {model_name} – Exp. {exp}...")
    t0 = time.time()
    model = model_class()
    model, history = train_model(model, X_train, y_train, X_val, y_val)
    tt = time.time() - t0

    # ─── Détection overfitting ──────────────────────────────────────────────
    overfit_report = detect_overfitting(history)

    # ─── Évaluation sur train (pour gap de généralisation sur test) ──────────
    train_metrics = evaluate_model(model, X_train, y_train)

    # ─── Évaluation sur test ────────────────────────────────────────────────
    metrics = evaluate_model(model, X_test, y_test)
    metrics['train_time_sec'] = tt
    metrics['exp_name'] = exp
    metrics['model'] = model_name
    metrics['train_accuracy'] = train_metrics['accuracy']
    metrics['train_test_gap'] = abs(train_metrics['accuracy'] - metrics['accuracy'])
    metrics['overfitting_report'] = overfit_report
    metrics['data_leak_report'] = leak_report

    # ─── Affichage résultats ────────────────────────────────────────────────
    print(f"\n   ✅ Résultats {model_name} – Exp. {exp} :")
    print(f"      Accuracy    = {metrics['accuracy']:.4f}")
    print(f"      F1 (stress) = {metrics['f1']:.4f}")
    print(f"      Recall      = {metrics['recall']:.4f}")
    print(f"      Precision   = {metrics['precision']:.4f}")
    print(f"      F1-macro    = {metrics['f1_macro']:.4f}")
    print(f"      F1-weighted   = {metrics['f1_weighted']:.4f}")
    print(f"      AUC         = {metrics['auc']:.4f}")
    print(f"      Spécificité = {metrics['specificity']:.4f}")
    print(f"      Incertitude = {metrics['pct_uncertain']:.1f}%")
    print(f"      Temps       = {tt:.1f}s")
    print(f"      Train Acc   = {train_metrics['accuracy']:.4f}")
    print(f"      Gap Train-Test = {metrics['train_test_gap']:.4f}")

    # ─── Taux concentration / stress ────────────────────────────────────────
    print(f"\n{format_rates_output(metrics)}")

    # ─── Rapport anti-overfitting ───────────────────────────────────────────
    print(f"\n{format_overfitting_report(overfit_report)}")

    # ─── Alerte score parfait ───────────────────────────────────────────────
    if metrics['accuracy'] >= OVERFIT_PERFECT_SCORE:
        print(f"\n   🚨🚨🚨  ALERTE : SCORE PARFAIT ({metrics['accuracy']:.4f})  🚨🚨🚨")
        print(f"   Un score parfait en EEG est QUASIMENT JAMAIS légitime.")
        print(f"   Causes probables :")
        print(f"     1. Fuite de données (mêmes sujets dans train et test)")
        print(f"     2. Z-score par epoch crée un pattern trivial")
        print(f"     3. Dataset trop petit pour le modèle")
        print(f"     4. Labels facilement séparables dans l'espace z-score")
        print(f"   → Vérifiez impérativement le split par sujet !")

    # ─── Graphiques ─────────────────────────────────────────────────────────
    save_plots(metrics['y_true'], metrics['y_pred'],
               metrics['y_proba'], od, model_name, exp)

    # Courbes d'apprentissage (NOUVEAU)
    plot_learning_curves(history, od, model_name, exp)

    # Distribution des taux (NOUVEAU)
    plot_rates_distribution(
        metrics['y_true'],
        metrics['y_proba_concentration'],
        metrics['y_proba'],
        od, model_name, exp
    )

    # ─── Sauvegarde métriques ───────────────────────────────────────────────
    metrics_save = {k: v for k, v in metrics.items()
                    if k not in ('y_true', 'y_pred', 'y_proba',
                                 'y_proba_concentration',
                                 'overfitting_report', 'data_leak_report')}
    metrics_save['overfitting'] = {
        'is_overfitting': overfit_report['is_overfitting'],
        'severity': overfit_report['severity'],
        'generalization_gap': overfit_report['generalization_gap'],
        'val_loss_trend': overfit_report['val_loss_trend'],
        'perfect_score': overfit_report['perfect_score'],
        'warnings': overfit_report['warnings'],
    }
    metrics_save['data_leak'] = {
        'has_leakage': leak_report['has_leakage'],
        'message': leak_report['message'],
    }

    with open(od / 'metrics.json', 'w') as f:
        json.dump(metrics_save, f, indent=2, default=str)

    with open(od / 'metrics.txt', 'w') as f:
        f.write(f"{model_name} – Expérience {exp}\n")
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
            for r in overfit_report['recommendations']:
                f.write(f"  {r}\n")
        f.write(f"\nFuite de données : {leak_report['message']}\n")

    # ─── Sauvegarde modèle (CORRIGÉ — vérification répertoire) ──────────────
    model_path = md / f"{model_name}_{exp}_best.pt"
    try:
        # Double vérification que le répertoire existe
        md.mkdir(parents=True, exist_ok=True)
        if not md.exists():
            os.makedirs(str(md), exist_ok=True)
        torch.save(model.state_dict(), model_path)
        print(f"   Modèle sauvegardé : {model_path}")
    except Exception as e:
        # Fallback : sauvegarder dans le répertoire de sortie
        fallback_path = od / f"{model_name}_{exp}_best.pt"
        try:
            torch.save(model.state_dict(), fallback_path)
            print(f"   ⚠️ Modèle sauvegardé (fallback) : {fallback_path}")
        except Exception as e2:
            print(f"   ❌ Impossible de sauvegarder le modèle : {e2}")

    print(f"\n✅ Terminé pour l'expérience {exp}.\n")
    return metrics['accuracy']

def plot_test_accuracy(exp_names, test_accuracies, model_name, outdir):
    """
    Crée un barplot de l'accuracy sur le test pour chaque expérience.
    """
    plt.figure(figsize=(8, 5))
    bars = plt.bar(exp_names, test_accuracies, color=['#2980B9', '#27AE60', '#F39C12', '#E74C3C', '#8E44AD'])
    plt.ylim(0, 1.05)
    plt.ylabel('Accuracy sur le jeu de test')
    plt.xlabel('Expérience d\'augmentation')
    plt.title(f'{model_name} – Test Accuracy par augmentation')
    
    # Ajouter les valeurs sur les barres
    for bar, acc in zip(bars, test_accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f'{acc:.4f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(outdir / 'test_accuracy_per_exp.png', dpi=150)
    plt.close()


# ============================================================================
# LOSO VALIDATION (MODIFIÉE : overfitting + rates)
# ============================================================================
def run_loso_validation(model_name, model_class):
    """Validation LOSO sur l'expérience A avec détection d'overfitting et taux."""
    exp = 'A'
    print("\n" + "=" * 70)
    print(f"NeuroCap – {model_name} – Validation LOSO sur expérience {exp}")
    print("=" * 70)

    X_path = AUGMENTED_DIR / f"X_train_{exp}.npy"
    y_path = AUGMENTED_DIR / f"y_train_{exp}.npy"
    if not X_path.exists():
        print(f"  ⚠ Fichier X_train_{exp}.npy manquant, LOSO ignorée")
        return

    X = np.load(X_path)
    y = np.load(y_path)

    sids = None
    for sn in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        sp = AUGMENTED_DIR / sn
        if sp.exists():
            sids = np.load(sp)
            break
    if sids is None:
        print(f"  ⚠ subject_ids introuvable, LOSO ignorée")
        return

    if len(sids) != len(X):
        min_len = min(len(sids), len(X))
        sids, X, y = sids[:min_len], X[:min_len], y[:min_len]

    unique_subjects = np.unique(sids)
    print(f"  {len(X)} epochs, {len(unique_subjects)} sujets")
    if len(unique_subjects) < 2:
        print("  ⚠ Moins de 2 sujets, LOSO ignorée")
        return

    all_yt, all_yp, all_yprob = [], [], []
    fold_metrics = []
    overfitting_folds = 0
    t0 = time.time()

    for test_subj in unique_subjects:
        test_mask = (sids == test_subj)
        train_mask = ~test_mask
        X_tr_full, y_tr_full = X[train_mask], y[train_mask]
        X_te, y_te = X[test_mask], y[test_mask]

        if len(np.unique(y_tr_full)) < 2 or len(X_te) == 0:
            continue

        n_val = max(1, int(len(X_tr_full) * 0.1))
        idx = np.random.permutation(len(X_tr_full))
        X_tr = X_tr_full[idx[n_val:]]
        y_tr = y_tr_full[idx[n_val:]]
        X_val_l = X_tr_full[idx[:n_val]]
        y_val_l = y_tr_full[idx[:n_val]]

        model = model_class()
        model, hist = train_model(model, X_tr, y_tr, X_val_l, y_val_l,
                                  epochs=20, patience=5)

        # Vérifier overfitting sur ce fold
        of = detect_overfitting(hist)
        if of['is_overfitting']:
            overfitting_folds += 1

        met = evaluate_model(model, X_te, y_te)
        # Calcul du gap train-test pour ce fold
        train_acc_fold = evaluate_model(model, X_tr, y_tr)['accuracy']
        gap_fold = train_acc_fold - met['accuracy']

        fold_metrics.append({
            'subject': int(test_subj),
            'accuracy': met['accuracy'],
            'f1_macro': met['f1_macro'],
            'auc': met['auc'],
            'n_samples': len(y_te),
            'overfitting': of['is_overfitting'],
            'overfitting_severity': of['severity'],
            'concentration_rate': met['rates']['avg_concentration_rate'],
            'stress_rate': met['rates']['avg_stress_rate'],
            'train_test_gap': gap_fold,
        })
        all_yt.extend(y_te.tolist())
        all_yp.extend(met['y_pred'])
        all_yprob.extend(met['y_proba'])

        of_icon = '🔴' if of['is_overfitting'] else '✅'
        print(f"    Fold sujet {int(test_subj):2d}: "
              f"Acc={met['accuracy']:.3f} "
              f"Gap={gap_fold:.3f} " 
              f"F1m={met['f1_macro']:.3f} "
              f"F1w={met['f1_weighted']:.3f} "
              f"Conc={met['rates']['avg_concentration_rate']:.1f}% "
              f"Stress={met['rates']['avg_stress_rate']:.1f}% "
              f"{of_icon} ({len(y_te)} samples)")

    elapsed = time.time() - t0

    if not all_yt:
        print(f"  ⚠ LOSO échouée")
        return

    # ─── Métriques globales LOSO ─────────────────────────────────────────────
    global_metrics = {
        'accuracy':    accuracy_score(all_yt, all_yp),
        'f1':          f1_score(all_yt, all_yp, zero_division=0),
        'f1_macro':    f1_score(all_yt, all_yp, average='macro', zero_division=0),
        'f1_weighted': f1_score(all_yt, all_yp, average='weighted', zero_division=0),
        'precision':   precision_score(all_yt, all_yp, zero_division=0),
        'recall':      recall_score(all_yt, all_yp, zero_division=0),
        'specificity': 0.0,
        'auc':         0.5,
        'pct_uncertain': 0.0,
        'n_folds':     len(fold_metrics),
        'overfitting_folds': overfitting_folds,
        'fold_metrics': fold_metrics,
        'train_time_sec': elapsed,
        'model': model_name,
        'validation': 'LOSO',
        'exp': exp,
    }

    # Après avoir construit global_metrics, ajoutez cette ligne :
    global_metrics['train_test_gap'] = np.mean([f['train_test_gap'] for f in fold_metrics])

    cm = confusion_matrix(all_yt, all_yp)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        global_metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    if len(np.unique(all_yt)) > 1:
        try:
            global_metrics['auc'] = roc_auc_score(all_yt, all_yprob)
        except Exception:
            pass
    max_probs = np.max(
        np.column_stack([1 - np.array(all_yprob), all_yprob]), axis=1)
    global_metrics['pct_uncertain'] = float(
        np.sum(max_probs < 0.60) / len(all_yt) * 100)

    # ─── Taux LOSO ──────────────────────────────────────────────────────────
    y_arr = np.array(all_yt)
    prob_stress = np.array(all_yprob)
    prob_conc = 1 - prob_stress

    loso_rates = {
        'avg_concentration_rate': float(np.mean(prob_conc) * 100),
        'avg_stress_rate': float(np.mean(prob_stress) * 100),
        'concentration_on_concentration': float(np.mean(prob_conc[y_arr == 0]) * 100) if (y_arr == 0).any() else 0.0,
        'stress_on_concentration': float(np.mean(prob_stress[y_arr == 0]) * 100) if (y_arr == 0).any() else 0.0,
        'concentration_on_stress': float(np.mean(prob_conc[y_arr == 1]) * 100) if (y_arr == 1).any() else 0.0,
        'stress_on_stress': float(np.mean(prob_stress[y_arr == 1]) * 100) if (y_arr == 1).any() else 0.0,
    }
    global_metrics['rates'] = loso_rates

    # ─── Affichage ──────────────────────────────────────────────────────────
    print(f"\n  ✅ LOSO exp {exp}: Acc={global_metrics['accuracy']:.4f} "
          f"F1m={global_metrics['f1_macro']:.4f} "
          f"F1w={global_metrics['f1_weighted']:.4f} "
          f"AUC={global_metrics['auc']:.4f} "
          f"Gap={global_metrics['train_test_gap']:.3f} "
          f"({global_metrics['n_folds']} folds, {elapsed:.1f}s)")

    print(f"\n  ┌─ TAUX LOSO ──────────────────────────────────────────┐")
    print(f"  │  Concentration moyen : {loso_rates['avg_concentration_rate']:>6.1f}%               │")
    print(f"  │  Stress moyen        : {loso_rates['avg_stress_rate']:>6.1f}%               │")
    print(f"  │  Conc. sur Conc.     : {loso_rates['concentration_on_concentration']:>6.1f}%               │")
    print(f"  │  Stress sur Conc.    : {loso_rates['stress_on_concentration']:>6.1f}%               │")
    print(f"  │  Conc. sur Stress    : {loso_rates['concentration_on_stress']:>6.1f}%               │")
    print(f"  │  Stress sur Stress   : {loso_rates['stress_on_stress']:>6.1f}%               │")
    print(f"  └────────────────────────────────────────────────────────┘")

    overfit_pct = overfitting_folds / max(len(fold_metrics), 1) * 100
    print(f"\n  Folds avec overfitting : {overfitting_folds}/{len(fold_metrics)} ({overfit_pct:.0f}%)")

    if global_metrics['accuracy'] >= OVERFIT_PERFECT_SCORE:
        print(f"\n  🚨 ALERTE LOSO : Score parfait ({global_metrics['accuracy']:.4f})")
        print(f"  → Même en LOSO, un score parfait est suspect en EEG")
        print(f"  → Vérifiez si les epochs d'un même sujet sont réellement indépendants")

    # ─── Sauvegarde ─────────────────────────────────────────────────────────
    out_dir = OUTPUT_BASE / model_name / f"LOSO_exp_{exp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_plots(all_yt, all_yp, all_yprob, out_dir, model_name, f"LOSO_{exp}")

    plot_rates_distribution(all_yt, (1 - np.array(all_yprob)).tolist(),
                           all_yprob, out_dir, model_name, f"LOSO_{exp}")

    metrics_save = {k: v for k, v in global_metrics.items()
                    if k not in ('y_true', 'y_pred', 'y_proba', 'fold_metrics')}
    metrics_save['fold_metrics'] = fold_metrics
    with open(out_dir / 'metrics.json', 'w') as f:
        json.dump(metrics_save, f, indent=2, default=str)


# ============================================================================
# POINT D'ENTRÉE PRINCIPAL (MODIFIÉ)
# ============================================================================
def dl_main(model_name, model_class):
    """
    Point d'entrée principal : 5 expériences + LOSO.
    Chaque expérience inclut maintenant :
      - Vérification fuite de données
      - Détection overfitting
      - Taux concentration/stress
      - Courbes d'apprentissage
    """
    print(f"\n{'='*70}")
    print(f"NeuroCap DL v2 – {model_name}")
    print(f"Device : {DEVICE} | AMP : {USE_AMP}")
    print(f"Anti-overfitting : GAP<{OVERFIT_GAP_THRESHOLD:.0%} | "
          f"Score parfait <{OVERFIT_PERFECT_SCORE:.1%}")
    print(f"{'='*70}\n")

    exp_names = ['A', 'B', 'C', 'D', 'FULL']
    test_accuracies = []

    for exp in exp_names:
        acc = run_experiment(model_name, model_class, exp)   # ← run_experiment retourne l'accuracy
        test_accuracies.append(acc)

    # Graphique des test accuracies
    out_dir = OUTPUT_BASE / model_name
    plot_test_accuracy(exp_names, test_accuracies, model_name, out_dir)

    run_loso_validation(model_name, model_class)

    print(f"\n{'='*70}")
    print(f"✅ {model_name} — TERMINÉ (5 expériences + LOSO)")
    print(f"{'='*70}")
   
    print("\n📊 Test accuracies par expérience :")
    for exp, acc in zip(exp_names, test_accuracies):
        print(f"   {exp}: {acc:.4f}")
    


# ============================================================================
# FONCTIONS UTILITAIRES POUR PRÉDICTION EN TEMPS RÉEL (NOUVEAU)
# ============================================================================
def predict_rates(model, epoch_signal):
    """
    Prédit les taux de concentration/stress pour un signal EEG prétraité.

    Paramètres :
        model : modèle PyTorch entraîné
        epoch_signal : array (1000,) ou (1, 1000) — 1 epoch de 4s à 250 Hz

    Retourne :
        dict avec taux_concentration et taux_stress en pourcentage
    """
    model.eval()
    if isinstance(epoch_signal, np.ndarray):
        x = torch.FloatTensor(epoch_signal)
        if x.dim() == 1:
            x = x.unsqueeze(0).unsqueeze(0)  # (1, 1, 1000)
        elif x.dim() == 2:
            x = x.unsqueeze(0)  # (1, 1, 1000)
    else:
        x = epoch_signal

    with torch.no_grad():
        out = model(x.to(DEVICE))
        probs = torch.softmax(out, 1).cpu().numpy()[0]

    return {
        'taux_concentration': float(probs[0] * 100),
        'taux_stress': float(probs[1] * 100),
        'prediction': 'Concentration' if probs[0] > 0.5 else 'Stress',
        'confiance': float(max(probs) * 100),
    }


def predict_rates_batch(model, X_batch):
    """
    Prédit les taux pour un batch d'epochs.

    Paramètres :
        model : modèle PyTorch entraîné
        X_batch : array (N, 1000) — N epochs

    Retourne :
        list de dicts avec taux_concentration, taux_stress, prediction, confiance
    """
    model.eval()
    X_t = torch.FloatTensor(X_batch)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)  # (N, 1, 1000)

    with torch.no_grad():
        out = model(X_t.to(DEVICE))
        probs = torch.softmax(out, 1).cpu().numpy()

    results = []
    for p in probs:
        results.append({
            'taux_concentration': float(p[0] * 100),
            'taux_stress': float(p[1] * 100),
            'prediction': 'Concentration' if p[0] > 0.5 else 'Stress',
            'confiance': float(max(p) * 100),
        })

    return results


def format_realtime_output(rate_result):
    """
    Formate la sortie pour l'affichage temps réel NeuroCap.

    Exemple de sortie :
    ┌─────────────────────────────────────┐
    │  CONCENTRATION : ████████░░  82.3%  │
    │  STRESS        : ██░░░░░░░░  17.7%  │
    │  Prédiction    : Concentration      │
    │  Confiance     : 82.3%              │
    └─────────────────────────────────────┘
    """
    conc = rate_result['taux_concentration']
    stress = rate_result['taux_stress']
    pred = rate_result['prediction']
    conf = rate_result['confiance']

    # Barres de progression (10 caractères)
    conc_bar = '█' * int(conc / 10) + '░' * (10 - int(conc / 10))
    stress_bar = '█' * int(stress / 10) + '░' * (10 - int(stress / 10))

    lines = [
        "  ┌─────────────────────────────────────┐",
        f"  │  CONCENTRATION : {conc_bar}  {conc:>5.1f}%  │",
        f"  │  STRESS        : {stress_bar}  {stress:>5.1f}%  │",
        f"  │  Prédiction    : {pred:<20s}  │",
        f"  │  Confiance     : {conf:>5.1f}%              │",
        "  └─────────────────────────────────────┘",
    ]
    return '\n'.join(lines)