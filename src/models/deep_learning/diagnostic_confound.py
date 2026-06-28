"""
NeuroCap — Diagnostic qualité des données de régression
=========================================================
Analyses par target (conc, stress) :
  1. Distribution des sujets et scores
  2. PCA / t-SNE des epochs (séparabilité inter-sujets)
  3. Analyse spectrale (PSD moyenne par sujet / niveau de difficulté)
  4. Bilan des métriques de régression (lecture des metrics.json)

Usage : python diagnostic_confound.py
"""

import numpy as np
import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from scipy import signal as scipy_signal
import warnings
warnings.filterwarnings('ignore')

# ─── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).resolve().parents[3]
REGRESSION_DIR = PROJECT_ROOT / "data" / "Regression" / "augmented"
DL_OUTPUT_BASE = PROJECT_ROOT / "reports" / "Regression" / "DL"
DIAG_DIR       = PROJECT_ROOT / "reports" / "Regression" / "diagnostic"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

ALL_MODELS = [
    "CNN1D", "CNN2D", "CNN3D", "EEGNet", "TCN",
    "CNN_LSTM_Att", "CNN_GRU_Att",
    "LSTM_1L", "LSTM_2L", "LSTM_Att",
    "BiLSTM_1L", "BiLSTM_2L", "BiLSTM_Att",
    "GRU_1L", "GRU_2L", "GRU_Att",
    "BiGRU_1L", "BiGRU_2L", "BiGRU_Att",
]
TARGETS     = ["conc", "stress"]
EXPERIMENTS = ["A", "B", "C", "D", "FULL"]
FS          = 250


def _load_target(target: str, exp: str = "A"):
    """Charge X, y_score, subject_ids pour un target."""
    d = REGRESSION_DIR / target
    X    = np.load(d / f"X_train_{exp}.npy")
    y    = np.load(d / f"y_train_{exp}.npy").astype(np.float32)
    sids = None
    for name in [f"subject_ids_train_{exp}.npy", "subject_ids_train.npy"]:
        p = d / name
        if p.exists():
            sids = np.load(p); break
    return X, y, sids


# ─── Test 1 : Distribution des scores par sujet ────────────────────────────
def test1_score_distribution():
    """
    Vérifie que les scores sont bien distribués (0-10) par sujet.
    Détecte les sujets dont les scores sont trop uniformes (peu de variance).
    """
    print("\n" + "=" * 65)
    print("TEST 1 : Distribution des scores par sujet et par target")
    print("=" * 65)

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Distribution des scores de régression par sujet",
                 fontsize=13, fontweight="bold")

    for i, target in enumerate(TARGETS):
        try:
            X, y, sids = _load_target(target)
        except FileNotFoundError:
            print(f"  {target} : données introuvables")
            continue

        print(f"\n  {target.upper()} : {len(X)} epochs | "
              f"{len(np.unique(sids)) if sids is not None else '?'} sujets | "
              f"Score [min={y.min():.2f}, max={y.max():.2f}, "
              f"mean={y.mean():.2f}, std={y.std():.2f}]")

        ax = axes[i]
        if sids is not None:
            unique_subj = np.unique(sids)
            means = [y[sids == s].mean() for s in unique_subj]
            stds  = [y[sids == s].std()  for s in unique_subj]
            ax.bar(range(len(unique_subj)), means, yerr=stds,
                   color="#2980B9" if target == "conc" else "#E74C3C",
                   alpha=0.8, capsize=3)
            ax.set_xlabel("Sujet (index)")

            # Identifier les sujets à faible variance (< 0.5)
            low_var = [int(s) for s, std in zip(unique_subj, stds) if std < 0.5]
            if low_var:
                print(f"  Sujets à faible variance de score (std<0.5) : {low_var}")
        else:
            ax.hist(y, bins=30, color="#2980B9" if target == "conc" else "#E74C3C",
                    alpha=0.8)
            ax.set_xlabel("Score")

        ax.set_ylabel("Score moyen ± std")
        ax.set_title(f"{target.upper()} – Score par sujet")
        ax.axhline(5.0, color="gray", ls="--", lw=1.5, label="Seuil Low/High (5.0)")
        ax.set_ylim(0, 10.5)
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(DIAG_DIR / "01_score_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Figure : {DIAG_DIR / '01_score_distribution.png'}")


