import streamlit as st
import easyocr
import re
import random
import pandas as pd
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AI NutriCare", layout="wide")
st.title("🥗 AI NutriCare - Intelligent Diet Recommendation System")

# ======================================================
# OCR EXTRACTION
# ======================================================
def extract_value(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        nums = re.findall(r"\d+\.?\d*", match.group())
        if nums:
            return float(nums[-1])
    return None

uploaded_file = st.file_uploader("Upload Lab Report Image", type=["png","jpg","jpeg"])

glucose = cholesterol = bp = bmi = insulin = None

if uploaded_file:
    with open("temp.png", "wb") as f:
        f.write(uploaded_file.getbuffer())

    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext("temp.png")
    ocr_text = " ".join([text for _, text, _ in results])

    glucose = extract_value(r'(GLUCOSE|FBS|FASTING BLOOD SUGAR).*?\d+', ocr_text)
    cholesterol = extract_value(r'(TOTAL CHOLESTEROL|CHOLESTEROL).*?\d+', ocr_text)
    bp = extract_value(r'(BLOOD PRESSURE|BP).*?\d+', ocr_text)
    bmi = extract_value(r'(BMI).*?\d+', ocr_text)
    insulin = extract_value(r'(INSULIN).*?\d+', ocr_text)

    st.success("Report analyzed successfully. Values auto-filled.")

# ======================================================
# SIDEBAR VALUES
# ======================================================
st.sidebar.header("Health Metrics")

glucose = st.sidebar.number_input("Glucose", value=float(glucose) if glucose else 110.0)
cholesterol = st.sidebar.number_input("Cholesterol", value=float(cholesterol) if cholesterol else 180.0)
bp = st.sidebar.number_input("Blood Pressure", value=float(bp) if bp else 120.0)
bmi = st.sidebar.number_input("BMI", value=float(bmi) if bmi else 24.0)

# ======================================================
# HEALTH STATUS
# ======================================================
def diabetes_status(val):
    if val >= 126:
        return "🔴 High Diabetes"
    elif 100 <= val <= 125:
        return "🟡 Pre-Diabetic"
    return "🟢 Normal"

def cholesterol_status(val):
    if val >= 240:
        return "🔴 High Cholesterol"
    elif 200 <= val <= 239:
        return "🟡 Borderline"
    return "🟢 Normal"

def bp_status(val):
    if val >= 140:
        return "🔴 High BP"
    elif 120 <= val < 140:
        return "🟡 Elevated"
    return "🟢 Normal"

def bmi_status(val):
    if val >= 30:
        return "🔴 Obese"
    elif 25 <= val < 30:
        return "🟡 Overweight"
    return "🟢 Normal"

# ======================================================
# DIET DATABASE
# ======================================================
diet_db = {
    "Recommended": [
        "Oats", "Brown Rice", "Multigrain Chapati",
        "Sprouts", "Green Vegetables",
        "Grilled Paneer", "Boiled Eggs",
        "Quinoa", "Dal", "Salad Bowl",
        "Fruit Bowl", "Nuts", "Green Tea"
    ],
    "Avoid": [
        "Sugar", "White Rice", "Fried Foods",
        "Soft Drinks", "Extra Salt",
        "Processed Food", "Butter",
        "Red Meat", "Bakery Items"
    ],
    "Meals": {
        "Breakfast": [
            "Oats with chia", "Moong dal chilla", "Vegetable omelette",
            "Upma", "Sprouts salad", "Multigrain toast",
            "Idli", "Poha", "Fruit smoothie"
        ],
        "Lunch": [
            "Brown rice + dal", "Chapati + sabzi",
            "Grilled chicken + salad", "Quinoa bowl",
            "Vegetable khichdi", "Tofu curry"
        ],
        "Snacks": [
            "Almonds", "Roasted chana", "Apple slices",
            "Boiled corn", "Walnuts", "Green tea"
        ],
        "Dinner": [
            "Lentil soup", "Vegetable stir fry",
            "Grilled paneer", "Clear soup"
        ]
    }
}

# ======================================================
# GENERATE PLAN
# ======================================================
if st.button("Generate Diet Plan"):

    st.subheader("🩺 Health Status")
    st.write("Diabetes:", diabetes_status(glucose))
    st.write("Cholesterol:", cholesterol_status(cholesterol))
    st.write("Blood Pressure:", bp_status(bp))
    st.write("BMI:", bmi_status(bmi))

    st.subheader("🥦 Main Recommended Foods")
    for item in diet_db["Recommended"]:
        st.success(item)

    st.subheader("⚠ Foods To Avoid")
    for item in diet_db["Avoid"]:
        st.warning(item)

    st.subheader("📅 7-Day Personalized Weekly Plan")

    meals = diet_db["Meals"]
    for meal in meals:
        random.shuffle(meals[meal])

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    week_data = []

    for i, day in enumerate(days):
        week_data.append({
            "Day": day,
            "Breakfast": meals["Breakfast"][i % len(meals["Breakfast"])],
            "Lunch": meals["Lunch"][i % len(meals["Lunch"])],
            "Snacks": meals["Snacks"][i % len(meals["Snacks"])],
            "Dinner": meals["Dinner"][i % len(meals["Dinner"])]
        })

    df = pd.DataFrame(week_data)
    st.table(df)

    # JSON Export
    json_data = df.to_json(orient="records")
    st.download_button("Download Weekly Plan (JSON)",
                       data=json_data,
                       file_name="weekly_plan.json",
                       mime="application/json")

    # PDF Export
    doc = SimpleDocTemplate("diet_plan.pdf")
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("AI NutriCare Weekly Diet Plan", styles['Title']))
    elements.append(Spacer(1, 12))

    for _, row in df.iterrows():
        elements.append(Paragraph(
            f"{row['Day']} - {row['Breakfast']}, {row['Lunch']}, "
            f"{row['Snacks']}, {row['Dinner']}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 8))

    doc.build(elements)

    with open("diet_plan.pdf", "rb") as f:
        st.download_button("Download Weekly Plan (PDF)",
                           data=f,
                           file_name="weekly_plan.pdf",
                           mime="application/pdf")
