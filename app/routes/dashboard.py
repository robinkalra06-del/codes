# app/routes/dashboard.py
from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Site, Subscription, NotificationLog
from app.utils import get_current_user
from app.storage import save_file
import json
from pywebpush import webpush, WebPushException
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/overview", response_class=HTMLResponse)
def dashboard_overview(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    sites = db.query(Site).filter(Site.owner_id == user.id).all()
    stats = []
    for s in sites:
        subcount = db.query(Subscription).filter(Subscription.site_id == s.id).count()
        sent = db.query(NotificationLog).filter(NotificationLog.site_id == s.id).count()
        stats.append({"site": s, "subscribers": subcount, "sent": sent})
    return templates.TemplateResponse("dashboard/overview.html", {"request": request, "user": user, "stats": stats})

@router.get("/dashboard/send", response_class=HTMLResponse)
def dashboard_send_get(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    sites = db.query(Site).filter(Site.owner_id == user.id).all()
    db.close()
    return templates.TemplateResponse("dashboard/send.html", {"request": request, "sites": sites})

@router.post("/dashboard/send")
def dashboard_send_post(request: Request, site_id: int = Form(...), title: str = Form(...), message: str = Form(...), icon: UploadFile = File(None), image: UploadFile = File(None)):
    user = get_current_user(request)
    db = SessionLocal()
    site = db.query(Site).filter(Site.id == site_id, Site.owner_id == user.id).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404)
    icon_url = None
    image_url = None
    if icon:
        icon_url = save_file(icon, "icon")
    if image:
        image_url = save_file(image, "image")
    subs = db.query(Subscription).filter(Subscription.site_id == site.id).all()
    payload = {"title": title, "body": message, "icon": icon_url, "image": image_url}
    sent = 0
    for s in subs:
        try:
            sub_json = json.loads(s.keys_json)
            webpush(subscription_info=sub_json, data=json.dumps(payload), vapid_private_key=site.vapid_private, vapid_claims={"sub": settings.VAPID_EMAIL})
            sent += 1
        except Exception as e:
            print("push error", e)
    log = NotificationLog(site_id=site.id, title=title, message=message, payload=json.dumps(payload), sent_to=sent)
    db.add(log)
    db.commit()
    db.close()
    return RedirectResponse("/dashboard/overview", status_code=302)

@router.get("/dashboard/subscribers", response_class=HTMLResponse)
def dashboard_subs(request: Request, site_id: int = None):
    user = get_current_user(request)
    db = SessionLocal()
    site = db.query(Site).filter(Site.owner_id == user.id).first() if not site_id else db.query(Site).filter(Site.id == site_id, Site.owner_id == user.id).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404)
    subs = db.query(Subscription).filter(Subscription.site_id == site.id).all()
    db.close()
    return templates.TemplateResponse("dashboard/subscribers.html", {"request": request, "site": site, "subscriptions": subs})
