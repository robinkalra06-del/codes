from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from .views import router as views_router, init_db
from .api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
init_db()

# static mounts
import os
os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=settings.UPLOADS_PATH), name='uploads')
app.mount('/static', StaticFiles(directory='app/static'), name='static')

app.include_router(views_router)
app.include_router(api_router, prefix='/api')

# minimal CORS to allow dashboard origin (others validated per-site)
origins = [settings.DASHBOARD_DOMAIN]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True
)
