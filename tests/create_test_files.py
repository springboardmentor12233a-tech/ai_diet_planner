"""
Script to create test medical report files for testing
"""
import os
from pathlib import Path

def create_test_text_file():
    """Create a sample text medical report"""
    test_dir = Path("./tests/test_data")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    sample_report = """
MEDICAL REPORT
Patient Name: John Doe
Date: January 15, 2024
Doctor: Dr. Smith

LABORATORY RESULTS:

Blood Test Results:
-------------------
Fasting Blood Sugar (FBS): 125 mg/dl
Total Cholesterol: 220 mg/dl
HDL Cholesterol: 45 mg/dl
LDL Cholesterol: 150 mg/dl
Triglycerides: 180 mg/dl
Hemoglobin (Hb): 14.5 g/dl
Serum Iron: 85 mcg/dl

Vital Signs:
------------
Blood Pressure: 135/85 mmHg
BMI: 26.5 kg/m²
Weight: 75 kg
Height: 170 cm

PRESCRIPTION:
1. Metformin 500mg - Twice daily after meals
2. Atorvastatin 20mg - Once daily at bedtime
3. Aspirin 75mg - Once daily

DOCTOR'S NOTES:
Patient presents with elevated blood sugar and cholesterol levels.
Recommendations:
- Follow a diabetic diet plan
- Reduce sugar and carbohydrate intake
- Increase physical activity to 30 minutes daily
- Monitor blood sugar levels regularly
- Follow-up appointment in 3 months

Dietary Restrictions:
- Avoid high sugar foods
- Limit saturated fats
- Low sodium diet recommended
- Increase fiber intake

Signed,
Dr. Smith
"""
    
    file_path = test_dir / "sample_medical_report.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(sample_report)
    
    print(f"[OK] Created test file: {file_path}")
    return file_path

def create_simple_text_file():
    """Create a simpler test file"""
    test_dir = Path("./tests/test_data")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    simple_report = """
Blood Sugar: 95
Cholesterol: 180
BMI: 23.5
BP: 120/80

Continue medication. Follow healthy diet.
"""
    
    file_path = test_dir / "simple_report.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(simple_report)
    
    print(f"[OK] Created simple test file: {file_path}")
    return file_path

if __name__ == "__main__":
    print("Creating test files...")
    create_test_text_file()
    create_simple_text_file()
    print("\nTest files created successfully!")
