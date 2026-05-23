# protocol/neurofeedback_protocol.py
"""
Protocole Neurofeedback 15 séances — Mou et al. (2024)
=======================================================
Paliers adaptatifs alpha :
  P1  S1-3   : facteur 85-90%  , Δ ±1.0 µV²/Hz
  P2  S4-7   : facteur 95-110% , Δ ±0.5 µV²/Hz
  P3  S8-12  : facteur 110-125%, Δ ±0.3 µV²/Hz
  P4  S13-15 : facteur 125-140%, Δ ±0.2 µV²/Hz

Structure séance (~35-40 min) :
  baseline (2 min yeux fermés) → IAPF (1 min yeux ouverts)
  → 5 blocs × 3 min neurofeedback → pause 20 s inter-bloc
  → repos final (3 min)

Seuil journalier :
  seuil_j = (0.70 × P_alpha_hist + 0.30 × P_alpha_j) × facteur_palier

Adaptation inter-blocs (Mou 2024) :
  taux_succes > 60% → seuil += delta
  taux_succes < 40% → seuil -= delta
  sinon            → inchangé
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("Protocol")

# ─── Chemins persistance ─────────────────────────────────────────────────────
DATA_DIR = Path("protocol_data")
DATA_DIR.mkdir(exist_ok=True)


# ─── Constantes protocole ─────────────────────────────────────────────────────
PALIERS = {
    "P1": {"sessions": range(1,  4),  "factor_min": 0.85, "factor_max": 0.90, "delta": 1.0},
    "P2": {"sessions": range(4,  8),  "factor_min": 0.95, "factor_max": 1.10, "delta": 0.5},
    "P3": {"sessions": range(8,  13), "factor_min": 1.10, "factor_max": 1.25, "delta": 0.3},
    "P4": {"sessions": range(13, 16), "factor_min": 1.25, "factor_max": 1.40, "delta": 0.2},
}

N_BLOCS          = 5
BLOC_DURATION_S  = 180   # 3 min
BASELINE_S       = 120   # 2 min yeux fermés
IAPF_S           = 60    # 1 min yeux ouverts
INTERBOC_S       = 20    # pause inter-bloc
REST_FINAL_S     = 180   # 3 min
SUCCESS_THRESHOLD_HIGH = 0.60
SUCCESS_THRESHOLD_LOW  = 0.40


# ─── Helpers palier ───────────────────────────────────────────────────────────
def get_palier_for_session(session_n: int) -> tuple[str, dict]:
    for name, p in PALIERS.items():
        if session_n in p["sessions"]:
            return name, p
    # Au-delà de 15 séances : reste en P4
    return "P4", PALIERS["P4"]


def palier_factor(session_n: int) -> float:
    """Retourne le facteur central du palier (moyenne min+max)."""
    _, p = get_palier_for_session(session_n)
    return (p["factor_min"] + p["factor_max"]) / 2


def palier_delta(session_n: int) -> float:
    _, p = get_palier_for_session(session_n)
    return p["delta"]


# ─── Calcul du seuil ─────────────────────────────────────────────────────────
def compute_seuil_initial(
    p_alpha_hist: float,
    p_alpha_jour: float,
    session_n: int,
) -> float:
    """
    Seuil de départ de la séance.
    p_alpha_hist : puissance alpha médiane des séances précédentes (µV²/Hz)
    p_alpha_jour : puissance alpha mesurée pendant la baseline de la séance (µV²/Hz)
    """
    weighted = 0.70 * p_alpha_hist + 0.30 * p_alpha_jour
    factor   = palier_factor(session_n)
    return round(weighted * factor, 4)


def adapt_seuil_inter_blocs(
    current_seuil: float,
    taux_succes: float,
    session_n: int,
) -> tuple[float, str]:
    """
    Adaptation du seuil entre deux blocs.
    taux_succes : fraction [0-1] du temps passé au-dessus du seuil dans le bloc précédent.
    Retourne (nouveau_seuil, direction : 'up' | 'down' | 'stable').
    """
    delta = palier_delta(session_n)
    if taux_succes > SUCCESS_THRESHOLD_HIGH:
        return round(current_seuil + delta, 4), "up"
    elif taux_succes < SUCCESS_THRESHOLD_LOW:
        return round(max(0.1, current_seuil - delta), 4), "down"
    return round(current_seuil, 4), "stable"


def compute_taux_succes(samples_above: int, total_samples: int) -> float:
    if total_samples == 0:
        return 0.0
    return round(samples_above / total_samples, 4)


# ─── Modèles Pydantic ─────────────────────────────────────────────────────────
class BaselinePayload(BaseModel):
    user_id: str
    session_n: int
    p_alpha_baseline: float      # puissance alpha baseline de la séance (yeux fermés)
    iapf_hz: Optional[float] = None  # fréquence de pic alpha (Hz)


class BlocEndPayload(BaseModel):
    user_id: str
    session_n: int
    bloc_n: int                  # 1-5
    samples_above: int
    total_samples: int
    current_seuil: float
    mean_alpha: Optional[float] = None  # puissance alpha moyenne du bloc


class SessionEndPayload(BaseModel):
    user_id: str
    session_n: int
    notes: Optional[str] = ""


class FeedbackPayload(BaseModel):
    user_id: str
    session_n: int
    bloc_n: int
    rating: int                  # 1-5


# ─── Persistance JSON ─────────────────────────────────────────────────────────
def _user_path(user_id: str) -> Path:
    safe = "".join(c for c in user_id if c.isalnum() or c in "-_")
    return DATA_DIR / f"{safe}.json"


def load_user_program(user_id: str) -> dict:
    p = _user_path(user_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "sessions": [],
        "p_alpha_hist": None,   # médiane historique — mis à jour en fin de séance
    }


def save_user_program(user_id: str, data: dict) -> None:
    _user_path(user_id).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _get_or_create_session(program: dict, session_n: int) -> dict:
    for s in program["sessions"]:
        if s["session_n"] == session_n:
            return s
    palier_name, _ = get_palier_for_session(session_n)
    s = {
        "session_n":   session_n,
        "palier":      palier_name,
        "started_at":  datetime.now().isoformat(),
        "ended_at":    None,
        "baseline":    None,   # p_alpha de la baseline
        "iapf_hz":     None,
        "seuil_initial": None,
        "blocs":       [],
        "taux_succes_global": None,
        "notes":       "",
    }
    program["sessions"].append(s)
    return s


# ─── Router FastAPI ───────────────────────────────────────────────────────────
router = APIRouter(prefix="/api/protocol", tags=["protocol"])


@router.get("/user/{user_id}")
def get_user_program(user_id: str):
    """Retourne l'ensemble du programme d'un utilisateur."""
    prog = load_user_program(user_id)
    completed = [s for s in prog["sessions"] if s.get("ended_at")]
    next_n    = max((s["session_n"] for s in completed), default=0) + 1
    palier_name, palier_info = get_palier_for_session(min(next_n, 15))
    return {
        "user_id":       user_id,
        "sessions_done": len(completed),
        "next_session":  next_n,
        "palier":        palier_name,
        "palier_info":   {k: v for k, v in palier_info.items() if k != "sessions"},
        "p_alpha_hist":  prog.get("p_alpha_hist"),
        "history":       prog["sessions"],
    }


@router.post("/session/baseline")
def record_baseline(payload: BaselinePayload):
    """
    Enregistre la baseline de début de séance et calcule le seuil initial.
    Doit être appelé après les 2 min de baseline (yeux fermés) + 1 min IAPF.
    """
    prog = load_user_program(payload.user_id)
    sess = _get_or_create_session(prog, payload.session_n)

    p_hist = prog.get("p_alpha_hist") or payload.p_alpha_baseline
    seuil  = compute_seuil_initial(p_hist, payload.p_alpha_baseline, payload.session_n)

    sess["baseline"]      = payload.p_alpha_baseline
    sess["iapf_hz"]       = payload.iapf_hz
    sess["seuil_initial"] = seuil
    # Le premier bloc commence avec le seuil initial
    sess["seuil_current"] = seuil

    palier_name, _ = get_palier_for_session(payload.session_n)
    sess["palier"] = palier_name

    save_user_program(payload.user_id, prog)
    logger.info(f"[Protocol] user={payload.user_id} s={payload.session_n} seuil={seuil:.3f}")
    return {
        "session_n":      payload.session_n,
        "palier":         palier_name,
        "p_alpha_hist":   p_hist,
        "p_alpha_jour":   payload.p_alpha_baseline,
        "seuil_initial":  seuil,
        "delta":          palier_delta(payload.session_n),
        "n_blocs":        N_BLOCS,
        "bloc_duration_s": BLOC_DURATION_S,
    }


@router.post("/bloc/end")
def end_bloc(payload: BlocEndPayload):
    """
    Enregistre les résultats d'un bloc et calcule le seuil du bloc suivant.
    """
    prog = load_user_program(payload.user_id)
    sess = _get_or_create_session(prog, payload.session_n)

    taux = compute_taux_succes(payload.samples_above, payload.total_samples)
    new_seuil, direction = adapt_seuil_inter_blocs(
        payload.current_seuil, taux, payload.session_n
    )

    bloc_record = {
        "bloc_n":        payload.bloc_n,
        "samples_above": payload.samples_above,
        "total_samples": payload.total_samples,
        "taux_succes":   taux,
        "seuil_used":    payload.current_seuil,
        "seuil_next":    new_seuil,
        "direction":     direction,
        "mean_alpha":    payload.mean_alpha,
        "timestamp":     datetime.now().isoformat(),
    }

    # Remplace si bloc déjà enregistré (re-envoi)
    existing = [b for b in sess["blocs"] if b["bloc_n"] != payload.bloc_n]
    existing.append(bloc_record)
    sess["blocs"] = sorted(existing, key=lambda b: b["bloc_n"])
    sess["seuil_current"] = new_seuil

    save_user_program(payload.user_id, prog)
    logger.info(f"[Protocol] bloc {payload.bloc_n} taux={taux:.0%} seuil {payload.current_seuil:.2f}→{new_seuil:.2f} ({direction})")

    return {
        "bloc_n":        payload.bloc_n,
        "taux_succes":   taux,
        "seuil_used":    payload.current_seuil,
        "seuil_next":    new_seuil,
        "direction":     direction,
        "is_last_bloc":  payload.bloc_n >= N_BLOCS,
        "feedback_msg":  _feedback_message(taux, direction),
    }


@router.post("/session/end")
def end_session(payload: SessionEndPayload):
    """
    Clôture la séance, calcule le taux global, met à jour p_alpha_hist.
    """
    prog = load_user_program(payload.user_id)
    sess = _get_or_create_session(prog, payload.session_n)

    blocs = sess.get("blocs", [])
    if blocs:
        global_taux = round(sum(b["taux_succes"] for b in blocs) / len(blocs), 4)
        mean_alpha_all = [b["mean_alpha"] for b in blocs if b.get("mean_alpha") is not None]
        mean_alpha_sess = round(sum(mean_alpha_all) / len(mean_alpha_all), 4) if mean_alpha_all else None
    else:
        global_taux    = 0.0
        mean_alpha_sess = None

    sess["taux_succes_global"] = global_taux
    sess["mean_alpha_session"] = mean_alpha_sess
    sess["notes"]    = payload.notes
    sess["ended_at"] = datetime.now().isoformat()

    # Mise à jour de la médiane historique p_alpha_hist
    alpha_values = [
        s.get("baseline") for s in prog["sessions"]
        if s.get("baseline") is not None
    ]
    if alpha_values:
        sorted_vals = sorted(alpha_values)
        n = len(sorted_vals)
        mid = n // 2
        prog["p_alpha_hist"] = (
            sorted_vals[mid] if n % 2 else
            round((sorted_vals[mid - 1] + sorted_vals[mid]) / 2, 4)
        )

    save_user_program(payload.user_id, prog)

    # Calcul du bilan rapide
    bilan = _generate_bilan(prog, payload.session_n)

    logger.info(f"[Protocol] fin séance {payload.session_n} user={payload.user_id} taux_global={global_taux:.0%}")
    return {
        "session_n":           payload.session_n,
        "taux_succes_global":  global_taux,
        "p_alpha_hist_updated": prog["p_alpha_hist"],
        "bilan": bilan,
    }


@router.get("/session/{user_id}/{session_n}")
def get_session(user_id: str, session_n: int):
    """Détail d'une séance spécifique."""
    prog = load_user_program(user_id)
    for s in prog["sessions"]:
        if s["session_n"] == session_n:
            return s
    raise HTTPException(404, detail=f"Séance {session_n} introuvable pour {user_id}")


