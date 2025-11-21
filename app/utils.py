# app/utils.py
import secrets, time
from passlib.context import CryptContext
import jwt
from fastapi import Request, HTTPException
from .config import settings
from .db import SessionLocal
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt has 72 bytes limit; ensure short or truncate externally if needed
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_jwt(data: dict, expire_seconds: int = 60*60*24*7):
    payload = data.copy()
    payload["exp"] = int(time.time()) + expire_seconds
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_jwt(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None

def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    data = decode_jwt(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = SessionLocal()
    user = db.get(User, user_id)
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
