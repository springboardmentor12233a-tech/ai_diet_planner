def generate_health_alerts(patient_data):
    alerts = []

    # Glucose (Diabetes indicator)
    if patient_data['Glucose'] >= 126:
        alerts.append("High glucose level: Possible diabetes risk")

    # BMI (Obesity indicator)
    if patient_data['BMI'] >= 30:
        alerts.append("High BMI: Obesity risk")

    # Blood Pressure (Hypertension indicator)
    if patient_data['BloodPressure'] >= 90:
        alerts.append("High blood pressure: Hypertension risk")

    if not alerts:
        alerts.append("All parameters are within normal range")

    return alerts


if __name__ == "__main__":
    sample_patient = {
        "Glucose": 140,
        "BMI": 32,
        "BloodPressure": 95
    }

    alerts = generate_health_alerts(sample_patient)

    print("Health Alerts:")
    for alert in alerts:
        print("-", alert)
