"""
NeuroCap — Routes Feedback Session
POST /api/feedback/sessions          → créer une session feedback
POST /api/feedback/recommend         → prochain média selon état EEG
POST /api/feedback/submit            → soumettre évaluation utilisateur
POST /api/feedback/skip              → skipper média (pénalité)
POST /api/feedback/sam               → note SAM 1-5
POST /api/feedback/end               → clore session + rapport Claude
WS   /feedback/ws/{session_id}       → stream temps réel (play/end commands)
"""

import asyncio
import json
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from pydantic import BaseModel, Field
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user, get_token_user_id
from app.services.ai_report import generate_session_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

# ── In-memory WebSocket registry ──────────────────────────────────────────────
_session_sockets: dict[str, list[WebSocket]] = {}


async def _broadcast(session_id: str, payload: dict):
    sockets = _session_sockets.get(session_id, [])
    dead = []
    for ws in sockets:
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(ws)
    for ws in dead:
        sockets.remove(ws)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SessionStart(BaseModel):
    objective: str = "concentration"
    eeg_snapshot: Optional[dict] = None


class RecommendRequest(BaseModel):
    session_id: str
    eeg_state:   str            = "neutral"
    media_type:  Optional[str]  = None
    # Features du classificateur EEG (live ou snapshot fichier)
    confidence:  Optional[float] = None   # 0–1, confiance LightGBM
    features:    Optional[dict]  = None   # rel_alpha, rel_beta, theta_beta, engagement…


class SubmitFeedback(BaseModel):
    session_id: str
    media_id: Optional[str] = None
    liked: Optional[bool] = None
    sam_score: Optional[int] = Field(None, ge=1, le=5)
    note_concentration: Optional[int] = Field(None, ge=1, le=5)
    note_stress: Optional[int] = Field(None, ge=1, le=5)
    delta_alpha: Optional[float] = None
    delta_beta: Optional[float] = None


class SkipRequest(BaseModel):
    session_id: str
    media_id: Optional[str] = None


class SamRequest(BaseModel):
    session_id: str
    score: int = Field(..., ge=1, le=5)


class EndRequest(BaseModel):
    session_id: str
    items_played: int = 0
    items_efficaces: int = 0
    delta_alpha_global: float = 0.0
    delta_beta_global: float = 0.0
    media_played: list = []


class MediaGuideRequest(BaseModel):
    session_id: str
    media_id:   str
    eeg_state:  str           = "neutral"
    features:   Optional[dict] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pick_media(
    medias: list,
    eeg_state: str,
    media_type: Optional[str],
    confidence: Optional[float] = None,
    features: Optional[dict] = None,
) -> Optional[dict]:
    """
    Sélection de médias basée sur :
      1. Type de média (si forcé)
      2. État EEG cible — pondéré par la confiance du classificateur
      3. Features EEG (TBR, rel_alpha) pour affiner entre relaxation et focus
      4. Thompson sampling sur les poids appris (alpha/bêta bayésiens)
    """
    if not medias:
        return None

    # 1. Filtrer par type si demandé
    pool = [m for m in medias if not media_type or m.get("type") == media_type]
    if not pool:
        pool = list(medias)

    # 2. Ciblage par état EEG
    # Si confiance < 60 % → ne pas imposer l'état, utiliser tout le pool
    use_state = eeg_state if (confidence is None or confidence >= 0.60) else "neutral"
    targeted = [m for m in pool if m.get("eeg_target_state") in (use_state, "all")]
    if targeted:
        pool = targeted

    # 3. Affinage par features EEG (uniquement si disponibles)
    if features:
        tbr       = features.get("theta_beta", 1.0) or 1.0   # Theta/Beta ratio
        rel_alpha = features.get("rel_alpha",   0.3) or 0.3   # Puissance alpha relative
        rel_beta  = features.get("rel_beta",    0.2) or 0.2   # Puissance bêta relative

        # TBR élevé (>2.0) + alpha faible → déficit attentionnel → médias focus
        if tbr > 2.0 and rel_alpha < 0.25 and use_state != "stress":
            focus = [m for m in pool if m.get("eeg_target_state") == "focus"]
            if focus:
                pool = focus

        # Alpha très élevé (>0.45) → relaxation profonde → médias calme/neutre
        elif rel_alpha > 0.45 and use_state != "stress":
            calm = [m for m in pool if m.get("eeg_target_state") in ("neutral", "all")]
            if calm:
                pool = calm

        # Bêta élevé (>0.35) + état stress → médias relaxants prioritaires
        elif rel_beta > 0.35 and use_state == "stress":
            relax = [m for m in pool if m.get("eeg_target_state") in ("stress", "neutral")]
            if relax:
                pool = relax

    # 4. Thompson sampling sur les poids bayésiens appris
    def thompson_score(m):
        a = m.get("item_weights_alpha", 1.0) or 1.0
        b = m.get("item_weights_beta",  1.0) or 1.0
        return random.betavariate(a, b)

    return max(pool, key=thompson_score)


