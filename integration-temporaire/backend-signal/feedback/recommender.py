"""
NeuroCap EEG — Moteur de recommandation adaptatif v2.0
=======================================================
Corrections appliquées suite à évaluation experte :

1. Vecteurs cibles EEG→contenu basés sur littérature validée
   (Thaut 1999, Sammler 2007, Valdez & Mehrabian 1994)
2. Fenêtre delta EEG = 32s minimum (Birbaumer et al. 1999)
3. Buffer état EEG = 28s (Makeig et al. 1999)
4. Cold start epsilon-greedy (5 premières séances)
5. Prior Thompson informé par features statiques
6. Habituation threshold par type de média
   (Grill-Spector & Malach 2001)
7. Niveau adaptatif coloriage (pas seulement seuils fixes)
8. Rapport IA généré en arrière-plan (non bloquant)

Architecture 3 couches :
  Couche 1 : Content-Based Filtering cosine similarity
             Adomavicius & Tuzhilin 2005, Lops et al. 2011
  Couche 2 : Thompson Sampling bandit contextuel
             Chapelle & Li 2011 NeurIPS
  Couche 3 : Claude API rapport post-seance
             Bickmore & Picard 2005 TOCHI

PFE Ingenierie Biomedicale · Oumama SENDADI · ENSAM Rabat
"""

import json
import time
import random
import asyncio
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime

# ─── Chemins ──────────────────────────────────────────────────────────────────
# feedback/recommender.py est dans integration-temporaire/backend-signal/feedback/
# Les fichiers metadata sont dans <project_root>/Feedback METADATA/
BASE_DIR     = Path(__file__).parent
METADATA_DIR = BASE_DIR.parent.parent.parent / "Feedback METADATA"
MERGED_CSV   = METADATA_DIR / "merged_features.csv"
MAPPING_JSON = METADATA_DIR / "mapping.json"
HISTORY_JSON = METADATA_DIR / "session_history.json"
WEIGHTS_JSON = METADATA_DIR / "item_weights.json"

# ─── Parametres systeme ────────────────────────────────────────────────────────

# CORRECTION 3 — Buffer etat EEG = 28s (Makeig et al. 1999)
STATE_CHANGE_THRESHOLD = 7   # 7 epoques x 4s = 28s

# CORRECTION 2 — Fenetre delta EEG = 32s (Birbaumer et al. 1999)
DELTA_WINDOW_EPOCHS = 8   # 8 x 4s = 32s

# CORRECTION 4 — Cold start : exploration pendant N seances
EXPLORATION_SESSIONS = 5

# CORRECTION 6 — Habituation threshold par type (Grill-Spector & Malach 2001)
HABITUATION_THRESHOLD = {
    "image": 2,
    "audio": 3,
    "video": 2,
    "game":  1,
}

ITEM_MIN_DURATION = {"audio": 120, "image": 30, "video": 45, "game": 120}
ITEM_MAX_DURATION = {"audio": 300, "image": 60, "video": 120, "game": 600}

# ─── Features par type ────────────────────────────────────────────────────────
FEATURE_COLS = {
    "audio": [
        "tempo_bpm", "rms_mean", "zcr_mean", "spec_centroid_mean",
        "spectral_flux", "harm_perc_ratio", "spectral_stationarity",
        "mfcc1_mean", "mfcc2_mean", "mfcc3_mean",
    ],
    "image": [
        "brightness_global", "contrast_rms", "saturation_mean",
        "edge_density", "glcm_homogeneity", "symmetry_h",
        "hue_mean", "chroma_mean",
    ],
    "video": [
        "optical_flow_mean", "temporal_energy_var", "scene_change_rate",
        "motion_regularity", "spatial_freq_hf_ratio", "brightness_mean",
    ],
}

