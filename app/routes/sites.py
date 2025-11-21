# app/routes/sites.py

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.site import Site
from app.utils.vapid import generate_vapid
from app.auth import get_current_user
from app.templates import templates
import secrets

router = APIRouter()


# ---------------------------------------------------------
# List all websites for user
# ---------------------------------------------------------
@router.get("/dashboard/sites", response_class=HTMLResponse)
def sites_list(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    sites = db.query(Site).filter_by(user_id=user.id).all()
    return templates.TemplateResponse(
        "dashboard/sites_list.html",
        {"request": request, "sites": sites, "user": user}
    )


# ---------------------------------------------------------
# Page: Create new website
# ---------------------------------------------------------
@router.get("/dashboard/sites/new", response_class=HTMLResponse)
def sites_new(
    request: Request,
    user=Depends(get_current_user)
):
    return templates.TemplateResponse(
        "dashboard/site_new.html",
        {"request": request, "user": user}
    )


# ---------------------------------------------------------
# POST: Create website
# ---------------------------------------------------------
@router.post("/dashboard/sites")
def sites_create(
    request: Request,
    name: str = Form(...),
    domain: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Generate unique site key + VAPID keys
    site_key = secrets.token_urlsafe(32)
    vapid_private, vapid_public = generate_vapid()

    new_site = Site(
        user_id=user.id,
        name=name,
        domain=domain,
        site_key=site_key,
        vapid_public=vapid_public,
        vapid_private=vapid_private
    )

    db.add(new_site)
    db.commit()

    return RedirectResponse(
        f"/dashboard/sites/{site_key}/integration",
        status_code=302
    )


# ---------------------------------------------------------
# Integration Page
# ---------------------------------------------------------
@router.get("/dashboard/sites/{site_key}/integration", response_class=HTMLResponse)
def site_integration(
    site_key: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    site = db.query(Site).filter_by(site_key=site_key, user_id=user.id).first()

    if not site:
        return RedirectResponse("/dashboard/sites", 302)

    return templates.TemplateResponse(
        "dashboard/site_integration.html",
        {"request": request, "site": site, "user": user}
    )
