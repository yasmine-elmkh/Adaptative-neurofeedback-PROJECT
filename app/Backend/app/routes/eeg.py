"""
NeuroCap — Routes EEG Temps Réel
==================================
Préfixe : /api/eeg

REST :
  GET  /status             → état ESP32 + baseline + qualité signal
  GET  /analyze            → rapport DSP détaillé
  POST /baseline/finalise  → calcule les Z-scores individuels
  POST /recording/start
  POST /recording/stop
  GET  /recording/export
  GET  /wifi/networks
  POST /wifi/configure
  POST /wifi/use_saved
  POST /wifi/reset
  POST /analyze_file       → analyse fichier EEG offline (.edf / .csv / .txt)
  POST /report             → sauvegarde rapport EEG (live ou fichier) + notifie thérapeute
  GET  /my-reports         → liste des rapports EEG du patient authentifié

WebSocket (déclaré dans main.py) :
  /ws/eeg                  → flux temps réel (eeg | epoch | electrode | esp32_status)

SQL migration requise (Supabase) :
  CREATE TABLE IF NOT EXISTS eeg_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    therapist_id UUID REFERENCES users(id) ON DELETE SET NULL,
    type TEXT NOT NULL DEFAULT 'live',
    filename TEXT,
    duration_s FLOAT,
    n_epochs_accepted INTEGER DEFAULT 0,
    n_epochs_rejected INTEGER DEFAULT 0,
    dominant_state TEXT,
    concentration_pct FLOAT,
    stress_pct FLOAT,
    uncertain_pct FLOAT,
    mean_confidence FLOAT,
    states_json JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
"""

import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.eeg.eeg_pipeline import pipeline
from app.schemas import EEGReportCreate

logger = logging.getLogger("NeuroCap.EEG")
router = APIRouter(prefix="/api/eeg", tags=["EEG Temps Réel"])

HIGH_CONF_THR = 0.85   # seuil pour stocker les features dans training_epochs


