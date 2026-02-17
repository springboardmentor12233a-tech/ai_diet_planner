import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./ainutricare.db"
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Hugging Face (alternative to OpenAI)
    HUGGINGFACE_API_KEY: Optional[str] = None
    USE_HUGGINGFACE: bool = False
    
    # OCR
    OCR_ENGINE: str = "easyocr"  # or "tesseract"
    TESSERACT_CMD: Optional[str] = None  # Path to tesseract executable
    
    # File Storage
    UPLOAD_DIR: str = "./data/raw"
    PROCESSED_DIR: str = "./data/processed"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Security
    SECRET_KEY: str = "ai-nutricare-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ENCRYPTION_KEY: Optional[str] = None
    
    # ML Models
    ML_MODEL_PATH: str = "./models/trained"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
