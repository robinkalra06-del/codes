# app/routes/__init__.py
from .sites import router as sites_router
from .dashboard import router as dashboard_router

__all__ = ["sites_router", "dashboard_router"]
