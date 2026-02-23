def detect_conditions(metrics, extracted_text):

    conditions = []

    glucose = metrics.get("Glucose")
    bmi = metrics.get("BMI")
    systolic = metrics.get("Systolic")
    diastolic = metrics.get("Diastolic")
    cholesterol = metrics.get("Cholesterol")
    age = metrics.get("Age")

    # Diabetes logic
    if glucose:
        if glucose > 126:
            conditions.append("Diabetes")
        elif glucose >= 100:
            conditions.append("Prediabetes")

    # BMI logic
    if bmi:
        if bmi >= 30:
            conditions.append("Obesity")
        elif bmi >= 25:
            conditions.append("Overweight")

    # Blood pressure
    if systolic and diastolic:
        if systolic > 140 or diastolic > 90:
            conditions.append("Hypertension")

    # Cholesterol
    if cholesterol and cholesterol > 240:
        conditions.append("High Cholesterol")

    # Age
    if age and age > 45:
        conditions.append("Higher Risk Age Group")

    # Doctor note keywords
    if "iron deficiency" in extracted_text.lower():
        conditions.append("Iron Deficiency")

    return list(set(conditions))
