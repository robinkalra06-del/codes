from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from .db import engine, SessionLocal
from .models import Base, User, Site, Subscription, NotificationLog
from .utils import hash_password, verify_password, gen_site_key, create_jwt
from .vapid import generate_vapid_keys
from .config import settings
from .storage import save_file
from sqlalchemy.orm import Session
import json

templates = Jinja2Templates(directory='app/templates')
router = APIRouter()

def init_db():
    Base.metadata.create_all(bind=engine)

@router.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@router.get('/register', response_class=HTMLResponse)
def reg_get(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

@router.post('/register')
def reg_post(request: Request, email: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    if db.query(User).filter(User.email==email).first():
        db.close()
        return templates.TemplateResponse('register.html', {'request': request, 'error': 'Email exists'})
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    # create default site
    site_key = gen_site_key()
    priv, pub = generate_vapid_keys()
    site = Site(owner_id=user.id, name=email + ' site', domain=email.split('@')[0]+'.example.com', site_key=site_key, vapid_public=pub, vapid_private=priv, allow_origins=settings.DASHBOARD_DOMAIN)
    db.add(site)
    db.commit()
    db.close()
    return RedirectResponse('/login', status_code=302)

@router.get('/login', response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

@router.post('/login')
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email==email).first()
    if not user or not verify_password(password, user.password_hash):
        db.close()
        return templates.TemplateResponse('login.html', {'request': request, 'error':'Invalid credentials', 'request': request})
    # set simple auth via redirect with token cookie (for demo simple approach)
    token = create_jwt({'user_id': user.id})
    resp = RedirectResponse('/dashboard/overview', status_code=302)
    resp.set_cookie('session', token, httponly=True, samesite='lax')
    db.close()
    return resp

def get_current_user(request: Request):
    token = request.cookies.get('session')
    if not token:
        raise HTTPException(status_code=401)
    data = create_jwt.__globals__['jwt'].decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    user_id = data.get('user_id')
    db = SessionLocal()
    user = db.query(User).filter(User.id==user_id).first()
    db.close()
    if not user:
        raise HTTPException(status_code=401)
    return user

@router.get('/dashboard/overview', response_class=HTMLResponse)
def dashboard_overview(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    sites = db.query(Site).filter(Site.owner_id==user.id).all()
    # analytics: subscribers count per site
    stats = []
    for s in sites:
        subcount = db.query(Subscription).filter(Subscription.site_id==s.id).count()
        sent = db.query(NotificationLog).filter(NotificationLog.site_id==s.id).count()
        stats.append({'site': s, 'subscribers': subcount, 'sent': sent})
    db.close()
    return templates.TemplateResponse('dashboard/overview.html', {'request': request, 'user': user, 'stats': stats})

@router.get('/pushclient/{site_key}.js')
def pushclient_js(site_key: str):
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key==site_key).first()
    db.close()
    if not site:
        raise HTTPException(status_code=404)
    path = 'app/static/js/pushclient_template.js'
    with open(path, 'r') as f:
        t = f.read()
    js = t.replace('__SITE_KEY__', site.site_key).replace('__VAPID_PUBLIC_KEY__', site.vapid_public.strip().replace('\n','\\n'))
    return PlainTextResponse(js, media_type='application/javascript')

@router.get('/service-worker.js')
def service_worker():
    return PlainTextResponse(open('app/static/sw/service-worker.js').read(), media_type='application/javascript')

@router.get('/dashboard/send', response_class=HTMLResponse)
def dashboard_send_get(request: Request, site_id: int = None):
    user = get_current_user(request)
    db = SessionLocal()
    site = db.query(Site).filter(Site.owner_id==user.id).first() if not site_id else db.query(Site).filter(Site.id==site_id, Site.owner_id==user.id).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404, detail='Site not found')
    db.close()
    return templates.TemplateResponse('dashboard/send.html', {'request': request, 'site': site})

@router.post('/dashboard/send')
def dashboard_send_post(request: Request, site_id: int = Form(...), title: str = Form(...), message: str = Form(...), url: str = Form(None), icon: UploadFile = File(None), image: UploadFile = File(None)):
    user = get_current_user(request)
    db = SessionLocal()
    site = db.query(Site).filter(Site.id==site_id, Site.owner_id==user.id).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404)
    icon_url = None
    image_url = None
    if icon:
        icon_url = save_file(icon, 'icon')
    if image:
        image_url = save_file(image, 'image')
    # send to subscribers synchronously (for demo)
    subs = db.query(Subscription).filter(Subscription.site_id==site.id).all()
    payload = {'title': title, 'body': message, 'url': url, 'icon': icon_url, 'image': image_url}
    sent = 0
    from pywebpush import webpush, WebPushException
    for s in subs:
        try:
            sub_json = json.loads(s.keys_json)
            webpush(subscription_info=sub_json, data=json.dumps(payload), vapid_private_key=site.vapid_private, vapid_claims={'sub': settings.VAPID_EMAIL})
            sent += 1
        except Exception as e:
            print('push error', e)
    log = NotificationLog(site_id=site.id, title=title, message=message, payload=json.dumps(payload), sent_to=sent)
    db.add(log)
    db.commit()
    db.close()
    return RedirectResponse('/dashboard/overview', status_code=302)

@router.get('/dashboard/subscribers', response_class=HTMLResponse)
def dashboard_subs(request: Request, site_id: int = None):
    user = get_current_user(request)
    db = SessionLocal()
    site = db.query(Site).filter(Site.owner_id==user.id).first() if not site_id else db.query(Site).filter(Site.id==site_id, Site.owner_id==user.id).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404)
    subs = db.query(Subscription).filter(Subscription.site_id==site.id).all()
    db.close()
    return templates.TemplateResponse('dashboard/subscribers.html', {'request': request, 'site': site, 'subscriptions': subs})
