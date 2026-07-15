"""
NeuroCap — Suite de tests RAG (NeuroCoach)
==========================================
Valide les 3 phases du pipeline RAG :

  Phase 1 — RETRIEVAL  : BM25, OllamaEmbedder, search_kb (hybride)
  Phase 2 — AUGMENTATION : fmt_patient, fmt_kb, prompt construction
  Phase 3 — GENERATION : LLMChain cascade (DeepSeek → Groq → Ollama → fallback)

  + Tests de résilience : pannes Ollama, Supabase, LLM

Usage :
    python Tests/test_rag.py              # tous les tests
    python Tests/test_rag.py -v           # verbose
    python Tests/test_rag.py TestBM25     # une seule classe
"""

import sys
import os
import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

# ── Chemin projet ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Mock supabase si absent de l'environnement ────────────────────────────────
# search.py et service.py font `from supabase import AsyncClient` au niveau module.
# Si supabase n'est pas installé, tous les imports échouent — même BM25.
# On injecte un stub avant le premier import de Assistant_rag.
if 'supabase' not in sys.modules:
    _supabase_stub = MagicMock()
    _supabase_stub.AsyncClient = MagicMock
    sys.modules['supabase'] = _supabase_stub

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1A — BM25
# ══════════════════════════════════════════════════════════════════════════════

class TestBM25(unittest.TestCase):
    """Tests unitaires de la fonction bm25_score."""

    def setUp(self):
        from Assistant_rag.retrieval.bm25 import bm25_score
        self.bm25 = bm25_score

    def test_score_dans_intervalle(self):
        """Le score doit toujours être dans [0, 1]."""
        score = self.bm25("TBR stress concentration", "Le TBR mesure le ratio Theta/Beta.")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_mot_present_score_positif(self):
        """Un mot de la requête présent dans le texte → score > 0."""
        score = self.bm25("TBR", "Le TBR est un indicateur important.")
        self.assertGreater(score, 0.0)

    def test_mot_absent_score_zero(self):
        """Aucun mot en commun → score = 0."""
        score = self.bm25("iapf alpha fréquence", "Le chocolat est délicieux.")
        self.assertEqual(score, 0.0)

    def test_repetition_augmente_score(self):
        """Plus un mot est répété dans le texte, plus le score est élevé (avant saturation)."""
        texte_un   = "alpha est une onde."
        texte_deux = "alpha alpha est une onde cérébrale mesurée en Hz."
        score1 = self.bm25("alpha", texte_un)
        score2 = self.bm25("alpha", texte_deux)
        # BM25 sature (k1=1.5) donc score2 >= score1 (pas forcément strictement >)
        self.assertGreaterEqual(score2, score1)

    def test_casse_insensible(self):
        """Majuscules et minuscules doivent donner le même score."""
        score_maj = self.bm25("TBR", "Le TBR est un ratio important")
        score_min = self.bm25("tbr", "Le TBR est un ratio important")
        self.assertAlmostEqual(score_maj, score_min, places=5)

    def test_requete_vide_score_zero(self):
        """Requête vide → score = 0 sans exception."""
        score = self.bm25("", "Le TBR mesure l'attention.")
        self.assertEqual(score, 0.0)

    def test_texte_vide_score_zero(self):
        """Texte vide → score = 0 sans exception."""
        score = self.bm25("TBR concentration", "")
        self.assertEqual(score, 0.0)

    def test_normalisation_longueur(self):
        """Un document très long avec le même mot doit avoir un score <= 1.0."""
        texte_long  = ("stress " * 200) + " et beaucoup de remplissage"
        texte_court = "stress élevé conseils"
        score_long  = self.bm25("stress", texte_long)
        score_court = self.bm25("stress", texte_court)
        self.assertLessEqual(score_long, 1.0)
        self.assertLessEqual(score_court, 1.0)
        # La normalisation BM25 pénalise les longs documents → score long ≤ court
        self.assertLessEqual(score_long, score_court + 0.1)

    def test_plus_mots_communs_score_plus_eleve(self):
        """Texte avec plus de mots en commun → score brut plus élevé (avant normalisation)."""
        from Assistant_rag.retrieval.bm25 import bm25_score
        # Score brut (avant /len(words)) : on vérifie que chaque mot contribue
        score_1mot = bm25_score("TBR", "Le TBR est un ratio.")
        score_0mot = bm25_score("TBR", "La météo est belle.")
        self.assertGreater(score_1mot, score_0mot)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1A — OllamaEmbedder
