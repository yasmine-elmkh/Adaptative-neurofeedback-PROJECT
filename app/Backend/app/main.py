"""
NeuroCap — Point d'entrée FastAPI
===================================
WebSocket EEG temps réel + routers REST.
Toutes les opérations DB passent par le client Supabase (plus SQLAlchemy).

v2.1 : pipeline EEG temps réel (ESP32 → DSP → WS /ws/eeg)
v2.2 : suppression de la session live adaptative (remplacée par EEG live + analyse fichier)
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

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
from app.routes.eeg import router as eeg_router
from app.routes.media import router as media_router
from app.routes.feedback import router as feedback_router
from app.routes.eeg_feedback import router as eeg_feedback_router
from app.routes.protocol    import router as protocol_router
from app.routes.recommendations import router as recommendations_router
from app.services.eeg.eeg_pipeline import pipeline as eeg_pipeline
from app.services.finetune.scheduler import start_scheduler, stop_scheduler

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

    # Démarrer le pipeline EEG temps réel (TCPReceiver + WifiManager + DSP)
    await eeg_pipeline.start()
    logger.info("Pipeline EEG démarré")

    # Démarrer le scheduler de fine-tuning automatique
    try:
        start_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler fine-tuning non démarré (APScheduler manquant?): {e}")

    yield

    await eeg_pipeline.stop()
    logger.info("NeuroCap arrêt.")

    try:
        stop_scheduler()
    except Exception:
        pass


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="NeuroCap API",
    description="Système intelligent de neurofeedback EEG adaptatif (CdC 2026)",
    version="2.2.0",
    lifespan=lifespan,
    redirect_slashes=False,
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


# ── Handler 500 — log le traceback complet ───────────────────────────────────

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "500 Internal Server Error: %s %s — %s",
        request.method, request.url.path, exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erreur interne : {type(exc).__name__}: {exc}"},
    )


# ── Routers API ───────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(profile_router)
app.include_router(admin_router)
app.include_router(assistant_router)
app.include_router(therapist_router)
app.include_router(eeg_router)          # /api/eeg/*
app.include_router(media_router)        # /api/media/*
app.include_router(feedback_router)     # /api/feedback/*
app.include_router(eeg_feedback_router) # /api/eeg-feedback/*
app.include_router(protocol_router)     # /api/protocol/*
app.include_router(recommendations_router)  # /api/sessions/*/media-* + /api/patients/* + /api/eeg-reports/* + /api/finetuning/*


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["Système"])
@app.get("/api/health", tags=["Système"])
async def health():
    return {"status": "ok", "version": "2.2.0"}


# ── WebSocket EEG Temps Réel ──────────────────────────────────────────────────
#
# Chemin : ws://host/ws/eeg?token=<access_token>
# Diffuse : type="eeg" (62 Hz), type="epoch" (toutes 4s),
#           type="electrode" (heartbeat), type="esp32_status"
#
# Le token JWT est optionnel (lecture publique du signal).
# Pour lier le signal à une session, le frontend envoie :
#   {"command": "SET_SESSION", "session_id": "<uuid>"}
# ─────────────────────────────────────────────────────────────────────────────

@app.websocket("/ws/eeg")
async def ws_eeg(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: AsyncClient = Depends(get_db),
):
    ws_mgr = eeg_pipeline.ws_manager
    if ws_mgr is None:
        await websocket.close(code=1011, reason="Pipeline EEG non initialisé")
        return

    await ws_mgr.connect(websocket)

    st = eeg_pipeline.state

    # Message d'initialisation
    try:
        await websocket.send_text(json.dumps({
            "type":              "init",
            "esp32_connected":   st.esp32_connected,
            "esp32_ip":          st.esp32_ip,
            "wifi_configured":   st.wifi_configured,
            "esp32_ap_detected": st.esp32_ap_detected,
            "baseline_ok":       eeg_pipeline.rt.epocher.pipeline.has_baseline(),
            **eeg_pipeline.electrode_mon.status_detail,
        }))
    except Exception as e:
        logger.warning(f"[WS/EEG] Init failed: {e}")
        ws_mgr.disconnect(websocket)
        return

    await ws_mgr.register(websocket)

    try:
        while True:
            try:
                raw = await websocket.receive_text()
                try:
                    cmd = json.loads(raw).get("command", "")
                    if cmd == "FINALISE_BASELINE":
                        ok = eeg_pipeline.rt.epocher.pipeline.finalise_baseline()
                        await websocket.send_text(json.dumps({
                            "type": "baseline_ready", "success": ok,
                        }))
                    elif cmd == "START_REC":
                        path = eeg_pipeline.start_recording()
                        await websocket.send_text(json.dumps({
                            "type": "rec_started", "file": path,
                        }))
                    elif cmd == "STOP_REC":
                        path = eeg_pipeline.stop_recording()
                        await websocket.send_text(json.dumps({
                            "type": "rec_stopped", "file": path,
                        }))
                    elif cmd == "ANALYZE_NOW":
                        rm = eeg_pipeline.rt.raw_metrics()
                        es = eeg_pipeline.electrode_mon.status_detail
                        await websocket.send_text(json.dumps({
                            "type":           "report",
                            "esp32_ip":       st.esp32_ip,
                            "esp32_connected": st.esp32_connected,
                            "epoch_total":    eeg_pipeline.rt.epocher.n_total,
                            "epoch_accepted": eeg_pipeline.rt.epocher.n_accepted,
                            "epoch_rejected": eeg_pipeline.rt.epocher.n_rejected,
                            "cal_progress":   eeg_pipeline.rt.epocher.pipeline.cal_progress,
                            "baseline_ok":    eeg_pipeline.rt.epocher.pipeline.has_baseline(),
                            **es, **rm,
                        }, default=str))
                except Exception:
                    pass
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        ws_mgr.disconnect(websocket)

