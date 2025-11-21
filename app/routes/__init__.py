from .dashboard import router as dashboard_router
from .sites import router as sites_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(sites_router)
