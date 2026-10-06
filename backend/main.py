import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.models import Capture
from backend.services.synthetic_pcap_generator import generate_demo_pcap
from backend.api.captures import router as captures_router, process_and_save_capture
from backend.api.packets import router as packets_router
from backend.api.statistics import router as statistics_router
from backend.api.traffic_analysis import (
    protocols_router, conversations_router, endpoints_router, ports_router
)
from backend.api.dns_http import dns_router, http_router
from backend.api.security import router as security_router
from backend.api.reports import router as reports_router
from backend.api.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed demo capture if no captures exist
    db = SessionLocal()
    try:
        existing = db.query(Capture).first()
        if not existing:
            demo_file = generate_demo_pcap()
            process_and_save_capture(db, demo_file, "demo_capture.pcap", is_demo=1)
            print("[INFO] Auto-seeded demonstration PCAP capture.")
    except Exception as e:
        print(f"[WARN] Failed to auto-seed demo data: {e}")
    finally:
        db.close()
        
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Defensive network protocol analysis platform for cybersecurity and network education.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe error handling (No exposed raw stack traces to users)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[ERROR] Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing network packets."}
    )

# Include API Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(captures_router, prefix="/api")
app.include_router(packets_router, prefix="/api")
app.include_router(statistics_router, prefix="/api")
app.include_router(protocols_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(endpoints_router, prefix="/api")
app.include_router(ports_router, prefix="/api")
app.include_router(dns_router, prefix="/api")
app.include_router(http_router, prefix="/api")
app.include_router(security_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
