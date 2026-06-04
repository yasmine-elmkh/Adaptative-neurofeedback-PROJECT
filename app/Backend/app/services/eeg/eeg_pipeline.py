"""
NeuroCap — Pipeline EEG Temps Réel
====================================
Singleton qui orchestre :
  • TCPReceiver  → reçoit les samples CSV de l'ESP32 via TCP :9000
  • WifiManager  → configure le WiFi de l'ESP32 via UDP
  • DSP          → filtre, extrait les époques et classifie l'état cognitif
  • WSManager    → diffuse les trames vers les clients WebSocket /ws/eeg

Utilisation dans main.py (lifespan) :
  await pipeline.start()
  yield
  await pipeline.stop()
"""

import asyncio
import json
import logging
import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("NeuroCap.EEG")


# ─── Imports conditionnels ────────────────────────────────────────────────────
try:
    from app.services.eeg.dsp import RealTimeProcessor, ElectrodeMonitor
    from app.services.eeg.utils.constants import HARDWARE_GAIN
    _DSP_OK = True
except ImportError:
    _DSP_OK = False
    HARDWARE_GAIN = 1000
    logger.warning("[EEG] Module DSP non disponible — mode simulation")

try:
    from app.services.eeg.tcp_receiver import TCPReceiver
    from app.services.eeg.wifi_manager import WifiManager
    _HW_OK = True
except ImportError:
    _HW_OK = False
    logger.warning("[EEG] TCP/WiFi non disponibles — pas de hardware")


# ─── Fallbacks mode simulation ────────────────────────────────────────────────
class _FakeRT:
    class _Pipeline:
        cal_progress = 0.0
        @staticmethod
        def has_baseline(): return False
        @staticmethod
        def finalise_baseline(): return False

    class _Epocher:
        n_total = n_accepted = n_rejected = 0
        pipeline = None  # initialisé ci-dessous

    def __init__(self):
        self.epocher = self._Epocher()
        self.epocher.pipeline = self._Pipeline()

    def push(self, uv, electrode_ok=True, lo_score=0):
        return uv, None

    def metrics(self):
        return {"bands": {}, "state": "neutral", "cqe_score": 0}

    def raw_metrics(self):
        return {}


class _FakeEM:
    lo_score = 0

    def update(self, lo_plus, lo_minus): pass

    def should_send_heartbeat(self): return False

    @property
    def electrode_ok(self): return True

    @property
    def status_detail(self):
        return {
            "electrode_ok": True,
            "fp2_connected": True,
            "m2_connected": True,
        }


# ─── WebSocket Manager ────────────────────────────────────────────────────────
class WSManager:
    def __init__(self):
        self.active_connections: list = []
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

    async def broadcast(self, data: dict):
        if not self.active_connections:
            return
        msg = json.dumps(data, default=str)
        dead = []
        for ws in list(self.active_connections):
            try:
                from starlette.websockets import WebSocketState
                if ws.client_state != WebSocketState.CONNECTED:
                    dead.append(ws)
                    continue
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        async with self._lock:
            for ws in dead:
                if ws in self.active_connections:
                    self.active_connections.remove(ws)


# ─── État global EEG ──────────────────────────────────────────────────────────
class EEGState:
    """État partagé thread-safe (lecture seule pour les routes REST)."""
    def __init__(self):
        self.esp32_connected   = False
        self.esp32_ip          = ""
        self.wifi_configured   = False
        self.esp32_ap_detected = False
        self.esp32_ap_ssid     = ""
        self.known_networks: list = []
        self.last_wifi_result: Optional[dict] = None


