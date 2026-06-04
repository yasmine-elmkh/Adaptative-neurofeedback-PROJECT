"""
NeuroCap — Routes d'Authentification
======================================
POST /api/auth/send-code    → Envoyer un code de vérification par email
POST /api/auth/register     → Inscription (avec vérification du code)
POST /api/auth/login        → Connexion (erreurs distinctes email/password)
POST /api/auth/refresh      → Rafraîchir le token
GET  /api/auth/me           → Profil de l'utilisateur connecté
"""

import logging
import random
import uuid
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

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
from app.schemas import (
    UserCreate, UserLogin, UserOut, TokenOut, TokenRefresh,
    PasswordChange, EmailVerificationRequest,
)
from app.services.email_service import send_verification_email, EmailSendError

router = APIRouter(prefix="/api/auth", tags=["Authentification"])
settings = get_settings()

# ── Stockage en mémoire des codes en attente ──────────────────────────────────
# { email: {"code": "12345678", "expires_at": datetime} }
# Simple et efficace pour un déploiement mono-instance.
_pending_codes: dict[str, dict] = {}

CODE_TTL_MINUTES = 10


@router.post("/send-code", status_code=200)
async def send_verification_code(
    data: EmailVerificationRequest,
    db: AsyncClient = Depends(get_db),
):
    """
    Envoie un code de vérification à 8 chiffres par email.
    Vérifie d'abord que l'email n'est pas déjà utilisé.
    """
    # Vérifier que l'email n'existe pas déjà
    resp = await db.table("users").select("id").eq("email", data.email).execute()
    if resp.data:
        raise HTTPException(
            status_code=409,
            detail="Un compte existe déjà avec cet email"
        )

    # Générer un code à 8 chiffres
    code = f"{random.randint(0, 99_999_999):08d}"

    # Stocker avec TTL
    _pending_codes[data.email] = {
        "code": code,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES),
    }

    # Envoyer l'email via Resend — lève HTTPException 503 si l'envoi échoue
    try:
        await send_verification_email(data.email, code)
    except EmailSendError as exc:
        # Supprimer le code stocké car l'email n'a pas été envoyé
        _pending_codes.pop(data.email, None)
        logger.error("Échec envoi code vérification pour %s : %s", data.email, exc)
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    response = {"message": f"Code envoyé à {data.email}"}
    # _dev_code seulement si SMTP_USER absent (email pas vraiment envoyé)
    if not settings.SMTP_USER:
        response["_dev_code"] = code

    return response


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(data: UserCreate, db: AsyncClient = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    Workflow :
      1. Valider le code de vérification
      2. Vérifier que l'email n'existe pas déjà
      3. Générer le username
      4. Hasher le mot de passe avec bcrypt
      5. Créer l'utilisateur dans Supabase
      6. Retourner access + refresh token (auto-login)
    """
    # Valider le code de vérification
    pending = _pending_codes.get(data.email)
    if not pending:
        raise HTTPException(
            status_code=400,
            detail="Aucun code envoyé pour cet email. Demandez d'abord un code de vérification."
        )
    if datetime.now(timezone.utc) > pending["expires_at"]:
        _pending_codes.pop(data.email, None)
        raise HTTPException(
            status_code=400,
            detail="Code expiré. Demandez un nouveau code de vérification."
        )
    if pending["code"] != data.verification_code:
        raise HTTPException(
            status_code=400,
            detail="Code de vérification incorrect"
        )

    # Supprimer le code utilisé
    _pending_codes.pop(data.email, None)

    # Validation force du mot de passe (double vérification côté serveur)
    if not data.password_is_strong:
        raise HTTPException(
            status_code=400,
            detail="Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial."
        )

    # Vérification unicité email
    resp = await db.table("users").select("id").eq("email", data.email).execute()
    if resp.data:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")

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
        if "first_name" in err_msg or "last_name" in err_msg or "PGRST204" in err_msg:
            user_payload.pop("first_name", None)
            user_payload.pop("last_name", None)
            try:
                await db.table("users").insert(user_payload).execute()
            except Exception as e2:
                raise HTTPException(status_code=500, detail=f"Erreur base de données : {e2}")
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
    Retourne des erreurs distinctes pour email introuvable vs mot de passe incorrect.
    """
    ip = request.client.host if request.client else "unknown"
    check_brute_force(ip)

    # Rechercher l'utilisateur par email
    resp = await db.table("users").select("*").eq("email", data.email).execute()
    user = resp.data[0] if resp.data else None

    if not user:
        record_failed_login(ip)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte trouvé avec cet email",
        )

    if not verify_password(data.password, user.get("hashed_password", "")):
        record_failed_login(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect",
        )

    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Compte désactivé")

    reset_failed_login(ip)

    token_data = {"sub": user["id"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    try:
        await db.table("audit_logs").insert({
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "action": "LOGIN",
            "ip_address": ip,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        logger.warning("audit_logs insert failed (table may not exist): %s", e)

    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
async def refresh_token(data: TokenRefresh, db: AsyncClient = Depends(get_db)):
    try:
        payload = jwt.decode(
            data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

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
    return current_user


@router.post("/change-password", status_code=204)
async def change_password(
    data: PasswordChange,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    if data.current_password:
        if not verify_password(data.current_password, current_user.get("hashed_password", "")):
            raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    hashed = hash_password(data.new_password)
    await db.table("users").update({
        "hashed_password": hashed,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", current_user["id"]).execute()
    return Response(status_code=204)
