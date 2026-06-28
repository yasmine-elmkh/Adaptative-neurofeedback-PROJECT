"""
NeuroCap — Couche Base de Données (Supabase REST via thread pool)
=================================================================
Fix Windows DNS asyncio : utilise le client supabase SYNCHRONE wrappé
dans asyncio.to_thread. Toutes les requêtes HTTP sont exécutées dans
un thread worker (socket.getaddrinfo synchrone, toujours fiable sur Windows).

Le proxy _AsyncProxy rend le client sync compatible avec le code async
existant — même interface: await db.table("x").select("*").eq(...).execute()
Aucune modification des routes requise.
"""

import asyncio
import logging
from supabase import create_client, Client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Singleton client sync ──────────────────────────────────────────────────────
_supabase_client: Client | None = None

# Stub pour la rétrocompatibilité avec d'éventuels imports existants
class Base:
    pass

engine = None


# ── Proxy async transparent ────────────────────────────────────────────────────

class _AsyncProxy:
    """
    Proxy qui enveloppe un builder sync supabase-py et rend .execute() awaitable
    via asyncio.to_thread. Toutes les méthodes de chaînage (select, eq, insert…)
    délèguent au builder sous-jacent et retournent self ou un nouveau proxy.
    """

    __slots__ = ('_b',)

    def __init__(self, builder):
        object.__setattr__(self, '_b', builder)

    def __getattr__(self, name: str):
        b = object.__getattribute__(self, '_b')
        attr = getattr(b, name)

        if name == 'execute':
            # Rendre execute() awaitable via thread pool
            async def _exec(*args, **kwargs):
                return await asyncio.to_thread(attr, *args, **kwargs)
            return _exec

        if callable(attr):
            def _method(*args, **kwargs):
                result = attr(*args, **kwargs)
                # Si le builder renvoie lui-même → même proxy
                if result is b:
                    return self
                # Sinon wraper le nouveau builder
                return _AsyncProxy(result)
            return _method

        return attr

    def __setattr__(self, name, value):
        b = object.__getattribute__(self, '_b')
        setattr(b, name, value)


class _AsyncClientWrapper:
    """
    Enveloppe un Client sync Supabase pour l'exposer comme AsyncClient.
    Seules les méthodes réellement utilisées dans les routes sont déclarées;
    le reste passe par __getattr__.
    """

    def __init__(self, client: Client):
        object.__setattr__(self, '_c', client)

    def table(self, name: str) -> _AsyncProxy:
        c = object.__getattribute__(self, '_c')
        return _AsyncProxy(c.table(name))

    def from_(self, name: str) -> _AsyncProxy:
        c = object.__getattribute__(self, '_c')
        return _AsyncProxy(c.from_(name))

    def rpc(self, fn: str, params=None) -> _AsyncProxy:
        c = object.__getattribute__(self, '_c')
        return _AsyncProxy(c.rpc(fn, params))

    def __getattr__(self, name: str):
        c = object.__getattribute__(self, '_c')
        return getattr(c, name)


# ── Singleton wrapper ──────────────────────────────────────────────────────────
_wrapper: _AsyncClientWrapper | None = None


def _build_client_sync() -> Client:
    """Crée le client Supabase synchrone (appel bloquant, exécuté dans thread)."""
    global _supabase_client
    if _supabase_client is None:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SERVICE_ROLE_KEY
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY sont requis dans le fichier .env"
            )
        _supabase_client = create_client(url, key)
        logger.info("Client Supabase (sync/thread) initialisé → %s", url)
    return _supabase_client


async def _build_client() -> _AsyncClientWrapper:
    """Retourne (ou crée) le wrapper async autour du client sync."""
    global _wrapper
    if _wrapper is None:
        client = await asyncio.to_thread(_build_client_sync)
        _wrapper = _AsyncClientWrapper(client)
    return _wrapper


async def get_db() -> _AsyncClientWrapper:
    """
    Dépendance FastAPI — retourne le client Supabase wrappé.
    Usage identique à l'ancien AsyncClient :
        db: AsyncClient = Depends(get_db)
        resp = await db.table('users').select('*').execute()
    """
    return await _build_client()


async def init_db() -> None:
    """
    Vérification de la connexion au démarrage (lifespan).
    Vérifie que les tables existent dans Supabase.
    """
    try:
        client = await _build_client()
        await client.table("users").select("id").limit(1).execute()
        logger.info("Supabase connecté — tables vérifiées ✅")
    except Exception as exc:
        logger.warning(
            "Tables Supabase inaccessibles. "
            "Exécutez supabase_migration.sql dans l'éditeur SQL Supabase "
            "(https://supabase.com/dashboard/project/qwxkhkumyokzykykindv/sql/new). "
            "Erreur : %s", exc,
        )


__all__ = ["Base", "engine", "get_db", "init_db", "_build_client"]
