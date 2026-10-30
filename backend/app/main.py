import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.schemas.common import HealthResponse
from app.routes.planner import router as planner_router
from app.routes.plans import router as plans_router
from app.routes.export import router as export_router
from app.services.firestore_service import storage_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("eventgenie")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="EventGenie AI: Intelligent, Culturally-Grounded, Full-Stack GenAI Event Planning Platform"
)

# ---------------------------------------------------------------------------
# CORS: only trusted origins. The production SPA is served from the same
# origin as the API, so it does not depend on CORS. Extra origins can be added
# through the ALLOWED_ORIGINS environment variable (comma separated).
# ---------------------------------------------------------------------------
DEFAULT_ALLOWED_ORIGINS = [
    "https://eventgenie-ai-v9o3.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
extra_origins = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()
]
ALLOWED_ORIGINS = DEFAULT_ALLOWED_ORIGINS + extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # the app does not use cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Attach baseline security headers to every response."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    return response


# Mount Routers
app.include_router(planner_router)
app.include_router(plans_router)
app.include_router(export_router)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint displaying system readiness, Gemini and Firestore status."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        gemini_configured=settings.has_gemini_key,
        firestore_configured=bool(storage_service.firestore_db is not None),
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# Check for production frontend build
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    FRONTEND_DIST = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist"
    )
    if os.path.exists(FRONTEND_DIST):
        STATIC_DIR = FRONTEND_DIST

if os.path.exists(STATIC_DIR):
    STATIC_ROOT = Path(STATIC_DIR).resolve()
    app.mount("/assets", StaticFiles(directory=str(STATIC_ROOT / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Allow API routes to be handled by routers
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        # Resolve the requested path and make sure it stays inside the static
        # directory (blocks path traversal such as ../../etc/passwd).
        candidate = (STATIC_ROOT / full_path).resolve()
        if candidate.is_file() and STATIC_ROOT in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(STATIC_ROOT / "index.html")
else:
    @app.get("/", tags=["Root"])
    def root_info():
        return {
            "app": settings.APP_NAME,
            "version": settings.VERSION,
            "description": "EventGenie AI API is running. Build frontend/dist to serve SPA.",
            "documentation": "/docs"
        }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred in EventGenie AI. Please check server logs."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)