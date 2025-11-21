from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Site
from app.auth import get_current_user
from app.utils.vapid import generate_vapid
from app.views import templates
import secrets

router = APIRouter()


# ------------------------------
# LIST WEBSITES
# ------------------------------
@router.get("/dashboard/sites", response_class=HTMLResponse)
def sites_list(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    sites = db.query(Site).filter_by(owner_id=user.id).all()
    return templates.TemplateResponse(
        "dashboard/sites_list.html",
        {"request": request, "sites": sites}
    )


# ------------------------------
# NEW WEBSITE FORM
# ------------------------------
@router.get("/dashboard/sites/new", response_class=HTMLResponse)
def sites_new(request: Request):
    return templates.TemplateResponse(
        "dashboard/site_new.html",
        {"request": request}
    )


# ------------------------------
# CREATE WEBSITE
# ------------------------------
@router.post("/dashboard/sites")
def sites_create(
    request: Request,
    name: str = Form(...),
    domain: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # generate keys
    site_key = secrets.token_urlsafe(32)
    priv, pub = generate_vapid()

    new_site = Site(
        owner_id=user.id,
        name=name,
        domain=domain,
        site_key=site_key,
        vapid_public=pub,
        vapid_private=priv
    )
    db.add(new_site)
    db.commit()

    return RedirectResponse(
        f"/dashboard/sites/{site_key}/integration",
        status_code=302
    )


# ------------------------------
# INTEGRATION PAGE
# ------------------------------
@router.get("/dashboard/sites/{site_key}/integration", response_class=HTMLResponse)
def site_integration(
    site_key: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    site = db.query(Site).filter_by(site_key=site_key, owner_id=user.id).first()

    if not site:
        raise HTTPException(404, "Site not found")

    return templates.TemplateResponse(
        "dashboard/site_integration.html",
        {"request": request, "site": site}
    )