async def _update_weights(db: AsyncClient, media_id: str, success: bool):
    """Met à jour les poids Thompson d'un média."""
    try:
        resp = await db.table("medias").select("item_weights_alpha,item_weights_beta").eq("id", media_id).execute()
        if not resp.data:
            return
        m = resp.data[0]
        alpha = (m.get("item_weights_alpha") or 1.0)
        beta  = (m.get("item_weights_beta")  or 1.0)
        if success:
            alpha += 1.0
        else:
            beta += 1.0
        await db.table("medias").update({"item_weights_alpha": alpha, "item_weights_beta": beta}).eq("id", media_id).execute()
    except Exception as e:
        logger.warning("update_weights error: %s", e)


# ── Endpoints ─────────────────────────────────────────────────────────────────

def _phase_for_session(n: int) -> str:
    if n <= 3:   return "phase1"
    if n <= 10:  return "phase2"
    return "phase3"

def _palier_label(n: int) -> str:
    return f"P{max(1, min(4, n))}"

PALIER_FOR_SESSION = {
    **{n: 1 for n in range(1, 4)},
    **{n: 2 for n in range(4, 8)},
    **{n: 3 for n in range(8, 13)},
    **{n: 4 for n in range(13, 16)},
}


@router.get("/status")
async def get_protocol_status(
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne le statut actuel du protocole pour l'utilisateur connecté."""
    try:
        resp = await (
            db.table("feedback_sessions")
            .select("session_number,phase,palier,status")
            .eq("patient_id", current_user["id"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception:
        resp = type("R", (), {"data": []})()

    completed = 0
    try:
        cnt = await (
            db.table("feedback_sessions")
            .select("id")
            .eq("patient_id", current_user["id"])
            .eq("status", "completed")
            .execute()
        )
        completed = len(cnt.data or [])
    except Exception:
        pass

    if not resp.data:
        return {
            "session_number": 1,
            "phase": "phase1",
            "palier": 1,
            "palier_label": "P1",
            "completed": 0,
            "remaining": 15,
        }

    last = resp.data[0]
    last_num  = last.get("session_number") or 0
    next_num  = min(last_num + 1, 16)
    palier_raw = last.get("palier") or PALIER_FOR_SESSION.get(next_num, 1)
    palier_int = int(str(palier_raw).replace("P", "")) if isinstance(palier_raw, str) else int(palier_raw)

    return {
        "session_number": next_num,
        "phase": _phase_for_session(next_num),
        "palier": palier_int,
        "palier_label": _palier_label(palier_int),
        "completed": completed,
        "remaining": max(0, 15 - completed),
    }


@router.post("/sessions", status_code=201)
async def start_feedback_session(
    data: SessionStart,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Crée une nouvelle session de feedback adaptative."""
    # Récupérer le numéro de séance suivant
    resp = await db.table("feedback_sessions").select("id").eq("patient_id", current_user["id"]).execute()
    session_num = len(resp.data) + 1

    # Déterminer la phase selon le numéro de séance
    if session_num <= 3:
        phase = "phase1"
    elif session_num <= 10:
        phase = "phase2"
    else:
        phase = "phase3"

    # Lire le palier depuis eeg_profiles
    palier = 1
    try:
        p = await db.table("eeg_profiles").select("palier").eq("user_id", current_user["id"]).execute()
        if p.data:
            pal_str = p.data[0].get("palier", "P1") or "P1"
            palier = int(pal_str.replace("P", "")) if pal_str.startswith("P") else 1
    except Exception:
        pass

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    new_session = {
        "id": session_id,
        "patient_id": current_user["id"],
        "session_number": session_num,
        "phase": phase,
        "palier": palier,
        "objective": data.objective,
        "status": "running",
        "eeg_snapshot": data.eeg_snapshot,
        "started_at": now,
        "created_at": now,
    }
    await db.table("feedback_sessions").insert(new_session).execute()

    return {
        "session_id": session_id,
        "session_number": session_num,
        "phase": phase,
        "palier": palier,
        "objective": data.objective,
    }


@router.post("/recommend")
async def recommend_media(
    data: RecommendRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne le prochain média adapté à l'état EEG."""
    resp = await db.table("medias").select("*").execute()
    medias = resp.data or []

    # ── Adapter la sélection selon le dernier score de concentration ──
    forced_type = data.media_type
    forced_state = data.eeg_state
    try:
        last_inter = await (
            db.table("media_interactions")
            .select("note_concentration, liked, efficace, media_id")
            .eq("patient_id", current_user["id"])
            .order("created_at", desc=True)
            .limit(3)
            .execute()
        )
        if last_inter.data:
            last = last_inter.data[0]
            note_conc = last.get("note_concentration")
            # Concentration faible (≤2) → forcer média de type image à haute stimulation
            if note_conc is not None and note_conc <= 2:
                forced_state = "focus"
                # Prioriser images et jeux cognitifs
                if not forced_type:
                    forced_type = "image"
            # Concentration forte (≥4) → maintenir le cap, élargir le pool
            elif note_conc is not None and note_conc >= 4:
                forced_state = data.eeg_state  # garder l'état EEG réel
    except Exception:
        pass

    media = _pick_media(
        medias,
        forced_state,
        forced_type,
        confidence=data.confidence,
        features=data.features,
    )
    if not media:
        raise HTTPException(status_code=404, detail="Aucun média disponible")

    # Log événement (avec features et confiance pour analyse ultérieure)
    event_data = {
        "media_id":   media["id"],
        "eeg_state":  data.eeg_state,
        "media_type": media["type"],
    }
    if data.confidence is not None:
        event_data["confidence"] = round(data.confidence, 3)
    if data.features:
        event_data["tbr"]       = round(data.features.get("theta_beta", 0) or 0, 3)
        event_data["rel_alpha"] = round(data.features.get("rel_alpha",  0) or 0, 3)
        event_data["rel_beta"]  = round(data.features.get("rel_beta",   0) or 0, 3)

    await db.table("feedback_session_events").insert({
        "id":         str(uuid.uuid4()),
        "session_id": data.session_id,
        "event_type": "media_recommended",
        "event_data": event_data,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    }).execute()

    # Broadcast WebSocket
    media_url = media.get("url_cloudinary") or media.get("url") or ""
    await _broadcast(data.session_id, {
        "action": "play",
        "media": {
            "id":              media["id"],
            "type":            media["type"],
            "url":             media_url,
            "url_cloudinary":  media.get("url_cloudinary"),
            "filename":        media.get("filename", ""),
            "preset":          "Naturel",
            "game_prefix":     media.get("game_prefix"),
            "difficulty_level": media.get("difficulty_level", 1),
            "duration_seconds": media.get("duration_seconds"),
        },
    })

    return {"action": "play", "media": media}


@router.post("/submit")
async def submit_feedback(
    data: SubmitFeedback,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Enregistre l'évaluation de l'utilisateur et met à jour les poids Thompson."""
    now = datetime.now(timezone.utc).isoformat()

    # Calculer si efficace (delta EEG)
    efficace = False
    if data.delta_alpha is not None and data.delta_beta is not None:
        efficace = data.delta_alpha > 0.05 and data.delta_beta < -0.05

    if data.media_id:
        # Sauvegarder interaction
        await db.table("media_interactions").insert({
            "id": str(uuid.uuid4()),
            "session_id": data.session_id,
            "patient_id": current_user["id"],
            "media_id": data.media_id,
            "liked": data.liked,
            "sam_score": data.sam_score,
            "note_concentration": data.note_concentration,
            "note_stress": data.note_stress,
            "delta_alpha": data.delta_alpha,
            "delta_beta": data.delta_beta,
            "efficace": efficace,
            "was_skipped": False,
            "created_at": now,
        }).execute()

        # Mettre à jour poids Thompson
        success = data.liked is True or efficace
        await _update_weights(db, data.media_id, success)

        # SAM score influence les poids
        if data.sam_score is not None:
            if data.sam_score >= 4:
                await _update_weights(db, data.media_id, True)
            elif data.sam_score <= 2:
                await _update_weights(db, data.media_id, False)

    return {"status": "ok"}


@router.post("/skip")
async def skip_media(
    data: SkipRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Pénalise un média skipé (beta += 1)."""
    if data.media_id:
        await _update_weights(db, data.media_id, False)
        await db.table("media_interactions").insert({
            "id": str(uuid.uuid4()),
            "session_id": data.session_id,
            "patient_id": current_user["id"],
            "media_id": data.media_id,
            "was_skipped": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

    await db.table("feedback_session_events").insert({
        "id": str(uuid.uuid4()),
        "session_id": data.session_id,
        "event_type": "media_skipped",
        "event_data": {"media_id": data.media_id},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).execute()

    return {"status": "skipped"}


@router.post("/sam")
async def save_sam(
    data: SamRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    await db.table("feedback_session_events").insert({
        "id": str(uuid.uuid4()),
        "session_id": data.session_id,
        "event_type": "sam_rating",
        "event_data": {"score": data.score},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).execute()
    return {"status": "ok"}


@router.post("/end")
async def end_feedback_session(
    data: EndRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Clôt la session, génère le rapport Claude API, sauvegarde dans Supabase
    et broadcast le rapport via WebSocket.
    """
    now = datetime.now(timezone.utc).isoformat()
    session_success = data.delta_alpha_global > 0.05 and data.delta_beta_global < -0.05

    # Récupérer la session pour avoir le contexte
    s_resp = await db.table("feedback_sessions").select("*").eq("id", data.session_id).execute()
    session = s_resp.data[0] if s_resp.data else {}

    # Profil patient
    patient_profile = {"profile_type": "B", "palier": 1, "session_number": session.get("session_number", 1)}
    try:
        p = await db.table("eeg_profiles").select("profile_type,palier").eq("user_id", current_user["id"]).execute()
        if p.data:
            pal = p.data[0].get("palier", "P1") or "P1"
            patient_profile = {
                "profile_type": p.data[0].get("profile_type", "B"),
                "palier": int(pal.replace("P", "")) if pal.startswith("P") else 1,
                "session_number": session.get("session_number", 1),
            }
    except Exception:
        pass

    # Calculer score (0-100 basé sur efficacité et succès)
    score = 0
    if data.items_played > 0:
        eff_rate = data.items_efficaces / data.items_played
        score = int(eff_rate * 70 + (30 if session_success else 0))

    # Mise à jour session dans Supabase
    await db.table("feedback_sessions").update({
        "status": "completed",
        "completed_at": now,
        "score": score,
        "delta_alpha": data.delta_alpha_global,
        "delta_beta": data.delta_beta_global,
        "session_success": session_success,
        "items_played": data.items_played,
        "items_efficaces": data.items_efficaces,
    }).eq("id", data.session_id).execute()

    metrics = {
        "session_id": data.session_id,
        "items_played": data.items_played,
        "items_efficaces": data.items_efficaces,
        "delta_alpha_global": data.delta_alpha_global,
        "delta_beta_global": data.delta_beta_global,
        "session_success": session_success,
        "score": score,
    }

    # Générer rapport Claude en tâche asynchrone (non bloquant)
    asyncio.create_task(_generate_and_broadcast_report(
        db=db,
        session_id=data.session_id,
        session_data={
            **metrics,
            "objective": session.get("objective", "concentration"),
            "duration_min": session.get("duration_minutes", 0),
            "patient_profile": patient_profile,
            "media_played": data.media_played,
        },
    ))

    return {"status": "ok", "metrics": metrics, "rapport_ia": None}


async def _generate_and_broadcast_report(db: AsyncClient, session_id: str, session_data: dict):
    """Génère le rapport Claude et le broadcast + sauvegarde dans Supabase."""
    report_text = await generate_session_report(session_data)

    if report_text:
        try:
            await db.table("feedback_sessions").update({"report_text": report_text}).eq("id", session_id).execute()
        except Exception:
            pass

    await _broadcast(session_id, {
        "action": "session_ended",
        "report": report_text,
        "metrics": session_data,
    })


@router.post("/media-guide")
async def get_media_guide(
    data: MediaGuideRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Génère un guide d'interaction IA pour le média en cours.
    Tient compte : propriétés du média, état EEG, historique des préférences.
    """
    # 1. Récupérer le média
    m_resp = await db.table("medias").select("*").eq("id", data.media_id).maybe_single().execute()
    if not m_resp.data:
        raise HTTPException(status_code=404, detail="Média introuvable")
    media = m_resp.data

    # 2. Récupérer l'historique des interactions récentes (pour personnalisation)
    liked_history = []
    try:
        hist = await (
            db.table("media_interactions")
            .select("liked, efficace, note_concentration, note_stress")
            .eq("patient_id", current_user["id"])
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
        liked_history = hist.data or []
    except Exception:
        pass

    # 3. Générer le guide via Claude Haiku (rapide, ~200ms)
    from app.services.ai_report import generate_media_guide
    guide = await generate_media_guide(
        media        = media,
        eeg_state    = data.eeg_state,
        eeg_features = data.features,
        liked_history= liked_history,
    )

    # 4. Fallback statique si Claude échoue
    if not guide:
        fallback = {
            "image": "Fixez le centre de l'image et laissez votre regard explorer naturellement les contours. Cette stimulation visuelle favorise la synchronisation des ondes alpha.",
            "audio": "Fermez les yeux et respirez au rythme du son, 4s inspirez — 4s expirez. La musique guide votre cerveau vers un état de cohérence neurale.",
            "video": "Suivez le mouvement principal du regard sans effort. Le flux visuel régulier module vos ondes thêta-alpha.",
            "game":  "Abordez le jeu avec méthode : cherchez d'abord les patterns. La charge cognitive active le cortex préfrontal et renforce la concentration.",
        }
        guide = fallback.get(media.get("type", "image"), fallback["image"])

    return {
        "guide":     guide,
        "media_id":  data.media_id,
        "eeg_state": data.eeg_state,
    }


# ── WebSocket feedback session ─────────────────────────────────────────────────

@router.websocket("/ws/{session_id}")
async def ws_feedback_session(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Query(None),
):
    """
    WebSocket pour la session de feedback.
    Reçoit des commandes du backend (broadcast via _broadcast).
    Permet aussi au frontend d'envoyer des événements.
    """
    await websocket.accept()

    if session_id not in _session_sockets:
        _session_sockets[session_id] = []
    _session_sockets[session_id].append(websocket)

    try:
        while True:
            try:
                raw = await websocket.receive_text()
                try:
                    msg = json.loads(raw)
                    # Broadcaster aux autres clients de la même session
                    await _broadcast(session_id, msg)
                except Exception:
                    pass
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        sockets = _session_sockets.get(session_id, [])
        if websocket in sockets:
            sockets.remove(websocket)
