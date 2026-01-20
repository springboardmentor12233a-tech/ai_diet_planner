def get_health_alerts(patient_data):
    alerts = []
    
    # Glucose Alert(diabetes Indicator)
    glucose = patient_data.get('Glucose')
    if glucose >= 126:
        alerts.append({"metric": "Glucose", "status": "Critical", "message": "High Blood Sugar (Diabetes Range)"})
    elif 100 <= glucose < 126:
        alerts.append({"metric": "Glucose", "status": "Warning", "message": "Elevated Blood Sugar (Prediabetes Range)"})

    # BMI Alert(Obesity Indicator)
    bmi = patient_data.get('BMI')
    if bmi >= 30:
        alerts.append({"metric": "BMI", "status": "Critical", "message": "High BMI (Obesity Range)"})
    elif 25 <= bmi < 30:
        alerts.append({"metric": "BMI", "status": "Warning", "message": "Elevated BMI (Overweight Range)"})

    # Blood Pressure Alert (Hypertension Indicator)
    bp = patient_data.get('BloodPressure')
    if bp >= 90: 
        alerts.append({"metric": "Blood Pressure", "status": "Critical", "message": "High Blood Pressure Detected"})
        
    return alerts

# Example Usage
sample_patient = {'Glucose': 145, 'BMI': 32, 'BloodPressure': 85}
active_alerts = get_health_alerts(sample_patient)

for alert in active_alerts:
    print(f"[{alert['status']}] {alert['metric']}: {alert['message']}")