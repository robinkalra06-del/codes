from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal
from app.models import Base, User, Site, Subscription, NotificationLog
from app.utils import hash_password, verify_password, gen_site_key, create_jwt
from app.vapid import generate_vapid_keys
from app.config import settings
from app.storage import save_file
import secrets
import json

templates = Jinja2Templates(directory='app/templates')
router = APIRouter()


# -------------------------------
# Init DB
# -------------------------------
def init_db():
    Base.metadata.create_all(bind=engine)


# -------------------------------
# Public pages
# -------------------------------
@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------------
# Register
# -------------------------------
@router.get("/register", response_class=HTMLResponse)
def reg_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def reg_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    db: Session = SessionLocal()
    if db.query(User).filter(User.email == email).first():
        db.close()
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Email exists"}
        )

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.close()

    return RedirectResponse("/login", status_code=302)


# -------------------------------
# Login
# -------------------------------
@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        db.close()
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}
        )

    token = create_jwt({"user_id": user.id})
    resp = RedirectResponse("/dashboard/overview", status_code=302)
    resp.set_cookie("session", token, httponly=True, samesite="lax")
    db.close()
    return resp


# -------------------------------
# Current user helper
# -------------------------------
def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    import jwt
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    db = SessionLocal()
    user = db.query(User).filter(User.id == data["user_id"]).first()
    db.close()

    if not user:
        raise HTTPException(status_code=401)

    return user


