from fastapi import APIRouter, Request, HTTPException
from .db import SessionLocal
from .models import Site, Subscription, NotificationLog
from .config import settings
from pywebpush import webpush, WebPushException
import json

router = APIRouter()

@router.post('/subscribe')
async def subscribe(request: Request):
    data = await request.json()
    site_key = data.get('site_key')
    subscription = data.get('subscription')
    if not site_key or not subscription:
        raise HTTPException(status_code=400, detail='Missing')
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key==site_key).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404, detail='Site not found')
    # origin check
    origin = request.headers.get('origin') or request.headers.get('referer')
    if origin:
        origin = origin.rstrip('/')
        allowed = (site.allow_origins or '').split(',')
        allowed = [a.strip() for a in allowed if a.strip()]
        if origin not in allowed and origin != settings.DASHBOARD_DOMAIN.rstrip('/'):
            db.close()
            raise HTTPException(status_code=403, detail='Origin not allowed')
    # store subscription
    import json as _json
    existing = db.query(Subscription).filter(Subscription.endpoint==subscription.get('endpoint')).first()
    if existing:
        existing.keys_json = _json.dumps(subscription)
        db.commit()
        db.close()
        return {'ok': True}
    s = Subscription(site_id=site.id, endpoint=subscription.get('endpoint'), keys_json=_json.dumps(subscription))
    db.add(s)
    db.commit()
    db.close()
    return {'ok': True}

@router.post('/send')
async def send_notification(request: Request):
    data = await request.json()
    site_key = data.get('site_key')
    title = data.get('title')
    message = data.get('message')
    url = data.get('url')
    icon = data.get('icon')
    image = data.get('image')
    if not site_key:
        raise HTTPException(status_code=400)
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key==site_key).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404)
    subs = db.query(Subscription).filter(Subscription.site_id==site.id).all()
    payload = {'title': title, 'body': message, 'url': url, 'icon': icon, 'image': image}
    sent = 0
    for s in subs:
        try:
            sub_json = json.loads(s.keys_json)
            webpush(subscription_info=sub_json, data=json.dumps(payload),
                    vapid_private_key=site.vapid_private, vapid_claims={'sub': settings.VAPID_EMAIL})
            sent += 1
        except WebPushException as e:
            # optionally handle 410/404 => delete
            print('push error', e)
    # log
    log = NotificationLog(site_id=site.id, title=title, message=message, payload=json.dumps(payload), sent_to=sent)
    db.add(log)
    db.commit()
    db.close()
    return {'ok': True, 'sent': sent}
