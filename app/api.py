# app/api.py
from fastapi import APIRouter, Request, Depends, HTTPException, Response, UploadFile, File, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from app.db import SessionLocal
from app.models import Site, Subscription, NotificationLog
from app.schemas import SubscribeIn
from app.utils import get_current_user
from app.vapid import generate_vapid_keys, gen_site_key
from app.config import settings
import json
from pywebpush import webpush, WebPushException

router = APIRouter()

@router.post("/subscribe")
async def subscribe(data: SubscribeIn):
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key == data.site_key).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404, detail="Site not found")
    # verify domain origin should be handled via CORS; trusting site key for now
    try:
        sub = Subscription(site_id=site.id, endpoint=data.subscription.get("endpoint"), keys_json=json.dumps(data.subscription))
        db.add(sub)
        db.commit()
    finally:
        db.close()
    return {"ok": True}

@router.get("/get-public-vapid/{site_key}")
def get_public_vapid(site_key: str):
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key == site_key).first()
    db.close()
    if not site:
        raise HTTPException(status_code=404)
    return {"vapid_public": site.vapid_public}

@router.post("/send")
def api_send(request: Request, site_key: str = Form(...), title: str = Form(...), message: str = Form(...)):
    # protected: only dashboard UI should call or authenticated API keys
    # here we'll just find site by site_key
    db = SessionLocal()
    site = db.query(Site).filter(Site.site_key == site_key).first()
    if not site:
        db.close()
        raise HTTPException(status_code=404)
    subs = db.query(Subscription).filter(Subscription.site_id == site.id).all()
    payload = {"title": title, "body": message}
    sent = 0
    for s in subs:
        try:
            sub_json = json.loads(s.keys_json)
            webpush(subscription_info=sub_json, data=json.dumps(payload), vapid_private_key=site.vapid_private, vapid_claims={"sub": settings.VAPID_EMAIL})
            sent += 1
        except WebPushException as e:
            # log or delete invalid subscription
            print("webpush error:", e)
    log = NotificationLog(site_id=site.id, title=title, message=message, payload=json.dumps(payload), sent_to=sent)
    db.add(log)
    db.commit()
    db.close()
    return {"sent": sent}
