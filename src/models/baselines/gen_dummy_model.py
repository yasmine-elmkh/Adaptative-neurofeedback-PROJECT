"""
Génère un modèle LightGBM synthétique pour les tests sans données EEG réelles.

Simule deux classes EEG distincts :
  - Concentration : alpha dominant (10 Hz), beta modéré, theta faible
  - Stress         : beta dominant (22 Hz), alpha faible, theta élevé

Le modèle résultant est fonctionnel (chargeable par MLClassifier) mais
les prédictions ne sont valides que pour des tests de développement.
"""

import sys
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.feature_eng import extract_all_features, get_feature_names
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
import joblib

FS            = 250
EPOCH_SAMPLES = 1000
N_PER_CLASS   = 300
RNG           = np.random.default_rng(42)


def _make_epoch(state: int, rng) -> np.ndarray:
    t = np.linspace(0, 4, EPOCH_SAMPLES, endpoint=False)
    phases = rng.uniform(0, 2 * np.pi, 5)

    if state == 0:  # concentration — alpha dominant
        sig = (
            1.8 * np.sin(2 * np.pi * 10 * t + phases[0])   # alpha fort
            + 0.6 * np.sin(2 * np.pi * 11 * t + phases[1])  # alpha large
            + 0.5 * np.sin(2 * np.pi * 18 * t + phases[2])  # beta modéré
            + 0.2 * np.sin(2 * np.pi * 6 * t  + phases[3])  # theta faible
            + 0.25 * rng.standard_normal(EPOCH_SAMPLES)
        )
    else:            # stress — beta dominant, theta élevé
        sig = (
            0.3 * np.sin(2 * np.pi * 10 * t + phases[0])   # alpha faible
            + 1.6 * np.sin(2 * np.pi * 22 * t + phases[1])  # beta fort
            + 0.9 * np.sin(2 * np.pi * 6 * t  + phases[2])  # theta fort
            + 0.4 * np.sin(2 * np.pi * 28 * t + phases[3])  # beta haut
            + 0.5 * rng.standard_normal(EPOCH_SAMPLES)
        )

    # Z-score (identique au pipeline temps réel)
    sig = (sig - sig.mean()) / (sig.std() + 1e-12)
    return sig.astype(np.float64)


def main():
    print("=" * 60)
    print("NeuroCap — Génération modèle LightGBM synthétique")
    print(f"Projet : {PROJECT_ROOT}")
    print("=" * 60)

    # ── Génération des epochs ─────────────────────────────────────
    print(f"\nGénération de {2 * N_PER_CLASS} epochs...")
    epochs = [_make_epoch(0, RNG) for _ in range(N_PER_CLASS)] + \
             [_make_epoch(1, RNG) for _ in range(N_PER_CLASS)]
    labels = [0] * N_PER_CLASS + [1] * N_PER_CLASS

    # ── Extraction des features ───────────────────────────────────
    print("Extraction des features...")
    feature_rows = []
    for i, epoch in enumerate(epochs):
        feats = extract_all_features(epoch)
        feature_rows.append(list(feats.values()))
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(epochs)}")

    feat_names = get_feature_names()
    X = np.array(feature_rows, dtype=np.float64)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    y = np.array(labels)
    print(f"Matrice features : {X.shape}  ({len(feat_names)} features)")

    # ── Entraînement ──────────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Entraînement LightGBM...")
    model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        verbose=-1,
        force_col_wise=True,
    )
    model.fit(X_scaled, y)

    # ── Sauvegarde ────────────────────────────────────────────────
    MODEL_DIR = PROJECT_ROOT / "models" / "baseline_FeatEng" / "baseline_models"
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_path  = MODEL_DIR / "LightGBM_concentration_vs_stress.joblib"
    scaler_path = MODEL_DIR / "LightGBM_scaler.joblib"

    joblib.dump(model,  model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n[OK] Modele  : {model_path}")
    print(f"[OK] Scaler  : {scaler_path}")

    # ── Vérification rapide ───────────────────────────────────────
    print("\nVérification (3 exemples) :")
    proba = model.predict_proba(X_scaled[:3])
    states = ["concentration", "stress"]
    for i, p in enumerate(proba):
        conf  = max(p)
        state = states[np.argmax(p)] if conf >= 0.60 else "uncertain"
        true  = states[y[i]]
        print(f"  [{i}] P(conc)={p[0]:.2%}  P(stress)={p[1]:.2%}"
              f"  → {state}  (vérité: {true})")

    print("\n[OK] Termine — relancez uvicorn pour charger le modele.")


if __name__ == "__main__":
    main()
