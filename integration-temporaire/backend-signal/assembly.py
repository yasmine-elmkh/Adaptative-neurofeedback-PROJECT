# backend/assembly.py
"""
Point d'entrée principal NeuroCap EEG v7.2
Les routes WiFi dans api.py utilisent app.state.wifi_manager
"""

import asyncio
import logging
import os
import threading
import json

import uvicorn

try:
    from . import api as api_module
    from .api import app, WSManager, processing_loop
    from .wifi_manager import WifiManager
    from .tcp_receiver import TCPReceiver
except ImportError:
    import api as api_module
    from api import app, WSManager, processing_loop
    from wifi_manager import WifiManager
    from tcp_receiver import TCPReceiver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NeuroCap")


# ═══════════════════════════════════════════════════════════════
# ÉTAT PARTAGÉ
# ═══════════════════════════════════════════════════════════════
_state = {
    "esp32_connected":   False,
    "esp32_ip":          "",
    "known_networks":    [],
    "last_wifi_result":  None,
    "wifi_configured":   False,
    "esp32_ap_detected": False,
    "esp32_ap_ssid":     "",
}


def _sync_state():
    """Copie l'état dans api_module."""
    api_module.esp32_connected  = _state["esp32_connected"]
    api_module.esp32_ip         = _state["esp32_ip"]
    api_module.known_networks   = _state["known_networks"]
    api_module.last_wifi_result = _state["last_wifi_result"]
    api_module.wifi_configured  = _state["wifi_configured"]
    api_module.esp32_ap_detected = _state["esp32_ap_detected"]
    api_module.esp32_ap_ssid     = _state["esp32_ap_ssid"]


# ═══════════════════════════════════════════════════════════════
# BROADCAST SYNC
# ═══════════════════════════════════════════════════════════════
_loop_ref = None

def bcast_sync(payload: dict):
    if _loop_ref is None or not api_module.ws_manager:
        return
    asyncio.run_coroutine_threadsafe(
        api_module.ws_manager.broadcast(payload), _loop_ref
    )


# ═══════════════════════════════════════════════════════════════
# CALLBACKS WIFI MANAGER
# ═══════════════════════════════════════════════════════════════
def on_esp32_announce(ip: str):
    _state["esp32_ip"] = ip
    _sync_state()
    logger.info(f"[WiFi] ESP32 annoncé: {ip}")


def on_wifi_result(success: bool, ip: str, ssid: str, reason: str):
    _state["last_wifi_result"] = {
        "success": success, "ip": ip, "ssid": ssid, "reason": reason
    }
    if success:
        _state["wifi_configured"] = True
        _state["esp32_ip"] = ip
        logger.info(f"[WiFi] ✓ {ssid} @ {ip}")
    else:
        logger.warning(f"[WiFi] ✗ {ssid}: {reason}")
    _sync_state()


def on_networks_received(networks: list):
    _state["known_networks"] = networks
    _sync_state()
    logger.info(f"[WiFi] Réseaux mémorisés: {networks}")


# ═══════════════════════════════════════════════════════════════
# CALLBACKS TCP RECEIVER
# ═══════════════════════════════════════════════════════════════
def on_tcp_connected(ip: str):
    _state["esp32_connected"] = True
    _state["esp32_ip"] = ip
    _sync_state()


def on_tcp_disconnected():
    # Reset COMPLET a la deconnexion ESP32.
    # wifi_configured repassse a False pour que le frontend
    # reaffiche la page de configuration WiFi automatiquement.
    _state["esp32_connected"]   = False
    _state["esp32_ip"]          = ""
    _state["wifi_configured"]   = False   # force page config
    _state["last_wifi_result"]  = None
    _state["esp32_ap_detected"] = False
    _state["esp32_ap_ssid"]     = ""
    _sync_state()
    # Vider la queue DSP + reset filtres
    try:
        api_module.reset_on_disconnect()
    except Exception:
        pass
    # Notifier le frontend via WebSocket immediatement
    bcast_sync({
        "type":            "esp32_status",
        "connected":       False,
        "wifi_configured": False,
        "esp32_ip":        "",
    })


