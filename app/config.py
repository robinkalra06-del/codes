# app/config.py
import os
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALGORITHM: str = "HS256"
    DASHBOARD_DOMAIN: str = os.getenv("DASHBOARD_DOMAIN", "https://your-render-app.onrender.com")
    UPLOADS_PATH: str = os.getenv("UPLOADS_PATH", "uploads")
    VAPID_EMAIL: str = os.getenv("VAPID_EMAIL", "mailto:admin@example.com")
    USE_S3: bool = False  # set true and configure S3 env vars if using S3

    class Config:
        env_file = ".env"

settings = Settings()
