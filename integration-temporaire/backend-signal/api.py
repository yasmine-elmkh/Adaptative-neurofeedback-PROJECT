# backend/api.py
"""
API REST + WebSocket NeuroCap EEG v7.2
Les routes WiFi utilisent app.state.wifi_manager (injecté par assembly.py).
"""

import asyncio
import json
import queue
import os
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from websockets.exceptions import ConnectionClosedError

logger = logging.getLogger("NeuroCap")

app = FastAPI(title="NeuroCap EEG v7.2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# DSP
# ═══════════════════════════════════════════════════════════════
try:
    from dsp import RealTimeProcessor, ElectrodeMonitor
    rt            = RealTimeProcessor()
    electrode_mon = ElectrodeMonitor()
except ImportError:
    class _FakeRT:
        def push(self, uv, electrode_ok=True): return uv, None
        def metrics(self): return {"bands": {}, "state": "neutral", "focus": 0, "stress": 0}
        def raw_metrics(self): return {}
        class epocher:
            n_total = n_accepted = n_rejected = 0
            class pipeline:
                cal_progress = 0.0
                @staticmethod
                def has_baseline(): return False
                @staticmethod
                def finalise_baseline(): return False

    class _FakeEM:
        def update(self, lo_plus, lo_minus): pass
        def should_send_heartbeat(self): return False
        @property
        def electrode_ok(self): return True
        @property
        def status_detail(self):
            return {"electrode_ok": True, "fp2_connected": True, "m2_connected": True}

    rt            = _FakeRT()
    electrode_mon = _FakeEM()
    logger.warning("[API] DSP non disponible — mode test")

# ═══════════════════════════════════════════════════════════════
# ÉTAT GLOBAL
# ═══════════════════════════════════════════════════════════════
sample_queue     = queue.Queue(maxsize=5000)
ws_manager       = None
loop             = None

esp32_connected  = False
esp32_ip         = ""
known_networks   = []
last_wifi_result = None
wifi_configured  = False
esp32_ap_detected = False
esp32_ap_ssid     = ""

# ── Reset a la deconnexion ESP32 ────────────────────────────────────
def reset_on_disconnect():
    """
    Appele par assembly.on_tcp_disconnected.
    Vide la queue de samples pour eviter que le DSP traite
    des donnees obsoletes apres reconnexion.
    Reset egalement l'etat de l'epoch extractor.
    """
    # Vider la queue
    drained = 0
    while not sample_queue.empty():
        try:
            sample_queue.get_nowait()
            drained += 1
        except Exception:
            break
    logger.info(f"[DSP] Deconnexion ESP32 — {drained} samples purges de la queue")

    # Reset du processeur DSP (filtres + epocher)
    try:
        rt.epocher.pipeline.filters._dc_initialized = False
    except Exception:
        pass

# Enregistrement CSV
_rec_active         = False
_csv_signal_file    = None
_csv_signal_writer  = None
_csv_epochs_file    = None
_csv_epochs_writer  = None
_last_rec_sig_path  = ""


# ═══════════════════════════════════════════════════════════════
# WEBSOCKET MANAGER
# ═══════════════════════════════════════════════════════════════
class WSManager:
    def __init__(self):
        self.active_connections = []
        self._lock = asyncio.Lock()

    async def connect(self, ws):
        await ws.accept()

    async def register(self, ws):
        async with self._lock:
            if ws not in self.active_connections:
                self.active_connections.append(ws)

    def disconnect(self, ws):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def broadcast(self, data):
        if not self.active_connections:
            return
        msg  = json.dumps(data, default=str)
        dead = []
        for ws in list(self.active_connections):
            try:
                if hasattr(ws, 'client_state') and ws.client_state.name != 'CONNECTED':
                    dead.append(ws); continue
                await ws.send_text(msg)
            except (WebSocketDisconnect, ConnectionClosedError, RuntimeError):
                dead.append(ws)
            except Exception:
                dead.append(ws)
        async with self._lock:
            for ws in dead:
                if ws in self.active_connections:
                    self.active_connections.remove(ws)


# ═══════════════════════════════════════════════════════════════
# BOUCLE DSP
# ═══════════════════════════════════════════════════════════════
async def processing_loop():
    import csv
    global _csv_signal_writer, _csv_epochs_writer

    while True:
        if sample_queue.qsize() > 250:
            for _ in range(sample_queue.qsize() - 100):
                try: sample_queue.get_nowait()
                except Exception: break

        batch = []
        try:
            while len(batch) < 10:
                batch.append(sample_queue.get_nowait())
        except queue.Empty:
            pass

        if not batch:
            await asyncio.sleep(0.004)
            continue

        if not hasattr(processing_loop, '_contact_buf'):
            processing_loop._contact_buf = []
        _display_counter = 0
        for s in batch:
            _display_counter += 1
            elec_ok     = electrode_mon.electrode_ok
            elec_status = electrode_mon.status_detail

            # Détection contact par variance signal filtré (fallback LO_BYPASS)
            _contact_ok = True
            if len(processing_loop._contact_buf) >= 250:
                import numpy as np
                _var = float(np.var(processing_loop._contact_buf))
                _contact_ok = _var > 0.5

            # LO_BYPASS mode (lo_plus==0 et lo_minus==0) : remplacer par variance
            if s.get("lo_plus", 1) == 0 and s.get("lo_minus", 1) == 0:
                elec_ok = _contact_ok

            flt, epoch_result = rt.push(
                s["uv"],
                electrode_ok = elec_ok,
                lo_score     = electrode_mon.lo_score if elec_ok else 0,
            )

            processing_loop._contact_buf.append(flt)
            if len(processing_loop._contact_buf) > 250:
                processing_loop._contact_buf.pop(0)
            m   = rt.metrics()
            _rm = rt.raw_metrics()

            payload = {
                "type": "eeg", "ts": s["ts"], "uv": s["uv"],
                "filtered": round(float(flt), 3),
                "electrode_ok": elec_ok,
                "fp2_connected": elec_status.get("fp2_connected", True),
                "m2_connected": elec_status.get("m2_connected", True),
                "batt_V": s.get("batt_V", 0),
                "raw_metrics": {
                    "rms_raw": _rm.get("rms_uv",  0.0),
                    "peak":    _rm.get("peak_uv", 0.0),
                    "dc_uv":   _rm.get("dc_uv",   0.0),
                },
                "cal_progress": rt.epocher.pipeline.cal_progress,
            }
            payload.update(m)

            # Broadcast EEG seulement 1 sample sur 4 → ~62 Hz pour le browser
            if _display_counter % 4 == 0 and ws_manager:
                await ws_manager.broadcast(payload)

            if electrode_mon.should_send_heartbeat():
                if ws_manager:
                    await ws_manager.broadcast({
                        "type": "electrode", **elec_status,
                        "timestamp": datetime.now().isoformat(),
                    })

            if _rec_active and _csv_signal_writer:
                _csv_signal_writer.writerow([
                    s["ts"], s["uv"], round(float(flt), 3),
                    s.get("batt_V", 0), s.get("lo_plus", -1),
                    s.get("lo_minus", -1), s.get("pkt_id", -1), int(elec_ok),
                ])

            if epoch_result:
                etype = epoch_result.get("type")
                if etype == "epoch":
                    if ws_manager:
                        await ws_manager.broadcast(epoch_result)
                    if _rec_active and _csv_epochs_writer:
                        feat = epoch_result["features"]
                        grf  = epoch_result.get("graph", {})
                        _csv_epochs_writer.writerow([
                            epoch_result["epoch_idx"], epoch_result["timestamp"],
                            feat.get("fractal_dim", 0), grf.get("degree_dist_mean", 0),
                            grf.get("clustering_coeff", 0), grf.get("jaccard_mean", 0),
                            feat.get("rel_alpha", 0), feat.get("rel_beta", 0),
                            feat.get("theta_beta", 0), feat.get("engagement", 0),
                            feat.get("stress_idx", 0), feat.get("pac_theta_gamma", 0),
                            feat.get("sef95", 0), feat.get("hjorth_complexity", 0),
                            feat.get("spectral_entropy", 0),
                        ])
                elif etype == "epoch_rejected":
                    if ws_manager:
                        await ws_manager.broadcast(epoch_result)


# ═══════════════════════════════════════════════════════════════
# API REST
# ═══════════════════════════════════════════════════════════════

# ── Helper pour accéder au WifiManager ─────────────────────────
def _get_wifi_mgr(request: Request):
    return request.app.state.wifi_manager


# ── WiFi ───────────────────────────────────────────────────────
@app.post("/api/wifi/configure")
async def configure_wifi(request: Request):
    mgr = _get_wifi_mgr(request)
    if not mgr:
        return JSONResponse({"error": "WifiManager non initialisé"}, status_code=500)
    try:
        data = await request.json()
        ssid = data.get("ssid", "").strip()
        pwd  = data.get("password", "")
        if not ssid:
            return JSONResponse({"error": "SSID requis"}, status_code=400)
        result = mgr.send_wifi_config(ssid, pwd)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"[WiFi] configure error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.options("/api/wifi/configure")
async def options_wifi_configure():
    return Response(status_code=200)

@app.get("/api/wifi/networks")
def get_known_networks():
    return {"networks": known_networks}

@app.post("/api/wifi/use_saved")
async def use_saved_network(request: Request):
    mgr = _get_wifi_mgr(request)
    if not mgr:
        return JSONResponse({"error": "WifiManager non initialisé"}, status_code=500)
    try:
        data = await request.json()
        ssid = data.get("ssid", "").strip()
        if not ssid:
            return JSONResponse({"error": "SSID requis"}, status_code=400)
        mgr.send_use_saved(ssid)
        return JSONResponse({"message": f"Commande envoyée pour '{ssid}'"})
    except Exception as e:
        logger.error(f"[WiFi] use_saved error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/wifi/reset")
async def reset_wifi(request: Request):
    mgr = _get_wifi_mgr(request)
    if not mgr:
        return JSONResponse({"error": "WifiManager non initialisé"}, status_code=500)
    mgr.send_reset()
    return JSONResponse({"message": "Reset WiFi envoyé"})

# ── Statut ────────────────────────────────────────────────────
@app.get("/api/status")
def get_status():
    return {
        "esp32_connected":   esp32_connected,
        "esp32_ip":          esp32_ip,
        "baseline_ok":       rt.epocher.pipeline.has_baseline(),
        "epoch_count":       rt.epocher.n_accepted,
        "recording":         _rec_active,
        "wifi_result":       last_wifi_result,
        "wifi_configured":   wifi_configured,
        "esp32_ap_detected": esp32_ap_detected,
        "esp32_ap_ssid":     esp32_ap_ssid,
        **electrode_mon.status_detail,
    }

@app.get("/api/electrode")
def get_electrode():
    return electrode_mon.status_detail

@app.post("/api/analyze")
async def analyze_signal():
    rm = rt.raw_metrics()
    es = electrode_mon.status_detail
    return {
        "esp32_connected": esp32_connected,
        "epoch_total": rt.epocher.n_total,
        "epoch_accepted": rt.epocher.n_accepted,
        "epoch_rejected": rt.epocher.n_rejected,
        "cal_progress": rt.epocher.pipeline.cal_progress,
        "baseline_ok": rt.epocher.pipeline.has_baseline(),
        **es, **rm,
    }

# ── Baseline ──────────────────────────────────────────────────
@app.post("/api/baseline/finalise")
async def finalise_baseline():
    ok = rt.epocher.pipeline.finalise_baseline()
    if ws_manager:
        await ws_manager.broadcast({"type": "baseline_ready", "success": ok})
    return {"success": ok}

# ── Enregistrement CSV ────────────────────────────────────────
@app.post("/api/recording/start")
def start_rec():
    import csv
    global _rec_active, _csv_signal_file, _csv_signal_writer
    global _csv_epochs_file, _csv_epochs_writer, _last_rec_sig_path

    os.makedirs("recordings", exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    sig_path = f"recordings/signal_{ts_str}.csv"
    _csv_signal_file   = open(sig_path, "w", newline="")
    _csv_signal_writer = csv.writer(_csv_signal_file)
    _csv_signal_writer.writerow([
        "timestamp_us", "raw_uV", "filtered_uV", "batt_V",
        "lo_plus_raw", "lo_minus_raw", "pkt_id", "electrode_ok"
    ])
    _last_rec_sig_path = sig_path

    ep_path = f"recordings/epochs_{ts_str}.csv"
    _csv_epochs_file   = open(ep_path, "w", newline="")
    _csv_epochs_writer = csv.writer(_csv_epochs_file)
    _csv_epochs_writer.writerow([
        "epoch_idx", "timestamp",
        "fractal_dim", "fd_degree_dist_mean", "fd_clustering_coeff", "fd_jaccard_mean",
        "rel_alpha", "rel_beta", "theta_beta", "engagement", "stress_idx",
        "pac_theta_gamma", "sef95", "hjorth_complexity", "spectral_entropy",
    ])
    _rec_active = True
    logger.info(f"[REC] Démarré → {sig_path}")
    return {"message": "Enregistrement démarré", "file": sig_path}

@app.post("/api/recording/stop")
def stop_rec():
    global _rec_active, _csv_signal_file, _csv_signal_writer
    global _csv_epochs_file, _csv_epochs_writer

    _rec_active = False
    for f in [_csv_signal_file, _csv_epochs_file]:
        if f: f.close()
    _csv_signal_file = _csv_epochs_file = None
    _csv_signal_writer = _csv_epochs_writer = None
    logger.info("[REC] Arrêté")
    return {"message": "Arrêté", "signal_file": _last_rec_sig_path}

@app.get("/api/recording/export")
def export_csv():
    if not _last_rec_sig_path or not os.path.exists(_last_rec_sig_path):
        return JSONResponse({"error": "Aucun enregistrement"}, status_code=404)
    return FileResponse(_last_rec_sig_path, media_type="text/csv",
                        filename=os.path.basename(_last_rec_sig_path))


# ── WebSocket ─────────────────────────────────────────────────
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    if ws_manager is None:
        await ws.close()
        return

    await ws_manager.connect(ws)

    try:
        await ws.send_text(json.dumps({
            "type": "init",
            "esp32_connected":  esp32_connected,
            "esp32_ip":         esp32_ip,
            "wifi_configured":  wifi_configured,
            "esp32_ap_detected": esp32_ap_detected,
            "baseline_ok":      rt.epocher.pipeline.has_baseline(),
            **electrode_mon.status_detail,
        }))
    except Exception as e:
        logger.warning(f"[WS] Init failed: {e}")
        ws_manager.disconnect(ws)
        return

    await ws_manager.register(ws)

    try:
        while True:
            try:
                msg = await ws.receive_text()
                try:
                    cmd = json.loads(msg).get("command", "")
                    if cmd == "FINALISE_BASELINE":
                        ok = rt.epocher.pipeline.finalise_baseline()
                        await ws.send_text(json.dumps({"type": "baseline_ready", "success": ok}))
                    elif cmd == "START_REC":
                        start_rec()
                    elif cmd == "STOP_REC":
                        stop_rec()
                    elif cmd == "ANALYZE_NOW":
                        rm = rt.raw_metrics()
                        es = electrode_mon.status_detail
                        await ws.send_text(json.dumps({
                            "type": "report",
                            "esp32_ip": esp32_ip, "esp32_connected": esp32_connected,
                            "epoch_total": rt.epocher.n_total,
                            "epoch_accepted": rt.epocher.n_accepted,
                            "epoch_rejected": rt.epocher.n_rejected,
                            "cal_progress": rt.epocher.pipeline.cal_progress,
                            "baseline_ok": rt.epocher.pipeline.has_baseline(),
                            **es, **rm,
                        }, default=str))
                except Exception:
                    pass
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        ws_manager.disconnect(ws)


# ── Fichiers statiques React ──────────────────────────────────
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse("static/index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        from fastapi import HTTPException
        if full_path.startswith("api/") or full_path == "api" or full_path.startswith("ws"):
            raise HTTPException(status_code=404)
        fp = f"static/{full_path}"
        return FileResponse(fp) if os.path.exists(fp) else FileResponse("static/index.html")