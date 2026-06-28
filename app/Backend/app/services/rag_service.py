"""
Thin wrapper — délègue tout à Assistant_rag (module racine du projet).
"""

import sys
from pathlib import Path

# Ajoute la racine du projet au path pour que `import Assistant_rag` fonctionne
_project_root = Path(__file__).resolve().parents[4]  # app/Backend/app/services → racine
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from Assistant_rag import RAGService, build_user_context  # noqa: F401

__all__ = ["RAGService", "build_user_context"]
