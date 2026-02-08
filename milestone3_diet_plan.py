import joblib
import numpy as np

# -----------------------------
# Load trained ML model
# -----------------------------
model = joblib.load("models/health_model.pkl")

# -----------------------------
# Risk Level
# -----------------------------
def health_alert(prob):
    if prob >= 0.80:
        return "🔴 Critical Risk"
    elif prob >= 0.55:
        return "🟠 Moderate Risk"
    else:
        return "🟢 Low Risk"

# -----------------------------
# BMI-Based Calories
# -----------------------------
def bmi_calories(bmi):
    if bmi >= 30:
        return 1500
    elif bmi >= 25:
        return 1800
    else:
        return 2200

# -----------------------------
# Age-Based Adjustment
# -----------------------------
def age_adjustment(age):
    if age < 30:
        return 0
    elif age <= 50:
        return 200
    else:
        return 400

# -----------------------------
# Diet Plan Logic
# -----------------------------
def diet_plan(calories, risk):
    if "Critical" in risk:
        return {
            "Calories": calories,
            "Breakfast": "Oats + boiled egg",
            "Lunch": "Brown rice + vegetables + dal",
            "Dinner": "Soup + salad",
            "Avoid": "Sugar, white rice, fried food"
        }

    elif "Moderate" in risk:
        return {
            "Calories": calories,
            "Breakfast": "Whole grain toast + fruit",
            "Lunch": "Chapati + vegetables + curd",
            "Dinner": "Grilled vegetables + soup",
            "Avoid": "Excess sugar, junk food"
        }

    else:
        return {
            "Calories": calories,
            "Breakfast": "Milk + fruits",
            "Lunch": "Balanced home food",
            "Dinner": "Light food",
            "Avoid": "Overeating"
        }

# -----------------------------
# Main Health Analysis
# -----------------------------
def analyze_patient(data):
    data_array = np.array(data).reshape(1, -1)

    probability = model.predict_proba(data_array)[0][1]
    risk = health_alert(probability)

    bmi = data[5]
    age = data[7]

    base_cal = bmi_calories(bmi)
    final_cal = base_cal - age_adjustment(age)

    plan = diet_plan(final_cal, risk)

    return probability, risk, final_cal, plan

# -----------------------------
# Sample Patient
# -----------------------------
# Preg, Glucose, BP, Skin, Insulin, BMI, DPF, Age
patient = [6, 160, 95, 35, 210, 34.5, 0.7, 52]

prob, risk, calories, plan = analyze_patient(patient)

# -----------------------------
# Output
# -----------------------------
print("\n🩺 Health Report")
print("---------------------")
print(f"Diabetes Probability : {prob:.2f}")
print(f"Risk Level           : {risk}")
print(f"Daily Calories       : {calories} kcal")

print("\n🍽️ Diet Recommendation")
for k, v in plan.items():
    print(f"{k}: {v}")
