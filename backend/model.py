from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PatientReport(Base):
    __tablename__ = "patient_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    glucose = Column(Float)
    blood_pressure = Column(Float)
    bmi = Column(Float)
    # This stores the list of rules generated in Milestone 3
    diet_plan = Column(JSON) 
    status = Column(String) # e.g., "SUCCESS" or "FALLBACK"