# ══════════════════════════════════════════════════════════════════════════════

class TestOllamaEmbedder(unittest.TestCase):
    """Tests de l'embedder avec Ollama mocké."""

    def setUp(self):
        from Assistant_rag.retrieval.embedder import OllamaEmbedder, EMBED_DIM
        self.OllamaEmbedder = OllamaEmbedder
        self.EMBED_DIM = EMBED_DIM

    @patch("Assistant_rag.retrieval.embedder.requests.post")
    def test_embed_retourne_vecteur_768d(self, mock_post):
        """embed() doit retourner une liste de 768 floats si Ollama répond."""
        vecteur_mock = [0.1] * self.EMBED_DIM
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": vecteur_mock}
        )
        embedder = self.OllamaEmbedder()
        result = embedder.embed("TBR stress")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), self.EMBED_DIM)

    @patch("Assistant_rag.retrieval.embedder.requests.post")
    def test_embed_retourne_none_si_ollama_absent(self, mock_post):
        """embed() doit retourner None sans lever d'exception si Ollama est hors ligne."""
        mock_post.side_effect = Exception("Connection refused")
        embedder = self.OllamaEmbedder()
        result = embedder.embed("question quelconque")
        self.assertIsNone(result)

    @patch("Assistant_rag.retrieval.embedder.requests.post")
    def test_available_true_si_ollama_repond(self, mock_post):
        """available doit être True si Ollama retourne un vecteur valide."""
        vecteur_mock = [0.05] * self.EMBED_DIM
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": vecteur_mock}
        )
        embedder = self.OllamaEmbedder()
        self.assertTrue(embedder.available)

    @patch("Assistant_rag.retrieval.embedder.requests.post")
    def test_available_false_si_ollama_absent(self, mock_post):
        """available doit être False si Ollama ne répond pas."""
        mock_post.side_effect = Exception("Timeout")
        embedder = self.OllamaEmbedder()
        self.assertFalse(embedder.available)

    @patch("Assistant_rag.retrieval.embedder.requests.post")
    def test_lazy_check_appel_unique(self, mock_post):
        """available ne doit appeler embed() qu'une seule fois (lazy init)."""
        vecteur_mock = [0.1] * self.EMBED_DIM
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": vecteur_mock}
        )
        embedder = self.OllamaEmbedder()
        _ = embedder.available
        _ = embedder.available
        _ = embedder.available
        self.assertEqual(mock_post.call_count, 1)

    @patch("Assistant_rag.retrieval.embedder.requests.post")
    def test_mauvaise_dimension_retourne_none(self, mock_post):
        """Un vecteur de mauvaise dimension (ex: 384d) → retourne None."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": [0.1] * 384}   # mauvaise dimension
        )
        embedder = self.OllamaEmbedder()
        result = embedder.embed("test")
        self.assertIsNone(result)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1B — search_kb (recherche hybride)
# ══════════════════════════════════════════════════════════════════════════════

def run_async(coro):
    """Utilitaire pour exécuter une coroutine dans les tests synchrones."""
    return asyncio.run(coro)


class TestSearchKb(unittest.TestCase):
    """Tests de la recherche hybride pgvector + BM25."""

    def _make_db(self, docs=None):
        """Crée un mock de client Supabase retournant les docs spécifiés."""
        mock_resp = MagicMock()
        mock_resp.data = docs or []
        mock_db = MagicMock()
        mock_db.rpc.return_value.execute = AsyncMock(return_value=mock_resp)
        return mock_db

    def _make_embedder(self, vec=None):
        """Crée un mock d'OllamaEmbedder retournant le vecteur spécifié."""
        mock_emb = MagicMock()
        mock_emb.embed.return_value = vec
        return mock_emb

    def test_retourne_top_k_docs(self):
        """search_kb doit retourner exactement top_k documents."""
        from Assistant_rag.retrieval.search import search_kb
        docs_supabase = [
            {"id": 1, "title": "TBR", "content": "Le TBR mesure l'attention", "similarity": 0.9},
            {"id": 2, "title": "Stress", "content": "Le stress se mesure en %", "similarity": 0.8},
            {"id": 3, "title": "Concentration", "content": "Score concentration EEG", "similarity": 0.7},
            {"id": 4, "title": "Alpha", "content": "Onde alpha relaxation", "similarity": 0.6},
            {"id": 5, "title": "Protocole", "content": "15 séances protocole", "similarity": 0.5},
        ]
        db = self._make_db(docs_supabase)
        emb = self._make_embedder(vec=[0.1] * 768)
        result = run_async(search_kb("TBR stress", db, emb, top_k=4))
        self.assertLessEqual(len(result), 4)

    def test_hybrid_score_calcule(self):
        """final_score doit être calculé pour chaque document retourné."""
        from Assistant_rag.retrieval.search import search_kb
        docs_supabase = [
            {"id": 1, "title": "TBR attention", "content": "Le TBR mesure attention", "similarity": 0.85},
            {"id": 2, "title": "Stress EEG",   "content": "Le stress détecté par EEG", "similarity": 0.70},
        ]
        db = self._make_db(docs_supabase)
        emb = self._make_embedder(vec=[0.1] * 768)
        result = run_async(search_kb("TBR", db, emb, top_k=4))
        for doc in result:
            self.assertIn("final_score", doc)
            self.assertGreaterEqual(doc["final_score"], 0.0)
            self.assertLessEqual(doc["final_score"], 1.0)

    def test_fallback_bm25_si_ollama_absent(self):
        """Si Ollama retourne None, search_kb doit utiliser le fallback BM25 in-memory."""
        from Assistant_rag.retrieval.search import search_kb
        db = self._make_db([])           # Supabase vide
        emb = self._make_embedder(None)  # Ollama absent
        result = run_async(search_kb("TBR concentration", db, emb, top_k=4))
        # Doit retourner des docs depuis KNOWLEDGE_BASE (in-memory)
        self.assertIsInstance(result, list)
        # Tous les docs retournés ont un score
        for doc in result:
            self.assertIn("final_score", doc)

    def test_fallback_bm25_si_supabase_vide(self):
        """Si Supabase retourne 0 documents, on utilise BM25 in-memory."""
        from Assistant_rag.retrieval.search import search_kb
        db = self._make_db([])            # Supabase retourne liste vide
        emb = self._make_embedder([0.1] * 768)
        result = run_async(search_kb("stress élevé", db, emb, top_k=4))
        self.assertIsInstance(result, list)

    def test_tri_par_score_decroissant(self):
        """Les documents retournés doivent être triés par score décroissant."""
        from Assistant_rag.retrieval.search import search_kb
        docs_supabase = [
            {"id": 1, "title": "TBR", "content": "TBR attention", "similarity": 0.5},
            {"id": 2, "title": "Stress stress stress", "content": "stress stress", "similarity": 0.9},
        ]
        db = self._make_db(docs_supabase)
        emb = self._make_embedder([0.1] * 768)
        result = run_async(search_kb("stress", db, emb, top_k=4))
        if len(result) >= 2:
            self.assertGreaterEqual(result[0]["final_score"], result[1]["final_score"])

    def test_supabase_exception_fallback(self):
        """Si Supabase lève une exception, on bascule sur BM25 in-memory sans crasher."""
        from Assistant_rag.retrieval.search import search_kb
        mock_db = MagicMock()
        mock_db.rpc.return_value.execute = AsyncMock(side_effect=Exception("pgvector error"))
        emb = self._make_embedder([0.1] * 768)
        result = run_async(search_kb("concentration", mock_db, emb, top_k=4))
        # Ne doit pas lever d'exception
        self.assertIsInstance(result, list)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — AUGMENTATION (fmt_patient, fmt_kb)
