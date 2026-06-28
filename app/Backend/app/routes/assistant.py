"""
NeuroCap — Route Assistant RAG
================================
POST /api/assistant/ask      – Q&A conversationnelle (RAG + contexte patient)
POST /api/assistant/explain  – Explication complète du dashboard patient
POST /api/assistant/feedback – Enregistrement du feedback 👍/👎

Architecture :
  build_user_context()   → Assistant_rag.context (module racine du projet)
  RAGService             → Assistant_rag.service
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import AssistantRequest, AssistantResponse, AssistantFeedback
from app.services.rag_service import RAGService, build_user_context

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])

_rag = RAGService()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/ask", response_model=AssistantResponse)
async def ask(
    data: AssistantRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Q&A conversationnelle RAG.

    1. Agrège le contexte patient complet depuis Supabase
    2. Fusionne avec le snapshot EEG optionnel envoyé par le client
    3. Recherche sémantique dans knowledge_documents (pgvector)
    4. Génère une réponse ancrée via Ollama mistral
    """
    ctx = await build_user_context(current_user["id"], db)

    # Le client peut envoyer un snapshot EEG live (ex: métriques temps réel)
    # Ces valeurs n'écrasent pas les données serveur
    if data.eeg_context:
        for k, v in data.eeg_context.items():
            if k not in ctx or ctx[k] is None:
                ctx[k] = v

    from Assistant_rag.retrieval.search import search_kb
    docs    = await search_kb(data.question, db, _rag.embedder, top_k=3)
    sources = [d["title"] for d in docs]
    answer  = await _rag.answer_question(data.question, ctx, db)

    return AssistantResponse(answer=answer, sources=sources)


@router.post("/explain", response_model=AssistantResponse)
async def explain_dashboard(
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Explication complète et structurée du dashboard patient.

    Appel depuis le bouton "Analyser mes résultats" dans le frontend.
    Pas de body nécessaire — tout est récupéré côté serveur.
    Retourne une réponse en 3 sections : résultats / insights / recommandations.
    """
    snapshot = await build_user_context(current_user["id"], db)
    result   = await _rag.explain_dashboard(snapshot, db)
    return AssistantResponse(answer=result["response"], sources=result["sources"])


@router.post("/feedback", status_code=204)
async def record_feedback(
    data: AssistantFeedback,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Enregistre le feedback 👍/👎 sur une réponse (audit_logs)."""
    try:
        await db.table("audit_logs").insert({
            "id":         str(uuid.uuid4()),
            "user_id":    current_user["id"],
            "action":     f"ASSISTANT_FEEDBACK_{data.feedback.upper()}",
            "details":    f"Q: {(data.question or '')[:200]} | A: {(data.answer or '')[:200]}",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception:
        pass  # non-bloquant
