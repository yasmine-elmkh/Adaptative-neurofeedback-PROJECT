# backend/utils/constants.py
"""
Constantes NeuroCap EEG
"""

# Fréquence d'échantillonnage
FS = 250  # Hz

# Gain total de la chaîne d'amplification AD8232
# L'ADS1115 mesure la tension amplifiée (en µV ADC). Diviser par ce gain
# dans le pipeline DSP pour retrouver les µV EEG réels au scalp.
#
# Comment calculer : G = (1 + 470kΩ/R_G) pour l'INA interne × gain du filtre HP.
# Valeurs communes NeuroCap :
#   R_G = 470Ω  → G_INA ≈ 1000  (EEG typique)
#   R_G = 4.7kΩ → G_INA ≈ 100
# Calibration rapide : RMS cible = 5-50 µV au repos (yeux fermés, sans cligner).
AD8232_GAIN = 1000.0

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