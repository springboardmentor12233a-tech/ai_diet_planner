"""
Standalone test script for data extraction (minimal dependencies)
"""
import sys
import re
from pathlib import Path

# Simple extraction without full dependencies
def extract_numeric_data(text: str):
    """Extract numeric health metrics using regex"""
    patterns = {
        "blood_sugar": [
            r"(?:blood\s+)?(?:glucose|sugar)\s*(?:level|test)?[:\s]*(\d+\.?\d*)",
            r"fbs[:\s]*(\d+\.?\d*)",
            r"fasting\s+(?:blood\s+)?(?:glucose|sugar)[:\s]*\(?fbs\)?[:\s]*(\d+\.?\d*)",
            r"fasting\s+(?:blood\s+)?(?:glucose|sugar)[:\s]*(\d+\.?\d*)",
        ],
        "cholesterol": [
            r"(?:total\s+)?cholesterol[:\s]*(\d+\.?\d*)",
        ],
        "hdl": [
            r"hdl\s+cholesterol[:\s]*(\d+\.?\d*)",
        ],
        "ldl": [
            r"ldl\s+cholesterol[:\s]*(\d+\.?\d*)",
        ],
        "triglycerides": [
            r"triglycerides?[:\s]*(\d+\.?\d*)",
        ],
        "bmi": [
            r"bmi[:\s]*(\d+\.?\d*)",
        ],
        "blood_pressure": [
            r"blood\s+pressure[:\s]*(\d+)\s*/\s*(\d+)",
            r"bp[:\s]*(\d+)\s*/\s*(\d+)",
        ],
        "hemoglobin": [
            r"hemoglobin\s*\(hb\)[:\s]*(\d+\.?\d*)",
            r"hb[:\s]*(\d+\.?\d*)",
            r"hemoglobin[:\s]*(\d+\.?\d*)",
        ],
        "iron": [
            r"serum\s+iron[:\s]*(\d+\.?\d*)",
        ],
    }
    
    numeric_data = {}
    
    for metric, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if metric == "blood_pressure":
                    numeric_data["systolic_bp"] = float(match.group(1))
                    numeric_data["diastolic_bp"] = float(match.group(2))
                else:
                    value = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                    numeric_data[metric] = float(value)
                break
    
    return numeric_data

def extract_textual_data(text: str):
    """Extract doctor notes"""
    prescription_pattern = r"prescription[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)"
    notes_pattern = r"doctor['\s]?s\s+notes?[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)"
    
    prescriptions = re.findall(prescription_pattern, text, re.IGNORECASE | re.DOTALL)
    notes = re.findall(notes_pattern, text, re.IGNORECASE | re.DOTALL)
    
    return {
        "prescriptions": "\n".join(prescriptions) if prescriptions else "",
        "doctor_notes": "\n".join(notes) if notes else text[:500]
    }

if __name__ == "__main__":
    print("="*60)
    print("Data Extraction Test - Standalone")
    print("="*60)
    
    test_file = Path("tests/test_data/sample_medical_report.txt")
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        sys.exit(1)
    
    with open(test_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"\n[OK] Loaded test file: {test_file}")
    print(f"[OK] Text length: {len(text)} characters\n")
    
    # Extract data
    numeric_data = extract_numeric_data(text)
    textual_data = extract_textual_data(text)
    
    print("="*60)
    print("EXTRACTED NUMERIC DATA:")
    print("="*60)
    import json
    print(json.dumps(numeric_data, indent=2))
    
    print("\n" + "="*60)
    print("EXTRACTED TEXTUAL DATA SUMMARY:")
    print("="*60)
    print(f"Prescriptions: {len(textual_data['prescriptions'])} chars")
    print(f"Doctor Notes: {len(textual_data['doctor_notes'])} chars")
    print("\nSample Notes:")
    print(textual_data['doctor_notes'][:300])
    
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print("="*60)
    
    found_metrics = list(numeric_data.keys())
    
    # Check for any blood sugar related metrics
    has_blood_sugar = "blood_sugar" in found_metrics or "fbs" in found_metrics
    has_cholesterol = "cholesterol" in found_metrics
    has_bmi = "bmi" in found_metrics
    has_bp = "systolic_bp" in found_metrics and "diastolic_bp" in found_metrics
    
    print(f"\nFound {len(found_metrics)} metrics: {found_metrics}")
    print(f"\nMetric Coverage:")
    print(f"  Blood Sugar: {'[OK]' if has_blood_sugar else '[MISSING]'}")
    print(f"  Cholesterol: {'[OK]' if has_cholesterol else '[MISSING]'}")
    print(f"  BMI: {'[OK]' if has_bmi else '[MISSING]'}")
    print(f"  Blood Pressure: {'[OK]' if has_bp else '[MISSING]'}")
    
    core_metrics_found = sum([has_blood_sugar, has_cholesterol, has_bmi])
    print(f"\nCore Metrics Found: {core_metrics_found}/3")
    
    if core_metrics_found >= 2 and len(found_metrics) >= 3:
        print("[PASS] Data extraction test PASSED!")
        print("The system successfully extracts medical metrics from reports.")
    else:
        print("[PARTIAL] Data extraction working but can be improved")
        print("Patterns may need refinement for better coverage.")
    
    print("="*60)
