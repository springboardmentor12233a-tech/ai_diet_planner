def get_health_alerts(patient_data):
    alerts = []
    glucose = patient_data.get("Glucose")

    if glucose < 70:
        alerts.append(("Glucose", "Warning", "Low Blood Sugar"))
    elif 70 <= glucose < 100:
        alerts.append(("Glucose", "Normal", "Glucose level is normal"))
    elif 100 <= glucose < 126:
        alerts.append(("Glucose", "Warning", "Prediabetes Range"))
    else:
        alerts.append(("Glucose", "Critical", "Diabetes Range"))

   
    bmi = patient_data.get("BMI")

    if bmi < 18.5:
        alerts.append(("BMI", "Warning", "Underweight"))
    elif 18.5 <= bmi < 25:
        alerts.append(("BMI", "Normal", "Healthy BMI"))
    elif 25 <= bmi < 30:
        alerts.append(("BMI", "Warning", "Overweight"))
    else:
        alerts.append(("BMI", "Critical", "Obesity Risk"))

    bp = patient_data.get("BloodPressure")

    bp = patient_data.get("BloodPressure")

    if bp < 60:
       alerts.append(("Blood Pressure", "Warning", "Low Blood Pressure (Hypotension)"))
    elif 60 <= bp < 80:
       alerts.append(("Blood Pressure", "Normal", "Blood Pressure is normal"))
    elif 80 <= bp < 90:
       alerts.append(("Blood Pressure", "Warning", "Elevated Blood Pressure"))
    else:
       alerts.append(("Blood Pressure", "Critical", "High Blood Pressure"))

    return alerts


if __name__ == "__main__":
    print(" HEALTH ALERT SYSTEM \n")

    glucose = float(input("Enter Glucose level (mg/dL): "))
    bmi = float(input("Enter BMI value: "))
    bp = float(input("Enter Diastolic Blood Pressure (mm Hg): "))

    patient_data = {
        "Glucose": glucose,
        "BMI": bmi,
        "BloodPressure": bp
    }

    alerts = get_health_alerts(patient_data)

    print("\n HEALTH ALERTS ")
    for metric, status, message in alerts:
        print(f"[{status}] {metric}: {message}")

