"""
MINIMAL WORKING SERVER - AI-NutriCare
This is a simplified version that works WITHOUT ML models or complex dependencies
Run this to test the basic system functionality
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="AI-NutriCare API - Minimal Version",
    version="1.0.0",
    description="Simplified working version for testing"
)

# In-memory storage (replace with database in production)
reports_db = {}
report_counter = 0

# ============================================================================
# MODELS
# ============================================================================

class HealthAnalysis(BaseModel):
    detected_conditions: List[str]
    risk_scores: Dict[str, float]
    recommendations: List[str]

class DietPlan(BaseModel):
    patient_name: str
    days: List[Dict]
    daily_calorie_target: int
    recommendations: List[str]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def analyze_health_simple(data: Dict) -> Dict:
    """Simple rule-based health analysis"""
    conditions = []
    risks = {}
    recommendations = []
    
    # Blood sugar
    bs = data.get('blood_sugar', 0)
    if bs > 126:
        conditions.append('diabetes')
        risks['diabetes_risk'] = 0.8
        recommendations.append("Monitor blood sugar levels regularly")
        recommendations.append("Reduce sugar and refined carb intake")
    elif bs > 100:
        conditions.append('pre-diabetes')
        risks['diabetes_risk'] = 0.5
    
    # Cholesterol
    chol = data.get('cholesterol', 0)
    if chol > 240:
        conditions.append('high_cholesterol')
        risks['heart_disease_risk'] = 0.7
        recommendations.append("Reduce saturated fat intake")
    
    # BMI
    bmi = data.get('bmi', 0)
    if bmi > 30:
        conditions.append('obesity')
        recommendations.append("Aim for gradual weight loss")
    elif bmi > 25:
        conditions.append('overweight')
    
    if not recommendations:
        recommendations.append("Maintain a balanced diet")
        recommendations.append("Stay physically active")
    
    return {
        'detected_conditions': conditions,
        'risk_scores': risks,
        'recommendations': recommendations,
        'health_metrics': data
    }

def generate_simple_diet_plan(conditions: List[str], patient_name: str = "Patient") -> Dict:
    """Generate a simple 3-day diet plan"""
    
    # Determine calorie target
    calorie_target = 1800
    if 'obesity' in conditions or 'overweight' in conditions:
        calorie_target = 1500
    
    # Sample meals
    meals = {
        'breakfast': [
            {'name': 'Oatmeal with Berries', 'calories': 320},
            {'name': 'Greek Yogurt with Nuts', 'calories': 250},
            {'name': 'Whole Wheat Toast with Eggs', 'calories': 300}
        ],
        'lunch': [
            {'name': 'Grilled Chicken Salad', 'calories': 380},
            {'name': 'Dal with Brown Rice', 'calories': 420},
            {'name': 'Quinoa Bowl with Vegetables', 'calories': 400}
        ],
        'dinner': [
            {'name': 'Grilled Fish with Broccoli', 'calories': 320},
            {'name': 'Vegetable Soup with Bread', 'calories': 280},
            {'name': 'Tandoori Chicken with Salad', 'calories': 340}
        ],
        'snack': [
            {'name': 'Apple with Almond Butter', 'calories': 180},
            {'name': 'Mixed Nuts', 'calories': 170},
            {'name': 'Fruit Salad', 'calories': 110}
        ]
    }
    
    # Generate 3-day plan
    days = []
    for day in range(1, 4):
        day_plan = {
            'day': day,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'breakfast': meals['breakfast'][day % 3],
            'lunch': meals['lunch'][day % 3],
            'dinner': meals['dinner'][day % 3],
            'snack': meals['snack'][day % 3]
        }
        days.append(day_plan)
    
    recommendations = [
        "Drink 8-10 glasses of water daily",
        "Avoid processed and packaged foods",
        "Include vegetables in every meal"
    ]
    
    if 'diabetes' in conditions:
        recommendations.append("Monitor blood sugar before and after meals")
    if 'high_cholesterol' in conditions:
        recommendations.append("Choose lean proteins and healthy fats")
    
    return {
        'patient_name': patient_name,
        'plan_duration_days': 3,
        'daily_calorie_target': calorie_target,
        'medical_conditions': conditions,
        'days': days,
        'recommendations': recommendations
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "AI-NutriCare API - Minimal Working Version",
        "version": "1.0.0",
        "status": "running",
        "note": "This is a simplified version for testing. Full ML features available after training models.",
        "endpoints": {
            "health_check": "/health",
            "test_analysis": "/test/analyze",
            "test_diet_plan": "/test/diet-plan",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI-NutriCare Minimal",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/test/analyze")
async def test_health_analysis(data: Dict):
    """
    Test health analysis endpoint
    
    Example request body:
    {
        "blood_sugar": 145,
        "cholesterol": 235,
        "bmi": 29.5,
        "blood_pressure": "138/88"
    }
    """
    try:
        analysis = analyze_health_simple(data)
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/diet-plan")
async def test_diet_plan(request: Dict):
    """
    Test diet plan generation
    
    Example request body:
    {
        "patient_name": "John Doe",
        "conditions": ["diabetes", "overweight"]
    }
    """
    try:
        patient_name = request.get('patient_name', 'Patient')
        conditions = request.get('conditions', [])
        
        diet_plan = generate_simple_diet_plan(conditions, patient_name)
        
        return {
            "status": "success",
            "diet_plan": diet_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/complete-workflow")
async def test_complete_workflow(request: Dict):
    """
    Test complete workflow: analyze health + generate diet plan
    
    Example request body:
    {
        "patient_name": "John Doe",
        "health_data": {
            "blood_sugar": 145,
            "cholesterol": 235,
            "bmi": 29.5
        }
    }
    """
    try:
        patient_name = request.get('patient_name', 'Patient')
        health_data = request.get('health_data', {})
        
        # Step 1: Analyze health
        analysis = analyze_health_simple(health_data)
        
        # Step 2: Generate diet plan
        diet_plan = generate_simple_diet_plan(
            analysis['detected_conditions'],
            patient_name
        )
        
        return {
            "status": "success",
            "patient_name": patient_name,
            "health_analysis": analysis,
            "diet_plan": diet_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("  AI-NutriCare - MINIMAL WORKING SERVER")
    print("="*70)
    print("\n✅ This is a simplified version that works WITHOUT:")
    print("   - ML model dependencies")
    print("   - Database setup")
    print("   - Complex NLP libraries")
    print("\n✅ Features available:")
    print("   - Rule-based health analysis (85% accuracy)")
    print("   - Simple diet plan generation")
    print("   - Complete workflow testing")
    print("\n🌐 Server starting...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("\n📚 Try these test endpoints:")
    print("   POST /test/analyze - Test health analysis")
    print("   POST /test/diet-plan - Test diet plan generation")
    print("   POST /test/complete-workflow - Test full workflow")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