@router.get("/paliers")
def get_paliers():
    """Décrit les 4 paliers du protocole."""
    return {
        name: {
            "sessions": f"{min(p['sessions'])}-{max(p['sessions'])}",
            "factor_min_pct": round(p["factor_min"] * 100),
            "factor_max_pct": round(p["factor_max"] * 100),
            "delta": p["delta"],
        }
        for name, p in PALIERS.items()
    }


@router.get("/constants")
def get_constants():
    """Retourne toutes les constantes du protocole (pour le frontend)."""
    return {
        "n_blocs":           N_BLOCS,
        "bloc_duration_s":   BLOC_DURATION_S,
        "baseline_s":        BASELINE_S,
        "iapf_s":            IAPF_S,
        "interbloc_s":       INTERBOC_S,
        "rest_final_s":      REST_FINAL_S,
        "success_high":      SUCCESS_THRESHOLD_HIGH,
        "success_low":       SUCCESS_THRESHOLD_LOW,
        "total_sessions":    15,
    }


@router.post("/feedback")
def submit_feedback(payload: FeedbackPayload):
    """Enregistre la note subjective d'un bloc (1-5)."""
    prog = load_user_program(payload.user_id)
    sess = _get_or_create_session(prog, payload.session_n)
    for b in sess["blocs"]:
        if b["bloc_n"] == payload.bloc_n:
            b["subjective_rating"] = payload.rating
            break
    save_user_program(payload.user_id, prog)
    return {"ok": True}


