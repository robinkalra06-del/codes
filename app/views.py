# app/views.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base, User, Site
from .utils import hash_password, verify_password, create_jwt
from .vapid import generate_vapid_keys, gen_site_key
from .config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def init_db():
    Base.metadata.create_all(bind=engine)

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def reg_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def reg_post(request: Request, email: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    if db.query(User).filter(User.email == email).first():
        db.close()
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already exists"})
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    # create default site placeholder
    site_key = gen_site_key()
    priv, pub = generate_vapid_keys()
    site = Site(
        owner_id=user.id,
        name=f"{email} site",
        domain=f"https://{email.split('@')[0]}.example.com",
        site_key=site_key,
        vapid_public=pub,
        vapid_private=priv
    )
    db.add(site)
    db.commit()
    db.close()
    return RedirectResponse("/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        db.close()
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_jwt({"user_id": user.id})
    resp = RedirectResponse("/dashboard/overview", status_code=302)
    resp.set_cookie("session", token, httponly=True, samesite="lax")
    db.close()
    return resp

@router.get("/logout")
def logout():
    resp = RedirectResponse("/login")
    resp.delete_cookie("session")
    return resp
