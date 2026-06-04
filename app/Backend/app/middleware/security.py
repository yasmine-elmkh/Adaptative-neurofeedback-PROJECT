"""
NeuroCap — Middleware de Sécurité Complet
==========================================
Ce module centralise TOUTES les couches de protection de l'API :

  ┌─────────────────────────────────────────────────────────────────┐
  │ Couche 1 : CORS            — origines autorisées uniquement     │
  │ Couche 2 : Rate Limiting   — max 100 req/IP/60s (sliding window)│
  │ Couche 3 : Taille requête  — max 10 MB (anti-DDoS payload)      │
  │ Couche 4 : Headers HTTP    — CSP, HSTS, X-Frame, Referrer       │
  │ + Brute Force Auth         — 5 échecs → blocage 15 min          │
  └─────────────────────────────────────────────────────────────────┘

Pourquoi sans bibliothèque externe (pas de slowapi) ?
  → Pas de dépendance supplémentaire, fonctionne en SQLite ET PostgreSQL,
    et suffisant pour un déploiement à instance unique.
  → Pour multi-instances, remplacer _rate_limit_store par Redis.

Attaques couvertes :
  - DDoS applicatif         : rate limiting par IP
  - Brute force login       : lockout progressif
  - Clickjacking            : X-Frame-Options: DENY
  - MIME sniffing           : X-Content-Type-Options: nosniff
  - Injection XSS           : Content-Security-Policy stricte
  - Man-in-the-Middle HTTP  : HSTS (en production)
  - Payload flooding        : limite de taille de requête
  - CSRF                    : SameSite cookies + Origin check dans CORS
  - Credential leakage      : Referrer-Policy restrictive
"""

import time
import logging
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Tuple, Optional

from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ════════════════════════════════════════════════════════════════════════════
# STOCKAGE EN MÉMOIRE (thread-safe)
# ════════════════════════════════════════════════════════════════════════════
#
# Pour un déploiement multi-instances (Kubernetes, etc.) :
#   → Remplacer ces dicts par des appels Redis :
#       await redis.incr(f"rl:{ip}", amount=1, ex=60)
#       await redis.expire(f"bf:{ip}", settings.LOGIN_LOCKOUT_SECONDS)
#
# Structure rate limit  : { "1.2.3.4": [1716800000.1, 1716800001.3, ...] }
# Structure brute force : { "1.2.3.4": (attempts: int, first_ts: float) }
# ════════════════════════════════════════════════════════════════════════════

_rate_limit_store: Dict[str, List[float]] = defaultdict(list)
_brute_force_store: Dict[str, Tuple[int, float]] = {}
_lock = Lock()  # Protège les deux dicts contre les race conditions


# ════════════════════════════════════════════════════════════════════════════
# RATE LIMITING — Fenêtre Glissante (Sliding Window)
# ════════════════════════════════════════════════════════════════════════════

def check_rate_limit(ip: str, path: str = "") -> None:
    """
    Vérifie si une IP a dépassé le quota de requêtes.

    Algorithme : Sliding Window Counter
      - On conserve la liste des timestamps des N dernières requêtes.
      - Avant chaque requête, on purge les timestamps hors de la fenêtre.
      - Si la liste dépasse RATE_LIMIT_MAX après purge → HTTP 429.

    Paramètres :
        ip   : adresse IP du client (depuis request.client.host)
        path : chemin de la requête (pour les logs)

    Lève :
        HTTPException 429 si le quota est dépassé.
    """
    now = time.time()
    window = settings.RATE_LIMIT_WINDOW
    max_req = settings.RATE_LIMIT_MAX

    with _lock:
        # Supprimer les entrées hors de la fenêtre temporelle
        _rate_limit_store[ip] = [
            ts for ts in _rate_limit_store[ip]
            if now - ts < window
        ]

        if len(_rate_limit_store[ip]) >= max_req:
            logger.warning("Rate limit: IP=%s path=%s count=%d", ip, path, max_req)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Trop de requêtes. Maximum {max_req} par {window}s.",
                headers={"Retry-After": str(window)},
            )

        # Enregistrer la requête courante
        _rate_limit_store[ip].append(now)


# ════════════════════════════════════════════════════════════════════════════
# PROTECTION ANTI-BRUTE FORCE (Login)
# ════════════════════════════════════════════════════════════════════════════