# ─── Helpers internes ─────────────────────────────────────────────────────────
def _feedback_message(taux: float, direction: str) -> str:
    if direction == "up":
        return f"Excellent ! {taux:.0%} de succès → seuil augmenté pour le prochain bloc."
    elif direction == "down":
        return f"Seuil réduit pour le prochain bloc ({taux:.0%} de succès)."
    return f"Bon équilibre ({taux:.0%}) — seuil maintenu."


def _generate_bilan(prog: dict, session_n: int) -> dict:
    completed = [s for s in prog["sessions"] if s.get("ended_at")]
    if not completed:
        return {}

    taux_list = [s["taux_succes_global"] for s in completed if s.get("taux_succes_global") is not None]
    trend     = "stable"
    if len(taux_list) >= 3:
        recent = taux_list[-3:]
        if recent[-1] > recent[0] + 0.05:
            trend = "improving"
        elif recent[-1] < recent[0] - 0.05:
            trend = "declining"

    alpha_vals = [s.get("mean_alpha_session") for s in completed if s.get("mean_alpha_session")]
    alpha_trend = None
    if len(alpha_vals) >= 2:
        alpha_trend = round(alpha_vals[-1] - alpha_vals[0], 4)

    sessions_left = max(0, 15 - session_n)
    palier_name, _ = get_palier_for_session(session_n)

    return {
        "sessions_done":    len(completed),
        "sessions_left":    sessions_left,
        "current_palier":   palier_name,
        "avg_taux_succes":  round(sum(taux_list) / len(taux_list), 3) if taux_list else None,
        "trend":            trend,
        "alpha_delta":      alpha_trend,
        "message":          _bilan_message(trend, taux_list, sessions_left),
    }


def _bilan_message(trend: str, taux_list: list, sessions_left: int) -> str:
    avg = sum(taux_list) / len(taux_list) if taux_list else 0
    base = f"Moyenne de succès : {avg:.0%}. "
    if trend == "improving":
        base += "Progression constante détectée — continuez sur cette lancée."
    elif trend == "declining":
        base += "Légère baisse récente — envisagez une pause ou réduisez la difficulté."
    else:
        base += "Progression stable."
    if sessions_left > 0:
        base += f" Il reste {sessions_left} séance(s) au protocole."
    else:
        base += " Protocole de 15 séances complété."
    return base