# -------------------------------
# Dashboard: Overview
# -------------------------------
@router.get("/dashboard/overview", response_class=HTMLResponse)
def dashboard_overview(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    sites = db.query(Site).filter(Site.owner_id == user.id).all()

    stats = []
    for s in sites:
        subscribers = db.query(Subscription).filter(Subscription.site_id == s.id).count()
        sent = db.query(NotificationLog).filter(NotificationLog.site_id == s.id).count()
        stats.append({"site": s, "subscribers": subscribers, "sent": sent})

    db.close()
    return templates.TemplateResponse(
        "dashboard/overview.html",
        {"request": request, "user": user, "stats": stats},
    )


# ============================================================================
#          MULTI-WEBSITE SYSTEM  (PushAlert style)
# ============================================================================

# -------------------------------
# List sites
# -------------------------------
@router.get("/dashboard/sites", response_class=HTMLResponse)
def sites_list(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    sites = db.query(Site).filter(Site.owner_id == user.id).all()
    db.close()
    return templates.TemplateResponse(
        "dashboard/sites_list.html", {"request": request, "sites": sites}
    )


# -------------------------------
# Add new site (Form)
# -------------------------------
@router.get("/dashboard/sites/new", response_class=HTMLResponse)
def sites_new(request: Request):
    return templates.TemplateResponse(
        "dashboard/site_new.html", {"request": request}
    )


# -------------------------------
# Create new website
# -------------------------------
@router.post("/dashboard/sites")
def sites_create(
    request: Request,
    name: str = Form(...),
    domain: str = Form(...),
):
    user = get_current_user(request)
    db = SessionLocal()

    site_key = secrets.token_urlsafe(32)
    priv, pub = generate_vapid_keys()

    site = Site(
        owner_id=user.id,
        name=name,
        domain=domain,
        site_key=site_key,
        vapid_public=pub,
        vapid_private=priv,
    )

    db.add(site)
    db.commit()
    db.close()

    return RedirectResponse(
        f"/dashboard/sites/{site_key}/integration", status_code=302
    )


# -------------------------------
# Integration page
# -------------------------------
@router.get(
    "/dashboard/sites/{site_key}/integration", response_class=HTMLResponse
)
def site_integration(site_key: str, request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    site = (
        db.query(Site)
        .filter(Site.site_key == site_key, Site.owner_id == user.id)
        .first()
    )
    db.close()

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    return templates.TemplateResponse(
        "dashboard/site_integration.html",
        {"request": request, "site": site},
    )


# -------------------------------
# Dynamic pushclient.js
# -------------------------------
@router.get("/pushclient/{site_key}.js")
def pushclient_js(site_key: str):
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key == site_key).first()
    db.close()

    if not site:
        raise HTTPException(status_code=404)

    template = """
const SITE_KEY = "{{site_key}}";
const VAPID_PUBLIC_KEY = "{{vapid}}";

async function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\\-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function registerPush() {
    if (!('serviceWorker' in navigator)) return;
    const sw = await navigator.serviceWorker.register('/service-worker.js');

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return;

    const applicationServerKey = await urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
    const subscription = await sw.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey
    });

    await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            site_key: SITE_KEY,
            subscription: subscription
        })
    });
}

registerPush();
"""

    js = template.replace("{{site_key}}", site.site_key).replace(
        "{{vapid}}", site.vapid_public.replace("\n", "\\n")
    )

    return PlainTextResponse(js, media_type="application/javascript")


# -------------------------------
# Service Worker
# -------------------------------
@router.get("/service-worker.js")
def service_worker():
    sw = open("app/static/sw/service-worker.js").read()
    return PlainTextResponse(sw, media_type="application/javascript")


# ============================================================================
# Send Notification
# ============================================================================
@router.get("/dashboard/send", response_class=HTMLResponse)
def dashboard_send_get(request: Request, site_id: int = None):
    user = get_current_user(request)
    db = SessionLocal()

    site = (
        db.query(Site).filter(Site.owner_id == user.id).first()
        if not site_id
        else db.query(Site)
        .filter(Site.id == site_id, Site.owner_id == user.id)
        .first()
    )

    if not site:
        db.close()
        raise HTTPException(status_code=404)

    db.close()
    return templates.TemplateResponse(
        "dashboard/send.html", {"request": request, "site": site}
    )


@router.post("/dashboard/send")
def dashboard_send_post(
    request: Request,
    site_id: int = Form(...),
    title: str = Form(...),
    message: str = Form(...),
    url: str = Form(None),
    icon: UploadFile = File(None),
    image: UploadFile = File(None),
):
    user = get_current_user(request)
    db = SessionLocal()

    site = (
        db.query(Site)
        .filter(Site.id == site_id, Site.owner_id == user.id)
        .first()
    )
    if not site:
        db.close()
        raise HTTPException(status_code=404)

    icon_url = save_file(icon, "icon") if icon else None
    image_url = save_file(image, "image") if image else None

    subs = db.query(Subscription).filter(Subscription.site_id == site.id).all()

    payload = {
        "title": title,
        "body": message,
        "url": url,
        "icon": icon_url,
        "image": image_url,
    }

    sent = 0
    from pywebpush import webpush

    for s in subs:
        try:
            sub_json = json.loads(s.keys_json)
            webpush(
                subscription_info=sub_json,
                data=json.dumps(payload),
                vapid_private_key=site.vapid_private,
                vapid_claims={"sub": settings.VAPID_EMAIL},
            )
            sent += 1
        except Exception as e:
            print("push error", e)

    log = NotificationLog(
        site_id=site.id,
        title=title,
        message=message,
        payload=json.dumps(payload),
        sent_to=sent,
    )
    db.add(log)
    db.commit()
    db.close()

    return RedirectResponse("/dashboard/overview", status_code=302)


# ============================================================================
# Subscribers
# ============================================================================
@router.get("/dashboard/subscribers", response_class=HTMLResponse)
def dashboard_subs(request: Request, site_id: int = None):
    user = get_current_user(request)
    db = SessionLocal()

    site = (
        db.query(Site).filter(Site.owner_id == user.id).first()
        if not site_id
        else db.query(Site)
        .filter(Site.id == site_id, Site.owner_id == user.id)
        .first()
    )

    if not site:
        db.close()
        raise HTTPException(status_code=404)

    subs = db.query(Subscription).filter(Subscription.site_id == site.id).all()
    db.close()

    return templates.TemplateResponse(
        "dashboard/subscribers.html",
        {"request": request, "site": site, "subscriptions": subs},
    )