# ─── Test 2 : PCA / t-SNE ─────────────────────────────────────────────────
def test2_pca_tsne():
    """
    PCA et t-SNE sur les epochs bruts.
    Les clusters doivent correspondre aux scores (gradient), pas aux sujets.
    Si les clusters = sujets -> possible confound inter-sujet.
    """
    print("\n" + "=" * 65)
    print("TEST 2 : PCA / t-SNE des epochs (séparabilité)")
    print("=" * 65)

    for target in TARGETS:
        try:
            X, y, sids = _load_target(target)
        except FileNotFoundError:
            print(f"  {target} : données introuvables")
            continue

        n_max = 1500
        if len(X) > n_max:
            idx = np.random.choice(len(X), n_max, replace=False)
            X_s = X[idx]; y_s = y[idx]
            sids_s = sids[idx] if sids is not None else None
        else:
            X_s, y_s, sids_s = X, y, sids

        X_flat = X_s.reshape(len(X_s), -1)
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_flat)
        var = pca.explained_variance_ratio_.sum()
        print(f"\n  {target.upper()} : PCA variance expliquée = {var:.1%}")

        fig, axes = plt.subplots(1, 2 if sids_s is not None else 1,
                                 figsize=(12 if sids_s is not None else 6, 5))
        if sids_s is None:
            axes = [axes]
        fig.suptitle(f"PCA – {target.upper()} (variance={var:.1%})",
                     fontsize=12, fontweight="bold")

        # Coloré par score continu
        sc = axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=y_s, s=10,
                             cmap="RdYlGn_r", alpha=0.6, vmin=0, vmax=10)
        plt.colorbar(sc, ax=axes[0], label="Score (0-10)")
        axes[0].set_title("Coloré par score")
        axes[0].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
        axes[0].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")

        # Coloré par sujet
        if sids_s is not None:
            sc2 = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=sids_s,
                                  s=10, cmap="tab20", alpha=0.6)
            plt.colorbar(sc2, ax=axes[1], label="Sujet ID")
            axes[1].set_title("Coloré par sujet")
            axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")

        plt.tight_layout()
        plt.savefig(DIAG_DIR / f"02_pca_{target}.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Figure : {DIAG_DIR / f'02_pca_{target}.png'}")

        # t-SNE (sous-échantillonné à 800)
        n_tsne = min(800, len(X_s))
        idx_tsne = np.random.choice(len(X_s), n_tsne, replace=False)
        print(f"  t-SNE sur {n_tsne} epochs...")
        try:
            tsne = TSNE(n_components=2, perplexity=30, random_state=42, n_iter=500)
            X_tsne = tsne.fit_transform(X_flat[idx_tsne])

            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            fig.suptitle(f"t-SNE – {target.upper()}", fontsize=12, fontweight="bold")

            sc = axes[0].scatter(X_tsne[:, 0], X_tsne[:, 1],
                                 c=y_s[idx_tsne], s=10, cmap="RdYlGn_r",
                                 alpha=0.6, vmin=0, vmax=10)
            plt.colorbar(sc, ax=axes[0], label="Score")
            axes[0].set_title("Coloré par score")

            if sids_s is not None:
                sc2 = axes[1].scatter(X_tsne[:, 0], X_tsne[:, 1],
                                      c=sids_s[idx_tsne], s=10,
                                      cmap="tab20", alpha=0.6)
                plt.colorbar(sc2, ax=axes[1], label="Sujet ID")
                axes[1].set_title("Coloré par sujet")

            plt.tight_layout()
            plt.savefig(DIAG_DIR / f"03_tsne_{target}.png", dpi=150, bbox_inches="tight")
            plt.close()
            print(f"  Figure : {DIAG_DIR / f'03_tsne_{target}.png'}")
        except Exception as e:
            print(f"  t-SNE échoué : {e}")


# ─── Test 3 : Analyse spectrale ────────────────────────────────────────────
def test3_spectral_analysis():
    """
    PSD moyenne par target et par quartile de score.
    Vérifie que le signal EEG varie réellement avec le score.
    """
    print("\n" + "=" * 65)
    print("TEST 3 : Analyse spectrale (variation signal/score)")
    print("=" * 65)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Analyse spectrale par target et quartile de score",
                 fontsize=13, fontweight="bold")

    for row, target in enumerate(TARGETS):
        try:
            X, y, sids = _load_target(target)
        except FileNotFoundError:
            print(f"  {target} : données introuvables")
            continue

        # PSD par quartile de score
        quartiles = np.percentile(y, [0, 25, 50, 75, 100])
        colors = ["#2980B9", "#27AE60", "#F39C12", "#E74C3C"]
        labels_q = [f"Q1 [{quartiles[0]:.1f}-{quartiles[1]:.1f}]",
                    f"Q2 [{quartiles[1]:.1f}-{quartiles[2]:.1f}]",
                    f"Q3 [{quartiles[2]:.1f}-{quartiles[3]:.1f}]",
                    f"Q4 [{quartiles[3]:.1f}-{quartiles[4]:.1f}]"]

        ax = axes[row, 0]
        for q_idx in range(4):
            mask = (y >= quartiles[q_idx]) & (y < quartiles[q_idx + 1])
            if q_idx == 3:
                mask = (y >= quartiles[q_idx]) & (y <= quartiles[q_idx + 1])
            n_q = np.sum(mask)
            if n_q == 0:
                continue
            idx_q = np.where(mask)[0][:min(200, n_q)]
            psds = []
            for i in idx_q:
                f_arr, p = scipy_signal.welch(X[i].flatten(), FS, nperseg=256)
                psds.append(p)
            psd_mean = np.mean(psds, axis=0)
            fmask = f_arr <= 45
            ax.semilogy(f_arr[fmask], psd_mean[fmask], color=colors[q_idx],
                        lw=2, alpha=0.85, label=labels_q[q_idx])

        ax.set_xlabel("Fréquence (Hz)")
        ax.set_ylabel("PSD (log)")
        ax.set_title(f"{target.upper()} – PSD par quartile de score")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # Histogramme des scores
        ax2 = axes[row, 1]
        ax2.hist(y, bins=25, color="#2980B9" if target == "conc" else "#E74C3C",
                 alpha=0.8, edgecolor="white")
        ax2.axvline(5.0, color="gray", ls="--", lw=1.5, label="Seuil Low/High")
        pct_high = np.mean(y >= 5.0) * 100
        ax2.set_xlabel("Score (0-10)")
        ax2.set_ylabel("Fréquence")
        ax2.set_title(f"{target.upper()} – Distribution des scores\n"
                      f"High (≥5) = {pct_high:.1f}%")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        print(f"  {target.upper()} : {len(X)} epochs | "
              f"Q1={quartiles[1]:.2f} Q2={quartiles[2]:.2f} "
              f"Q3={quartiles[3]:.2f} | High={pct_high:.1f}%")

    plt.tight_layout()
    plt.savefig(DIAG_DIR / "04_spectral_analysis.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure : {DIAG_DIR / '04_spectral_analysis.png'}")


