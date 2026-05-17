"""
NeuroCap — Point d'entrée FastAPI
===================================
WebSocket EEG temps réel + routers REST.
Toutes les opérations DB passent par le client Supabase (plus SQLAlchemy).
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from supabase import AsyncClient

from app.config import get_settings
from app.core.database import get_db, init_db
from app.core.security import get_token_user_id
from app.middleware.security import add_security_middleware
from app.routes.auth import router as auth_router
from app.routes.sessions import router as sessions_router
from app.routes.Profile import router as profile_router
from app.routes.admin import router as admin_router
from app.routes.assistant import router as assistant_router
from app.routes.therapist import router as therapist_router
from app.services.signal_processing import process_epoch
from app.services.classifieur import classifier
from app.services.adaptative_engine import AdaptiveEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NeuroCap démarrage…")
    await init_db()
    logger.info("Base de données initialisée")
    yield
    logger.info("NeuroCap arrêt.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="NeuroCap API",
    description="Système intelligent de neurofeedback EEG adaptatif (CdC 2026)",
    version="2.0.0",
    lifespan=lifespan,
)

add_security_middleware(app)


# ── Handler 422 — log le détail pour faciliter le debug ──────────────────────

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"422 Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# ── Routers API ───────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(profile_router)
app.include_router(admin_router)
app.include_router(assistant_router)
app.include_router(therapist_router)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["Système"])
async def health():
    return {"status": "ok", "version": "2.0.0"}


# ── WebSocket EEG temps réel ──────────────────────────────────────────────────
#
# Chemin : ws://host/ws/session/{session_id}?token=<access_token>
# Le frontend (SessionLive.jsx) s'y connecte via useSessionStore().connect(id)
#
# Protocole :
#   → Client envoie : {"samples": [float, ...]}   (1000 flottants = 4s @ 250Hz)
#     ou              {"action": "pause"|"resume"|"set_feedback_mode:visual"}
#   ← Serveur envoie : WSFrame JSON toutes les ~500ms
#
# Durée max : 40 min = 6 blocs × 3 min + transitions
# ─────────────────────────────────────────────────────────────────────────────

@app.websocket("/ws/session/{session_id}")
async def ws_eeg_session(
    session_id: str,
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: AsyncClient = Depends(get_db),
):
    # ── 1. Authentification par query-param token ──────────────────────────────
    if not token:
        await websocket.close(code=4001, reason="Token manquant")
        return

    user_id = await get_token_user_id(token, db)
    if not user_id:
        await websocket.close(code=4001, reason="Token invalide")
        return

    # ── 2. Vérifier que la session appartient à l'utilisateur ─────────────────
    sess_resp = await (
        db.table("sessions")
        .select("*")
        .eq("id", session_id)
        .eq("user_id", user_id)
        .execute()
    )
    session = sess_resp.data[0] if sess_resp.data else None
    if not session:
        await websocket.close(code=4004, reason="Session introuvable")
        return

    await websocket.accept()
    logger.info(f"WS ouvert — session={session_id} user={user_id}")

    # ── 3. Charger le profil utilisateur pour le moteur adaptatif ─────────────
    profile_resp = await (
        db.table("eeg_profiles")
        .select("current_threshold,palier")
        .eq("user_id", user_id)
        .execute()
    )
    profile = profile_resp.data[0] if profile_resp.data else None
    initial_threshold = float(profile["current_threshold"]) if profile and profile.get("current_threshold") else 0.5
    initial_palier = profile["palier"] if profile and profile.get("palier") else "P1_INITIATION"

    engine = AdaptiveEngine(initial_threshold=initial_threshold, palier=initial_palier)

    # Marquer la session comme "running" dans Supabase
    now_iso = datetime.now(timezone.utc).isoformat()
    await (
        db.table("sessions")
        .update({"status": "running", "started_at": now_iso})
        .eq("id", session_id)
        .execute()
    )

    total_conc, total_stress, epoch_count = 0.0, 0.0, 0
    block_start_time = datetime.now(timezone.utc)
    feedback_mode = session.get("feedback_mode", "visual")
    is_paused = False

    # File d'attente pour les messages entrants du client
    incoming: asyncio.Queue = asyncio.Queue()

    async def _reader():
        """Tâche de fond : lit les messages client et les enfile."""
        try:
            while True:
                raw = await websocket.receive_text()
                await incoming.put(raw)
        except Exception:
            await incoming.put(None)  # signal d'arrêt

    reader_task = asyncio.create_task(_reader())

    try:
        while True:
            # ── Tick 500ms — vider les messages en attente ─────────────────────
            await asyncio.sleep(0.5)

            while not incoming.empty():
                raw = incoming.get_nowait()
                if raw is None:
                    raise WebSocketDisconnect()
                try:
                    msg = json.loads(raw)
                    action = msg.get("action", "")
                    if action == "pause":
                        is_paused = True
                    elif action == "resume":
                        is_paused = False
                    elif action.startswith("set_feedback_mode:"):
                        feedback_mode = action.split(":", 1)[1]
                except Exception:
                    pass

            if is_paused:
                await websocket.send_json({"type": "paused"})
                continue

            # ── Générer / traiter des données EEG ─────────────────────────────
            # En production, les samples arrivent du frontend (ESP32 via BLE/USB).
            # En développement, on génère un epoch synthétique.
            epoch = _demo_epoch()

            # ── Pipeline signal → features spectrales ─────────────────────────
            features = process_epoch(epoch)

            # ── Classification → concentration / stress ────────────────────────
            prediction = classifier.predict(features)

            # ── Moteur adaptatif → seuil + bloc ───────────────────────────────
            adaptive = engine.update(prediction)

            # ── Temps écoulé dans le bloc courant (3 min max) ─────────────────
            now = datetime.now(timezone.utc)
            block_time_sec = (now - block_start_time).total_seconds()
            if block_time_sec >= 180:
                block_start_time = now

            # ── Accumuler les métriques pour le score final ────────────────────
            conc = prediction["concentration_rate"]
            stress = prediction["stress_rate"]
            total_conc += conc
            total_stress += stress
            epoch_count += 1

            # ── Persister l'événement dans Supabase ───────────────────────────
            await (
                db.table("session_events")
                .insert({
                    "id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "concentration_rate": round(conc, 4),
                    "stress_rate": round(stress, 4),
                    "confidence": round(prediction.get("confidence", 0.0), 4),
                    "tbr": round(prediction.get("tbr", 0.0), 4),
                    "ei": round(prediction.get("ei", 0.0), 4),
                    "signal_quality": round(features.get("signal_quality", 0.0), 4),
                    "is_artifact": bool(features.get("is_artifact", False)),
                    "feedback_mode": feedback_mode,
                    "feedback_active": prediction.get("confidence", 0.0) >= 60.0,
                    "block_number": adaptive["block_number"],
                    "created_at": now.isoformat(),
                })
                .execute()
            )

            # ── Trame WebSocket → frontend ─────────────────────────────────────
            frame = {
                "timestamp": now.isoformat(),
                "concentration": round(conc / 100, 4),
                "stress": round(stress / 100, 4),
                "features": {
                    "alpha": round(features.get("powers", {}).get("alpha", 0.0), 4),
                    "theta_beta_ratio": round(prediction.get("tbr", 0.0), 4),
                    "engagement_index": round(prediction.get("ei", 0.0), 4),
                    "iapf": round(prediction.get("iapf", 10.0), 2),
                },
                "threshold": adaptive["threshold"],
                "ewma": round(adaptive["ewma_concentration"] / 100, 4),
                "feedback_command": {
                    "intensity": min(1.0, conc / 100),
                    "is_success": (conc / 100) > adaptive["threshold"],
                },
                "signal_quality": features.get("signal_quality", 0.0),
                "block_number": adaptive["block_number"],
                "block_time_sec": round(block_time_sec, 1),
                "success_rate": round(
                    engine.state.session_total_success
                    / max(1, engine.state.session_total_epochs),
                    4,
                ),
            }
            await websocket.send_json(frame)

    except WebSocketDisconnect:
        logger.info(f"WS fermé normalement — session={session_id}")
    except Exception as exc:
        logger.error(f"WS erreur — session={session_id}: {exc}", exc_info=True)
    finally:
        reader_task.cancel()

        # ── Finaliser la session dans Supabase ─────────────────────────────────
        final = {
            "status": "completed",
            "ended_at": datetime.now(timezone.utc).isoformat(),
        }
        if epoch_count:
            final["avg_concentration"] = round(total_conc / epoch_count, 2)
            final["avg_stress"] = round(total_stress / epoch_count, 2)
            final["score"] = round(engine.state.session_score, 1)
            final["n_blocks"] = engine.state.block_number
            final["recommendations"] = engine.get_recommendations()

        await (
            db.table("sessions")
            .update(final)
            .eq("id", session_id)
            .execute()
        )
        logger.info(f"Session {session_id} terminée — epochs={epoch_count}")


# ── Données EEG de démo (sans matériel) ──────────────────────────────────────

_rng = np.random.default_rng(42)
_t = np.linspace(0, 4, 1000)  # 4s @ 250Hz


def _demo_epoch() -> np.ndarray:
    """
    Génère un epoch EEG synthétique réaliste (Fp2 mono-canal).
    Compose les bandes alpha (10 Hz), theta (6 Hz), beta (20 Hz) avec bruit
    pour simuler le signal AD8232 en l'absence de matériel physique.
    """
    alpha = 10.0 * np.sin(2 * np.pi * 10 * _t + _rng.uniform(0, 2 * np.pi))
    theta = 5.0 * np.sin(2 * np.pi * 6 * _t + _rng.uniform(0, 2 * np.pi))
    beta = 3.0 * np.sin(2 * np.pi * 20 * _t + _rng.uniform(0, 2 * np.pi))
    noise = _rng.normal(0, 2.0, 1000)
    return (alpha + theta + beta + noise).astype(np.float32)
