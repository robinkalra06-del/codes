import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env only for local development
load_dotenv(BASE_DIR / '.env')

class Config:
    # Flask secret key
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')

    # Database
    # Render gives DATABASE_URL automatically (PostgreSQL)
    # For local it falls back to SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "app.db"}'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # VAPID Keys for Web Push
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
    VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')

    VAPID_CLAIMS = {
        "sub": os.getenv('VAPID_SUB', 'mailto:admin@example.com')
    }

    # Uploads
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        str(BASE_DIR / 'static' / 'uploads')
    )
