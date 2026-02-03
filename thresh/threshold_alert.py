def health_alert_system(bmi, systolic_bp, diastolic_bp, glucose):
    alerts = []

    # BMI check
    if bmi < 18.5:
        alerts.append("BMI Alert: Underweight")
    elif 18.5 <= bmi <= 24.9:
        alerts.append("BMI Status: Normal")
    elif 25 <= bmi <= 29.9:
        alerts.append("BMI Alert: Overweight")
    else:
        alerts.append("BMI Alert: Obese")

    # Blood Pressure check
    if systolic_bp < 90 or diastolic_bp < 60:
        alerts.append("Blood Pressure Alert: Low BP")
    elif 90 <= systolic_bp <= 120 and 60 <= diastolic_bp <= 80:
        alerts.append("Blood Pressure Status: Normal")
    elif systolic_bp >= 140 or diastolic_bp >= 90:
        alerts.append("Blood Pressure Alert: High BP")
    else:
        alerts.append("Blood Pressure Status: Slightly Elevated")

    # Glucose check
    if glucose < 70:
        alerts.append("Glucose Alert: Low Blood Sugar")
    elif 70 <= glucose <= 99:
        alerts.append("Glucose Status: Normal")
    elif 100 <= glucose <= 125:
        alerts.append("Glucose Alert: Prediabetes")
    else:
        alerts.append("Glucose Alert: Diabetes")

    return alerts

if __name__ == "__main__":

    bmi = float(input("Enter BMI value: "))
    systolic_bp = int(input("Enter Systolic Blood Pressure: "))
    diastolic_bp = int(input("Enter Diastolic Blood Pressure: "))
    glucose = int(input("Enter Glucose Level: "))

    alerts = health_alert_system(bmi, systolic_bp, diastolic_bp, glucose)

    print("\n=== HEALTH ALERTS ===")
    for alert in alerts:
        print(alert)


