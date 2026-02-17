from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class MedicalReport(Base):
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String(255))
    file_type = Column(String(50))  # pdf, image, text
    encrypted_data = Column(Text)  # Encrypted original content
    extraction_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Extracted structured data (encrypted)
    numeric_data = Column(JSON)  # {blood_sugar: 120, cholesterol: 200, ...}
    textual_data = Column(Text)  # Doctor notes, prescriptions
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

class HealthAnalysis(Base):
    __tablename__ = "health_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    
    # ML Analysis Results
    detected_conditions = Column(JSON)  # ["diabetes", "high_cholesterol"]
    risk_scores = Column(JSON)  # {"diabetes_risk": 0.85, "heart_disease_risk": 0.62}
    health_metrics = Column(JSON)  # All extracted numeric values
    
    # NLP Insights
    nlp_insights = Column(JSON)  # Interpreted doctor notes
    dietary_restrictions = Column(JSON)  # ["no_sugar", "low_sodium"]
    
    created_at = Column(DateTime, default=datetime.utcnow)

class DietPlan(Base):
    __tablename__ = "diet_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    analysis_id = Column(Integer, index=True)
    
    plan_data = Column(JSON)  # Full diet plan structure
    export_format = Column(String(50))  # pdf, json, html
    file_path = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Database setup
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
