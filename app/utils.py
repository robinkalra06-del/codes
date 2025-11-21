import secrets, jwt, datetime
from passlib.context import CryptContext
from .config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    password = password[:72]        
    return pwd.hash(password)
def verify_password(password: str, hashed: str):
    password = password[:72]
    return pwd.verify(password, hashed)

def gen_site_key(): return secrets.token_urlsafe(32)

def create_jwt(payload: dict, days: int = 3650):
    exp = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    payload2 = payload.copy()
    payload2.update({"exp": exp})
    return jwt.encode(payload2, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_jwt(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None
