import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for seamless development and Cloud Run deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check for production frontend build
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
    if os.path.exists(FRONTEND_DIST):
        STATIC_DIR = FRONTEND_DIST

if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Allow API routes to be handled by routers
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
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