def on_filter_reset():
    # reset() réinitialise TOUS les états IIR (zi_notch, zi_n100, zi_bp)
    # + le flag _dc_initialized + le CQE + le compteur de warmup.
    # Appeler seulement _dc_initialized laissait les zi_* avec l'ancien DC,
    # causant un artefact transitoire au démarrage de chaque reconnexion.
    try:
        api_module.rt.reset()
        logger.info("[DSP] RealTimeProcessor reset complet (IIR + CQE + warmup)")
    except Exception as e:
        logger.warning(f"[DSP] reset impossible: {e}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
async def main():
    global _loop_ref
    _loop_ref = asyncio.get_event_loop()
    os.makedirs("recordings", exist_ok=True)

    # 1. WSManager
    ws_mgr = WSManager()
    api_module.ws_manager = ws_mgr

    # 2. WifiManager
    wifi_mgr = WifiManager(
        on_esp32_announce    = on_esp32_announce,
        on_wifi_result       = on_wifi_result,
        on_networks_received = on_networks_received,
        bcast_sync_fn        = bcast_sync,
    )

    # 3. TCPReceiver
    tcp_recv = TCPReceiver(
        sample_queue      = api_module.sample_queue,
        electrode_monitor = api_module.electrode_mon,
        on_connected      = on_tcp_connected,
        on_disconnected   = on_tcp_disconnected,
        filter_reset_cb   = on_filter_reset,
        bcast_sync_fn     = bcast_sync,
    )

    # 4. Injecter dans api_module
    api_module.loop = _loop_ref

    # 5. Injecter WifiManager dans app.state (accès par les routes api.py)
    app.state.wifi_manager = wifi_mgr

    # 6. Démarrer threads réseau
    wifi_mgr.start()
    tcp_recv.start()

    # 7. Mise à jour périodique de esp32_ap_detected depuis wifi_mgr
    async def _poll_ap_status():
        while True:
            _state["esp32_ap_detected"] = wifi_mgr.esp32_ap_detected
            _state["esp32_ap_ssid"]     = wifi_mgr.esp32_ap_ssid
            _sync_state()
            await asyncio.sleep(2)

    # 8. Infos démarrage
    local_ip = WifiManager.get_local_ip()
    print("\n" + "═" * 55)
    print("  NeuroCap EEG v7.2 — WiFi Setup First")
    print(f"  API  : http://{local_ip}:8765/api/status")
    print(f"  WS   : ws://{local_ip}:8765/ws")
    print(f"  Docs : http://{local_ip}:8765/docs")
    print("═" * 55 + "\n")

    # 9. Lancer serveur + DSP + polling
    # Tuer automatiquement tout process qui occupe le port 8000
    import socket as _socket
    import subprocess as _sub
    import sys as _sys

    def _kill_port(port: int):
        """Libere le port sur Windows et Linux avant de bind."""
        try:
            # Test rapide : le port est-il libre ?
            probe = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            probe.settimeout(0.2)
            result = probe.connect_ex(("127.0.0.1", port))
            probe.close()
            if result != 0:
                return  # Port libre, rien a faire

            # Windows
            import platform
            if platform.system() == "Windows":
                out = _sub.check_output(
                    f"netstat -ano | findstr :{port}", shell=True
                ).decode(errors="replace")
                pids = set()
                for line in out.splitlines():
                    parts = line.strip().split()
                    if parts and parts[-1].isdigit():
                        pids.add(parts[-1])
                for pid in pids:
                    _sub.call(f"taskkill /PID {pid} /F", shell=True,
                              stdout=_sub.DEVNULL, stderr=_sub.DEVNULL)
                    logger.warning(f"[NET] Port {port} libere (PID {pid} tue)")
            else:
                # Linux / Mac
                _sub.call(f"fuser -k {port}/tcp", shell=True,
                          stdout=_sub.DEVNULL, stderr=_sub.DEVNULL)
                logger.warning(f"[NET] Port {port} libere (fuser -k)")

            import time as _time
            _time.sleep(0.5)  # laisser l OS liberer le port
        except Exception as e:
            logger.warning(f"[NET] Impossible de liberer le port {port}: {e}")

    _kill_port(8765)

    config = uvicorn.Config(app, host="0.0.0.0", port=8765,
                            log_level="info", reload=False)
    server = uvicorn.Server(config)

    await asyncio.gather(
        server.serve(),
        processing_loop(),
        _poll_ap_status(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Arrêt NeuroCap")