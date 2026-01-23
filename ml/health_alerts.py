def get_health_alerts(patient_data):
    alerts = []

    # Glucose Alert (diabetes indicator)
    glucose = patient_data.get("Glucose")
    if glucose is not None:
        if glucose >= 126:
            alerts.append({"metric": "Glucose", "status": "Critical", "message": "High Blood Sugar (Diabetes Range)"})
        elif 100 <= glucose < 126:
            alerts.append({"metric": "Glucose", "status": "Warning", "message": "Elevated Blood Sugar (Prediabetes Range)"})

    # BMI Alert (obesity indicator)
    bmi = patient_data.get("BMI")
    if bmi is not None:
        if bmi >= 30:
            alerts.append({"metric": "BMI", "status": "Critical", "message": "High BMI (Obesity Range)"})
        elif 25 <= bmi < 30:
            alerts.append({"metric": "BMI", "status": "Warning", "message": "Elevated BMI (Overweight Range)"})

    # Blood Pressure Alert (hypertension indicator)
    bp = patient_data.get("BloodPressure")
    if bp is not None and bp >= 90:
        alerts.append({"metric": "Blood Pressure", "status": "Critical", "message": "High Blood Pressure Detected"})

    return alerts


def _read_float(prompt):
    while True:
        raw_value = input(prompt).strip()
        try:
            return float(raw_value)
        except ValueError:
            print("Please enter a valid number.")


def get_patient_data_from_user():
    return {
        "Glucose": _read_float("Enter fasting glucose (mg/dL): "),
        "BMI": _read_float("Enter BMI: "),
        "BloodPressure": _read_float("Enter diastolic blood pressure (mm Hg): "),
    }


if __name__ == "__main__":
    patient = get_patient_data_from_user()
    alerts = get_health_alerts(patient)

    if not alerts:
        print("No active alerts. Keep up the good work!")
    else:
        for alert in alerts:
            print(f"[{alert['status']}] {alert['metric']}: {alert['message']}")