async def _try_get_user(request: Request, db: AsyncClient) -> Optional[dict]:
    """Retourne le user si le token JWT est valide, None sinon (silencieux)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        from app.core.security import _decode_token
        payload = _decode_token(auth[7:])
        uid = payload.get("sub")
        if not uid or payload.get("type") != "access":
            return None
        r = await db.table("users").select("id, role").eq("id", uid).limit(1).execute()
        return r.data[0] if r.data else None
    except Exception:
        return None


async def _store_training_epochs(patient_id: str, report_id: Optional[str],
                                 epochs: list, db: AsyncClient):
    """
    Insère les époques haute confiance dans training_epochs (batch par 100).

    Stocke pour chaque époque :
      - features       : 78 features FeatEng
      - epoch_filtered : 1000 floats signal filtré (pour EEGNet fine-tuning)
      - conc_score     : pct 0-100 DualClassifier (label régression EEGNet/conc)
      - stress_score   : pct 0-100 DualClassifier (label régression EEGNet_LR/stress)
    """
    rows = []
    for ep in epochs:
        pred = ep.get("ml_prediction") or {}
        conf = pred.get("confidence", 0.0)
        if not ep.get("ml_features") or conf < HIGH_CONF_THR:
            continue

        conc_pred    = pred.get("concentration") or {}
        stress_pred  = pred.get("stress") or {}
        # Sauvegarder en 0-100 (pct) — échelle cohérente avec l'affichage et le fine-tuning
        conc_score   = conc_pred.get("pct")   if isinstance(conc_pred,   dict) else None
        stress_score = stress_pred.get("pct") if isinstance(stress_pred, dict) else None
        label        = 1 if pred.get("state") == "stress" else 0

        # epoch_filtered : 1000 floats — signal filtré z-scoré, nécessaire pour EEGNet
        ep_filt = ep.get("epoch_filtered") or []

        rows.append({
            "id":                   str(uuid.uuid4()),
            "patient_id":           patient_id,
            "report_id":            report_id,
            "epoch_index":          ep.get("epoch_idx", 0),
            "features":             ep["ml_features"],          # 78 features RF stress
            "epoch_filtered":       ep_filt[:1000] if ep_filt else None,  # EEGNet conc
            "conc_score":           conc_score,                 # score 0-10 concentration
            "stress_score":         stress_score,               # score 0-10 stress
            "predicted_label":      label,
            "predicted_confidence": round(conf, 4),
            "is_reliable":          conf >= 0.60,
            "is_high_confidence":   True,
            "used_in_finetuning":   False,
            "created_at":           datetime.now(timezone.utc).isoformat(),
        })
    if not rows:
        return 0
    try:
        for i in range(0, len(rows), 100):
            await db.table("training_epochs").insert(rows[i:i + 100]).execute()
        logger.info(f"[EEG] {len(rows)} époques stockées pour patient {patient_id[:8]}")
        return len(rows)
    except Exception as e:
        logger.warning(f"[EEG] Stockage époques échoué (table manquante?): {e}")
        return 0


# ── Statut modèles IA ────────────────────────────────────────────────────────
@router.get("/models/status", tags=["Modèles IA"])
def models_status():
    """
    Health check des modèles DualClassifier chargés en mémoire.
    Utilisé par le monitoring startup et le dashboard admin.
    """
    try:
        from app.services.eeg.dsp.file_processor import _dual_clf
        clf = _dual_clf
        if clf is None:
            return {
                "status":  "unavailable",
                "message": "DualClassifier non initialisé",
                "models":  {},
            }
        return {
            "status":  "ok" if (clf.status["conc_loaded"] and clf.status["stress_loaded"]) else "partial",
            "models":  clf.status,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "models": {}}


# ── Statut ─────────────────────────────────────────────────────────────────────
@router.get("/status")
def eeg_status():
    st = pipeline.state
    return {
        "esp32_connected":   st.esp32_connected,
        "esp32_ip":          st.esp32_ip,
        "baseline_ok":       pipeline.rt.epocher.pipeline.has_baseline(),
        "epoch_count":       pipeline.rt.epocher.n_accepted,
        "cal_progress":      pipeline.rt.epocher.pipeline.cal_progress,
        "recording":         pipeline._rec_active,
        "wifi_result":       st.last_wifi_result,
        "wifi_configured":   st.wifi_configured,
        "esp32_ap_detected": st.esp32_ap_detected,
        "esp32_ap_ssid":     st.esp32_ap_ssid,
        **pipeline.electrode_mon.status_detail,
    }


@router.get("/analyze")
def eeg_analyze():
    rm = pipeline.rt.raw_metrics()
    es = pipeline.electrode_mon.status_detail
    return {
        "esp32_connected":   pipeline.state.esp32_connected,
        "epoch_total":       pipeline.rt.epocher.n_total,
        "epoch_accepted":    pipeline.rt.epocher.n_accepted,
        "epoch_rejected":    pipeline.rt.epocher.n_rejected,
        "cal_progress":      pipeline.rt.epocher.pipeline.cal_progress,
        "baseline_ok":       pipeline.rt.epocher.pipeline.has_baseline(),
        **es, **rm,
    }


# ── Baseline ───────────────────────────────────────────────────────────────────
@router.post("/baseline/finalise")
async def finalise_baseline():
    ok = pipeline.rt.epocher.pipeline.finalise_baseline()
    if pipeline.ws_manager:
        await pipeline.ws_manager.broadcast({"type": "baseline_ready", "success": ok})
    return {"success": ok}


# ── Enregistrement CSV ─────────────────────────────────────────────────────────
@router.post("/recording/start")
def start_recording():
    path = pipeline.start_recording()
    return {"message": "Enregistrement démarré", "file": path}


@router.post("/recording/stop")
def stop_recording():
    path = pipeline.stop_recording()
    return {"message": "Arrêté", "signal_file": path}


@router.get("/recording/export")
def export_recording():
    path = pipeline._last_rec_sig_path
    if not path or not Path(path).exists():
        raise HTTPException(404, detail="Aucun enregistrement disponible")
    return FileResponse(path, media_type="text/csv", filename=Path(path).name)


# ── WiFi ───────────────────────────────────────────────────────────────────────
@router.get("/wifi/networks")
def wifi_networks():
    return {"networks": pipeline.state.known_networks}


@router.post("/wifi/configure")
async def wifi_configure(request: Request):
    if not pipeline._wifi_mgr:
        return JSONResponse({"error": "WifiManager non disponible (pas de hardware)"}, status_code=503)
    try:
        data = await request.json()
        ssid = data.get("ssid", "").strip()
        pwd  = data.get("password", "")
        if not ssid:
            return JSONResponse({"error": "SSID requis"}, status_code=400)
        result = pipeline._wifi_mgr.send_wifi_config(ssid, pwd)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"[WiFi] configure error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/wifi/use_saved")
async def wifi_use_saved(request: Request):
    if not pipeline._wifi_mgr:
        return JSONResponse({"error": "WifiManager non disponible"}, status_code=503)
    try:
        data = await request.json()
        ssid = data.get("ssid", "").strip()
        if not ssid:
            return JSONResponse({"error": "SSID requis"}, status_code=400)
        pipeline._wifi_mgr.send_use_saved(ssid)
        return JSONResponse({"message": f"Commande envoyée pour '{ssid}'"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/wifi/reset")
async def wifi_reset():
    if not pipeline._wifi_mgr:
        return JSONResponse({"error": "WifiManager non disponible"}, status_code=503)
    pipeline._wifi_mgr.send_reset()
    return JSONResponse({"message": "Reset WiFi envoyé"})


# ── Analyse fichier EEG offline ────────────────────────────────────────────────
@router.post("/analyze_file")
async def analyze_file(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncClient = Depends(get_db),
):
    """
    Analyse un fichier EEG (.edf, .csv, .txt) :
    Golden Filter → z-score → DualClassifier (GRU_Att conc + GRU_Att stress).
    Retourne la classification par époque + résumé de session + signal quality.

    Si le patient est authentifié, les époques haute confiance (≥ 0.85)
    sont automatiquement stockées dans training_epochs pour le fine-tuning.
    """
    content  = await file.read()
    filename = file.filename or "signal"
    ext      = Path(filename).suffix.lower()

    try:
        from app.services.eeg.dsp.file_processor import read_edf, read_csv_txt, process_signal
    except ImportError as e:
        raise HTTPException(500, detail=f"Module file_processor non disponible: {e}")

    try:
        if ext == ".edf":
            signal, fs = read_edf(content)
        elif ext in (".csv", ".txt"):
            signal, fs = read_csv_txt(content, filename)
        else:
            raise HTTPException(400, detail=f"Format '{ext}' non supporté. Formats: .edf, .csv, .txt")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, detail=f"Lecture fichier échouée: {e}")

    try:
        result = process_signal(signal, fs)
    except Exception as e:
        raise HTTPException(500, detail=f"Erreur DSP: {e}")

    result["filename"] = filename

    # Stocker les époques haute confiance si patient authentifié
    user = await _try_get_user(request, db)
    if user and user.get("role") == "patient":
        result["epochs_stored"] = await _store_training_epochs(
            patient_id=user["id"],
            report_id=None,
            epochs=result.get("epochs", []),
            db=db,
        )

    return result


# ── Mes rapports EEG (patient authentifié) ────────────────────────────────────
@router.get("/my-reports")
async def my_eeg_reports(
    limit: int = 100,
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne les rapports EEG du patient authentifié, tri chronologique inversé."""
    try:
        resp = (
            await db.table("eeg_reports")
            .select("*")
            .eq("patient_id", user["id"])
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture rapports EEG : {e}")


# ── Statut fine-tuning patient ────────────────────────────────────────────────
@router.get("/finetuning/status")
async def finetuning_status(
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Retourne l'état complet du fine-tuning pour le patient authentifié :
    activité récente, compteurs d'époques, version du modèle,
    dernier job (avec gain de précision), conditions de déclenchement.
    """
    from app.services.finetune.conditions import get_activity, check_finetune_trigger

    patient_id = user["id"]

    # Profil EEG
    prof_r = await db.table("eeg_profiles") \
        .select("finetuned_version, finetuned_model_checkpoint, last_finetune_at, calibrated_at, last_20_sessions_accuracy") \
        .eq("user_id", patient_id).limit(1).execute()
    profile = prof_r.data[0] if prof_r.data else {}

    # Activité récente
    activity = await get_activity(patient_id, db)

    # Total époques fiables
    r_total = await db.table("training_epochs").select("id", count="exact") \
        .eq("patient_id", patient_id).eq("is_high_confidence", True).execute()
    total_reliable = r_total.count or 0

    # Époques fiables non encore utilisées
    r_unused = await db.table("training_epochs").select("id", count="exact") \
        .eq("patient_id", patient_id) \
        .eq("is_high_confidence", True) \
        .eq("used_in_finetuning", False).execute()
    unused_reliable = r_unused.count or 0

    # Dernier job (complété ou échoué)
    jobs_r = await db.table("finetuning_jobs") \
        .select("*") \
        .eq("patient_id", patient_id) \
        .order("created_at", desc=True) \
        .limit(1).execute()
    last_job = jobs_r.data[0] if jobs_r.data else None

    # Prochain déclenchement prévu (conditions)
    try:
        should, reason, ttype = await check_finetune_trigger(patient_id, profile, db)
    except Exception:
        should, reason, ttype = False, "Erreur vérification", None

    return {
        "patient_id":               patient_id,
        "activity":                 activity,
        "finetuned_version":        profile.get("finetuned_version", 0),
        "finetuned_model_checkpoint": profile.get("finetuned_model_checkpoint"),
        "last_finetune_at":         profile.get("last_finetune_at"),
        "total_reliable_epochs":    total_reliable,
        "unused_reliable_epochs":   unused_reliable,
        "last_job":                 last_job,
        "trigger_ready":            should,
        "trigger_reason":           reason,
        "trigger_type":             ttype,
    }


# ── Rapport EEG (live ou fichier) ─────────────────────────────────────────────
@router.post("/report", status_code=201)
async def save_eeg_report(
    body: EEGReportCreate,
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Sauvegarde un rapport EEG (session live ou analyse fichier) dans eeg_reports.
    Lié au patient authentifié et à son thérapeute assigné.
    """
    report = {
        "id":                 str(uuid.uuid4()),
        "patient_id":         user["id"],
        "therapist_id":       user.get("therapist_id"),
        "type":               body.type,
        "filename":           body.filename,
        "duration_s":         body.duration_s,
        "n_epochs_accepted":  body.n_epochs_accepted,
        "n_epochs_rejected":  body.n_epochs_rejected,
        "dominant_state":     body.dominant_state,
        "concentration_pct":  body.concentration_pct,
        "stress_pct":         body.stress_pct,
        "uncertain_pct":      body.uncertain_pct,
        "mean_confidence":    body.mean_confidence,
        "states_json":        body.states_json or {},
        "notes":              body.notes,
        "created_at":         datetime.now(timezone.utc).isoformat(),
    }
    try:
        resp = await db.table("eeg_reports").insert(report).execute()
        return resp.data[0] if resp.data else report
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur sauvegarde rapport EEG : {e}. "
                   "Vérifiez que la table eeg_reports existe (voir SQL migration dans eeg.py).",
        )
