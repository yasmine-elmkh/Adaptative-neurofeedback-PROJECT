"""
Assistant_rag — Module RAG autonome pour NeuroCoach
====================================================
Architecture : Retrieval → Augmentation → Generation
Référence    : Ng et al., "RAG in Health Care", NEJM AI 2025;2(1)

Usage depuis l'app :
    from Assistant_rag.service import RAGService
    from Assistant_rag.retrieval.search import search_kb
"""

from .service import RAGService
from .context.patient_context import build_user_context

__all__ = ["RAGService", "build_user_context"]
