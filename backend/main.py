from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import numpy as np
from xgboost import XGBClassifier
import os
import json
from datetime import datetime
import logging

from ocr_utils import run_ocr
from nlp_utils import interpret_doctor_notes, generate_diet_plan
from ai_interpreter import get_ai_interpreter
from meal_planner import get_meal_planner
from health_extractor import HealthParameterExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Diet Planner – Diabetes API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
try:
    model = XGBClassifier()
    model_path = os.path.join(os.path.dirname(__file__), "model", "diabetes_xgb.json")
    if os.path.exists(model_path):
        model.load_model(model_path)
        logger.info("Model loaded successfully")
    else:
        logger.warning(f"Model file not found at {model_path}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")

# Model-level metric (from training)
MODEL_ROC_AUC = 0.81
OPTIMAL_THRESHOLD = 0.18


class DiabetesInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    dpf: float
    age: int
    
    @field_validator('glucose')
    @classmethod
    def validate_glucose(cls, v):
        if v < 0 or v > 1000:
            raise ValueError('Glucose must be between 0 and 1000')
        return v
    
    @field_validator('bmi')
    @classmethod
    def validate_bmi(cls, v):
        if v < 0 or v > 100:
            raise ValueError('BMI must be between 0 and 100')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v


def classify_risk(prob):
    if prob < OPTIMAL_THRESHOLD:
        return "Low Risk"
    elif prob < 0.5:
        return "Moderate Risk"
    else:
        return "High Risk"


os.makedirs("backend/uploads", exist_ok=True)
os.makedirs("backend/exports", exist_ok=True)


