# backend/tcp_receiver.py
"""
Récepteur TCP pour streaming EEG depuis ESP32.
Compatible firmware minimal (timestamp_ms,raw_adc,voltage_mV,pkt_id)
et firmware complet (timestamp_us,raw_adc,voltage_mV,batt_V,lo_plus,lo_minus,lead_off,pkt_id).
"""

import socket
import threading
import logging

logger = logging.getLogger("NeuroCap")

try:
    from utils.constants import AD8232_GAIN
except ImportError:
    AD8232_GAIN = 100.0  # fallback si constants non disponible

TCP_PORT = 9000


class DCRemover:
    """
    Suppression DC adaptative par filtre IIR premier ordre.
    Équivalent filtre passe-haut ~0.05 Hz (laisse passer delta→gamma).
    alpha = exp(-2*pi*0.05/250) ≈ 0.9987
    Ref : Widmann et al. 2015 — recommandation EEG temps réel.
    """
    def __init__(self, alpha: float = 0.9987):
        self._alpha = alpha
        self._dc    = None

    def remove(self, uv: float) -> float:
        if self._dc is None:
            self._dc = uv
        self._dc = self._alpha * self._dc + (1.0 - self._alpha) * uv
        return uv - self._dc

    def reset(self):
        self._dc = None


def parse_csv_line(line: str, lc: list) -> dict | None:
    """
    Parse une ligne CSV de l'ESP32.
    Supporte les deux formats firmware :
      Minimal  : timestamp_ms, raw_adc, voltage_mV, pkt_id
      Complet  : timestamp_us, raw_adc, voltage_mV, batt_V, lo_plus, lo_minus, lead_off, pkt_id
    """
    if not line or line.startswith("#"):
        return None
    try:
        parts = line.split(",")
        if len(parts) < 4:
            return None

        ts      = int(parts[0])
        raw_adc = int(parts[1])
        mv      = float(parts[2])

        # Firmware minimal : 4 colonnes
        if len(parts) == 4:
            return {
                "ts":      ts,
                "uv":      mv * 1000.0,   # mV → µV pour compatibilité DSP
                "raw_adc": raw_adc,
                "batt_V":  0.0,
                "lo_plus":  0,
                "lo_minus": 0,
                "pkt_id":  int(parts[3]),
            }

        # Firmware complet : 8 colonnes
        batt_V   = float(parts[3]) if parts[3] else 0.0
        lo_plus  = int(parts[4])   if parts[4] else 0
        lo_minus = int(parts[5])   if parts[5] else 0
        pkt_id   = int(parts[7])   if len(parts) > 7 and parts[7] else -1

        lc[0] += 1
        return {
            "ts":      ts,
            "uv":      mv,         # déjà en µV dans firmware complet (voltage_mV = raw * ADS_LSB_UV)
            "raw_adc": raw_adc,
            "batt_V":  batt_V,
            "lo_plus":  lo_plus,
            "lo_minus": lo_minus,
            "pkt_id":  pkt_id,
        }
    except Exception as e:
        logger.debug(f"[TCP] Parse error: {e} | line='{line}'")
        return None


class TCPReceiver:
    """
    Serveur TCP qui accepte la connexion de l'ESP32 et parse le flux CSV.
    Callbacks injectés par assembly.py pour découplage total.
    """

    def __init__(self, sample_queue, electrode_monitor,
                 on_connected, on_disconnected,
                 filter_reset_cb=None,
                 bcast_sync_fn=None):
        """
        Args:
            sample_queue:      queue.Queue — échantillons parsés
            electrode_monitor: ElectrodeMonitor — mise à jour lo_plus/lo_minus
            on_connected:      callback(ip: str)
            on_disconnected:   callback()
            filter_reset_cb:   callback() optionnel — reset filtres IIR
            bcast_sync_fn:     callback(payload: dict) — broadcast WebSocket
        """
        self.sample_queue      = sample_queue
        self.electrode_monitor = electrode_monitor
        self.on_connected      = on_connected
        self.on_disconnected   = on_disconnected
        self.filter_reset_cb   = filter_reset_cb
        self.bcast_sync        = bcast_sync_fn or (lambda _: None)

        self._connected  = False
        self._client_ip  = ""
        self._dc_remover = DCRemover()

    # ────────────────────────────────────────────────────────────
    def start(self):
        threading.Thread(target=self._tcp_thread, daemon=True).start()
        logger.info(f"[TCP] TCPReceiver démarré — écoute :{TCP_PORT}")

    # ────────────────────────────────────────────────────────────
    def _tcp_thread(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        srv.bind(("0.0.0.0", TCP_PORT))
        srv.listen(5)
        srv.settimeout(1.0)
        logger.info(f"[TCP] En écoute sur :{TCP_PORT}")

        while True:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            except Exception:
                break

            client_ip = addr[0]

            # Rejeter auto-connexion AP (ESP32 se connecte à lui-même via 192.168.4.1)
            if client_ip == "192.168.4.1":
                logger.warning("[TCP] Connexion 192.168.4.1 rejetée (ESP32 self-AP)")
                conn.close()
                continue

            # Connexion valide
            self._connected = True
            self._client_ip = client_ip
            logger.info(f"[TCP] ESP32 connecté: {client_ip}")

            # Reset filtres IIR et DC remover (évite artefact transitoire au démarrage)
            if self.filter_reset_cb:
                try:
                    self.filter_reset_cb()
                except Exception:
                    pass
            self._dc_remover.reset()

            self.on_connected(client_ip)
            self.bcast_sync({"type": "esp32_status", "connected": True, "ip": client_ip})

            conn.settimeout(5.0)   # 5s : detection rapide deconnexion ESP32
            buf   = ""
            lc    = [0]

            while True:
                try:
                    data = conn.recv(4096).decode(errors="replace")
                    if not data:
                        break
                    buf += data
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        sample = parse_csv_line(line.strip(), lc)
                        if sample:
                            # 1. Suppression DC adaptative (dérive électrode, offset MidRail résiduel)
                            sample["uv"] = self._dc_remover.remove(sample["uv"])
                            # 2. Normalisation gain AD8232 : voltage ADC µV → µV EEG au scalp
                            #    Sans cette division, les seuils DSP (EXTREME_PEAK 500 µV, etc.)
                            #    sont 100× trop bas et rejettent 100% des époques.
                            sample["uv"] /= AD8232_GAIN
                            # Mettre à jour électrodes
                            self.electrode_monitor.update(
                                sample.get("lo_plus", 0),
                                sample.get("lo_minus", 0)
                            )
                            # Enqueue
                            try:
                                self.sample_queue.put_nowait(sample)
                            except Exception:
                                pass  # queue pleine → drop
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"[TCP] Recv error: {e}")
                    break

            conn.close()
            self._connected = False
            logger.info(f"[TCP] ESP32 déconnecté ({lc[0]} samples reçus)")
            self.on_disconnected()
            self.bcast_sync({"type": "esp32_status", "connected": False})

    # ────────────────────────────────────────────────────────────
    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def client_ip(self) -> str:
        return self._client_ip