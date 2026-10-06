import time
from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=["Health"])

START_TIME = time.time()

@router.get("/health")
def health_check():
    """
    Returns API health status, version, and operational uptime.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "parser_engine": "Scapy 2.8.0 Defensive DPI",
        "database": "Active",
    }
