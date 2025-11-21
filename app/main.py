# main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.views import router as views_router, init_db
from app.api import router as api_router
from app.utils.domain_validator import get_allowed_domains

import os

app = FastAPI(title="WebPush Dashboard", version="1.0")

# Initialize database tables
init_db()

# -------------------------------------------------
# Create folders if not exist
# -------------------------------------------------
os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
os.makedirs("app/static", exist_ok=True)

# -------------------------------------------------
# Static Mounts
# -------------------------------------------------
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_PATH), name="uploads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# -------------------------------------------------
# Dynamic CORS Middleware
# -------------------------------------------------
# Dashboard domain is always trusted
BASE_ALLOWED = [
    settings.DASHBOARD_DOMAIN,          # e.g. https://your-render-app.onrender.com
]

def cors_allow_origin(origin: str) -> bool:
    """
    Dynamically validate allowed origins:
    - Dashboard domain always allowed
    - Any website added by user in dashboard allowed
    """
    if origin in BASE_ALLOWED:
        return True

    dynamic_domains = get_allowed_domains()  # pulls domains from DB

    return origin in dynamic_domains


@app.middleware("http")
async def dynamic_cors_middleware(request: Request, call_next):
    """
    Custom CORS logic:
    - Reads the 'Origin' header
    - Checks if the origin matches the dashboard domain or any user website
    - If valid, adds CORS headers
    """
    origin = request.headers.get("origin")
    response = await call_next(request)

    if origin and cors_allow_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

    return response


# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(views_router)                  # dashboard (HTML pages)
app.include_router(api_router, prefix="/api")     # backend API routes


# -------------------------------------------------
# Root Route
# -------------------------------------------------
@app.get("/")
def root():
    return {"status": "running", "dashboard": settings.DASHBOARD_DOMAIN}
