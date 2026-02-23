import re

def extract_metrics(text: str):

    metrics = {}

    # Glucose
    glucose_match = re.search(r'glucose\s*[:\-]?\s*(\d+)', text, re.I)
    if glucose_match:
        metrics["Glucose"] = int(glucose_match.group(1))

    # BMI
    bmi_match = re.search(r'bmi\s*[:\-]?\s*(\d+\.?\d*)', text, re.I)
    if bmi_match:
        metrics["BMI"] = float(bmi_match.group(1))

    # Blood Pressure
    bp_match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if bp_match:
        metrics["BP_Systolic"] = int(bp_match.group(1))
        metrics["BP_Diastolic"] = int(bp_match.group(2))

    # Iron deficiency keywords
    if re.search(r'iron\s*(deficiency|low)', text, re.I):
        metrics["Iron_Deficiency"] = True

    # Overweight mention
    if re.search(r'overweight', text, re.I):
        metrics["Overweight"] = True

    return metrics