# ─── Test 4 : Bilan métriques DL ──────────────────────────────────────────
def test4_metrics_report():
    """
    Lit les metrics.json des modèles DL entraînés et génère un bilan.
    Métriques : MAE, RMSE, R², AUC-ROC, F1-macro, Deploy Score.
    """
    print("\n" + "=" * 65)
    print("TEST 4 : Bilan des métriques DL de régression")
    print("=" * 65)

    rows = []
    for model in ALL_MODELS:
        for target in TARGETS:
            for exp in EXPERIMENTS:
                f = DL_OUTPUT_BASE / model / target / exp / "metrics.json"
                if not f.exists():
                    continue
                with open(f) as fp:
                    data = json.load(fp)
                rows.append({
                    "model": model, "target": target, "exp": exp, "source": "standard",
                    "mae":          data.get("mae",           np.nan),
                    "rmse":         data.get("rmse",          np.nan),
                    "r2":           data.get("r2",            np.nan),
                    "auc_roc":      data.get("auc_roc",       np.nan),
                    "f1_macro":     data.get("f1_macro",      np.nan),
                    "train_time_s": data.get("train_time_sec", np.nan),
                })

            # LOSO
            lf = DL_OUTPUT_BASE / model / target / "LOSO" / "metrics.json"
            if lf.exists():
                with open(lf) as fp:
                    data = json.load(fp)
                rows.append({
                    "model": model, "target": target, "exp": "LOSO", "source": "LOSO",
                    "mae":          data.get("mae",           np.nan),
                    "rmse":         data.get("rmse",          np.nan),
                    "r2":           data.get("r2",            np.nan),
                    "auc_roc":      data.get("auc_roc",       np.nan),
                    "f1_macro":     data.get("f1_macro",      np.nan),
                    "train_time_s": data.get("train_time_sec", np.nan),
                })

    if not rows:
        print("  Aucun metrics.json trouvé. Lancez les entraînements d'abord.")
        return

    print(f"\n  {len(rows)} résultats trouvés.\n")
    print(f"  {'Modèle':<15} {'Cible':<7} {'Exp':<5} {'MAE':>6} {'R²':>7} {'AUC':>6}")
    print(f"  {'-'*54}")

    for r in sorted(rows, key=lambda x: (x["target"], x["model"], x["exp"])):
        mae = f"{r['mae']:.3f}" if not np.isnan(r.get('mae', np.nan)) else "  -  "
        r2  = f"{r['r2']:.3f}"  if not np.isnan(r.get('r2',  np.nan)) else "  -  "
        auc = f"{r['auc_roc']:.3f}" if not np.isnan(r.get('auc_roc', np.nan)) else "  -  "
        print(f"  {r['model']:<15} {r['target']:<7} {r['exp']:<5} "
              f"{mae:>6} {r2:>7} {auc:>6}")

    # CSV
    csv_path = DIAG_DIR / "metrics_report.csv"
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n  CSV : {csv_path}")

    # Résumé par target (meilleur modèle Exp A)
    for target in TARGETS:
        sub = [r for r in rows if r["target"] == target and r["exp"] == "A"
               and not np.isnan(r.get("r2", np.nan))]
        if sub:
            best = max(sub, key=lambda x: x["r2"])
            print(f"\n  Meilleur {target.upper()} (Exp A, R²) : "
                  f"{best['model']} — MAE={best['mae']:.3f} "
                  f"R²={best['r2']:.3f} AUC={best['auc_roc']:.3f}")

    return rows


# ─── Main ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("NeuroCap — Diagnostic qualité données régression EEG")
    print(f"Sortie : {DIAG_DIR}")
    print("=" * 65)

    test1_score_distribution()
    test2_pca_tsne()
    test3_spectral_analysis()
    test4_metrics_report()

    print("\n" + "=" * 65)
    print("DIAGNOSTIC TERMINÉ")
    print(f"Figures dans : {DIAG_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
