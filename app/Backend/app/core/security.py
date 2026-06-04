"""
NeuroCap — Sécurité (JWT, bcrypt, dépendances FastAPI)
=======================================================
Utilise Supabase AsyncClient (plus SQLAlchemy).
Corrige le hachage bcrypt avec troncature à 72 bytes.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import AsyncClient

from app.config import get_settings
from app.core.database import get_db

settings = get_settings()
bearer = HTTPBearer()

# ── Utilitaires mot de passe (bcrypt direct) ──────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hashe un mot de passe en clair avec bcrypt.
    Troncature automatique à 72 bytes (limite bcrypt).
    """
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Vérifie un mot de passe contre son hash bcrypt (troncature auto)."""
    plain_bytes = plain.encode('utf-8')[:72]
    return bcrypt.checkpw(plain_bytes, hashed.encode('utf-8'))

# ── Tokens JWT ────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["type"] = "access"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload["type"] = "refresh"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )

# ── Dépendances FastAPI ───────────────────────────────────────────────────────

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncClient = Depends(get_db),
) -> Dict[str, Any]:
    payload = _decode_token(creds.credentials)
    user_id: Optional[str] = payload.get("sub")
    if not user_id or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Token invalide")

    resp = await db.table("users").select("*").eq("id", user_id).execute()
    user = resp.data[0] if resp.data else None

    if not user or not user.get("is_active"):
        raise HTTPException(status_code=401, detail="Utilisateur introuvable ou inactif")

    return user

async def get_token_user_id(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncClient = Depends(get_db),
) -> str:
    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token invalide")
        resp = await db.table("users").select("id,is_active").eq("id", user_id).execute()
        user = resp.data[0] if resp.data else None
        if not user or not user.get("is_active"):
            raise HTTPException(status_code=401, detail="Utilisateur introuvable ou inactif")
        return user["id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs",
        )
    return current_user


async def get_therapist_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if current_user.get("role") not in ("therapist", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux thérapeutes",
        )
    return current_user


def is_patient(user: Dict[str, Any]) -> bool:
    """True si l'utilisateur est un patient (role user ou patient)."""
    return user.get("role") in ("user", "patient")