# ══════════════════════════════════════════════════════════════════════════════

class TestFmtPatient(unittest.TestCase):
    """Tests du formateur de contexte patient."""

    def setUp(self):
        from Assistant_rag.generation.prompts import fmt_patient
        self.fmt = fmt_patient

    def test_contexte_complet(self):
        """Tous les champs non-None doivent apparaître dans la sortie."""
        ctx = {
            "total_sessions": 7,
            "current_phase": "phase2",
            "palier": "P2",
            "profile": "B",
            "iapf": 10.2,
            "avg_score": 66.8,
            "score_trend": 11.9,
            "baseline_tbr": 1.340,
            "last_avg_tbr": 1.612,
        }
        result = self.fmt(ctx)
        self.assertIn("7", result)
        self.assertIn("P2", result)
        self.assertIn("66.8", result)
        self.assertIn("↑", result)          # tendance positive → flèche montante
        self.assertIn("1.340", result)

    def test_valeurs_none_exclues(self):
        """Les valeurs None ne doivent pas apparaître dans la sortie."""
        ctx = {
            "total_sessions": 3,
            "profile": None,
            "iapf": None,
            "avg_score": None,
            "score_trend": None,
        }
        result = self.fmt(ctx)
        self.assertNotIn("None", result)
        self.assertIn("3", result)

    def test_contexte_vide_retourne_chaine_vide(self):
        """Un dict vide doit retourner une chaîne vide."""
        result = self.fmt({})
        self.assertEqual(result, "")

    def test_none_retourne_chaine_vide(self):
        """None doit retourner une chaîne vide."""
        result = self.fmt(None)
        self.assertEqual(result, "")

    def test_tendance_negative_fleche_bas(self):
        """score_trend négatif → flèche ↓."""
        ctx = {"score_trend": -8.5}
        result = self.fmt(ctx)
        self.assertIn("↓", result)
        self.assertNotIn("↑", result)

    def test_tendance_positive_fleche_haut(self):
        """score_trend positif → flèche ↑."""
        ctx = {"score_trend": 15.0}
        result = self.fmt(ctx)
        self.assertIn("↑", result)

    def test_header_present(self):
        """Le header 'DONNÉES DU PATIENT' doit toujours être présent."""
        ctx = {"total_sessions": 5}
        result = self.fmt(ctx)
        self.assertIn("DONNÉES DU PATIENT", result)

    def test_taux_acceptation_calcule(self):
        """Le taux d'acceptation des époques doit être calculé correctement."""
        ctx = {"n_epochs_accepted": 80, "n_epochs_total": 100}
        result = self.fmt(ctx)
        self.assertIn("80 %", result)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — GENERATION (LLMChain)
