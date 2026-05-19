# backend/dsp/__init__.py
"""
Module DSP NeuroCap EEG v8.0

Exports publics :
  ElectrodeMonitor          — bit LO AD8232
  ArtifactDetector          — rejet/marquage artefacts
  ContactQualityEstimator   — score 0-100 qualité contact (NOUVEAU)
  FilterBank                — Golden Filter [1-45 Hz]
  wavelet_denoise_adaptive  — alias _wavelet_denoise (rétrocompat)
  higuchi_fd                — HFD Higuchi monocanal
  compute_sef95             — Spectral Edge Frequency 95 %
  extract_features          — vecteur 25+ features
  BANDS_V8                  — définition bandes v8.0 (NOUVEAU)
  PreprocessingPipeline     — filtrage + baseline spectrale
  EpochExtractor            — fenêtrage glissant 4 s / 75 %
  RealTimeProcessor         — point d'entrée DSP
  CognitiveStateClassifier  — classification Z-score + hystérésis (NOUVEAU)

Suppressions vs original :
  build_fractal_graph       — vecteur FD constant → bruit pur
  extract_fractal_vector    — idem
  compute_pac_proxy         — non conforme Tort 2010 MI
"""

from .artifacts import ElectrodeMonitor, ArtifactDetector, ContactQualityEstimator
from .filters   import FilterBank, wavelet_denoise_adaptive
from .features  import higuchi_fd, compute_sef95, extract_features, BANDS_V8
from .epochs    import PreprocessingPipeline, EpochExtractor
from .processor import RealTimeProcessor, CognitiveStateClassifier

__all__ = [
    "ElectrodeMonitor",
    "ArtifactDetector",
    "ContactQualityEstimator",
    "FilterBank",
    "wavelet_denoise_adaptive",
    "higuchi_fd",
    "compute_sef95",
    "extract_features",
    "BANDS_V8",
    "PreprocessingPipeline",
    "EpochExtractor",
    "RealTimeProcessor",
    "CognitiveStateClassifier",
]