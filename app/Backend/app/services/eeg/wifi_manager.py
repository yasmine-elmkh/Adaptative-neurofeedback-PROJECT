# backend/wifi_manager.py
"""
Gestionnaire WiFi pour communication avec ESP32.
Gère : découverte AP, configuration WiFi, réseaux mémorisés, découverte STA.
"""

import socket
import time
import threading
import logging

logger = logging.getLogger("NeuroCap")

UDP_LISTEN_PORT = 4322   # Annonces ESP32 (AP et STA)
UDP_CONFIG_PORT = 4320   # Envoie config WiFi à l'ESP32
UDP_STATUS_PORT = 4323   # Reçoit WIFI_OK / WIFI_FAILED / NETWORKS


class WifiManager:
    def __init__(self, on_esp32_announce, on_wifi_result, on_networks_received,
                 bcast_sync_fn=None):
        self.on_esp32_announce    = on_esp32_announce
        self.on_wifi_result       = on_wifi_result
        self.on_networks_received = on_networks_received
        self.bcast_sync           = bcast_sync_fn or (lambda _: None)

        self.known_networks   = []
        self.last_wifi_result = None
        self.esp32_ap_detected = False   # ← nouveau : ESP32 détecté en mode AP
        self.esp32_ap_ssid     = ""      # ← nouveau : SSID de l'AP

        self._sock_listen = None
        self._sock_status = None
        self._sock_send   = None

    def start(self):
        self._sock_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sock_listen.bind(("0.0.0.0", UDP_LISTEN_PORT))
        except Exception as e:
            logger.warning(f"[UDP] bind :{UDP_LISTEN_PORT} impossible — {e}")
        self._sock_listen.settimeout(0.5)

        self._sock_status = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock_status.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sock_status.bind(("0.0.0.0", UDP_STATUS_PORT))
        except Exception as e:
            logger.warning(f"[UDP] bind :{UDP_STATUS_PORT} impossible — {e}")
        self._sock_status.settimeout(0.5)

        self._sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        threading.Thread(target=self._udp_thread, daemon=True).start()
        logger.info(f"[WiFi] WifiManager démarré — :{UDP_LISTEN_PORT} + :{UDP_STATUS_PORT}")

    def _udp_thread(self):
        last_bcast   = 0.0
        last_net_req = 0.0

        while True:
            local_ip    = self.get_local_ip()
            respond_msg = f"EEG_SERVER_IP:{local_ip}".encode()

            # ── Annonces ESP32 (port 4322) ───────────────────────
            try:
                data, addr = self._sock_listen.recvfrom(256)
                msg = data.decode(errors="replace").strip()
                logger.info(f"[UDP] ← {addr[0]}:{addr[1]} → {msg}")

                if msg.startswith("ESP_EEG_AP:"):
                    # ESP32 en mode AP (pas encore connecté au WiFi)
                    parts = msg.split(":")
                    ap_ssid = parts[1] if len(parts) > 1 else ""
                    self.esp32_ap_detected = True
                    self.esp32_ap_ssid = ap_ssid
                    self.on_esp32_announce(addr[0])
                    self.bcast_sync({
                        "type": "esp32_ap_detected",
                        "ip": addr[0],
                        "ssid": ap_ssid,
                    })
                    logger.info(f"[UDP] ESP32 AP détecté: {ap_ssid}")

                elif msg.startswith("ESP_EEG:"):
                    # ESP32 en mode STA (connecté au WiFi)
                    self.esp32_ap_detected = False
                    self.on_esp32_announce(addr[0])
                    self.bcast_sync({"type": "esp32_announce", "ip": addr[0]})

                # Répondre EEG_SERVER_IP sur le port SOURCE (addr[1])
                self._sock_send.sendto(respond_msg, (addr[0], addr[1]))
                logger.info(f"[UDP] → {addr[0]}:{addr[1]} → {respond_msg.decode()}")

            except socket.timeout:
                pass
            except Exception as e:
                logger.debug(f"[UDP] Listen error: {e}")

            # ── Statut WiFi (port 4323) ──────────────────────────
            try:
                data, addr = self._sock_status.recvfrom(512)
                msg = data.decode(errors="replace").strip()
                logger.info(f"[UDP] Statut ← {addr[0]}: {msg}")

                if msg.startswith("WIFI_OK:"):
                    parts = msg.split(":", 2)
                    ip   = parts[1] if len(parts) > 1 else ""
                    ssid = parts[2] if len(parts) > 2 else ""
                    self.last_wifi_result = {"success": True, "ip": ip, "ssid": ssid}
                    self.on_wifi_result(True, ip, ssid, "")
                    self.bcast_sync({
                        "type": "wifi_result", "success": True, "ip": ip, "ssid": ssid
                    })

                elif msg.startswith("WIFI_FAILED:"):
                    parts  = msg.split(":", 2)
                    ssid   = parts[1] if len(parts) > 1 else ""
                    reason = parts[2] if len(parts) > 2 else "unknown"
                    self.last_wifi_result = {"success": False, "ssid": ssid, "reason": reason}
                    self.on_wifi_result(False, "", ssid, reason)
                    self.bcast_sync({
                        "type": "wifi_result", "success": False,
                        "ssid": ssid, "reason": reason
                    })

                elif msg.startswith("NETWORKS:"):
                    nets_str = msg[9:] if len(msg) > 9 else ""
                    nets = [n.strip() for n in nets_str.split(",") if n.strip()]
                    self.known_networks = nets
                    self.on_networks_received(nets)
                    logger.info(f"[UDP] Réseaux mémorisés: {nets}")

            except socket.timeout:
                pass
            except Exception as e:
                logger.debug(f"[UDP] Status error: {e}")

            # ── Broadcast périodique serveur (toutes les 2s) ─────
            if time.time() - last_bcast >= 2.0:
                last_bcast = time.time()
                try:
                    self._sock_send.sendto(respond_msg, ("<broadcast>", UDP_LISTEN_PORT))
                except Exception:
                    pass

            # ── Demander réseaux mémorisés (toutes les 5s) ──────
            if time.time() - last_net_req >= 5.0:
                last_net_req = time.time()
                for target in [
                    ("192.168.4.1", UDP_CONFIG_PORT),
                    ("192.168.4.255", UDP_CONFIG_PORT),
                ]:
                    try:
                        self._sock_send.sendto(b"GET_NETWORKS", target)
                    except Exception:
                        pass

    # ── Commandes vers ESP32 ──────────────────────────────────────

    def send_wifi_config(self, ssid: str, password: str) -> dict:
        if not ssid:
            return {"error": "SSID requis"}

        msg = f"WIFI_CONFIG:{ssid}:{password}".encode()
        local_ip = self.get_local_ip()

        targets = [
            ("192.168.4.1",     UDP_CONFIG_PORT),
            ("192.168.4.255",   UDP_CONFIG_PORT),
            ("255.255.255.255", UDP_CONFIG_PORT),
        ]

        sent = 0
        for t in targets:
            try:
                self._sock_send.sendto(msg, t)
                sent += 1
                logger.info(f"[WiFi] Config → {t[0]}: {ssid}")
            except Exception as e:
                logger.warning(f"[WiFi] Échec → {t}: {e}")

        # Retransmission 2× pour fiabilité
        for _ in range(2):
            time.sleep(0.3)
            for t in targets[:2]:
                try:
                    self._sock_send.sendto(msg, t)
                except Exception:
                    pass

        return {"message": f"Config envoyée pour '{ssid}'", "sent_to": sent,
                "local_ip": local_ip}

    def send_use_saved(self, ssid: str):
        msg = f"WIFI_USE_SAVED:{ssid}".encode()
        for t in [
            ("192.168.4.1", UDP_CONFIG_PORT),
            ("192.168.4.255", UDP_CONFIG_PORT),
        ]:
            try:
                self._sock_send.sendto(msg, t)
            except Exception as e:
                logger.warning(f"[WiFi] use_saved → {t}: {e}")
        logger.info(f"[WiFi] WIFI_USE_SAVED → '{ssid}'")

    def send_reset(self):
        for t in [
            ("192.168.4.1", UDP_CONFIG_PORT),
            ("255.255.255.255", UDP_CONFIG_PORT),
        ]:
            try:
                self._sock_send.sendto(b"RESET_WIFI", t)
            except Exception:
                pass
        logger.info("[WiFi] RESET_WIFI envoyé")

    @staticmethod
    def get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"