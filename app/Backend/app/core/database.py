"""
NeuroCap — Couche Base de Données (Supabase REST API)
======================================================
Utilise supabase-py v2.x (client asynchrone).
Toutes les routes reçoivent un AsyncClient via Depends(get_db).

Usage dans les routes :
    from app.core.database import get_db
    from supabase import AsyncClient

    @router.get("/example")
    async def example(db: AsyncClient = Depends(get_db)):
        resp = await db.table('users').select('*').eq('id', user_id).execute()
        return resp.data
"""

import logging
from supabase import AsyncClient, acreate_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Singleton — créé une seule fois au démarrage (lifespan)
_supabase_client: AsyncClient | None = None

# Stub pour la rétrocompatibilité avec d'éventuels imports existants
class Base:
    """Remplace DeclarativeBase SQLAlchemy — vide, conservé pour compatibilité."""
    pass

engine = None  # Plus utilisé avec Supabase


async def _build_client() -> AsyncClient:
    """
    Crée (ou retourne) le client Supabase asynchrone.
    La service_role key est requise pour bypasser RLS et accéder à toutes les tables.
    """
    global _supabase_client
    if _supabase_client is None:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SERVICE_ROLE_KEY
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY sont requis dans le fichier .env"
            )
        _supabase_client = await acreate_client(url, key)
        logger.info("Client Supabase initialisé → %s", url)
    return _supabase_client


async def get_db() -> AsyncClient:
    """
    Dépendance FastAPI — retourne le client Supabase.
    Toutes les routes qui accèdent à la base de données utilisent Depends(get_db).
    """
    return await _build_client()


async def init_db() -> None:
    """
    Vérification de la connexion au démarrage (lifespan).
    Vérifie que les tables existent dans Supabase.
    Si elles n'existent pas, affiche le message pour exécuter le script SQL.
    """
    try:
        client = await _build_client()
        # Requête minimale pour vérifier que la table 'users' existe
        await client.table("users").select("id").limit(1).execute()
        logger.info("Supabase connecté — tables vérifiées ✅")
    except Exception as exc:
        logger.warning(
            "Tables Supabase inaccessibles. "
            "Exécutez supabase_migration.sql dans l'éditeur SQL Supabase "
            "(https://supabase.com/dashboard/project/qwxkhkumyokzykykindv/sql/new). "
            "Erreur : %s", exc,
        )


# Rétrocompatibilité pour les imports du type :
# from app.core.database import Base, engine, get_db, init_db
__all__ = ["Base", "engine", "get_db", "init_db", "_build_client"]
