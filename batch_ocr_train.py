import os
import sys
import ssl
import cv2
import pandas as pd
import numpy as np
import re
from pathlib import Path
from tqdm import tqdm

# Fix SSL certificate issues for model downloads
ssl._create_default_https_context = ssl._create_unverified_context

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))
from app.services.ocr_service import OCRService

def extract_metrics(text):
    """Refined regex extraction for metabolic markers"""
    metrics = {
        'Glucose': 0,
        'BloodPressure_Systolic': 0,
        'BloodPressure_Diastolic': 0,
        'SkinThickness': 0,
        'Insulin': 0,
        'BMI': 0,
        'Age': 0,
        'Outcome': 0
    }
    
    # Glucose (Fasting)
    glucose_match = re.search(r'(?:Glucose|Sugar|Fasting)\s*(?:[:\- ]|Level)?\s*(\d{2,3})', text, re.I)
    if glucose_match: metrics['Glucose'] = int(glucose_match.group(1))
    
    # BP
    bp_match = re.search(r'(?:BP|Pressure)\s*(?:[:\- ]|Level)?\s*(\d{2,3})\s*/\s*(\d{2,3})', text, re.I)
    if bp_match:
        metrics['BloodPressure_Systolic'] = int(bp_match.group(1))
        metrics['BloodPressure_Diastolic'] = int(bp_match.group(2))
        
    # BMI
    bmi_match = re.search(r'BMI\s*(?:[:\- ]|Level)?\s*(\d{1,2}(?:\.\d)?)', text, re.I)
    if bmi_match: metrics['BMI'] = float(bmi_match.group(1))
    
    # Age
    age_match = re.search(r'(?:Age|Yrs|Years)\s*(?:[:\- ]|Level)?\s*(\d{1,2})', text, re.I)
    if age_match: metrics['Age'] = int(age_match.group(1))
    
    # Outcome (Based on keywords in notes)
    diabetic_keywords = ["diabetes", "diabetic", "hyperglycemia", "metformin", "insulin", "t2dm"]
    if any(k in text.lower() for k in diabetic_keywords):
        metrics['Outcome'] = 1
        
    return metrics

def build_dataset():
    image_dir = Path("lbmaske")
    images = list(image_dir.glob("*.png"))
    
    if not images:
        print("❌ No images found in lbmaske folder")
        return

    print(f"🚀 Starting Batch OCR on {len(images)} real images...")
    ocr = OCRService()
    extracted_data = []

    # Process first 50 images for a solid seed dataset (OCR is slow on CPU)
    # We can expand this later
    limit = 50
    for img_path in tqdm(images[:limit], desc="Processing Images"):
        try:
            text = ocr.extract_text(str(img_path))
            data = extract_metrics(text)
            data['filename'] = img_path.name
            extracted_data.append(data)
        except Exception as e:
            print(f"\n❌ Error on {img_path.name}: {e}")

    df = pd.DataFrame(extracted_data)
    df.to_csv("lbmaske_extracted_data.csv", index=False)
    print(f"\n✅ Created 'lbmaske_extracted_data.csv' with {len(df)} records")
    
    # Basic summary
    positives = df['Outcome'].sum()
    print(f"📊 Dataset Snapshot: {positives} Diabetic (1), {len(df)-positives} Non-Diabetic (0)")

if __name__ == "__main__":
    build_dataset()