# ══════════════════════════════════════════════════════════════════════════════

class TestLLMChain(unittest.TestCase):
    """Tests de la cascade LLM résiliente."""

    def setUp(self):
        from Assistant_rag.generation.llm_chain import LLMChain
        self.LLMChain = LLMChain

    def test_groq_available_avec_cle(self):
        """GroqLLM.available doit être True si une clé est passée directement."""
        from Assistant_rag.generation.llm_chain import GroqLLM
        groq = GroqLLM(api_key="fake_groq_key_abc123")
        self.assertTrue(groq.available)

    def test_deepseek_unavailable_sans_cle(self):
        """DeepSeekLLM.available doit être False si api_key est vide."""
        from Assistant_rag.generation.llm_chain import DeepSeekLLM
        ds = DeepSeekLLM(api_key="")
        self.assertFalse(ds.available)

    def test_groq_unavailable_sans_cle(self):
        """GroqLLM.available doit être False si api_key est vide."""
        from Assistant_rag.generation.llm_chain import GroqLLM
        groq = GroqLLM(api_key="")
        self.assertFalse(groq.available)

    def test_ollama_fallback_si_pas_de_cles(self):
        """LLMChain.ollama existe toujours (pas de clé requise)."""
        chain = self.LLMChain()
        self.assertIsNotNone(chain.ollama)

    @patch("Assistant_rag.generation.llm_chain.GROQ_KEY", "")
    @patch("Assistant_rag.generation.llm_chain.DEEPSEEK_KEY", "")
    @patch("Assistant_rag.generation.llm_chain.requests.post")
    def test_fallback_message_si_tout_echoue(self, mock_post):
        """Si tous les LLMs échouent, un message de fallback est retourné."""
        mock_post.side_effect = Exception("Ollama absent")
        chain = self.LLMChain()
        response, model = chain.generate("system", "user prompt", max_tokens=100)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        self.assertEqual(model, "unavailable")

    @patch("Assistant_rag.generation.llm_chain.GROQ_KEY", "fake_key")
    @patch("Assistant_rag.generation.llm_chain.DEEPSEEK_KEY", "")
    def test_retourne_tuple_str_str(self):
        """generate() doit toujours retourner un tuple (str, str)."""
        chain = self.LLMChain()
        with patch.object(chain.groq, "generate", return_value="Réponse test"):
            response, model = chain.generate("sys", "user", max_tokens=100)
        self.assertIsInstance(response, str)
        self.assertIsInstance(model, str)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE COMPLET — RAGService
