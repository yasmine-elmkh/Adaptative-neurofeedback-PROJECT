# backend/utils/constants.py
"""
Constantes NeuroCap EEG
"""

# Fréquence d'échantillonnage
FS = 250  # Hz

# Bandes de fréquence EEG (Hz)
BANDS = {
    'delta':    (0.5, 4),
    'theta':    (4, 8),
    'alpha':    (8, 12),
    'beta':     (12, 30),
    'gamma':    (30, 45),
}

# Époques
EPOCH_SEC   = 2.0   # durée en secondes
EPOCH_SAMP  = int(FS * EPOCH_SEC)  # échantillons par époque
EPOCH_STEP  = int(FS * 1.0)        # pas entre époques (1s overlap)

# Ports réseau
UDP_LISTEN_PORT  = 4320  # Annonces ESP32
UDP_RESPOND_PORT = 4321  # Réponses serveur
UDP_CONFIG_PORT  = 4322  # Config WiFi
UDP_STATUS_PORT  = 4323  # Statut WiFi
TCP_PORT         = 9000  # Streaming EEG

# Dossiers
REC_DIR = "recordings"

# Paramètres DSP
EPOCH_DURATION = 2.0  # secondes
OVERLAP_RATIO  = 0.5  # 50% overlap

# Seuils artefacts
EMG_THRESHOLD = 50.0  # µV pour EMG
LO_THRESHOLD  = 0.9   # seuil connexion électrode

# Paramètres WiFi
WIFI_TIMEOUT = 30  # secondes
OVERLAP_RATIO  = 0.5  # 50% overlap

# Seuils artefacts
EMG_THRESHOLD = 50.0  # µV pour EMG
LO_THRESHOLD  = 0.9   # seuil connexion électrode

# Paramètres WiFi
WIFI_TIMEOUT = 30  # secondes