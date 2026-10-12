import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine, Base, SessionLocal
from .models import *
from .seed_data import seed_database
from .engine import precedent_engine
from .routers import auth, proposals, precedents, workflow, audit, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed database with fictional police dataset and users
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Intelligent Proposal Management & Precedent Retrieval System for Police Departments",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory if it exists
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(proposals.router)
app.include_router(precedents.router)
app.include_router(workflow.router)
app.include_router(audit.router)
app.include_router(analytics.router)

@app.get("/api/health")
def healthcheck():
    return {
        "status": "healthy",
        "service": "IPMPRS API",
        "active_engine": precedent_engine.active_engine,
        "is_semantic": precedent_engine.is_semantic
    }

# Mount frontend production build if available
frontend_dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(frontend_dist_dir):
    from fastapi.responses import FileResponse
    assets_dir = os.path.join(frontend_dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist_dir, "index.html"))
