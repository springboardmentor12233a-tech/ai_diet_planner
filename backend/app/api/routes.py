from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import os
from datetime import datetime

from app.models.database import get_db, MedicalReport
from app.services.data_extraction import data_extraction_service
from app.config import settings
from app.services.ml_analysis import ml_analysis_service
from app.services.nlp_interpretation import nlp_interpretation_service
from app.services.diet_generator import diet_generator_service
from app.services.encryption import encryption_service
import json

router = APIRouter()

@router.post("/upload-report")
async def upload_report(
    file: UploadFile = File(...),
    user_id: int = 1,  # TODO: Get from authentication
    db: Session = Depends(get_db)
):
    """Upload medical report for processing"""
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".txt"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Save uploaded file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large")
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record
    report = MedicalReport(
        user_id=user_id,
        filename=file.filename,
        file_type=file_ext[1:],  # Remove dot
        extraction_status="pending"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Extract data
    try:
        extracted_data = data_extraction_service.extract_from_file(file_path, file_ext[1:])
        data_extraction_service.save_extracted_data(report.id, extracted_data, db)
        
        return {
            "report_id": report.id,
            "status": "success",
            "extracted_data": {
                "numeric_data": extracted_data["numeric_data"],
                "textual_summary": extracted_data["textual_data"]["doctor_notes"][:200]
            }
        }
    except Exception as e:
        report.extraction_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.get("/reports/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get report details"""
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Decrypt data
    try:
        from app.services.encryption import encryption_service
        numeric_data = report.numeric_data or {}
        textual_data = ""
        if report.textual_data:
            import json
            textual_data = json.loads(encryption_service.decrypt(report.textual_data))
    except Exception as e:
        textual_data = {"error": "Could not decrypt data"}
    
    return {
        "id": report.id,
        "filename": report.filename,
        "status": report.extraction_status,
        "numeric_data": numeric_data,
        "textual_data": textual_data,
        "uploaded_at": report.uploaded_at.isoformat() if report.uploaded_at else None,
        "processed_at": report.processed_at.isoformat() if report.processed_at else None
    }

@router.get("/reports")
async def list_reports(user_id: int = 1, db: Session = Depends(get_db)):
    """List all reports for a user"""
    reports = db.query(MedicalReport).filter(MedicalReport.user_id == user_id).all()
    return [{
        "id": r.id,
        "filename": r.filename,
        "status": r.extraction_status,
        "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None
    } for r in reports]

@router.delete("/reports/{report_id}")
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report"""
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Delete file if exists
    file_path = os.path.join(settings.UPLOAD_DIR, report.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass
    
    db.delete(report)
    db.commit()
    return {"status": "deleted", "report_id": report_id}

@router.post("/analyze-health/{report_id}")
async def analyze_health(report_id: int, db: Session = Depends(get_db)):
    """Perform ML-based health analysis on extracted data"""
    from app.services.ml_analysis import ml_analysis_service
    
    # Get report
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.numeric_data:
        raise HTTPException(status_code=400, detail="No numeric data available for analysis")
    
    # Perform ML analysis
    try:
        analysis_result = ml_analysis_service.analyze_health_metrics(report.numeric_data)
        recommendations = ml_analysis_service.get_health_recommendations(analysis_result)
        
        # Add recommendations to result
        analysis_result['recommendations'] = recommendations
        
        return {
            "report_id": report_id,
            "analysis": analysis_result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/interpret-notes/{report_id}")
async def interpret_notes(report_id: int, db: Session = Depends(get_db)):
    """Perform NLP interpretation on doctor notes and prescriptions"""
    from app.services.nlp_interpretation import nlp_interpretation_service
    from app.services.encryption import encryption_service
    import json
    
    # Get report
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.textual_data:
        raise HTTPException(status_code=400, detail="No textual data available for interpretation")
    
    # Decrypt textual data
    try:
        textual_data = json.loads(encryption_service.decrypt(report.textual_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt data: {str(e)}")
    
    # Perform NLP interpretation
    try:
        interpretation_result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        health_goals = nlp_interpretation_service.extract_health_goals(textual_data)
        
        interpretation_result['health_goals'] = health_goals
        
        return {
            "report_id": report_id,
            "interpretation": interpretation_result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interpretation failed: {str(e)}")

@router.post("/generate-diet-plan/{report_id}")
async def generate_diet_plan(
    report_id: int,
    num_days: int = 7,
    user_name: str = "Patient",
    db: Session = Depends(get_db)
):
    """Generate personalized diet plan based on health analysis"""
    from app.services.ml_analysis import ml_analysis_service
    from app.services.nlp_interpretation import nlp_interpretation_service
    from app.services.diet_generator import diet_generator_service
    from app.services.encryption import encryption_service
    import json
    
    # Get report
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Perform health analysis
    if not report.numeric_data:
        raise HTTPException(status_code=400, detail="No numeric data available")
    
    try:
        health_analysis = ml_analysis_service.analyze_health_metrics(report.numeric_data)
        
        # Perform NLP interpretation if textual data available
        nlp_result = None
        if report.textual_data:
            try:
                textual_data = json.loads(encryption_service.decrypt(report.textual_data))
                nlp_result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
            except:
                pass  # Continue without NLP if it fails
        
        # Generate diet plan
        user_prefs = {'name': user_name}
        diet_plan = diet_generator_service.generate_diet_plan(
            health_analysis,
            nlp_result=nlp_result,
            user_preferences=user_prefs,
            num_days=num_days
        )
        
        return {
            "report_id": report_id,
            "diet_plan": diet_plan,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diet plan generation failed: {str(e)}")

@router.post("/complete-analysis")
async def complete_analysis_from_file(
    file: UploadFile = File(...),
    user_name: str = "Patient",
    num_days: int = 7,
    db: Session = Depends(get_db)
):
    """Unified endpoint: Upload file and get complete analysis + diet plan in one call"""
    # 1. Perform Upload & Extraction (similar to upload_report logic)
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".txt"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record
    report = MedicalReport(
        user_id=1,  # Default
        filename=file.filename,
        file_type=file_ext[1:],
        extraction_status="processing"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Extract data
    try:
        print(f"[*] Starting data extraction for {file.filename}...")
        extracted_data = data_extraction_service.extract_from_file(file_path, file_ext[1:])
        print(f"[OK] Data extraction complete. Numeric fields: {list(extracted_data.get('numeric_data', {}).keys())}")
        data_extraction_service.save_extracted_data(report.id, extracted_data, db)
    except Exception as e:
        print(f"[ERROR] Data extraction failed: {str(e)}")
        report.extraction_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")
    
    # Process Analysis
    print(f"[*] Starting AI analysis and diet generation...")
    analysis_results = await complete_analysis(report.id, user_name, num_days, db)
    print(f"[OK] Analysis complete for {file.filename}")
    return analysis_results

@router.post("/complete-analysis/{report_id}")
async def complete_analysis(
    report_id: int,
    user_name: str = "Patient",
    num_days: int = 7,
    db: Session = Depends(get_db)
):
    """Complete end-to-end analysis: extraction → ML analysis → NLP → diet plan"""
    
    # Get report
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    result = {
        "report_id": report_id,
        "filename": report.filename,
        "status": "success"
    }
    
    # Step 1: Health Analysis
    if report.numeric_data:
        try:
            health_analysis = ml_analysis_service.analyze_health_metrics(report.numeric_data)
            recommendations = ml_analysis_service.get_health_recommendations(health_analysis)
            health_analysis['recommendations'] = recommendations
            result['health_analysis'] = health_analysis
        except Exception as e:
            result['health_analysis'] = {"error": str(e)}
    else:
        result['health_analysis'] = {"error": "No numeric data available"}
    
    # Step 2: NLP Interpretation
    nlp_result = None
    if report.textual_data:
        try:
            textual_data = json.loads(encryption_service.decrypt(report.textual_data))
            nlp_result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
            health_goals = nlp_interpretation_service.extract_health_goals(textual_data)
            nlp_result['health_goals'] = health_goals
            result['nlp_interpretation'] = nlp_result
        except Exception as e:
            result['nlp_interpretation'] = {"error": str(e)}
    else:
        result['nlp_interpretation'] = {"message": "No textual data available"}
    
    # Step 3: Diet Plan Generation
    if 'health_analysis' in result and 'error' not in result['health_analysis']:
        try:
            user_prefs = {'name': user_name}
            diet_plan = diet_generator_service.generate_diet_plan(
                result['health_analysis'],
                nlp_result=nlp_result,
                user_preferences=user_prefs,
                num_days=num_days
            )
            result['diet_plan'] = diet_plan
        except Exception as e:
            result['diet_plan'] = {"error": str(e)}
    else:
        result['diet_plan'] = {"error": "Cannot generate diet plan without health analysis"}
    
    return result

