"""
LLMChain — Cascade résiliente de LLMs (DeepSeek → Groq → Ollama).

Priorité :
  1. DeepSeek API   (deepseek-chat, payant ~$0.14/M tokens)
  2. Groq API       (llama-3.3-70b-versatile, GRATUIT 14 400 req/jour) ✅
  3. Ollama local   (mistral, deepseek-r1, etc.)
  4. Message de fallback structuré

Chaque LLM est compatible OpenAI SDK (même format, base_url différente).
Référence : Ng et al., NEJM AI 2025, Fig.3 "Graceful degradation".
"""

import logging
import os
from typing import Tuple

import requests

logger = logging.getLogger(__name__)

# ── Variables d'environnement ─────────────────────────────────────────────────
DEEPSEEK_KEY   = os.getenv("DEEPSEEK_API_KEY",  "")
DEEPSEEK_MODEL = "deepseek-chat"

GROQ_KEY       = os.getenv("GROQ_API_KEY",      "")
GROQ_MODEL     = os.getenv("GROQ_MODEL",        "llama-3.3-70b-versatile")

OLLAMA_BASE    = os.getenv("OLLAMA_URL",         "http://localhost:11434")
OLLAMA_MODEL   = os.getenv("LLM_MODEL",          "mistral")


# ─────────────────────────────────────────────────────────────────────────────
# LLM 1 — DeepSeek
# ─────────────────────────────────────────────────────────────────────────────

class DeepSeekLLM:
    """DeepSeek-V3 via API compatible OpenAI. Payant, ~$0.14/M tokens input."""

    def __init__(self, api_key: str = DEEPSEEK_KEY, model: str = DEEPSEEK_MODEL):
        self.api_key = api_key
        self.model   = model

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def generate(self, system: str, user: str, max_tokens: int = 700) -> str:
        if not self.available:
            return ""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("DeepSeek indisponible: %s", exc)
            return ""


# ─────────────────────────────────────────────────────────────────────────────
# LLM 2 — Groq (gratuit)
# ─────────────────────────────────────────────────────────────────────────────

class GroqLLM:
    """
    Groq Cloud — LLaMA 3.3 70B. Gratuit, 14 400 req/jour.
    Clé sur https://console.groq.com (inscription gratuite).
    Compatible OpenAI SDK : même format, base_url différente.
    """

    def __init__(self, api_key: str = GROQ_KEY, model: str = GROQ_MODEL):
        self.api_key = api_key
        self.model   = model

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def generate(self, system: str, user: str, max_tokens: int = 700) -> str:
        if not self.available:
            return ""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            logger.error("Groq erreur: %s", exc)
            return ""


# ─────────────────────────────────────────────────────────────────────────────
# LLM 3 — Ollama (local)
# ─────────────────────────────────────────────────────────────────────────────

class OllamaLLM:
    """Ollama local — mistral, deepseek-r1, llama3, etc. Aucune clé requise."""

    def __init__(self, base_url: str = OLLAMA_BASE, model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model    = model

    def generate(self, prompt: str, max_tokens: int = 700) -> str:
        try:
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model":       self.model,
                    "prompt":      prompt,
                    "stream":      False,
                    "num_predict": max_tokens,
                },
                timeout=90,
            )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception as exc:
            logger.error("Ollama erreur: %s", exc)
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrateur — LLMChain
# ─────────────────────────────────────────────────────────────────────────────

class LLMChain:
    """
    Chaîne LLM résiliente : essaie chaque LLM dans l'ordre,
    retourne le premier qui produit une réponse non vide.

    Retourne : (texte_généré, nom_modèle_utilisé)
    """

    def __init__(self):
        self.deepseek = DeepSeekLLM()
        self.groq     = GroqLLM()
        self.ollama   = OllamaLLM()

    def generate(
        self,
        system:     str,
        user_prompt: str,
        max_tokens: int = 700,
    ) -> Tuple[str, str]:

        # 1. DeepSeek
        if self.deepseek.available:
            text = self.deepseek.generate(system, user_prompt, max_tokens)
            if text:
                return text, "deepseek-chat"

        # 2. Groq — llama-3.3-70b-versatile
        if self.groq.available:
            text = self.groq.generate(system, user_prompt, max_tokens)
            if text:
                return text, f"groq-{self.groq.model}"

        # 3. Ollama local
        text = self.ollama.generate(f"{system}\n\n{user_prompt}", max_tokens)
        if text:
            return text, f"ollama-{self.ollama.model}"

        # 4. Fallback message structuré
        return (
            "Je ne suis pas disponible pour le moment.\n\n"
            "**Pour activer l'assistant :**\n"
            "- **Groq** (gratuit) : clé sur https://console.groq.com → `GROQ_API_KEY` dans `.env`\n"
            "- **DeepSeek** : recharger le solde → `DEEPSEEK_API_KEY` dans `.env`\n"
            "- **Ollama local** : `ollama serve && ollama pull mistral`\n\n"
            "Vos données EEG restent accessibles dans le dashboard."
        ), "unavailable"
