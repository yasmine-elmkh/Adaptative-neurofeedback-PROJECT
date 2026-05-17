"""
=============================================================================
SERVICE D'AUTHENTIFICATION
=============================================================================
Gère:
- Hash et vérification des mots de passe (bcrypt)
- Génération et validation des JWT tokens
- Récupération de l'utilisateur actuel depuis le token
- Rafraîchissement des tokens (refresh token)
=============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.config import get_settings
from app.models import User
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# ===== CONFIGURATION BCRYPT =====
# Hachage sécurisé des mots de passe avec bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Coût computationnel (plus élevé = plus sécurisé mais lent)
)


class AuthService:
    """Service centralisé d'authentification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hache un mot de passe en plaintext
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            Hash bcrypt
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie qu'un mot de passe en clair correspond au hash
        
        Args:
            plain_password: Mot de passe en clair
            hashed_password: Hash stocké en BD
            
        Returns:
            True si correct, False sinon
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crée un JWT access token
        
        Args:
            user_id: ID de l'utilisateur
            expires_delta: Durée de vie personnalisée (défaut: config)
            
        Returns:
            JWT token encodé
        """
        if expires_delta is None:
            expires_delta = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": user_id,  # "sub" (subject) = ID utilisateur
            "exp": expire,   # exp (expiration) = timestamp
            "iat": datetime.utcnow()  # iat (issued at) = timestamp création
        }
        
        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Vérifie et décode un JWT token
        
        Args:
            token: JWT token à vérifier
            
        Returns:
            user_id si valide, None sinon
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    @staticmethod
    def get_current_user(token: str, db: Session) -> Optional[User]:
        """
        Récupère l'utilisateur associé au token
        
        Args:
            token: JWT token
            db: Session SQLAlchemy
            
        Returns:
            Objet User ou None
        """
        user_id = AuthService.verify_token(token)
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return None
        
        return user