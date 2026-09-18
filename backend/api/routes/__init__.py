from fastapi import APIRouter

from api.routes.health import router as health_router
from api.routes.upload import router as upload_router
from api.routes.analysis import router as analysis_router
from api.routes.models import router as models_router
from api.routes.reports import router as reports_router
from api.routes.audit import router as audit_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(upload_router)
api_router.include_router(analysis_router)
api_router.include_router(models_router)
api_router.include_router(reports_router)
api_router.include_router(audit_router)

__all__ = ["api_router"]
