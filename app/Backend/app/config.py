"""
NeuroCap — Configuration Centrale
===================================
Toutes les variables sensibles sont lues depuis le fichier .env
(jamais codées en dur dans le code source).

Usage :
    from app.config import get_settings
    settings = get_settings()
    settings.SECRET_KEY  # → valeur lue depuis .env
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Charge le fichier .env si présent (développement local)
# En production (Docker / Railway / Heroku), les variables sont injectées directement
load_dotenv()


class Settings:
    # ── Base de données ────────────────────────────────────────────────────────
    # Supabase PostgreSQL :
    #   postgresql+asyncpg://postgres:[password]@db.[ref].supabase.co:5432/postgres
    # SQLite (dev local) :
    #   sqlite+aiosqlite:///./neurocap_dev.db
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
    )

    # ── Supabase ───────────────────────────────────────────────────────────────
    # URL et clés pour le client supabase-py (optionnel, pour les Storage / Auth Supabase)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    # La service_role key a des droits admin — utiliser uniquement côté serveur
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # ── Cloudinary (stockage médias) ───────────────────────────────────────────
    # Utilisé pour stocker les avatars / exports de rapports EEG
    # Obtenir les clés sur https://cloudinary.com/console
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # ── Sécurité JWT ───────────────────────────────────────────────────────────
    # SECRET_KEY : générer avec `python -c "import secrets; print(secrets.token_hex(32))"`
    # JAMAIS utiliser la valeur par défaut en production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "INSECURE_DEFAULT_CHANGE_ME")
    ALGORITHM: str = "HS256"                    # Algorithme HMAC-SHA256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30       # Access token : 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7          # Refresh token : 7 jours

    # ── Protection anti-brute force (voir middleware/security.py) ─────────────
    # Nombre maximum de tentatives de login avant blocage temporaire
    LOGIN_MAX_ATTEMPTS: int = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
    # Durée du blocage en secondes (900 = 15 minutes)
    LOGIN_LOCKOUT_SECONDS: int = int(os.getenv("LOGIN_LOCKOUT_SECONDS", "900"))
    # Fenêtre de rate limiting globale en secondes
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    # Nombre maximum de requêtes par IP dans la fenêtre
    RATE_LIMIT_MAX: int = int(os.getenv("RATE_LIMIT_MAX", "100"))

    # ── Paramètres EEG / neurofeedback ────────────────────────────────────────
    EEG_SAMPLING_RATE: int = 250           # Hz — AD8232 @ 250 Hz (CdC §3.1)
    EPOCH_SAMPLES: int = 1000              # Durée epoch = 4s × 250 Hz
    WINDOW_OVERLAP: float = 0.75           # Recouvrement 75% (pipeline_fp2.py)
    CONFIDENCE_THRESHOLD: float = 0.60    # Seuil de confiance classifieur (CdC §2.5.1)
    OPTIMAL_SUCCESS_RATE: tuple = (0.40, 0.60)  # Zone cible Mou et al. 2024

    # ── Modèle ML ─────────────────────────────────────────────────────────────
    MODEL_PATH: str = os.path.join(
        os.path.dirname(__file__),
        "../../models/best_model.pt",
    )

    # ── Email SMTP via Brevo (vérification à l'inscription) ───────────────────
    # Brevo (ex-Sendinblue) : 300 emails/jour gratuits, pas de domaine requis.
    # Setup (3 min) :
    #   1. Créer compte sur https://brevo.com
    #   2. Menu gauche → SMTP & API → onglet SMTP
    #   3. Copier : Login (ton email Brevo) + Master password (clé SMTP)
    #   4. Remplir SMTP_USER et SMTP_PASSWORD ci-dessous
    # Si SMTP_USER est vide → mode dev : le code s'affiche sur la page
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")           # ton email Brevo
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")   # clé SMTP Brevo (pas ton mdp)
    SMTP_FROM: str = os.getenv("SMTP_FROM", "NeuroCap <noreply@neurocap.app>")

    # ── Redis (cache optionnel) ────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ── LLM ───────────────────────────────────────────────────────────────────
    # Priorité : DeepSeek API (gratuit) → Ollama local (fallback)
    # Clé DeepSeek sur https://platform.deepseek.com/
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    # Groq (gratuit, fallback si DeepSeek vide/épuisé) — clé sur https://console.groq.com
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    # Ollama local (fallback final)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Origines autorisées à appeler l'API (depuis un navigateur)
    # En production, retirer localhost et ne garder que le domaine réel
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",            # Vite dev server
        "http://localhost:3000",            # Alternative dev
        "https://neurocap.example.com",    # Domaine de production (à changer)
    ]

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # DEBUG=True expose les stacktraces dans les réponses d'erreur — JAMAIS en prod
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne un singleton Settings mis en cache.
    lru_cache garantit que .env n'est lu qu'une seule fois au démarrage.
    """
    return Settings()
