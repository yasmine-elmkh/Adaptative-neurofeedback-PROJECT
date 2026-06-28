"""
OllamaEmbedder — Convertit du texte en vecteur 768d via Ollama nomic-embed-text.
Optionnel : si Ollama n'est pas disponible, le retrieval repasse en BM25 pur.
"""

import os
import logging
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)

OLLAMA_BASE = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM   = 768


class OllamaEmbedder:
    """
    Produit des embeddings 768d via Ollama nomic-embed-text.

    Cycle de vie :
      - Premier appel à embed() → test de disponibilité automatique
      - Si Ollama absent → retourne None silencieusement (fallback BM25)
      - available : bool — True si le dernier appel a réussi
    """

    def __init__(
        self,
        base_url: str = OLLAMA_BASE,
        model: str    = EMBED_MODEL,
    ) -> None:
        self.base_url = base_url
        self.model    = model
        self._ok: Optional[bool] = None

    def embed(self, text: str) -> Optional[List[float]]:
        """Retourne un vecteur de 768 floats, ou None si Ollama indisponible."""
        try:
            r = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=10,
            )
            if r.status_code == 200:
                vec = r.json().get("embedding")
                if vec and len(vec) == EMBED_DIM:
                    self._ok = True
                    return vec
        except Exception:
            pass
        self._ok = False
        return None

    @property
    def available(self) -> bool:
        """Vérifie la disponibilité Ollama (lazy, test unique au premier appel)."""
        if self._ok is None:
            self.embed("test")
        return bool(self._ok)