# ─── CORRECTION 1 — Vecteurs cibles valides par la litterature ───────────────
#
# Thaut et al. 1999 — Neural Entrainment : 60-75 BPM -> alpha up
# Sammler et al. 2007 — harmonicite -> relaxation
# Valdez & Mehrabian 1994 — luminosite -> valence, saturation -> arousal
# Berman et al. 2014 — complexite visuelle -> arousal
# PMC6841664 — contrast + homogeneity correles EEG frontal
#
EEG_STATE_TARGETS = {
    "stress": {
        "audio": {
            "tempo_bpm":             0.15,
            "rms_mean":              0.25,
            "zcr_mean":              0.10,
            "spec_centroid_mean":    0.20,
            "spectral_flux":         0.10,
            "harm_perc_ratio":       0.85,
            "spectral_stationarity": 0.80,
            "mfcc1_mean":            0.30,
            "mfcc2_mean":            0.40,
            "mfcc3_mean":            0.35,
        },
        "image": {
            "brightness_global": 0.70,
            "contrast_rms":      0.20,
            "saturation_mean":   0.35,
            "edge_density":      0.15,
            "glcm_homogeneity":  0.80,
            "symmetry_h":        0.75,
            "hue_mean":          0.55,
            "chroma_mean":       0.40,
        },
        "video": {
            "optical_flow_mean":     0.10,
            "temporal_energy_var":   0.10,
            "scene_change_rate":     0.05,
            "motion_regularity":     0.85,
            "spatial_freq_hf_ratio": 0.65,
            "brightness_mean":       0.65,
        },
    },
    "focus": {
        "audio": {
            "tempo_bpm":             0.55,
            "rms_mean":              0.50,
            "zcr_mean":              0.45,
            "spec_centroid_mean":    0.55,
            "spectral_flux":         0.50,
            "harm_perc_ratio":       0.55,
            "spectral_stationarity": 0.45,
            "mfcc1_mean":            0.55,
            "mfcc2_mean":            0.50,
            "mfcc3_mean":            0.52,
        },
        "image": {
            "brightness_global": 0.55,
            "contrast_rms":      0.55,
            "saturation_mean":   0.60,
            "edge_density":      0.55,
            "glcm_homogeneity":  0.45,
            "symmetry_h":        0.50,
            "hue_mean":          0.45,
            "chroma_mean":       0.55,
        },
        "video": {
            "optical_flow_mean":     0.50,
            "temporal_energy_var":   0.50,
            "scene_change_rate":     0.35,
            "motion_regularity":     0.55,
            "spatial_freq_hf_ratio": 0.45,
            "brightness_mean":       0.55,
        },
    },
    "neutral": {
        "audio": {
            "tempo_bpm":             0.35,
            "rms_mean":              0.40,
            "zcr_mean":              0.30,
            "spec_centroid_mean":    0.40,
            "spectral_flux":         0.30,
            "harm_perc_ratio":       0.65,
            "spectral_stationarity": 0.60,
            "mfcc1_mean":            0.42,
            "mfcc2_mean":            0.45,
            "mfcc3_mean":            0.43,
        },
        "image": {
            "brightness_global": 0.60,
            "contrast_rms":      0.38,
            "saturation_mean":   0.45,
            "edge_density":      0.35,
            "glcm_homogeneity":  0.62,
            "symmetry_h":        0.60,
            "hue_mean":          0.50,
            "chroma_mean":       0.47,
        },
        "video": {
            "optical_flow_mean":     0.30,
            "temporal_energy_var":   0.28,
            "scene_change_rate":     0.15,
            "motion_regularity":     0.70,
            "spatial_freq_hf_ratio": 0.55,
            "brightness_mean":       0.60,
        },
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def normalize_df(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    result = df.copy()
    for col in [c for c in cols if c in df.columns]:
        mn, mx = df[col].min(), df[col].max()
        result[col] = (df[col] - mn) / (mx - mn) if mx > mn else 0.5
    return result


def get_target_vector(eeg_state: str, media_type: str) -> np.ndarray:
    """Vecteur cible base sur litterature validee. CORRECTION 1."""
    targets = EEG_STATE_TARGETS.get(eeg_state, EEG_STATE_TARGETS["neutral"])
    mt      = targets.get(media_type, {})
    return np.array([mt.get(c, 0.5) for c in FEATURE_COLS.get(media_type, [])])


# ══════════════════════════════════════════════════════════════════════════════
# BUFFER EEG — CORRECTIONS 2 + 3
# ══════════════════════════════════════════════════════════════════════════════

class EEGBuffer:
    """
    Buffer circulaire pour lissage temporel du signal EEG.
    CORRECTION 2 : fenetre delta = 32s (Birbaumer et al. 1999)
    CORRECTION 3 : etat stable sur 28s (Makeig et al. 1999)
    """

    def __init__(self, max_epochs: int = 20):
        self.buffer     = []
        self.max_epochs = max_epochs

    def push(self, features: dict, state: str):
        self.buffer.append({"features": features.copy(), "state": state})
        if len(self.buffer) > self.max_epochs:
            self.buffer.pop(0)

    def get_stable_state(self, window: int = STATE_CHANGE_THRESHOLD) -> str:
        """Etat stable si N dernieres epoques identiques. N = 7 = 28s."""
        recent = self.buffer[-window:] if len(self.buffer) >= window else self.buffer
        states = [e["state"] for e in recent]
        if len(set(states)) == 1:
            return states[-1]
        return max(set(states), key=states.count)

    def compute_delta(self, feature: str, window: int = DELTA_WINDOW_EPOCHS) -> float:
        """Delta EEG sur fenetre 32s. CORRECTION 2."""
        if len(self.buffer) < window:
            return 0.0
        half   = window // 2
        before = np.mean([e["features"].get(feature, 0) for e in self.buffer[:half]])
        after  = np.mean([e["features"].get(feature, 0) for e in self.buffer[-half:]])
        return float(after - before)

    def get_mean_features(self, window: int = 4) -> dict:
        recent = self.buffer[-window:] if len(self.buffer) >= window else self.buffer
        if not recent:
            return {}
        keys = recent[0]["features"].keys()
        return {k: float(np.mean([e["features"].get(k, 0) for e in recent])) for k in keys}


# ══════════════════════════════════════════════════════════════════════════════
# THOMPSON SAMPLING AVEC PRIOR INFORME — CORRECTION 5
# ══════════════════════════════════════════════════════════════════════════════

class ThompsonSampler:
    """
    Bandit contextuel avec prior informe par features statiques.
    CORRECTION 5. Chapelle & Li 2011 NeurIPS.
    """

    def __init__(self, weights: dict, df: pd.DataFrame):
        self.weights = weights
        self.df      = df

    def _get_prior(self, filename: str, eeg_state: str) -> dict:
        """Prior base sur similarite cosinus item-cible. CORRECTION 5."""
        if self.df.empty:
            return {"alpha": 1.2, "beta": 1.0}
        row = self.df[self.df["filename"] == filename]
        if row.empty:
            return {"alpha": 1.2, "beta": 1.0}

        media_type = row.iloc[0].get("type", "audio")
        cols       = FEATURE_COLS.get(media_type, [])
        available  = [c for c in cols if c in row.columns]
        if not available:
            return {"alpha": 1.2, "beta": 1.0}

        target = get_target_vector(eeg_state, media_type)
        item_v = row.iloc[0][available].fillna(0).values
        n      = min(len(target), len(item_v))
        sim    = cosine_similarity(target[:n], item_v[:n]) if n > 0 else 0.5

        return {
            "alpha": 1.0 + sim * 0.5,
            "beta":  1.0 + (1 - sim) * 0.3,
        }

    def sample(self, filename: str, eeg_state: str = "stress") -> float:
        if filename not in self.weights:
            self.weights[filename] = self._get_prior(filename, eeg_state)
        w = self.weights[filename]
        return float(np.random.beta(max(0.1, w["alpha"]), max(0.1, w["beta"])))

    def update(self, filename: str, success: bool):
        if filename not in self.weights:
            self.weights[filename] = {"alpha": 1.2, "beta": 1.0}
        key = "alpha" if success else "beta"
        self.weights[filename][key] += 1.0

    def update_sam(self, filename: str, sam_score: int):
        if filename not in self.weights:
            self.weights[filename] = {"alpha": 1.2, "beta": 1.0}
        if sam_score >= 4:
            self.weights[filename]["alpha"] += (sam_score - 3) * 0.5
        elif sam_score <= 2:
            self.weights[filename]["beta"]  += (3 - sam_score) * 0.5


# ══════════════════════════════════════════════════════════════════════════════
# MOTEUR DE RECOMMANDATION
# ══════════════════════════════════════════════════════════════════════════════

class RecommendationEngine:

    def __init__(self):
        print("[RecommendationEngine] Chargement...")

        self.df = pd.read_csv(MERGED_CSV) if MERGED_CSV.exists() else pd.DataFrame()
        if not self.df.empty:
            print(f"  {len(self.df)} items charges")
            self._normalize()
        else:
            self.df_norm = pd.DataFrame()
            print("  ATTENTION : merged_features.csv introuvable")

        self.mapping = {}
        if MAPPING_JSON.exists():
            with open(MAPPING_JSON, encoding="utf-8") as f:
                self.mapping = json.load(f)

        self.weights = {}
        if WEIGHTS_JSON.exists():
            try:
                with open(WEIGHTS_JSON, encoding="utf-8") as f:
                    self.weights = json.load(f)
            except Exception:
                pass

        self.sampler    = ThompsonSampler(self.weights, self.df)
        self.n_sessions = self._count_sessions()

        mode = "exploration" if self.n_sessions < EXPLORATION_SESSIONS else "exploitation"
        print(f"  Sessions : {self.n_sessions} | Mode : {mode}")
        print("[RecommendationEngine] Pret")

    def _normalize(self):
        frames = []
        for t in ["audio", "image", "video"]:
            sub = self.df[self.df["type"] == t].copy()
            if not sub.empty:
                frames.append(normalize_df(sub, FEATURE_COLS.get(t, [])))
        self.df_norm = pd.concat(frames, ignore_index=True) if frames else self.df.copy()

    def _count_sessions(self) -> int:
        if not HISTORY_JSON.exists():
            return 0
        try:
            with open(HISTORY_JSON, encoding="utf-8") as f:
                return len(json.load(f))
        except Exception:
            return 0

    def select(
        self,
        eeg_state:  str,
        eeg_features: dict,
        media_type: str,
        exclude:    list = None,
    ) -> Optional[str]:
        """
        Selectionne le meilleur item.
        CORRECTION 4 : epsilon-greedy pour cold start.
        CORRECTION 1 : vecteur cible base sur litterature.
        CORRECTION 5 : prior Thompson informe.
        """
        exclude = exclude or []

        # CORRECTION 4 — Cold start
        if self.n_sessions < EXPLORATION_SESSIONS:
            epsilon = 1.0 - (self.n_sessions / EXPLORATION_SESSIONS)
            if random.random() < epsilon:
                return self._random_select(eeg_state, media_type, exclude)

        if self.df_norm.empty:
            return self._random_select(eeg_state, media_type, exclude)

        condition_map = {"stress": "relax", "focus": "focus", "neutral": "transition"}
        condition     = condition_map.get(eeg_state, "relax")

        candidates = self.df_norm[
            (self.df_norm["type"]      == media_type) &
            (self.df_norm["condition"] == condition)  &
            (~self.df_norm["filename"].isin(exclude))
        ].copy()

        if candidates.empty:
            candidates = self.df_norm[
                (self.df_norm["type"]      == media_type) &
                (self.df_norm["condition"] == condition)
            ].copy()

        if candidates.empty:
            return self._random_select(eeg_state, media_type, exclude)

        # CORRECTION 1 — Vecteur cible litterature
        target   = get_target_vector(eeg_state, media_type)
        cols     = FEATURE_COLS.get(media_type, [])
        avail    = [c for c in cols if c in candidates.columns]

        if avail:
            matrix = candidates[avail].fillna(0).values
            n      = min(len(target), matrix.shape[1])
            sims   = np.array([cosine_similarity(target[:n], row[:n]) for row in matrix])
        else:
            sims = np.ones(len(candidates))

        # CORRECTION 5 — Thompson Sampling avec prior informe
        ts = np.array([
            self.sampler.sample(f, eeg_state)
            for f in candidates["filename"].values
        ])

        scores = sims * ts
        return candidates.iloc[int(np.argmax(scores))]["filename"]

    def select_game(
        self,
        eeg_state:       str,
        eeg_features:    dict,
        session_history: list,
    ) -> dict:
        """
        Selectionne jeu et niveau adaptatif.
        CORRECTION 7 : niveau adaptatif meme pour le coloriage.
        Clement et al. 2015.
        """
        stress_idx = eeg_features.get("stress_idx", 1.5)
        engagement = eeg_features.get("engagement", 0.4)

        if eeg_state == "stress":
            # CORRECTION 7 — Adaptatif coloriage
            col_history = [h for h in session_history if h.get("game_type") == "coloriage"]
            motif_order = ["mandala", "nature", "geometrique"]

            if not col_history:
                idx = 2 if stress_idx < 2.0 else 1 if stress_idx < 3.0 else 0
            else:
                last  = col_history[-1]
                idx   = motif_order.index(last.get("subtype", "mandala")) if last.get("subtype") in motif_order else 0
                compl = last.get("completion_rate", 0.5)
                if compl > 0.8 and last.get("delta_alpha", 0) > 0.03:
                    idx = min(2, idx + 1)
                elif compl < 0.3:
                    idx = max(0, idx - 1)

            motif_type = motif_order[idx]
            files = (self.mapping.get("stress", {})
                     .get("game", {}).get("coloriage", {}).get(motif_type, []))
            return {"game_type": "coloriage", "subtype": motif_type,
                    "filename": random.choice(files) if files else None, "level": None}

        elif eeg_state == "focus":
            game_type = self._select_focus_game(session_history)
            level     = self._adaptive_level(game_type, session_history, engagement)
            files     = (self.mapping.get("focus", {}).get("game", {}).get(game_type, []))
            lvl_files = [f for f in files if f"NIV{level}_" in f] or files
            return {"game_type": game_type, "subtype": None,
                    "filename": random.choice(lvl_files) if lvl_files else None,
                    "level": level}

        else:  # neutral
            alpha = eeg_features.get("rel_alpha", 0.25)
            beta  = eeg_features.get("rel_beta",  0.35)
            ratio = alpha / (beta + 0.001)
            ptype = "sliding" if ratio > 1.2 else "jigsaw" if ratio < 0.8 else "tangram"
            files = self.mapping.get("neutral", {}).get("game", {}).get("puzzle", [])
            tfiles = [f for f in files if ptype[:3].upper() in f] or files
            return {"game_type": "puzzle", "subtype": ptype,
                    "filename": random.choice(tfiles) if tfiles else None, "level": 1}

    def _select_focus_game(self, history: list) -> str:
        game_types = ["sudoku", "memoire", "calcul", "enigmes"]
        if not history:
            return random.choice(game_types)
        best_type, best_score = None, -1
        for gt in game_types:
            scores    = [h.get("delta_alpha", 0) for h in history if h.get("game_type") == gt]
            successes = sum(1 for s in scores if s > 0.05)
            failures  = len(scores) - successes
            sampled   = float(np.random.beta(max(0.1, successes+1), max(0.1, failures+1)))
            if sampled > best_score:
                best_score = sampled
                best_type  = gt
        return best_type or "sudoku"

    def _adaptive_level(self, game_type: str, history: list, engagement: float) -> int:
        """Zone Proximale de Developpement. Vygotsky 1978, Clement et al. 2015."""
        th = [h for h in history if h.get("game_type") == game_type]
        if not th:
            return 3 if engagement > 0.6 else 2 if engagement > 0.4 else 1
        last = th[-1]
        lv   = last.get("level", 1)
        er   = last.get("error_rate", 0.5)
        db   = last.get("delta_beta", 0)
        if er < 0.2 and db > 0.05:
            return min(5, lv + 1)
        elif er > 0.6 or db < -0.1:
            return max(1, lv - 1)
        return lv

    def _random_select(self, eeg_state: str, media_type: str, exclude: list) -> Optional[str]:
        cm    = {"stress": "relax", "focus": "focus", "neutral": "transition"}
        state = cm.get(eeg_state, eeg_state)
        files = self.mapping.get(state, {}).get(media_type, [])
        if not files:
            files = self.mapping.get(eeg_state, {}).get(media_type, [])
        avail = [f for f in files if f not in exclude]
        return random.choice(avail) if avail else None

    def update_weights(self, filename: str, delta_alpha: float,
                       delta_beta: float, sam_score: Optional[int] = None):
        self.sampler.update(filename, delta_alpha > 0.05 and delta_beta < -0.05)
        if sam_score is not None:
            self.sampler.update_sam(filename, sam_score)
        self._save_weights()

    def _save_weights(self):
        WEIGHTS_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(WEIGHTS_JSON, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION
# Sitaram et al. 2017 — Closed-loop Brain Training
# Zander & Kothe 2011 — BCI passif adaptatif
# ══════════════════════════════════════════════════════════════════════════════

class Session:

    def __init__(self, engine: RecommendationEngine, objective: str = "stress_reduction",
                 duration_min: int = 30, allowed_types: list = None, user_id: str = "default"):
        self.engine        = engine
        self.objective     = objective
        self.duration_min  = duration_min
        self.allowed_types = allowed_types or ["audio", "image", "video", "game"]
        self.user_id       = user_id

        self.start_time   = time.time()
        self.current_item = None
        self.current_type = None
        self.item_start   = None
        self.item_history = []
        self.eeg_buffer   = EEGBuffer(max_epochs=20)
        self.last_state   = "neutral"
        self.last_feats   = {}
        self.eeg_baseline = None
        self.skip_count   = 0

        print(f"[Session] Demarree — objectif={objective} duree={duration_min}min")

    def set_baseline(self, eeg_features: dict):
        self.eeg_baseline = eeg_features.copy()
        print(f"[Session] Baseline — alpha={eeg_features.get('rel_alpha',0):.3f} "
              f"beta={eeg_features.get('rel_beta',0):.3f}")

    def on_epoch(self, eeg_state: str, eeg_features: dict, forced_type: str = None) -> Optional[dict]:
        """
        Appele toutes les 4s par server_final.py.
        CORRECTION 3 : etat stable detecte sur 28s.
        CORRECTION 2 : delta EEG sur 32s.
        """
        self.eeg_buffer.push(eeg_features, eeg_state)
        self.last_state = eeg_state
        self.last_feats = eeg_features

        stable_state = self.eeg_buffer.get_stable_state(STATE_CHANGE_THRESHOLD)

        item_elapsed = time.time() - self.item_start if self.item_start else 999
        min_dur      = ITEM_MIN_DURATION.get(self.current_type, 30)
        max_dur      = ITEM_MAX_DURATION.get(self.current_type, 300)

        # forced_type déclenche toujours un changement si le type actuel diffère
        type_mismatch = forced_type and self.current_type != forced_type

        should_change = (
            self.current_item is None or
            type_mismatch or
            item_elapsed > max_dur or
            (stable_state != self._last_item_state() and item_elapsed > min_dur)
        )

        return self._select_and_play(stable_state, eeg_features, forced_type=forced_type) if should_change else None

    def _last_item_state(self) -> str:
        return self.item_history[-1].get("eeg_state", "neutral") if self.item_history else "neutral"

    def _select_and_play(self, eeg_state: str, eeg_features: dict, forced_type: str = None) -> dict:
        # Enregistre fin item precedent avec delta EEG sur 32s (CORRECTION 2)
        if self.current_item and self.item_history:
            da = self.eeg_buffer.compute_delta("rel_alpha", DELTA_WINDOW_EPOCHS)
            db = self.eeg_buffer.compute_delta("rel_beta",  DELTA_WINDOW_EPOCHS)
            self.item_history[-1].update({
                "delta_alpha": round(da, 4),
                "delta_beta":  round(db, 4),
                "efficace":    bool(da > 0.05 and db < -0.05),
                "duration_s":  round(time.time() - self.item_start, 1),
            })
            self.engine.update_weights(self.current_item, da, db)
            print(f"[Session] Item fin — da={da:+.3f} db={db:+.3f} "
                  f"eff={self.item_history[-1]['efficace']}")

        media_type = forced_type if (forced_type and forced_type in self.allowed_types) else self._choose_media_type(eeg_state)
        played     = [h["filename"] for h in self.item_history[-10:]]
        smooth_eeg = self.eeg_buffer.get_mean_features(4)

        if media_type == "game":
            game_info = self.engine.select_game(eeg_state, eeg_features, self.item_history)
            filename  = game_info.get("filename")
            game_data = game_info
        else:
            filename  = self.engine.select(eeg_state, smooth_eeg, media_type, exclude=played)
            game_data = None

        self.current_item = filename
        self.current_type = media_type
        self.item_start   = time.time()

        self.item_history.append({
            "filename":   filename,
            "type":       media_type,
            "eeg_state":  eeg_state,
            "eeg_before": smooth_eeg,
            "started_at": datetime.now().isoformat(),
            "game":       game_data,
        })

        action = {"action": "play", "type": media_type, "filename": filename, "game": game_data}
        print(f"[Session] Nouvel item -> {media_type} : {filename}")
        return action

    def _choose_media_type(self, eeg_state: str) -> str:
        """CORRECTION 6 — Habituation threshold par type. Grill-Spector & Malach 2001."""
        available = self.allowed_types.copy()

        for media_type, threshold in HABITUATION_THRESHOLD.items():
            if media_type not in available:
                continue
            recent = [h["type"] for h in self.item_history[-threshold:]]
            if len(recent) >= threshold and all(t == media_type for t in recent):
                available = [t for t in available if t != media_type]

        if not available:
            available = self.allowed_types

        # Ponderations selon objectif
        if eeg_state == "stress" and "game" in available:
            weights = [3 if t == "game" else 1 for t in available]
        elif eeg_state == "focus" and "game" in available:
            weights = [2 if t == "game" else 1 for t in available]
        else:
            weights = [1] * len(available)

        total, r, cumul = sum(weights), random.uniform(0, sum(weights)), 0
        for t, w in zip(available, weights):
            cumul += w
            if r <= cumul:
                return t
        return available[0]

    def on_skip(self, forced_type: str = None) -> Optional[dict]:
        self.skip_count += 1
        if self.current_item and self.item_history:
            self.item_history[-1]["skipped"] = True
            self.engine.sampler.update(self.current_item, success=False)
            self.engine._save_weights()
        print(f"[Session] Skip #{self.skip_count} — {self.current_item}")
        return self._select_and_play(self.last_state, self.last_feats, forced_type=forced_type)

    def on_sam_rating(self, score: int):
        if self.item_history and self.current_item:
            self.item_history[-1]["sam_score"] = score
            self.engine.sampler.update_sam(self.current_item, score)
            self.engine._save_weights()
        print(f"[Session] SAM = {score}/5")

    async def end_session(self) -> dict:
        """Termine la seance. CORRECTION 8 : rapport IA non bloquant."""
        duration    = round((time.time() - self.start_time) / 60, 1)
        delta_alpha = self.eeg_buffer.compute_delta("rel_alpha", DELTA_WINDOW_EPOCHS)
        delta_beta  = self.eeg_buffer.compute_delta("rel_beta",  DELTA_WINDOW_EPOCHS)
        efficaces   = sum(1 for h in self.item_history if h.get("efficace"))

        result = {
            "user_id":            self.user_id,
            "objective":          self.objective,
            "duration_min":       duration,
            "items_played":       len(self.item_history),
            "items_efficaces":    efficaces,
            "skip_count":         self.skip_count,
            "delta_alpha_global": round(delta_alpha, 4),
            "delta_beta_global":  round(delta_beta,  4),
            "session_success":    bool(delta_alpha > 0.05 and delta_beta < -0.05),
            "history":            self.item_history,
            "timestamp":          datetime.now().isoformat(),
            "rapport_ia":         None,
        }

        self._save_history(result)
        self.engine.n_sessions += 1

        print(f"[Session] Terminee — {duration}min "
              f"da={delta_alpha:+.3f} db={delta_beta:+.3f} "
              f"eff={efficaces}/{len(self.item_history)}")

        return result

    async def generate_report_async(self, result: dict, broadcast_fn=None):
        """
        CORRECTION 8 — Rapport IA en arriere-plan non bloquant.
        Appel : asyncio.create_task(session.generate_report_async(result, ws_broadcast))
        """
        try:
            import aiohttp
            items_str = "\n".join([
                f"- {h['type']} {h.get('filename','?')[:25]} "
                f"da={h.get('delta_alpha',0):+.3f} "
                f"db={h.get('delta_beta',0):+.3f} "
                f"{'OK' if h.get('efficace') else '--'}"
                for h in result["history"][:6]
            ])

            prompt = f"""Tu es un systeme de neurofeedback adaptatif NeuroCap EEG.
Rapport de seance — bienveillant, scientifiquement precis, 150 mots max.

Donnees EEG :
- Objectif  : {result['objective']}
- Duree     : {result['duration_min']} min
- Delta alpha global : {result['delta_alpha_global']:+.4f} (cible > +0.05)
- Delta beta global  : {result['delta_beta_global']:+.4f} (cible < -0.05)
- Items efficaces    : {result['items_efficaces']} / {result['items_played']}

Items joues :
{items_str}

3 parties : 1) Resume objectif EEG 2) Ce qui a fonctionne 3) Recommandation prochaine seance.
Repondre directement en francais, sans titres markdown."""

            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model":      "claude-sonnet-4-20250514",
                        "max_tokens": 400,
                        "messages":   [{"role": "user", "content": prompt}],
                    },
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data   = await resp.json()
                    report = data["content"][0]["text"]

        except Exception as e:
            da     = result["delta_alpha_global"]
            report = (
                f"Seance de {result['duration_min']} min terminee. "
                f"Alpha {'en hausse' if da > 0 else 'stable'} (da={da:+.3f}). "
                f"{result['items_efficaces']}/{result['items_played']} items efficaces. "
                f"Le systeme a mis a jour ses recommandations."
            )
            print(f"[Session] Rapport IA erreur : {e}")

        result["rapport_ia"] = report

        if broadcast_fn:
            await broadcast_fn({"type": "session_report", "data": result})

        return report

    def _save_history(self, result: dict):
        history = []
        if HISTORY_JSON.exists():
            try:
                with open(HISTORY_JSON, encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass
        clean = {k: v for k, v in result.items() if k != "rapport_ia"}
        history.append(clean)
        if len(history) > 100:
            history = history[-100:]
        HISTORY_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_JSON, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION server_final.py
# ══════════════════════════════════════════════════════════════════════════════
"""
from recommender import RecommendationEngine, Session

engine  = RecommendationEngine()
session = None

# WebSocket START_SESSION
session = Session(engine, objective="stress_reduction", duration_min=30)
session.set_baseline(current_eeg_features)

# Dans RealTimeProcessor.process_epoch() — toutes les 4s
action = session.on_epoch(eeg_state, epoch_features)
if action:
    await broadcast(action)

# WebSocket SKIP
action = session.on_skip()
await broadcast(action)

# WebSocket SAM_RATING
session.on_sam_rating(score=4)

# WebSocket END_SESSION
result = await session.end_session()
await broadcast({"type": "session_end", "data": result})
asyncio.create_task(session.generate_report_async(result, broadcast))
"""

if __name__ == "__main__":
    print("Test RecommendationEngine v2.0...")
    engine = RecommendationEngine()

    eeg_test = {
        "rel_alpha": 0.18, "rel_beta": 0.72, "rel_theta": 0.20,
        "rel_delta": 0.25, "rel_gamma": 0.15,
        "stress_idx": 2.8, "engagement": 0.35,
        "alpha_beta": 0.25, "theta_beta": 0.28,
        "hjorth_activity": 14.2, "hjorth_mobility": 0.45,
        "spectral_entropy": 0.61,
    }

    for t in ["audio", "image", "video"]:
        item = engine.select("stress", eeg_test, t)
        print(f"  stress → {t} : {item}")

    game = engine.select_game("stress", eeg_test, [])
    print(f"  stress → game : {game}")

    engine.update_weights("AUD_REL_001.mp3", 0.08, -0.12, sam_score=4)
    print("  update weights OK")

    buf = EEGBuffer()
    for _ in range(10):
        buf.push(eeg_test, "stress")
    print(f"  stable state : {buf.get_stable_state()}")
    print(f"  delta alpha  : {buf.compute_delta('rel_alpha'):+.4f}")
