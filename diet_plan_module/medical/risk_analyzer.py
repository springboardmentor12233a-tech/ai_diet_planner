def analyze_conditions(metrics: dict):

    conditions = []

    glucose = metrics.get("Glucose")
    bmi = metrics.get("BMI")
    systolic = metrics.get("BP_Systolic")
    diastolic = metrics.get("BP_Diastolic")

    if glucose:
        if glucose > 126:
            conditions.append("Diabetes")
        elif glucose >= 100:
            conditions.append("Prediabetes")

    if bmi:
        if bmi >= 30:
            conditions.append("Obesity")
        elif bmi >= 25:
            conditions.append("Overweight")

    if systolic and diastolic:
        if systolic > 140 or diastolic > 90:
            conditions.append("Hypertension")

    if metrics.get("Iron_Deficiency"):
        conditions.append("Iron Deficiency")

    if metrics.get("Overweight"):
        if "Overweight" not in conditions:
            conditions.append("Overweight")

    return conditions
