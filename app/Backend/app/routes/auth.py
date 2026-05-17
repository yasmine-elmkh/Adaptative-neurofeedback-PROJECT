"""
NeuroCap — Routes d'Authentification
======================================
POST /api/auth/register  → Inscription (retourne access + refresh token)
POST /api/auth/login     → Connexion
POST /api/auth/refresh   → Rafraîchir le token
GET  /api/auth/me        → Profil de l'utilisateur connecté
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from jose import JWTError, jwt
from supabase import AsyncClient

from app.core.database import get_db
from app.core.config import get_settings
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    get_current_user,
)
from app.middleware.security import check_brute_force, record_failed_login, reset_failed_login
from fastapi.responses import Response
from app.schemas import UserCreate, UserLogin, UserOut, TokenOut, TokenRefresh, PasswordChange

router = APIRouter(prefix="/api/auth", tags=["Authentification"])
settings = get_settings()


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(data: UserCreate, db: AsyncClient = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.\
    Workflow :
      1. Vérifier que l'email n'existe pas déjà
      2. Générer un username depuis l'email si absent
      3. Hasher le mot de passe avec bcrypt
      4. Créer l'utilisateur dans Supabase
      5. Retourner access + refresh token (auto-login)
    """
    # Vérification unicité email
    resp = await db.table("users").select("id").eq("email", data.email).execute()
    if resp.data:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    # Dériver le username depuis prénom.nom ou email si non fourni
    if data.first_name and data.last_name:
        username = data.username or f"{data.first_name.lower()}.{data.last_name.lower()}"
    else:
        username = data.username or data.email.split("@")[0]

    # Unicité du username — ajouter un suffixe si nécessaire
    base_username = username
    suffix = 0
    while True:
        resp = await db.table("users").select("id").eq("username", username).execute()
        if not resp.data:
            break
        suffix += 1
        username = f"{base_username}{suffix}"

    # Créer l'utilisateur
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user_payload = {
        "id": user_id,
        "email": data.email,
        "username": username,
        "first_name": data.first_name or "",
        "last_name": data.last_name or "",
        "hashed_password": hash_password(data.password),
        "role": "user",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    try:
        await db.table("users").insert(user_payload).execute()
    except Exception as e:
        err_msg = str(e)
        # Colonnes first_name/last_name absentes → réessayer sans elles
        if "first_name" in err_msg or "last_name" in err_msg or "PGRST204" in err_msg:
            user_payload.pop("first_name", None)
            user_payload.pop("last_name", None)
            await db.table("users").insert(user_payload).execute()
        else:
            raise HTTPException(status_code=500, detail=f"Erreur base de données : {err_msg}")

    # Auto-login : retourner les tokens directement
    token_data = {"sub": user_id}
    return TokenOut(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/login", response_model=TokenOut)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncClient = Depends(get_db),
):
    """
    Connexion — retourne access + refresh token.

    Sécurité :
      - check_brute_force() bloque l'IP après LOGIN_MAX_ATTEMPTS échecs
      - Réponse générique (ne révèle pas si l'email existe)
      - reset_failed_login() après succès
    """
    ip = request.client.host if request.client else "unknown"

    # Vérification anti-brute force avant toute requête DB
    check_brute_force(ip)

    # Rechercher l'utilisateur par email
    resp = await db.table("users").select("*").eq("email", data.email).execute()
    user = resp.data[0] if resp.data else None

    if not user or not verify_password(data.password, user.get("hashed_password", "")):
        record_failed_login(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Compte désactivé")

    # Login réussi — réinitialiser le compteur d'échecs
    reset_failed_login(ip)

    # Créer les tokens JWT
    token_data = {"sub": user["id"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Audit log
    await db.table("audit_logs").insert({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "action": "LOGIN",
        "ip_address": ip,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
async def refresh_token(data: TokenRefresh, db: AsyncClient = Depends(get_db)):
    """
    Rafraîchit le token d'accès avec un refresh token valide.
    Appelé automatiquement par le frontend quand l'access token expire.
    """
    try:
        payload = jwt.decode(
            data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    # Vérifier que l'utilisateur existe encore
    resp = await db.table("users").select("id,is_active").eq("id", user_id).execute()
    user = resp.data[0] if resp.data else None
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    token_data = {"sub": user["id"]}
    return TokenOut(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    """Retourne le profil de l'utilisateur connecté."""
    return current_user


@router.post("/change-password", status_code=204)
async def change_password(
    data: PasswordChange,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Change le mot de passe de l'utilisateur connecté."""
    if not verify_password(data.current_password, current_user.get("hashed_password", "")):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    hashed = hash_password(data.new_password)
    await db.table("users").update({
        "hashed_password": hashed,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", current_user["id"]).execute()
    return Response(status_code=204)