def check_brute_force(ip: str) -> None:
    """
    Vérifie si une IP est actuellement bloquée suite à trop de tentatives.

    À appeler AU DÉBUT de la route /auth/login, AVANT de toucher la base.
    Ainsi, même les requêtes avec un email inexistant consomment le quota.

    Lève :
        HTTPException 429 si l'IP est en période de lockout.
    """
    now = time.time()
    lockout = settings.LOGIN_LOCKOUT_SECONDS
    max_attempts = settings.LOGIN_MAX_ATTEMPTS

    with _lock:
        if ip not in _brute_force_store:
            return  # Pas d'historique → autoriser

        attempts, first_ts = _brute_force_store[ip]

        if attempts >= max_attempts:
            elapsed = now - first_ts
            if elapsed < lockout:
                remaining = int(lockout - elapsed)
                logger.warning(
                    "Brute force bloqué: IP=%s tentatives=%d restant=%ds",
                    ip, attempts, remaining,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Compte temporairement bloqué après {max_attempts} échecs. "
                        f"Réessayez dans {remaining} secondes."
                    ),
                    headers={"Retry-After": str(remaining)},
                )
            else:
                # La fenêtre de lockout est expirée — réinitialiser proprement
                del _brute_force_store[ip]


def record_failed_login(ip: str) -> None:
    """
    Incrémente le compteur d'échecs de login pour une IP.

    À appeler dans /auth/login quand email ou mot de passe est incorrect.
    Ne révèle PAS si c'est l'email ou le mot de passe qui est faux
    (réponse générique pour éviter l'énumération de comptes).
    """
    now = time.time()
    lockout = settings.LOGIN_LOCKOUT_SECONDS
    max_attempts = settings.LOGIN_MAX_ATTEMPTS

    with _lock:
        if ip not in _brute_force_store:
            # Premier échec pour cette IP
            _brute_force_store[ip] = (1, now)
            logger.info("Échec login #1: IP=%s", ip)
        else:
            attempts, first_ts = _brute_force_store[ip]
            # Réinitialiser si la fenêtre est expirée
            if now - first_ts >= lockout:
                _brute_force_store[ip] = (1, now)
            else:
                new_count = attempts + 1
                _brute_force_store[ip] = (new_count, first_ts)
                logger.warning(
                    "Échec login #%d: IP=%s (lockout à #%d)",
                    new_count, ip, max_attempts,
                )


def reset_failed_login(ip: str) -> None:
    """
    Réinitialise le compteur d'échecs après un login réussi.

    À appeler dans /auth/login après une authentification réussie.
    Évite qu'un utilisateur légitime reste bloqué après un oubli de mot de passe.
    """
    with _lock:
        removed = _brute_force_store.pop(ip, None)
        if removed:
            logger.info("Compteur brute force réinitialisé: IP=%s", ip)


def get_brute_force_status(ip: str) -> Optional[Dict]:
    """
    Retourne l'état brute force d'une IP (utile pour les logs admin).
    Retourne None si l'IP n'a pas d'historique.
    """
    with _lock:
        if ip not in _brute_force_store:
            return None
        attempts, first_ts = _brute_force_store[ip]
        return {
            "ip": ip,
            "attempts": attempts,
            "first_attempt": first_ts,
            "locked": attempts >= settings.LOGIN_MAX_ATTEMPTS,
        }


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION GLOBALE DES MIDDLEWARES
# ════════════════════════════════════════════════════════════════════════════

