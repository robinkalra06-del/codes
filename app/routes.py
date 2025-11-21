from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from .views import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def login_required(request: Request):
    try:
        user = get_current_user(request)
        return user
    except:
        return RedirectResponse("/login")

@router.get("/dashboard", include_in_schema=False)
def dashboard_overview(request: Request, user = Depends(login_required)):
    return templates.TemplateResponse("dashboard/overview.html", {"request": request, "user": user})

@router.get("/dashboard/analytics", include_in_schema=False)
def dashboard_analytics(request: Request, user = Depends(login_required)):
    return templates.TemplateResponse("dashboard/analytics.html", {"request": request, "user": user})

@router.get("/dashboard/subscribers", include_in_schema=False)
def dashboard_subscribers(request: Request, user = Depends(login_required)):
    return templates.TemplateResponse("dashboard/subscribers.html", {"request": request, "user": user})

@router.get("/dashboard/send", include_in_schema=False)
def dashboard_send(request: Request, user = Depends(login_required)):
    return templates.TemplateResponse("dashboard/send.html", {"request": request, "user": user})