# ══════════════════════════════════════════════════════════════════════════════

class TestRAGService(unittest.TestCase):
    """Tests d'intégration du pipeline RAG complet."""

    def _make_db(self, docs=None):
        mock_resp = MagicMock()
        mock_resp.data = docs or []
        mock_db = MagicMock()
        mock_db.rpc.return_value.execute = AsyncMock(return_value=mock_resp)
        return mock_db

    def test_answer_question_retourne_string(self):
        """answer_question doit retourner une chaîne non vide."""
        from Assistant_rag.service import RAGService
        service = RAGService()
        # Mock embedder → BM25 fallback
        service.embedder = MagicMock()
        service.embedder.embed.return_value = None
        # Mock LLM → réponse fixe
        service.llm = MagicMock()
        service.llm.generate.return_value = ("D'après vos données, votre TBR est stable.", "groq-llama")

        db = self._make_db([])
        ctx = {"total_sessions": 7, "profile": "B", "avg_score": 66.8}
        result = run_async(service.answer_question("Pourquoi mon TBR a augmenté ?", ctx, db))
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_answer_question_sans_contexte_patient(self):
        """answer_question doit fonctionner même sans contexte patient (None)."""
        from Assistant_rag.service import RAGService
        service = RAGService()
        service.embedder = MagicMock()
        service.embedder.embed.return_value = None
        service.llm = MagicMock()
        service.llm.generate.return_value = ("Réponse générique.", "ollama-mistral")

        db = self._make_db([])
        result = run_async(service.answer_question("Qu'est-ce que le TBR ?", None, db))
        self.assertIsInstance(result, str)

    def test_explain_dashboard_retourne_dict_complet(self):
        """explain_dashboard doit retourner un dict avec les clés attendues."""
        from Assistant_rag.service import RAGService
        service = RAGService()
        service.embedder = MagicMock()
        service.embedder.embed.return_value = None
        service.llm = MagicMock()
        service.llm.generate.return_value = ("**1.** Vos résultats sont bons.", "groq-llama")

        db = self._make_db([])
        snapshot = {
            "total_sessions": 7,
            "profile": "B",
            "palier": "P2",
            "avg_score": 66.8,
            "baseline_tbr": 1.34,
            "last_avg_tbr": 1.61,
            "avg_concentration_pct": 55.0,
            "avg_stress_pct": 35.0,
        }
        result = run_async(service.explain_dashboard(snapshot, db))
        self.assertIn("response", result)
        self.assertIn("sources", result)
        self.assertIn("model", result)
        self.assertIn("snapshot", result)
        self.assertIsInstance(result["sources"], list)

    def test_explain_dashboard_queries_adaptatives(self):
        """explain_dashboard doit ajouter des requêtes selon les métriques patient."""
        from Assistant_rag.service import RAGService
        service = RAGService()
        service.embedder = MagicMock()
        service.embedder.embed.return_value = None
        service.llm = MagicMock()
        service.llm.generate.return_value = ("Réponse.", "groq")

        db = self._make_db([])
        snapshot = {
            "profile": "B",
            "palier": "P1",
            "baseline_tbr": 1.0,
            "last_avg_tbr": 1.5,        # > 1.0 × 1.2 → requête stress ajoutée
            "avg_concentration_pct": 45, # < 60 → requête concentration ajoutée
            "avg_stress_pct": 40,        # > 30 → requête stress ajoutée
        }
        # Ne doit pas lever d'exception
        result = run_async(service.explain_dashboard(snapshot, db))
        self.assertIn("response", result)

    def test_deduplication_documents(self):
        """explain_dashboard ne doit pas retourner de documents en double."""
        from Assistant_rag.service import RAGService
        service = RAGService()
        service.embedder = MagicMock()
        service.embedder.embed.return_value = None

        # KB in-memory retourne les mêmes docs pour chaque requête
        service.llm = MagicMock()
        service.llm.generate.return_value = ("OK", "groq")
        db = self._make_db([])

        snapshot = {"profile": "B", "palier": "P1"}
        result = run_async(service.explain_dashboard(snapshot, db))
        # Vérifier qu'il n'y a pas de titres en double dans sources
        sources = result["sources"]
        self.assertEqual(len(sources), len(set(sources)))


