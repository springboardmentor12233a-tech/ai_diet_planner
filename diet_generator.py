# diet_generator.py

# -----------------------------
# Risk Level Logic
# -----------------------------
def health_alert(glucose, bmi):

    if glucose > 180 or bmi > 30:
        return "Critical Risk"

    elif glucose > 140 or bmi > 25:
        return "Moderate Risk"

    else:
        return "Low Risk"


# -----------------------------
# Calories from BMI
# -----------------------------
def bmi_calories(bmi):

    if bmi >= 30:
        return 1500
    elif bmi >= 25:
        return 1800
    else:
        return 2200


# -----------------------------
# Weekly Diet Generator
# -----------------------------
def generate_weekly_diet(calories):

    return {
        "Monday": {
            "Breakfast": "Oats (1 bowl) + Milk (1 glass)",
            "Lunch": "Brown rice (1 cup) + Dal + Vegetables",
            "Dinner": "Soup + Salad"
        },
        "Tuesday": {
            "Breakfast": "Idli (3) + Sambar",
            "Lunch": "Chapati (2) + Vegetable curry",
            "Dinner": "Grilled vegetables"
        },
        "Wednesday": {
            "Breakfast": "Poha (1 bowl)",
            "Lunch": "Rice + Dal + Salad",
            "Dinner": "Fruit bowl"
        },
        "Thursday": {
            "Breakfast": "Upma (1 bowl)",
            "Lunch": "Chapati + Paneer curry",
            "Dinner": "Vegetable soup"
        },
        "Friday": {
            "Breakfast": "Boiled eggs (2) + Toast",
            "Lunch": "Brown rice + Dal",
            "Dinner": "Salad"
        },
        "Saturday": {
            "Breakfast": "Dosa (2)",
            "Lunch": "Chapati + Vegetables",
            "Dinner": "Soup"
        },
        "Sunday": {
            "Breakfast": "Fruit smoothie",
            "Lunch": "Light home food",
            "Dinner": "Salad"
        }
    }


# -----------------------------
# MAIN FUNCTION (IMPORTANT)
# This is what app.py imports
# -----------------------------
def generate_diet_plan(glucose, bmi):

    risk = health_alert(glucose, bmi)
    calories = bmi_calories(bmi)
    weekly_plan = generate_weekly_diet(calories)

    return {
        "risk_level": risk,
        "daily_calories": calories,
        "Diet Plan": weekly_plan
    }


# -----------------------------
# Test Run
# -----------------------------
if __name__ == "__main__":
    result = generate_diet_plan(150, 28)
    print(result)
