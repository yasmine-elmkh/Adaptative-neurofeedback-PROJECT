"""
NeuroCap — Route Assistant RAG
POST /api/assistant/ask      → Répondre à une question EEG/neurofeedback
POST /api/assistant/feedback → Enregistrer le feedback utilisateur (👍/👎)
"""

from fastapi import APIRouter, Depends
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import AssistantRequest, AssistantResponse, AssistantFeedback
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])
_rag = RAGService()


@router.post("/ask", response_model=AssistantResponse)
async def ask(
    data: AssistantRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Répond à une question EEG via le système RAG.
    Enrichit la réponse avec le profil EEG complet et l'historique de l'utilisateur.
    """
    # Sessions history
    sessions_resp = await (
        db.table("sessions")
        .select("id,score,avg_tbr,avg_concentration,avg_stress,created_at,objective")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    sessions_data = sessions_resp.data or []
    total_sessions = len(sessions_data)

    scores = [s["score"] for s in sessions_data if s.get("score") is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    # Trend: compare last 3 vs previous 3
    score_trend = None
    if len(scores) >= 6:
        recent = sum(scores[:3]) / 3
        older  = sum(scores[3:6]) / 3
        score_trend = round((recent - older) / older * 100, 1) if older else None

    # Full EEG profile
    profile_resp = await (
        db.table("eeg_profiles")
        .select("profile_type,iapf,baseline_tbr,baseline_alpha,baseline_beta,baseline_theta,reactivity_score,palier,current_threshold")
        .eq("user_id", current_user["id"])
        .execute()
    )
    profile_data = profile_resp.data[0] if profile_resp.data else {}

    user_context = {
        "total_sessions": total_sessions,
        "avg_score": avg_score,
        "score_trend": score_trend,
        "profile": profile_data.get("profile_type", "B"),
        "iapf": profile_data.get("iapf"),
        "baseline_tbr": profile_data.get("baseline_tbr"),
        "baseline_alpha": profile_data.get("baseline_alpha"),
        "palier": profile_data.get("palier"),
        "reactivity_score": profile_data.get("reactivity_score"),
        "last_objective": sessions_data[0].get("objective") if sessions_data else None,
        "last_avg_tbr": sessions_data[0].get("avg_tbr") if sessions_data else None,
    }

    # Merge client-supplied EEG snapshot (takes lower priority than server data)
    if data.eeg_context:
        for k, v in data.eeg_context.items():
            if k not in user_context or user_context[k] is None:
                user_context[k] = v

    answer = _rag.answer_question(data.question, user_context)

    docs = _rag.kb.search(data.question, top_k=3)
    sources = [d["title"] for d in docs]

    return AssistantResponse(answer=answer, sources=sources)


@router.post("/feedback", status_code=204)
async def record_feedback(
    data: AssistantFeedback,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Enregistre le feedback (👍/👎) de l'utilisateur sur une réponse.
    Stocké dans audit_logs pour analyse future.
    """
    import uuid
    from datetime import datetime, timezone

    try:
        await db.table("audit_logs").insert({
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "action": f"ASSISTANT_FEEDBACK_{data.feedback.upper()}",
            "details": f"Q: {(data.question or '')[:200]} | A: {(data.answer or '')[:200]}",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception:
        pass  # non-blocking
