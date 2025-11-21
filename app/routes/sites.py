# app/routes/sites.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Site
from app.utils import get_current_user
from app.vapid import generate_vapid_keys_pair, gen_site_key

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/sites", response_class=HTMLResponse)
def sites_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    sites = db.query(Site).filter(Site.owner_id == user.id).all()
    return templates.TemplateResponse("dashboard/sites_list.html", {"request": request, "sites": sites})

@router.get("/dashboard/sites/new", response_class=HTMLResponse)
def sites_new(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("dashboard/site_new.html", {"request": request})

@router.post("/dashboard/sites")
def sites_create(request: Request, name: str = Form(...), domain: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request)
    site_key = gen_site_key()

    # FIXED: Use pywebpush API
    priv, pub = generate_vapid_keys_pair()

    site = Site(
        owner_id=user.id,
        name=name,
        domain=domain,
        site_key=site_key,
        vapid_public=pub,
        vapid_private=priv
    )
    db.add(site)
    db.commit()
    return RedirectResponse(url=f"/dashboard/sites/{site_key}/integration", status_code=302)

@router.get("/dashboard/sites/{site_key}/integration", response_class=HTMLResponse)
def site_integration(site_key: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    site = db.query(Site).filter(Site.site_key == site_key, Site.owner_id == user.id).first()
    if not site:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("dashboard/site_integration.html", {"request": request, "site": site})
