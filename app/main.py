# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.views import router as views_router, init_db
from app.api import router as api_router
from app.routes import sites_router, dashboard_router
from app.utils import get_current_user
from app.db import SessionLocal
import os

app = FastAPI(title="WebPush Dashboard", version="1.0")

# create uploads
os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
os.makedirs("app/static", exist_ok=True)

# mount static & uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_PATH), name="uploads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# init DB
init_db()

# minimal CORS to allow dashboard domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DASHBOARD_DOMAIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(views_router)
app.include_router(api_router, prefix="/api")
app.include_router(sites_router)
app.include_router(dashboard_router)

# dynamic CORS middleware (override for user origins)
@app.middleware("http")
async def dynamic_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    response = await call_next(request)
    if origin:
        # check DB sites for domain match
        db = SessionLocal()
        from app.models import Site
        match = db.query(Site).filter(Site.domain == origin).first()
        db.close()
        if match or origin == settings.DASHBOARD_DOMAIN:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response
