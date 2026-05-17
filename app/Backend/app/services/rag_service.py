"""
=============================================================================
SERVICE RAG - ASSISTANT COGNITIF LOCAL
=============================================================================
Retrieval-Augmented Generation (RAG) locale avec Ollama

Architecture:
1. Indexation: Corpus EEG/neurofeedback → embeddings → ChromaDB
2. Retrieval: Question utilisateur → recherche sémantique (Top-K)
3. Augmentation: Injection du contexte dans le prompt
4. Generation: LLM local (Ollama) génère la réponse

Avantages RAG local:
✓ Confidentialité (données ne quittent pas le serveur)
✓ Faible latence (Ollama en local)
✓ Réponses ancrées dans les données réelles
✓ Pas de hallucinations générales (grounded in facts)

Installation Ollama:
$ brew install ollama
$ ollama pull mistral  # Télécharger le modèle
$ ollama serve        # Démarrer le serveur (port 11434)
=============================================================================
"""

import logging
from typing import List, Dict, Optional
import requests
import json
import numpy as np
from pathlib import Path
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Base de connaissances locale sur le neurofeedback EEG
    Stockée en SQLite pour légèreté
    """
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialiser la base de connaissances"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des documents de connaissances
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,  -- 'eeg_basics', 'concentration', 'stress', 'adaptation'
                embedding BLOB,  -- Vecteur embedding stocké en bytes
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Ajouter des documents de base
        self._populate_initial_docs()
    
    def _populate_initial_docs(self):
        """Ajouter les documents EEG/neurofeedback de base"""
        docs = [
            {
                "title": "Bandes EEG - Alpha",
                "content": """
                La bande ALPHA (8-13 Hz) représente un état de relaxation alerte.
                - Alpha élevé: Calme, méditation, fermeture des yeux
                - Alpha bas: Concentration intense, yeux ouverts
                - Individual Alpha Peak Frequency (IAPF): Varie entre 7-13 Hz selon l'individu
                
                Neurofeedback alpha: Augmenter alpha pour relaxation, diminuer pour concentration.
                """,
                "category": "eeg_basics"
            },
            {
                "title": "Theta/Beta Ratio (TBR) - Indicateur d'Attention",
                "content": """
                TBR = Puissance Theta / Puissance Beta
                
                Interprétation:
                - TBR < 0.5: État très concentré (normal travail cognitif)
                - TBR 0.5-2.0: État normal, attention variable
                - TBR > 2.0: État fatigué, déconcentré, somnolence
                
                Objectif: Réduire TBR pour améliorer la concentration
                Baseline individuelle calculée lors de la calibration S1.
                """,
                "category": "concentration"
            },
            {
                "title": "Stress et Asymétrie Alpha (FAA)",
                "content": """
                FAA = Frontal Alpha Asymmetry = log(P_alpha_F3) - log(P_alpha_F4)
                
                - FAA négatif (F4 > F3): État dépressif, retrait, stress négatif
                - FAA positif (F3 > F4): État d'approche, optimisme
                
                Détection du stress:
                - Beta haute-fréquence (> 20 Hz)
                - Theta augmenté
                - Asym alpha perturbée
                
                Feedback stress: Augmenter alpha frontale, diminuer high-beta.
                """,
                "category": "stress"
            },
            {
                "title": "Protocole Neurofeedback 15 séances",
                "content": """
                Phase 1 (S1-S3): Découverte
                - Calibration EEG individuelle
                - 1 séance/semaine
                - Établir la baseline personnelle
                
                Phase 2 (S4-S10): Entraînement actif
                - 2 séances/semaine
                - Apprentissage de la régulation
                - Adaptation dynamique des seuils
                
                Phase 3 (S11-S15): Consolidation
                - 2 séances/semaine
                - Réduction progressive du feedback
                - Transfer effect vers tâches quotidiennes
                
                Règle d'adaptation (Mou et al., 2024):
                - Succès > 60% → seuil +0.5 (augmenter difficulté)
                - Succès 40-60% → seuil inchangé (zone optimale)
                - Succès < 40% → seuil -0.5 (diminuer difficulté)
                """,
                "category": "adaptation"
            },
            {
                "title": "Profils utilisateur (A/B/C)",
                "content": """
                Profil A - Répondeur Rapide:
                - Ratio alpha/beta > 1.5 au repos
                - Réactivité ERD > 30%
                - Démarrage direct Palier P2
                - Durée programme: 12 séances
                
                Profil B - Répondeur Standard:
                - Ratio alpha/beta 0.8-1.5
                - Réactivité 15-30%
                - Programme standard 15 séances
                - 4 paliers progressifs
                
                Profil C - Répondeur Lent (risque inefficacy):
                - Ratio alpha/beta < 0.8
                - Réactivité < 15%
                - Phase 1 étendue à 5 séances
                - Seuils très accessibles
                - Arrêt anticipé si pas de progression à S10
                """,
                "category": "adaptation"
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for doc in docs:
            # Vérifier si doc existe déjà
            cursor.execute("SELECT COUNT(*) FROM documents WHERE title = ?", (doc["title"],))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO documents (title, content, category) VALUES (?, ?, ?)",
                    (doc["title"], doc["content"], doc["category"])
                )
        
        conn.commit()
        conn.close()
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Recherche sémantique simple par keyword (en production: utiliser embeddings)
        
        Args:
            query: Question/texte de l'utilisateur
            top_k: Nombre de documents à retourner
            
        Returns:
            Liste des documents pertinents
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recherche simple par keyword (en production: utiliser embeddings + similarité cosine)
        keywords = query.lower().split()
        
        cursor.execute("SELECT id, title, content, category FROM documents")
        all_docs = cursor.fetchall()
        
        # Scoring simple: nombre de keywords trouvés
        scored_docs = []
        for doc_id, title, content, category in all_docs:
            score = 0
            text = (title + " " + content).lower()
            for kw in keywords:
                if kw in text:
                    score += 1
            if score > 0:
                scored_docs.append({
                    "id": doc_id,
                    "title": title,
                    "content": content,
                    "category": category,
                    "relevance": score
                })
        
        # Trier par pertinence
        scored_docs.sort(key=lambda x: x["relevance"], reverse=True)
        
        conn.close()
        return scored_docs[:top_k]


class OllamaLLM:
    """
    Interface vers le serveur Ollama local
    Génère du texte via mistral ou autre modèle
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral"
    ):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Générer du texte via Ollama
        
        Args:
            prompt: Texte d'entrée
            max_tokens: Longueur maximale de réponse
            
        Returns:
            Texte généré
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": max_tokens
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return "Error generating response"
        
        except requests.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running? (ollama serve)")
            return "Error: Ollama server not available"
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return f"Error: {str(e)}"


