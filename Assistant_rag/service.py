"""
RAGService — Orchestrateur principal du pipeline RAG NeuroCap.

Pipeline conforme à Ng et al., NEJM AI 2025;2(1) :
  1. RETRIEVAL  : Hybrid Search (pgvector + BM25) via search_kb()
  2. AUGMENTATION : Context = KB docs + profil patient (Supabase)
  3. GENERATION : LLMChain (DeepSeek → Groq → Ollama → fallback)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from supabase import AsyncClient

from .kb.knowledge_base import fmt_kb
from .retrieval.embedder import OllamaEmbedder
from .retrieval.search import search_kb
from .generation.llm_chain import LLMChain
from .generation.prompts import SYSTEM_PROMPT, fmt_patient

logger = logging.getLogger(__name__)


class RAGService:
    """
    Pipeline RAG complet.

    answer_question(question, user_context, db)
        Q&A conversationnelle: récupère le contexte KB + patient, génère via LLMChain.

    explain_dashboard(snapshot, db)
        Explication structurée en 3 sections pour le dashboard patient.
        Utilise multi-query retrieval pour couvrir tous les métriques.
    """

    def __init__(self) -> None:
        self.embedder = OllamaEmbedder()
        self.llm      = LLMChain()

    # ── Q&A conversationnelle ──────────────────────────────────────────────────

    async def answer_question(
        self,
        question: str,
        user_context: Optional[Dict],
        db: AsyncClient,
    ) -> str:
        docs        = await search_kb(question, db, self.embedder, top_k=4)
        kb_ctx      = fmt_kb(docs)
        patient_ctx = fmt_patient(user_context) if user_context else ""
        user_prompt = (
            f"{kb_ctx}\n\n{patient_ctx}\n\n"
            f"Question du patient : {question}\n\nRéponse :"
        )
        response, model = self.llm.generate(SYSTEM_PROMPT, user_prompt, max_tokens=500)
        logger.info("RAG answer via %s | docs=%d", model, len(docs))
        return response

    # ── Explication complète du dashboard ─────────────────────────────────────

    async def explain_dashboard(
        self,
        snapshot: Dict,
        db: AsyncClient,
    ) -> Dict:
        """
        Explication en 3 sections : résultats / insights / recommandations.
        Multi-query retrieval ciblé sur les métriques réels du patient.
        """
        queries = [
            "résultats TBR concentration stress score séance profil EEG",
            f"profil {snapshot.get('profile', 'B')} palier {snapshot.get('palier', 'P1')} progression",
        ]
        tbr    = snapshot.get("last_avg_tbr")
        base   = snapshot.get("baseline_tbr")
        conc   = snapshot.get("avg_concentration_pct") or snapshot.get("last_concentration_pct")
        stress = snapshot.get("avg_stress_pct") or snapshot.get("last_stress_pct")

        if tbr and base and tbr > base * 1.2:
            queries.append("TBR élevé stress réduction conseils respiration")
        if conc is not None and conc < 60:
            queries.append("concentration faible améliorer exercices conseils")
        if stress is not None and stress > 30:
            queries.append("stress élevé relaxation techniques")
        queries.append("protocole 15 séances progression attendue habitudes cerveau")

        docs: List[Dict] = []
        seen: set = set()
        for q in queries:
            for d in await search_kb(q, db, self.embedder, top_k=3):
                if d["id"] not in seen:
                    docs.append(d)
                    seen.add(d["id"])
            if len(docs) >= 8:
                break

        user_prompt = (
            f"{fmt_kb(docs)}\n\n"
            f"{fmt_patient(snapshot)}\n\n"
            "Le patient demande une explication complète de ses résultats dashboard NeuroCap.\n"
            "Génère une réponse structurée en 3 parties :\n\n"
            "**1. Ce que montrent vos résultats**\n"
            "[Explique chaque métrique clé en le comparant à la référence du patient]\n\n"
            "**2. Points clés à retenir**\n"
            "[2–3 insights personnalisés, motivants, basés sur les données réelles]\n\n"
            "**3. Prochaines étapes recommandées**\n"
            "[2–3 actions concrètes adaptées au profil, palier et résultats actuels]\n\n"
            "Réponse :"
        )
        response, model = self.llm.generate(SYSTEM_PROMPT, user_prompt, max_tokens=800)
        logger.info("Dashboard explain via %s | docs=%d", model, len(docs))

        return {
            "response": response,
            "sources":  [d["title"] for d in docs[:6]],
            "model":    model,
            "snapshot": {
                "total_sessions":    snapshot.get("total_sessions"),
                "avg_score":         snapshot.get("avg_score"),
                "profile":           snapshot.get("profile"),
                "palier":            snapshot.get("palier"),
                "avg_concentration": conc,
                "avg_stress":        stress,
                "tbr_ratio":         round(tbr / base, 2) if tbr and base else None,
            },
        }