@app.post("/predict")
def predict(input: DiabetesInput):
    try:
        logger.info("Processing diabetes prediction request")
        
        data = np.array([
            input.pregnancies,
            input.glucose,
            input.blood_pressure,
            input.skin_thickness,
            input.insulin,
            input.bmi,
            input.dpf,
            input.age
        ]).reshape(1, -1)

        prob = model.predict_proba(data)[0][1]
        risk = classify_risk(prob)

        logger.info(f"Prediction completed: Risk={risk}, Probability={prob}")
        
        return {
            "diabetes_probability": round(float(prob), 3),
            "risk_level": risk,
            "model_roc_auc": MODEL_ROC_AUC,
            "message": (
                "Follow a low-GI diet and consult a doctor"
                if risk == "High Risk"
                else "Maintain a balanced diet and regular exercise"
            )
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    """Upload and analyze medical prescription using AI."""
    try:
        logger.info(f"Processing file upload: {file.filename}")
        
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf', 'txt'}
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type .{file_ext} not allowed")
        
        file_path = f"backend/uploads/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        logger.info(f"File saved to {file_path}")
        
        # Extract text using OCR
        extracted_text = run_ocr(file_path)
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            logger.warning("OCR extracted no text from file")
            extracted_text = "No text detected. Please ensure the image is clear and readable."
        
        # Auto-extract health parameters from text
        extracted_parameters = HealthParameterExtractor.extract_to_diabetes_form(extracted_text)
        logger.info(f"Extracted health parameters: {extracted_parameters}")
        
        # Use AI interpreter for intelligent analysis
        ai_interpreter = get_ai_interpreter()
        interpreted_data = ai_interpreter.interpret_medical_text(extracted_text)
        
        # Generate diet rules
        diet_rules = ai_interpreter.generate_diet_rules(interpreted_data)
        
        # Generate comprehensive 7-day meal plan
        meal_planner = get_meal_planner()
        meal_plan_data = meal_planner.generate_7day_meal_plan(
            conditions=interpreted_data.get("conditions", []),
            dietary_restrictions=interpreted_data.get("dietary_restrictions", [])
        )

        logger.info("Prescription analysis completed successfully")
        
        return {
            "extracted_text": extracted_text,
            "extracted_parameters": extracted_parameters,
            "interpreted_data": interpreted_data,
            "diet_rules": diet_rules,
            "meal_plan": meal_plan_data["week_plan"],  # 7-day plan
            "week_meal_plan": meal_plan_data["week_plan"],  # For frontend
            "weekly_summary": {
                "total_calories": meal_plan_data["weekly_total_calories"],
                "average_daily_calories": meal_plan_data["average_daily_calories"],
                "category": meal_plan_data["category"]
            },
            "message": "Health parameters extracted and 7-day meal plan generated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prescription upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


@app.post("/generate-meal-plan")
def generate_comprehensive_meal_plan(input: DiabetesInput):
    """Generate meal plan based on diabetes prediction."""
    try:
        logger.info("Generating comprehensive meal plan")
        
        # Predict diabetes risk
        data = np.array([
            input.pregnancies,
            input.glucose,
            input.blood_pressure,
            input.skin_thickness,
            input.insulin,
            input.bmi,
            input.dpf,
            input.age
        ]).reshape(1, -1)

        prob = model.predict_proba(data)[0][1]
        risk = classify_risk(prob)
        
        # Determine conditions based on ML results
        conditions = []
        if risk in ["Moderate Risk", "High Risk"]:
            conditions.append("diabetes")
        if input.blood_pressure > 90:
            conditions.append("hypertension")
        if input.bmi > 30:
            conditions.append("obesity")
        
        dietary_restrictions = []
        if risk != "Low Risk":
            dietary_restrictions.append("Low sugar / Low glycemic index foods")
        
        # Generate 7-day meal plan
        meal_planner = get_meal_planner()
        meal_plan_data = meal_planner.generate_7day_meal_plan(
            conditions=conditions if conditions else ["General health maintenance"],
            dietary_restrictions=dietary_restrictions,
            diabetes_risk=risk
        )
        
        logger.info("7-day meal plan generated successfully")
        
        return {
            "diabetes_probability": round(float(prob), 3),
            "risk_level": risk,
            "model_roc_auc": MODEL_ROC_AUC,
            "conditions": conditions if conditions else ["General health maintenance"],
            "meal_plan": meal_plan_data["week_plan"],  # 7-day plan
            "week_meal_plan": meal_plan_data["week_plan"],  # For frontend compatibility
            "weekly_summary": {
                "total_calories": meal_plan_data["weekly_total_calories"],
                "average_daily_calories": meal_plan_data["average_daily_calories"],
                "category": meal_plan_data["category"]
            },
            "message": (
                "Follow a low-GI diet and consult a doctor"
                if risk == "High Risk"
                else "Maintain a balanced diet and regular exercise"
            )
        }
    except Exception as e:
        logger.error(f"Meal plan generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Meal plan generation failed: {str(e)}")


@app.post("/export-json")
async def export_meal_plan_json(meal_plan_data: dict):
    """Export meal plan as JSON file."""
    try:
        # Ensure exports directory exists
        exports_dir = os.path.join(os.path.dirname(__file__), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diet_plan_{timestamp}.json"
        filepath = os.path.join(exports_dir, filename)
        
        # Add metadata
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "plan_type": "Personalized Diet Plan",
            "data": meal_plan_data
        }
        
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"JSON export created: {filename}")
        return FileResponse(filepath, filename=filename, media_type="application/json")
    except Exception as e:
        logger.error(f"JSON export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"JSON export failed: {str(e)}")


@app.post("/export-pdf")
async def export_meal_plan_pdf(meal_plan_data: dict):
    """Export meal plan as PDF file."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        
        # Ensure exports directory exists
        exports_dir = os.path.join(os.path.dirname(__file__), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diet_plan_{timestamp}.pdf"
        filepath = os.path.join(exports_dir, filename)
        
        logger.info(f"Creating PDF at: {filepath}")
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("AI Diet Planner", title_style))
        story.append(Paragraph("Personalized Meal Plan", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Date
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Health Information
        if 'risk_level' in meal_plan_data:
            story.append(Paragraph(f"<b>Diabetes Risk Level:</b> {meal_plan_data['risk_level']}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        if 'conditions' in meal_plan_data:
            conditions_text = ", ".join(meal_plan_data['conditions'])
            story.append(Paragraph(f"<b>Health Conditions:</b> {conditions_text}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Meal Plan
        meal_plan = meal_plan_data.get('meal_plan', {})
        
        if meal_plan:
            story.append(Paragraph("<b>7-Day Personalized Meal Plan</b>", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            
            # Check if this is a 7-day plan (has days as keys) or single day
            if "Monday" in meal_plan or "Tuesday" in meal_plan:
                # 7-day meal plan format
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                
                for day in days:
                    if day in meal_plan:
                        day_meals = meal_plan[day]
                        story.append(Paragraph(f"<b>{day}</b>", styles['Heading3']))
                        
                        # Breakfast
                        if 'breakfast' in day_meals and day_meals['breakfast']:
                            meal = day_meals['breakfast']
                            story.append(Paragraph(f"<b>Breakfast:</b> {meal.get('name', 'N/A')}", styles['Normal']))
                            story.append(Paragraph(f"Calories: {meal.get('calories', 0)} | Protein: {meal.get('protein', 'N/A')}", styles['Normal']))
                        
                        # Lunch
                        if 'lunch' in day_meals and day_meals['lunch']:
                            meal = day_meals['lunch']
                            story.append(Paragraph(f"<b>Lunch:</b> {meal.get('name', 'N/A')}", styles['Normal']))
                            story.append(Paragraph(f"Calories: {meal.get('calories', 0)} | Protein: {meal.get('protein', 'N/A')}", styles['Normal']))
                        
                        # Snack
                        if 'snack' in day_meals and day_meals['snack']:
                            meal = day_meals['snack']
                            story.append(Paragraph(f"<b>Snack:</b> {meal.get('name', 'N/A')}", styles['Normal']))
                            story.append(Paragraph(f"Calories: {meal.get('calories', 0)}", styles['Normal']))
                        
                        # Dinner
                        if 'dinner' in day_meals and day_meals['dinner']:
                            meal = day_meals['dinner']
                            story.append(Paragraph(f"<b>Dinner:</b> {meal.get('name', 'N/A')}", styles['Normal']))
                            story.append(Paragraph(f"Calories: {meal.get('calories', 0)} | Protein: {meal.get('protein', 'N/A')}", styles['Normal']))
                        
                        # Daily Total
                        if 'daily_total_calories' in day_meals:
                            story.append(Paragraph(f"<b>Daily Total:</b> ~{day_meals['daily_total_calories']} calories", styles['Normal']))
                        
                        story.append(Spacer(1, 0.15*inch))
            else:
                # Old single-day format (for backward compatibility)
                if 'breakfast' in meal_plan:
                    meal = meal_plan['breakfast']
                    story.append(Paragraph("<b>Breakfast:</b>", styles['Heading3']))
                    story.append(Paragraph(f"<b>{meal.get('name', 'N/A')}</b>", styles['Normal']))
                    if 'description' in meal:
                        story.append(Paragraph(meal['description'], styles['Normal']))
                    story.append(Paragraph(f"Calories: {meal.get('calories', 0)} | Protein: {meal.get('protein', 'N/A')} | Carbs: {meal.get('carbs', 'N/A')}", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
            
            # Hydration
            if 'hydration' in meal_plan_data:
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph("<b>Hydration:</b>", styles['Heading3']))
                story.append(Paragraph(meal_plan_data['hydration'], styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Notes
            if 'notes' in meal_plan_data:
                story.append(Paragraph("<b>Important Notes:</b>", styles['Heading3']))
                for note in meal_plan_data['notes']:
                    story.append(Paragraph(f"• {note}", styles['Normal']))
        
        # Diet Rules
        if 'diet_rules' in meal_plan_data:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("<b>Dietary Guidelines:</b>", styles['Heading3']))
            for rule in meal_plan_data['diet_rules']:
                story.append(Paragraph(f"• {rule}", styles['Normal']))
        
        # Weekly Summary for 7-day plans
        if 'weekly_summary' in meal_plan_data:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("<b>Weekly Summary</b>", styles['Heading2']))
            summary = meal_plan_data['weekly_summary']
            story.append(Paragraph(f"Total Weekly Calories: ~{summary.get('total_calories', 'N/A')} cal", styles['Normal']))
            story.append(Paragraph(f"Average Daily Calories: ~{summary.get('average_daily_calories', 'N/A')} cal", styles['Normal']))
            story.append(Paragraph(f"Meal Category: {summary.get('category', 'General Healthy')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("<b>Nutrition Balance:</b> Proteins, Carbs, and Healthy Fats optimized for your health profile", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF export created: {filename}")
        
        return FileResponse(filepath, filename=filename, media_type="application/pdf")
    
    except ImportError as ie:
        logger.error(f"PDF ImportError: {str(ie)}")
        return JSONResponse(
            status_code=500,
            content={"error": "PDF generation requires reportlab. Install with: pip install reportlab"}
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"PDF export error: {str(e)}\nTraceback: {error_traceback}")
        return JSONResponse(
            status_code=500,
            content={"error": f"PDF generation failed: {str(e)}"}
        )


@app.get("/")
def read_root():
    try:
        return {
            "message": "AI Diet Planner API",
            "version": "2.0",
            "status": "running",
            "endpoints": {
                "predict": "POST /predict - Diabetes risk prediction",
                "generate_meal_plan": "POST /generate-meal-plan - Complete meal plan with diabetes prediction",
                "upload_prescription": "POST /upload-prescription - AI-powered prescription analysis",
                "export_json": "POST /export-json - Export meal plan as JSON",
                "export_pdf": "POST /export-pdf - Export meal plan as PDF"
            }
        }
    except Exception as e:
        logger.error(f"Root endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


if __name__ == "__main__":
    import uvicorn
    import dotenv
    
    # Load environment variables
    dotenv.load_dotenv()
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    debug = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    logger.info(f"Starting AI Diet Planner API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    uvicorn.run(app, host=host, port=port, reload=debug)
