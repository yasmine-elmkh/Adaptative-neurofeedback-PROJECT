"""
Hybrid Search — pgvector (sémantique) + BM25 (lexical) avec reranking.

Score final = α × score_vectoriel  +  (1-α) × score_BM25
              α = 0.7 par défaut

Fallback automatique :
  - Si Ollama absent    → pgvector sauté, BM25 seul sur KB in-memory
  - Si Supabase vide    → BM25 seul sur KB in-memory

Référence : Ng et al., NEJM AI 2025, §Limitations :
  "hybrid search combining vector and keyword methods can enhance relevance."
"""

import logging
from typing import Dict, List

from supabase import AsyncClient

from .embedder import OllamaEmbedder
from .bm25 import bm25_score
from ..kb.knowledge_base import KNOWLEDGE_BASE

logger = logging.getLogger(__name__)


async def search_kb(
    query: str,
    db: AsyncClient,
    embedder: OllamaEmbedder,
    top_k: int = 4,
    vector_weight: float = 0.7,
) -> List[Dict]:
    """
    Recherche hybride dans la base de connaissances.

    Étapes :
      1. Embed la requête → vecteur 768d (Ollama)
      2. Requête pgvector via Supabase RPC `match_documents`
      3. Reranking : final_score = 0.7×vect + 0.3×BM25
      4. Fallback KB in-memory si pgvector indisponible

    Retourne les top_k documents triés par final_score décroissant.
    """
    vec = embedder.embed(query)
    supabase_docs: List[Dict] = []

    # ── Étape 1 : Tentative pgvector Supabase ────────────────────────────────
    if vec is not None:
        try:
            resp = await db.rpc(
                "match_documents",
                {
                    "query_embedding": vec,
                    "match_threshold":  0.3,
                    "match_count":      top_k + 2,
                },
            ).execute()
            supabase_docs = resp.data or []
        except Exception as exc:
            logger.warning("pgvector indisponible: %s — fallback BM25 in-memory", exc)

    # ── Étape 2 : Hybrid reranking sur docs Supabase ─────────────────────────
    if supabase_docs:
        for doc in supabase_docs:
            kw   = bm25_score(query, f"{doc['title']} {doc['content']}")
            vsim = doc.get("similarity", 0.0)
            doc["final_score"] = vector_weight * vsim + (1 - vector_weight) * kw
        supabase_docs.sort(key=lambda x: x["final_score"], reverse=True)
        return supabase_docs[:top_k]

    # ── Étape 3 : Fallback KB in-memory + BM25 pur ───────────────────────────
    logger.info("KB in-memory utilisée (Supabase knowledge_documents non peuplée)")
    scored = []
    for doc in KNOWLEDGE_BASE:
        score = bm25_score(query, f"{doc['title']} {doc['content']}")
        if score > 0:
            scored.append({**doc, "similarity": score, "final_score": score})

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k]