# ─── Pipeline principal ───────────────────────────────────────────────────────
class EEGPipeline:
    """Singleton orchestrateur du pipeline EEG temps réel."""

    def __init__(self):
        self.sample_queue  = queue.Queue(maxsize=5000)
        self.state         = EEGState()
        self.ws_manager: Optional[WSManager] = None

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._tasks: list = []
        self._contact_buf: list = []

        # DSP
        if _DSP_OK:
            self.rt            = RealTimeProcessor()
            self.electrode_mon = ElectrodeMonitor()
        else:
            self.rt            = _FakeRT()
            self.electrode_mon = _FakeEM()

        # Hardware
        self._wifi_mgr: Optional[object] = None
        self._tcp_recv: Optional[object] = None

        # Recording
        self._rec_active         = False
        self._csv_signal_file    = None
        self._csv_signal_writer  = None
        self._last_rec_sig_path  = ""

    # ── Broadcast thread-safe ──────────────────────────────────────────────────
    def _bcast_sync(self, payload: dict):
        if self._loop is None or self.ws_manager is None:
            return
        asyncio.run_coroutine_threadsafe(
            self.ws_manager.broadcast(payload), self._loop
        )

    # ── Callbacks TCP ─────────────────────────────────────────────────────────
    def _on_tcp_connected(self, ip: str):
        self.state.esp32_connected = True
        self.state.esp32_ip        = ip
        logger.info(f"[TCP] ESP32 connecté: {ip}")

    def _on_tcp_disconnected(self):
        self.state.esp32_connected   = False
        self.state.esp32_ip          = ""
        self.state.wifi_configured   = False
        self.state.last_wifi_result  = None
        self.state.esp32_ap_detected = False
        self.state.esp32_ap_ssid     = ""

        drained = 0
        while not self.sample_queue.empty():
            try:
                self.sample_queue.get_nowait()
                drained += 1
            except Exception:
                break
        logger.info(f"[DSP] Déconnexion — {drained} samples purgés")

        try:
            self.rt.reset()
        except Exception:
            pass

        self._bcast_sync({
            "type": "esp32_status",
            "connected": False,
            "wifi_configured": False,
            "esp32_ip": "",
        })

    def _on_filter_reset(self):
        try:
            self.rt.reset()
        except Exception:
            pass

    # ── Callbacks WiFi ────────────────────────────────────────────────────────
    def _on_esp32_announce(self, ip: str):
        self.state.esp32_ip = ip
        logger.info(f"[WiFi] ESP32 annoncé: {ip}")

    def _on_wifi_result(self, success: bool, ip: str, ssid: str, reason: str):
        self.state.last_wifi_result = {
            "success": success, "ip": ip, "ssid": ssid, "reason": reason,
        }
        if success:
            self.state.wifi_configured = True
            self.state.esp32_ip        = ip
            logger.info(f"[WiFi] ✓ {ssid} @ {ip}")
        else:
            logger.warning(f"[WiFi] ✗ {ssid}: {reason}")

    def _on_networks_received(self, networks: list):
        self.state.known_networks = networks
        logger.info(f"[WiFi] Réseaux mémorisés: {networks}")

    # ── Start / Stop ─────────────────────────────────────────────────────────
    async def start(self):
        self._loop      = asyncio.get_event_loop()
        self.ws_manager = WSManager()

        if _HW_OK:
            self._wifi_mgr = WifiManager(
                on_esp32_announce    = self._on_esp32_announce,
                on_wifi_result       = self._on_wifi_result,
                on_networks_received = self._on_networks_received,
                bcast_sync_fn        = self._bcast_sync,
            )
            self._tcp_recv = TCPReceiver(
                sample_queue      = self.sample_queue,
                electrode_monitor = self.electrode_mon,
                on_connected      = self._on_tcp_connected,
                on_disconnected   = self._on_tcp_disconnected,
                filter_reset_cb   = self._on_filter_reset,
                bcast_sync_fn     = self._bcast_sync,
            )
            self._wifi_mgr.start()
            self._tcp_recv.start()
            logger.info("[EEG] Pipeline démarré — TCPReceiver :9000 + WifiManager UDP")
        else:
            logger.info("[EEG] Pipeline démarré — mode simulation (pas de hardware)")

        self._tasks.append(asyncio.create_task(self._processing_loop()))

        if _HW_OK:
            self._tasks.append(asyncio.create_task(self._poll_ap_status()))

    async def stop(self):
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        logger.info("[EEG] Pipeline arrêté")

    # ── Boucle DSP ────────────────────────────────────────────────────────────
    async def _processing_loop(self):
        _display_counter = 0

        while True:
            # Throttle si la queue déborde
            if self.sample_queue.qsize() > 250:
                for _ in range(self.sample_queue.qsize() - 100):
                    try:
                        self.sample_queue.get_nowait()
                    except Exception:
                        break

            # Drainer jusqu'à 10 samples
            batch = []
            try:
                while len(batch) < 10:
                    batch.append(self.sample_queue.get_nowait())
            except queue.Empty:
                pass

            if not batch:
                await asyncio.sleep(0.004)
                continue

            for s in batch:
                _display_counter += 1
                elec_ok     = self.electrode_mon.electrode_ok
                elec_status = self.electrode_mon.status_detail

                # Normalisation hardware : convertit la sortie AD8232 amplifiée
                # en µV scalp physiologiques avant tout traitement DSP.
                # Tout le pipeline (filtres, CQE, détecteur artefacts, epocher)
                # reçoit des valeurs en µV scalp (10-150 µV), ce qui correspond
                # aux seuils définis dans artifacts.py.
                uv_norm = s["uv"] / HARDWARE_GAIN

                # Détection contact par variance (fallback quand LO bypassed)
                # Plage valide en µV scalp : 0.5 < variance < 250 000 µV²
                #   Trop faible (< 0.5)      → électrode morte / signal plat
                #   Trop élevée (> 250 000)  → électrode flottante (RMS > ~500 µV)
                _contact_ok = True
                if len(self._contact_buf) >= 250:
                    import numpy as np
                    _var = float(np.var(self._contact_buf))
                    _contact_ok = 0.5 < _var < 250_000
                if s.get("lo_plus", 1) == 0 and s.get("lo_minus", 1) == 0:
                    elec_ok = _contact_ok

                try:
                    flt, epoch_result = self.rt.push(
                        uv_norm,
                        electrode_ok = elec_ok,
                        lo_score     = self.electrode_mon.lo_score if elec_ok else 0,
                    )
                except Exception as _push_err:
                    logger.warning(f"[EEG] rt.push erreur : {_push_err}")
                    continue

                self._contact_buf.append(float(flt))
                if len(self._contact_buf) > 250:
                    self._contact_buf.pop(0)

                m   = self.rt.metrics()
                _rm = self.rt.raw_metrics()

                # Pendant le warm-up IIR (500 premiers samples = 2 s),
                # le filtre n'a pas convergé → on envoie 0 pour afficher
                # une ligne plate plutôt que le transitoire saturé.
                _is_settling = self.rt._warmup_samples <= self.rt._WARMUP_N
                _flt_display = 0.0 if _is_settling else round(float(flt), 3)

                # Diagnostic amplitude — log toutes les 250 itérations (~1 s)
                if _display_counter % 250 == 0 and not _is_settling:
                    logger.info(
                        f"[EEG] uv_raw={s['uv']:.1f} µV  "
                        f"uv_scalp={uv_norm:.2f} µV  "
                        f"flt={flt:.2f} µV  "
                        f"elec_ok={elec_ok}  "
                        f"warmup={self.rt._warmup_samples}"
                    )

                payload = {
                    "type":          "eeg",
                    "ts":            s["ts"],
                    # Signal en µV scalp physiologiques (normalisé à l'entrée du pipeline).
                    # Zéro pendant le warm-up, valeur réelle après convergence.
                    "filtered":      _flt_display,
                    "electrode_ok":  elec_ok,
                    "fp2_connected": elec_status.get("fp2_connected", True),
                    "m2_connected":  elec_status.get("m2_connected", True),
                    "batt_V":        s.get("batt_V", 0),
                    "raw_metrics": {
                        "rms_raw":  _rm.get("rms_uv",   0.0),
                        "peak":     _rm.get("peak_uv",  0.0),
                        "dc_uv":    _rm.get("dc_uv",    0.0),
                        "settling": _rm.get("settling", True),
                    },
                    "cal_progress": self.rt.epocher.pipeline.cal_progress,
                }
                payload.update(m)

                # Broadcast 1 sample sur 4 (~62 Hz côté browser)
                if _display_counter % 4 == 0 and self.ws_manager:
                    await self.ws_manager.broadcast(payload)

                # Heartbeat électrode
                if self.electrode_mon.should_send_heartbeat() and self.ws_manager:
                    await self.ws_manager.broadcast({
                        "type":      "electrode",
                        **elec_status,
                        "timestamp": datetime.now().isoformat(),
                    })

                # Époques
                if epoch_result:
                    etype = epoch_result.get("type")
                    if etype == "epoch" and self.ws_manager:
                        ws_payload = {k: v for k, v in epoch_result.items()
                                      if k != "epoch_filtered"}
                        await self.ws_manager.broadcast(ws_payload)
                    elif etype == "epoch_rejected" and self.ws_manager:
                        await self.ws_manager.broadcast(epoch_result)

    async def _poll_ap_status(self):
        while True:
            if self._wifi_mgr:
                self.state.esp32_ap_detected = getattr(
                    self._wifi_mgr, "esp32_ap_detected", False
                )
                self.state.esp32_ap_ssid = getattr(
                    self._wifi_mgr, "esp32_ap_ssid", ""
                )
            await asyncio.sleep(2)

    # ── Enregistrement CSV ────────────────────────────────────────────────────
    def start_recording(self) -> str:
        import csv, os
        os.makedirs("recordings", exist_ok=True)
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        sig_path = f"recordings/signal_{ts_str}.csv"
        self._csv_signal_file   = open(sig_path, "w", newline="")
        self._csv_signal_writer = csv.writer(self._csv_signal_file)
        self._csv_signal_writer.writerow([
            "timestamp_us", "raw_uV", "filtered_uV", "batt_V",
            "lo_plus_raw", "lo_minus_raw", "pkt_id", "electrode_ok",
        ])
        self._last_rec_sig_path = sig_path
        self._rec_active        = True
        logger.info(f"[REC] Démarré → {sig_path}")
        return sig_path

    def stop_recording(self) -> str:
        self._rec_active = False
        if self._csv_signal_file:
            self._csv_signal_file.close()
            self._csv_signal_file   = None
            self._csv_signal_writer = None
        logger.info("[REC] Arrêté")
        return self._last_rec_sig_path


# ── Singleton global ──────────────────────────────────────────────────────────
pipeline = EEGPipeline()
