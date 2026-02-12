from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import numpy as np
from xgboost import XGBClassifier
from fastapi.middleware.cors import CORSMiddleware

from fastapi import UploadFile, File
import os
import json
from datetime import datetime

from ocr_utils import run_ocr
from nlp_utils import interpret_doctor_notes, generate_diet_plan
from ai_interpreter import get_ai_interpreter
from meal_planner import get_meal_planner

app = FastAPI(title="AI Diet Planner – Diabetes API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
model = XGBClassifier()
model.load_model("model/diabetes_xgb.json")

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


def classify_risk(prob):
    if prob < OPTIMAL_THRESHOLD:
        return "Low Risk"
    elif prob < 0.5:
        return "Moderate Risk"
    else:
        return "High Risk"


@app.post("/predict")
def predict(input: DiabetesInput):
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
os.makedirs("backend/uploads", exist_ok=True)
os.makedirs("backend/exports", exist_ok=True)

@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    """Upload and analyze medical prescription using AI."""
    file_path = f"backend/uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text using OCR
    extracted_text = run_ocr(file_path)
    
    # Use AI interpreter for intelligent analysis
    ai_interpreter = get_ai_interpreter()
    interpreted_data = ai_interpreter.interpret_medical_text(extracted_text)
    
    # Generate diet rules
    diet_rules = ai_interpreter.generate_diet_rules(interpreted_data)
    
    # Generate comprehensive meal plan
    meal_planner = get_meal_planner()
    meal_plan = meal_planner.generate_meal_plan(
        conditions=interpreted_data.get("conditions", []),
        dietary_restrictions=interpreted_data.get("dietary_restrictions", [])
    )

    return {
        "extracted_text": extracted_text,
        "interpreted_data": interpreted_data,
        "diet_rules": diet_rules,
        "meal_plan": meal_plan
    }


@app.post("/generate-meal-plan")
def generate_comprehensive_meal_plan(input: DiabetesInput):
    """Generate meal plan based on diabetes prediction."""
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
    
    # Generate meal plan
    meal_planner = get_meal_planner()
    meal_plan = meal_planner.generate_meal_plan(
        conditions=conditions if conditions else ["General health maintenance"],
        dietary_restrictions=dietary_restrictions,
        diabetes_risk=risk
    )
    
    return {
        "diabetes_probability": round(float(prob), 3),
        "risk_level": risk,
        "model_roc_auc": MODEL_ROC_AUC,
        "conditions": conditions if conditions else ["General health maintenance"],
        "meal_plan": meal_plan,
        "message": (
            "Follow a low-GI diet and consult a doctor"
            if risk == "High Risk"
            else "Maintain a balanced diet and regular exercise"
        )
    }


@app.post("/export-json")
async def export_meal_plan_json(meal_plan_data: dict):
    """Export meal plan as JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diet_plan_{timestamp}.json"
    filepath = f"backend/exports/{filename}"
    
    # Add metadata
    export_data = {
        "generated_at": datetime.now().isoformat(),
        "plan_type": "Personalized Diet Plan",
        "data": meal_plan_data
    }
    
    with open(filepath, "w") as f:
        json.dump(export_data, f, indent=2)
    
    return FileResponse(filepath, filename=filename, media_type="application/json")


@app.post("/export-pdf")
async def export_meal_plan_pdf(meal_plan_data: dict):
    """Export meal plan as PDF file."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diet_plan_{timestamp}.pdf"
        filepath = f"backend/exports/{filename}"
        
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
            story.append(Paragraph("<b>Daily Meal Plan</b>", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            
            # Breakfast
            if 'breakfast' in meal_plan:
                meal = meal_plan['breakfast']
                story.append(Paragraph("<b>Breakfast:</b>", styles['Heading3']))
                story.append(Paragraph(f"<b>{meal['name']}</b>", styles['Normal']))
                story.append(Paragraph(meal['description'], styles['Normal']))
                story.append(Paragraph(f"Calories: {meal['calories']} | Protein: {meal['protein']} | Carbs: {meal['carbs']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Lunch
            if 'lunch' in meal_plan:
                meal = meal_plan['lunch']
                story.append(Paragraph("<b>Lunch:</b>", styles['Heading3']))
                story.append(Paragraph(f"<b>{meal['name']}</b>", styles['Normal']))
                story.append(Paragraph(meal['description'], styles['Normal']))
                story.append(Paragraph(f"Calories: {meal['calories']} | Protein: {meal['protein']} | Carbs: {meal['carbs']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Dinner
            if 'dinner' in meal_plan:
                meal = meal_plan['dinner']
                story.append(Paragraph("<b>Dinner:</b>", styles['Heading3']))
                story.append(Paragraph(f"<b>{meal['name']}</b>", styles['Normal']))
                story.append(Paragraph(meal['description'], styles['Normal']))
                story.append(Paragraph(f"Calories: {meal['calories']} | Protein: {meal['protein']} | Carbs: {meal['carbs']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Snacks
            if 'snacks' in meal_plan:
                story.append(Paragraph("<b>Recommended Snacks:</b>", styles['Heading3']))
                for snack in meal_plan['snacks']:
                    story.append(Paragraph(f"• {snack['name']} ({snack['calories']} cal) - {snack['description']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Daily Summary
            if 'daily_summary' in meal_plan:
                summary = meal_plan['daily_summary']
                story.append(Paragraph("<b>Daily Nutritional Summary</b>", styles['Heading3']))
                story.append(Paragraph(f"Total Calories: {summary['total_calories']}", styles['Normal']))
                story.append(Paragraph(f"Protein: {summary['protein']}", styles['Normal']))
                story.append(Paragraph(f"Carbohydrates: {summary['carbs']}", styles['Normal']))
                story.append(Paragraph(f"Focus: {summary['focus']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Hydration
            if 'hydration' in meal_plan:
                story.append(Paragraph("<b>Hydration:</b>", styles['Heading3']))
                story.append(Paragraph(meal_plan['hydration'], styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Notes
            if 'notes' in meal_plan:
                story.append(Paragraph("<b>Important Notes:</b>", styles['Heading3']))
                for note in meal_plan['notes']:
                    story.append(Paragraph(f"• {note}", styles['Normal']))
        
        # Diet Rules
        if 'diet_rules' in meal_plan_data:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("<b>Dietary Guidelines:</b>", styles['Heading3']))
            for rule in meal_plan_data['diet_rules']:
                story.append(Paragraph(f"• {rule}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return FileResponse(filepath, filename=filename, media_type="application/pdf")
    
    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"error": "PDF generation requires reportlab. Install with: pip install reportlab"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"PDF generation failed: {str(e)}"}
        )


@app.get("/")
def read_root():
    return {
        "message": "AI Diet Planner API",
        "version": "2.0",
        "endpoints": {
            "predict": "POST /predict - Diabetes risk prediction",
            "generate_meal_plan": "POST /generate-meal-plan - Complete meal plan with diabetes prediction",
            "upload_prescription": "POST /upload-prescription - AI-powered prescription analysis",
            "export_json": "POST /export-json - Export meal plan as JSON",
            "export_pdf": "POST /export-pdf - Export meal plan as PDF"
        }
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

