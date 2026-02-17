from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.config import settings
from app.models.database import init_db
from app.api.routes import router
from app.services.ml_analysis import ml_analysis_service
from app.services.nlp_interpretation import nlp_interpretation_service
from app.services.diet_generator import diet_generator_service
from app.services.encryption import encryption_service
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    os.makedirs(settings.ML_MODEL_PATH, exist_ok=True)
    os.makedirs("./data/kaggle_datasets", exist_ok=True)
    
    # Initialize database
    init_db()
    print("[OK] Database initialized")
    print("[OK] Application startup complete")
    
    yield
    
    # Shutdown
    print("[OK] Application shutdown complete")


app = FastAPI(
    title="AI-NutriCare API",
    version="1.0.0",
    description="AI/ML-Based Personalized Diet Plan Generator from Medical Reports",
    lifespan=lifespan
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {
        "message": "AI-NutriCare API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "/api/upload-report",
            "list_reports": "/api/reports",
            "get_report": "/api/reports/{report_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI-NutriCare"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
