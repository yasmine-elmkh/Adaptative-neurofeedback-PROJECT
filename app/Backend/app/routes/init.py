from app.routes.auth import router as auth_router
from app.routes.sessions import router as sessions_router
from app.routes.Profile import router as profile_router
from app.routes.admin import router as admin_router
from app.routes.assistant import router as assistant_router

__all__ = [
    "auth_router",
    "sessions_router",
    "profile_router",
    "admin_router",
    "assistant_router",
]