def add_security_middleware(app) -> None:
    """
    Enregistre toutes les couches de sécurité sur l'app FastAPI.

    À appeler UNE SEULE FOIS dans main.py, juste après `app = FastAPI(...)`.

    Ordre d'exécution des middlewares Starlette (LIFO — Last In First Out) :
      Le dernier middleware ajouté est exécuté EN PREMIER sur les requêtes
      et EN DERNIER sur les réponses.

      Ordre d'ajout   → Ordre d'exécution requête
      ─────────────────────────────────────────────
      1. CORS         → 4. CORS (vérifie Origin, gère OPTIONS preflight)
      2. Rate limit   → 3. Rate limit (bloque les IPs trop actives)
      3. Body size    → 2. Body size (rejette les payloads trop lourds)
      4. Sec headers  → 1. Sec headers (ajoute les headers à TOUTES les réponses)
    """

    # ── Couche 1 : CORS ───────────────────────────────────────────────────────
    # Protège contre les requêtes cross-origin non autorisées (CSRF navigateur).
    # En production, ALLOWED_ORIGINS ne doit contenir QUE le domaine frontend.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,   # Nécessaire pour les cookies httpOnly (refresh token)
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept-Language"],
        expose_headers=["X-Process-Time", "X-Request-ID"],
        max_age=600,              # Cache preflight OPTIONS 10 minutes
    )

    # ── Couche 2 : Rate limiting global ───────────────────────────────────────
    # 100 requêtes par IP par fenêtre de 60 secondes.
    # Les routes sensibles (/auth/login) ont leur propre limite via check_brute_force.
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Ignorer les endpoints de santé et les requêtes preflight OPTIONS
        if request.url.path in ("/health", "/api/health") or request.method == "OPTIONS":
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        try:
            check_rate_limit(ip, request.url.path)
        except HTTPException as exc:
            # Retourner un JSON propre avec les bons headers
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=dict(exc.headers or {}),
            )
        return await call_next(request)

    # ── Couche 3 : Limite de taille des requêtes (anti-DDoS payload) ──────────
    # Rejette les corps de requête dépassant 10 MB.
    # Les données EEG (1000 float32 = ~4 KB) sont très en dessous.
    @app.middleware("http")
    async def request_size_middleware(request: Request, call_next):
        max_size = 10 * 1024 * 1024  # 10 MB
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Requête trop volumineuse. Maximum 10 MB."},
            )
        return await call_next(request)

    # ── Couche 4 : Headers de sécurité HTTP ───────────────────────────────────
    # Ces headers sont ajoutés à TOUTES les réponses, y compris les erreurs.
    # Ils instruisent le navigateur sur la politique de sécurité du serveur.
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)

        # ── X-Content-Type-Options ──────────────────────────────────────────
        # Empêche le navigateur de deviner le type MIME d'une réponse.
        # Prévient les attaques de type "content-type confusion".
        response.headers["X-Content-Type-Options"] = "nosniff"

        # ── X-Frame-Options ──────────────────────────────────────────────────
        # Interdit l'affichage de l'app dans une iframe.
        # Prévient les attaques de clickjacking.
        response.headers["X-Frame-Options"] = "DENY"

        # ── Strict-Transport-Security (HSTS) ─────────────────────────────────
        # Force le navigateur à utiliser HTTPS pendant 1 an.
        # Activé uniquement hors DEBUG (en production derrière un reverse proxy).
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # ── Content-Security-Policy ──────────────────────────────────────────
        # Restreint les sources de contenu pour prévenir les injections XSS.
        # Explications :
        #   default-src 'self'          → tout le contenu doit venir du même domaine
        #   script-src 'self'           → scripts uniquement depuis le domaine (pas d'inline)
        #   style-src 'unsafe-inline'   → nécessaire pour Tailwind CSS (classes dynamiques)
        #   img-src cloudinary.com      → images depuis Cloudinary autorisées
        #   connect-src wss:            → WebSockets EEG autorisés
        #   frame-ancestors 'none'      → renforce X-Frame-Options
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            f"img-src 'self' data: https://res.cloudinary.com; "
            "connect-src 'self' wss: ws:; "
            "font-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

        # ── Referrer-Policy ───────────────────────────────────────────────────
        # Limite les informations envoyées dans le header Referer.
        # "strict-origin-when-cross-origin" : envoie uniquement l'origine (pas le path)
        # pour les requêtes cross-origin. Évite les fuites d'URL avec tokens.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # ── Permissions-Policy ────────────────────────────────────────────────
        # Désactive explicitement les APIs navigateur non utilisées.
        # Prévient les malwares qui tenteraient d'accéder à la caméra/micro.
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), "
            "usb=(), accelerometer=(), gyroscope=()"
        )

        # ── X-Process-Time ───────────────────────────────────────────────────
        # Temps de traitement en secondes (utile pour le monitoring).
        process_time = time.time() - start
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # ── Log structuré de chaque requête ──────────────────────────────────
        ip = request.client.host if request.client else "unknown"
        logger.info(
            "%-6s %-40s %d %.3fs %s",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            ip,
        )

        return response