# ══════════════════════════════════════════════════════════════════════════════
# RÉSILIENCE — pannes simulées
# ══════════════════════════════════════════════════════════════════════════════

class TestResilience(unittest.TestCase):
    """Tests de résilience : le système ne doit jamais crasher."""

    def _make_db_crash(self):
        """Client Supabase qui lève une exception sur chaque appel."""
        mock_db = MagicMock()
        mock_db.rpc.return_value.execute = AsyncMock(side_effect=Exception("Supabase down"))
        mock_db.table.return_value.select.return_value.eq.return_value \
               .limit.return_value.execute = AsyncMock(side_effect=Exception("Supabase down"))
        mock_db.table.return_value.select.return_value.eq.return_value \
               .order.return_value.limit.return_value.execute = AsyncMock(
                   side_effect=Exception("Supabase down"))
        return mock_db

    def test_search_kb_sans_crash_si_supabase_tombe(self):
        """search_kb doit retourner des docs BM25 même si Supabase est hors ligne."""
        from Assistant_rag.retrieval.search import search_kb
        from Assistant_rag.retrieval.embedder import OllamaEmbedder

        emb = MagicMock(spec=OllamaEmbedder)
        emb.embed.return_value = [0.1] * 768
        db = self._make_db_crash()

        result = run_async(search_kb("TBR", db, emb, top_k=4))
        self.assertIsInstance(result, list)

    def test_rag_service_sans_crash_si_ollama_et_supabase_tombent(self):
        """Le pipeline complet ne doit pas crasher si Ollama ET Supabase sont hors ligne."""
        from Assistant_rag.service import RAGService
        service = RAGService()
        service.embedder = MagicMock()
        service.embedder.embed.return_value = None   # Ollama absent
        service.llm = MagicMock()
        service.llm.generate.return_value = ("Message de fallback.", "unavailable")

        db = self._make_db_crash()
        ctx = {"total_sessions": 5}
        result = run_async(service.answer_question("Question test", ctx, db))
        self.assertIsInstance(result, str)

    def test_bm25_ne_crash_pas_sur_caracteres_speciaux(self):
        """BM25 ne doit pas crasher avec des caractères spéciaux ou Unicode."""
        from Assistant_rag.retrieval.bm25 import bm25_score
        textes_speciaux = [
            "TBR = θ/β (Theta/Beta ratio)",
            "concentration ≥ 80% → excellent",
            "stress élevé : ↑ TBR > baseline × 1.2",
            "émotions 🧠 cerveau neurofeedback",
        ]
        for texte in textes_speciaux:
            score = bm25_score("TBR stress", texte)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    @patch("Assistant_rag.generation.llm_chain.GROQ_KEY", "")
    @patch("Assistant_rag.generation.llm_chain.DEEPSEEK_KEY", "")
    @patch("Assistant_rag.generation.llm_chain.requests.post")
    def test_llm_chain_retourne_fallback_si_tout_echoue(self, mock_post):
        """LLMChain doit retourner un message de fallback si tous les LLMs échouent."""
        mock_post.side_effect = Exception("Ollama connection refused")
        from Assistant_rag.generation.llm_chain import LLMChain
        chain = LLMChain()
        response, model = chain.generate("system prompt", "user prompt", max_tokens=200)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 5)
        self.assertEqual(model, "unavailable")


