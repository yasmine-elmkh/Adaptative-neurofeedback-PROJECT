"""
Backward-compatibility shim — delegates to app.core.database.
"""
from app.core.database import Base, engine, AsyncSessionLocal, get_db, init_db

__all__ = ["Base", "engine", "AsyncSessionLocal", "get_db", "init_db"]
