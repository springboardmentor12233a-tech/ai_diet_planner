def health_alert(glucose, bmi, blood_pressure, age, insulin, skin_thickness, pregnancies, dpf):
    """
    Check health parameters and return status messages.
    
    Parameters:
        glucose (float): Blood glucose level (mg/dL)
        bmi (float): Body Mass Index
        blood_pressure (float): Blood pressure (mmHg)
        age (int): Age in years
        insulin (float): Insulin level (muU/ml)
        skin_thickness (float): Skinfold thickness (mm)
        pregnancies (int): Number of pregnancies
        dpf (float): Diabetes Pedigree Function

    Returns:
        dict: Status for each parameter and overall alert
    """

    alerts = {}

    # 1. Glucose Thresholds
    if glucose < 70:
        alerts['Glucose'] = 'Low - Hypoglycemia'
    elif 70 <= glucose <= 140:
        alerts['Glucose'] = 'Normal'
    elif 141 <= glucose <= 199:
        alerts['Glucose'] = 'Prediabetic / Borderline'
    else:  # glucose >= 200
        alerts['Glucose'] = 'High - Diabetes Risk'

    # 2. BMI Thresholds (WHO)
    if bmi < 18.5:
        alerts['BMI'] = 'Underweight'
    elif 18.5 <= bmi < 25:
        alerts['BMI'] = 'Normal'
    elif 25 <= bmi < 30:
        alerts['BMI'] = 'Overweight'
    else:  # bmi >= 30
        alerts['BMI'] = 'Obese'

    # 3. Blood Pressure Thresholds (mmHg)
    if blood_pressure < 90:
        alerts['BloodPressure'] = 'Low'
    elif 90 <= blood_pressure < 120:
        alerts['BloodPressure'] = 'Normal'
    elif 120 <= blood_pressure < 140:
        alerts['BloodPressure'] = 'Elevated'
    else:  # blood_pressure >= 140
        alerts['BloodPressure'] = 'High / Hypertension'

    # 4. Insulin (normal fasting: 2–25 muU/ml)
    if insulin < 2:
        alerts['Insulin'] = 'Low'
    elif 2 <= insulin <= 25:
        alerts['Insulin'] = 'Normal'
    else:
        alerts['Insulin'] = 'High'

    # 5. Skin Thickness (normal: 10–40 mm)
    if skin_thickness < 10:
        alerts['SkinThickness'] = 'Low'
    elif 10 <= skin_thickness <= 40:
        alerts['SkinThickness'] = 'Normal'
    else:
        alerts['SkinThickness'] = 'High'

    # 6. Age
    if age < 18:
        alerts['Age'] = 'Young'
    elif 18 <= age < 60:
        alerts['Age'] = 'Adult'
    else:
        alerts['Age'] = 'Senior'

    # 7. Pregnancies
    if pregnancies == 0:
        alerts['Pregnancies'] = 'None'
    elif 1 <= pregnancies <= 3:
        alerts['Pregnancies'] = 'Low'
    elif 4 <= pregnancies <= 6:
        alerts['Pregnancies'] = 'Moderate'
    else:
        alerts['Pregnancies'] = 'High'

    # 8. Diabetes Pedigree Function (DPF)
    if dpf < 0.3:
        alerts['DPF'] = 'Low Risk'
    elif 0.3 <= dpf < 0.6:
        alerts['DPF'] = 'Moderate Risk'
    else:
        alerts['DPF'] = 'High Risk'

    # 9. Overall Alert
    critical_values = ['High - Diabetes Risk', 'Obese', 'High / Hypertension', 'High Risk']
    if any(val in alerts.values() for val in critical_values):
        alerts['Overall'] = '⚠️ Critical: Medical attention advised!'
    elif any(val in alerts.values() for val in ['Prediabetic / Borderline', 'Overweight', 'Elevated', 'Moderate Risk']):
        alerts['Overall'] = '⚠️ Warning: Monitor lifestyle & health'
    else:
        alerts['Overall'] = '✅ Normal: Keep healthy habits'

    return alerts

if __name__ == "__main__":
    # Sample user input
    user_data = {
        'glucose': 180,
        'bmi': 32,
        'blood_pressure': 145,
        'age': 45,
        'insulin': 30,
        'skin_thickness': 20,
        'pregnancies': 2,
        'dpf': 0.7
    }

    alerts = health_alert(**user_data)

    # Print results
    for key, value in alerts.items():
        print(f"{key}: {value}")