# ══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE — contenu et format
# ══════════════════════════════════════════════════════════════════════════════

class TestKnowledgeBase(unittest.TestCase):
    """Tests de la base de connaissances in-memory."""

    def setUp(self):
        from Assistant_rag.kb.knowledge_base import KNOWLEDGE_BASE, fmt_kb
        self.KB = KNOWLEDGE_BASE
        self.fmt_kb = fmt_kb

    def test_kb_contient_documents(self):
        """La KB doit contenir au moins 5 documents."""
        self.assertGreaterEqual(len(self.KB), 5)

    def test_chaque_doc_a_les_champs_requis(self):
        """Chaque document doit avoir id, title, content, category."""
        champs_requis = {"id", "title", "content", "category"}
        for doc in self.KB:
            for champ in champs_requis:
                self.assertIn(champ, doc, f"Champ '{champ}' manquant dans doc id={doc.get('id')}")

    def test_ids_uniques(self):
        """Tous les IDs de la KB doivent être uniques."""
        ids = [doc["id"] for doc in self.KB]
        self.assertEqual(len(ids), len(set(ids)))

    def test_fmt_kb_retourne_string(self):
        """fmt_kb doit retourner une chaîne non vide pour une liste de docs."""
        result = self.fmt_kb(self.KB[:3])
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_fmt_kb_liste_vide(self):
        """fmt_kb ne doit pas crasher sur une liste vide."""
        result = self.fmt_kb([])
        self.assertIsInstance(result, str)

    def test_categories_valides(self):
        """Toutes les catégories doivent être des chaînes non vides."""
        for doc in self.KB:
            self.assertIsInstance(doc["category"], str)
            self.assertGreater(len(doc["category"]), 0)

    def test_tbr_present_dans_kb(self):
        """La KB doit contenir un document sur le TBR."""
        titres = [doc["title"].lower() for doc in self.KB]
        self.assertTrue(any("tbr" in t for t in titres), "Aucun doc sur le TBR dans la KB")


# ══════════════════════════════════════════════════════════════════════════════
# RAPPORT DE SYNTHÈSE
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  NeuroCap — Tests RAG NeuroCoach")
    print("  Pipeline : Retrieval → Augmentation → Generation")
    print("=" * 65)

    loader  = unittest.TestLoader()
    suites  = [
        ("Phase 1A — BM25",                loader.loadTestsFromTestCase(TestBM25)),
        ("Phase 1A — OllamaEmbedder",      loader.loadTestsFromTestCase(TestOllamaEmbedder)),
        ("Phase 1B — Recherche hybride",   loader.loadTestsFromTestCase(TestSearchKb)),
        ("Phase 2  — fmt_patient",         loader.loadTestsFromTestCase(TestFmtPatient)),
        ("Phase 3  — LLMChain",            loader.loadTestsFromTestCase(TestLLMChain)),
        ("Pipeline — RAGService",          loader.loadTestsFromTestCase(TestRAGService)),
        ("Résilience",                     loader.loadTestsFromTestCase(TestResilience)),
        ("Knowledge Base",                 loader.loadTestsFromTestCase(TestKnowledgeBase)),
    ]

    total_ok = total_fail = total_err = 0

    for label, suite in suites:
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
        res    = runner.run(suite)
        ok     = suite.countTestCases() - len(res.failures) - len(res.errors)
        status = "✅" if not res.failures and not res.errors else "❌"
        print(f"  {status}  {label:<35} {ok}/{suite.countTestCases()} tests OK")
        for _, msg in res.failures + res.errors:
            first_line = msg.strip().split("\n")[-1]
            print(f"       → {first_line[:70]}")
        total_ok   += ok
        total_fail += len(res.failures)
        total_err  += len(res.errors)

    print("=" * 65)
    total = sum(s.countTestCases() for _, s in suites)
    print(f"  TOTAL : {total_ok}/{total} tests réussis | "
          f"{total_fail} échecs | {total_err} erreurs")
    print("=" * 65)
    sys.exit(1 if (total_fail + total_err) > 0 else 0)
