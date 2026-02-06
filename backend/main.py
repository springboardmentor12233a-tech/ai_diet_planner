from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from xgboost import XGBClassifier
from fastapi.middleware.cors import CORSMiddleware

from fastapi import UploadFile, File
import os

from ocr_utils import run_ocr
from nlp_utils import interpret_doctor_notes, generate_diet_plan

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

@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    file_path = f"backend/uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    extracted_text = run_ocr(file_path)
    rules = interpret_doctor_notes(extracted_text)
    diet = generate_diet_plan(rules)

    return {
        "extracted_text": extracted_text,
        "diet_rules": rules,
        "diet_guidelines": diet
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
