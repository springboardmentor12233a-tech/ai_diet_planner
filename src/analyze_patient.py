import pandas as pd
import numpy as np
import pickle

with open("svm_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("robust_scaler.pkl", "rb") as f:
    robust_scaler = pickle.load(f)

with open("standard_scaler.pkl", "rb") as f:
    standard_scaler = pickle.load(f)


MODEL_FEATURES = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
    "NewBMI_Obesity_1",
    "NewBMI_Obesity_2",
    "NewBMI_Obesity_3",
    "NewBMI_Overweight",
    "NewBMI_Underweight",
    "NewInsulinScore_Normal",
    "NewGlucose_Low",
    "NewGlucose_Normal",
    "NewGlucose_Prediabetic"
]

# Fallback values learned from training
TRAINING_MEDIANS = {
    "Pregnancies": 3,
    "Glucose": 117,
    "BloodPressure": 72,
    "SkinThickness": 23,
    "Insulin": 102,
    "BMI": 32.0,
    "DiabetesPedigreeFunction": 0.37,
    "Age": 29
}


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi <= 24.9:
        return "Normal"
    elif bmi <= 29.9:
        return "Overweight"
    elif bmi <= 34.9:
        return "Obesity_1"
    elif bmi <= 39.9:
        return "Obesity_2"
    else:
        return "Obesity_3"


def insulin_score(insulin):
    return "Normal" if 16 <= insulin <= 166 else "Abnormal"


def glucose_category(glucose):
    if glucose <= 70:
        return "Low"
    elif glucose <= 99:
        return "Normal"
    elif glucose <= 126:
        return "Prediabetic"
    else:
        return "Diabetic"


def get_health_alerts(patient):
    alerts = []

    # Glucose
    g = patient.get("Glucose")
    if g is not None:
        if g > 126:
            alerts.append("Glucose: Diabetic range")
        elif g >= 100:
            alerts.append("Glucose: Prediabetic range")
        else:
            alerts.append("Glucose: Normal range")

    # BMI
    bmi = patient.get("BMI")
    if bmi is not None:
        if bmi >= 30:
            alerts.append("BMI: Obesity range")
        elif bmi >= 25:
            alerts.append("BMI: Overweight range")
        else:
            alerts.append("BMI: Normal range")

    # Blood Pressure
    bp = patient.get("BloodPressure")
    if bp is not None:
        if bp > 80:
            alerts.append("Blood Pressure: High")
        else:
            alerts.append("Blood Pressure: Normal")

    # Insulin
    insulin = patient.get("Insulin")
    if insulin is not None:
        if insulin < 16 or insulin > 166:
            alerts.append("Insulin: Abnormal")
        else:
            alerts.append("Insulin: Normal")

    # Age
    age = patient.get("Age")
    if age is not None:
        if age > 45:
            alerts.append("Age: Higher risk group")
        elif age >= 30:
            alerts.append("Age: Moderate risk group")
        else:
            alerts.append("Age: Lower risk group")

    return alerts


def prepare_input(patient):
    base_data = {}

    # Fill missing values using training medians
    for key in TRAINING_MEDIANS:
        base_data[key] = patient.get(key, TRAINING_MEDIANS[key])

    df = pd.DataFrame([base_data])

    # Feature engineering
    df["NewBMI"] = df["BMI"].apply(bmi_category)
    df["NewInsulinScore"] = df["Insulin"].apply(insulin_score)
    df["NewGlucose"] = df["Glucose"].apply(glucose_category)

    # One-hot encoding
    df = pd.get_dummies(
        df,
        columns=["NewBMI", "NewInsulinScore", "NewGlucose"],
        drop_first=True
    )

    # Align with model features
    df = df.reindex(columns=MODEL_FEATURES, fill_value=0)

    # Scaling 
    df_scaled = robust_scaler.transform(df)
    df_scaled = standard_scaler.transform(df_scaled)


    return df_scaled



def read_float(prompt):
    while True:
        value = input(prompt).strip()
        if value == "":
            return None
        try:
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a number or press Enter to skip.")

def get_patient_input():
    print("\nEnter patient details (press Enter to skip a field):")

    return {
        "Glucose": read_float("Glucose (mg/dL): "),
        "BloodPressure": read_float("Blood Pressure (mm Hg): "),
        "SkinThickness": read_float("Skin Thickness: "),
        "Insulin": read_float("Insulin: "),
        "BMI": read_float("BMI: "),
        "Age": read_float("Age: ")
    }


if __name__ == "__main__":

    patient = get_patient_input()

    print("\nHEALTH CONDITION REPORT")
    alerts = get_health_alerts(patient)

    if alerts:
        for alert in alerts:
            print("-", alert)
    else:
        print("No abnormal health indicators detected.")

    # ML Prediction
    X_new = prepare_input(patient)
    prediction = model.predict(X_new)[0]
    probability = model.predict_proba(X_new)[0][1]

    print("\nDIABETES PREDICTION RESULT")
    if prediction == 1:
        print("Prediction: Diabetic")
    else:
        print("Prediction: Not Diabetic")

    print(f"Risk Probability: {probability:.2f}")