class RAGService:
    """
    Service RAG complet: Retrieval → Augmentation → Generation
    """
    
    def __init__(
        self,
        knowledge_base: KnowledgeBase = None,
        llm: OllamaLLM = None
    ):
        self.kb = knowledge_base or KnowledgeBase()
        self.llm = llm or OllamaLLM()
    
    def answer_question(self, question: str, user_context: Dict = None) -> str:
        """
        Répondre à une question en combinant RAG
        
        Args:
            question: Question de l'utilisateur
            user_context: Contexte utilisateur (sessions récentes, scores, etc.)
            
        Returns:
            Réponse générée ancrée dans la base de connaissances
        """
        # 1. RETRIEVAL: Chercher les documents pertinents
        relevant_docs = self.kb.search(question, top_k=3)
        
        if not relevant_docs:
            return "Je n'ai pas trouvé d'informations pertinentes dans ma base de connaissances."
        
        # 2. AUGMENTATION: Construire le contexte enrichi
        context = self._build_context(relevant_docs, user_context)
        
        # 3. GENERATION: Appeler Ollama avec le prompt augmenté
        prompt = self._build_prompt(question, context, user_context)
        
        logger.info(f"RAG query: {question}")
        logger.debug(f"Prompt: {prompt}")
        
        response = self.llm.generate(prompt, max_tokens=500)
        
        return response
    
    def _build_context(self, docs: List[Dict], user_context: Dict = None) -> str:
        """
        Construire la chaîne de contexte à partir des documents
        """
        context = "# CONTEXTE PROVENANT DE LA BASE DE CONNAISSANCES\n\n"
        
        for doc in docs:
            context += f"## {doc['title']}\n"
            context += f"{doc['content']}\n\n"
        
        if user_context:
            context += "# PROFIL PATIENT\n"
            ctx = user_context
            if ctx.get('total_sessions') is not None:
                context += f"- Sessions complétées: {ctx['total_sessions']}\n"
            if ctx.get('avg_score') is not None:
                context += f"- Score moyen: {ctx['avg_score']:.1f}%\n"
            if ctx.get('score_trend') is not None:
                arrow = "↑" if ctx['score_trend'] > 0 else "↓"
                context += f"- Tendance score: {arrow} {abs(ctx['score_trend']):.1f}%\n"
            if ctx.get('profile'):
                context += f"- Profil EEG: {ctx['profile']}\n"
            if ctx.get('iapf') is not None:
                context += f"- IAPF: {ctx['iapf']:.1f} Hz\n"
            if ctx.get('baseline_tbr') is not None:
                context += f"- TBR baseline: {ctx['baseline_tbr']:.3f}\n"
            if ctx.get('last_avg_tbr') is not None:
                context += f"- TBR dernière session: {ctx['last_avg_tbr']:.3f}\n"
            if ctx.get('palier'):
                context += f"- Palier actuel: {ctx['palier']}\n"
            if ctx.get('last_objective'):
                context += f"- Objectif courant: {ctx['last_objective']}\n"

        return context
    
    def _build_prompt(
        self,
        question: str,
        context: str,
        user_context: Dict = None
    ) -> str:
        """
        Construire le prompt final pour le LLM
        """
        prompt = f"""Tu es un assistant spécialisé en neurofeedback EEG adaptatif pour l'application NeuroCap.
Tu dois répondre aux questions de l'utilisateur en te basant UNIQUEMENT sur le contexte fourni.

IMPORTANT:
- Réponds en français avec un ton bienveillant et professionnel
- Cite les sources (ex: "Selon la base de connaissances...")
- Ne formule JAMAIS de diagnostic médical
- Sois concis et actionnable

{context}

Question de l'utilisateur: {question}

Réponse:
"""
        return prompt

