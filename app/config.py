import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-jwt")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    DASHBOARD_DOMAIN = os.getenv("DASHBOARD_DOMAIN", "http://localhost:8000")
    VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:admin@example.com")
    USE_S3 = os.getenv("USE_S3", "false").lower() in ("1","true","yes")
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    S3_REGION = os.getenv("S3_REGION", "")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
    UPLOADS_PATH = os.getenv("UPLOADS_PATH", "./uploads")

settings = Settings()
