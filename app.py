# app.py

import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import json

from src.health_alerts import get_health_alerts
from src.rule_mapper import alerts_to_diet_rules
from src.diet_generator import generate_weekly_plan
from src.model_predictor import predict_diabetes

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AI-ML Diet Planner", layout="wide")

st.title("🥗 AI-ML Based Personalized Diet Plan Generator")
st.caption("Medical Report Analysis | Predictive Risk Modeling | Nutritional Planning")
st.markdown("---")

reader = easyocr.Reader(['en'], gpu=False)


# -------------------------------------------------
# OCR VALUE EXTRACTION
# -------------------------------------------------
def extract_values_from_text(text):
    glucose = None
    bmi = None
    bp = None

    glucose_match = re.search(r'glucose[^0-9]*([\d.]+)', text, re.IGNORECASE)
    bmi_match = re.search(r'bmi[^0-9]*([\d.]+)', text, re.IGNORECASE)
    bp_match = re.search(r'(blood pressure|bp)[^0-9]*([\d.]+)', text, re.IGNORECASE)

    if glucose_match:
        glucose = float(glucose_match.group(1))
    if bmi_match:
        bmi = float(bmi_match.group(1))
    if bp_match:
        bp = float(bp_match.group(2))

    return glucose, bmi, bp


# -------------------------------------------------
# INSIGHT GENERATOR
# -------------------------------------------------
def generate_insights(alerts, strictness):
    insights = []

    for metric, status, message in alerts:
        if status != "Normal":
            insights.append(f"{metric}: {message}")

    insights.append(
        f"Dietary strictness classified as {strictness} based on combined ML prediction and clinical evaluation."
    )

    return insights


# -------------------------------------------------
# PDF CREATOR
# -------------------------------------------------
def create_pdf(weekly_plan, glucose, bmi, bp, risk_level, probability, strictness):

    filename = "Personalized_Diet_Plan.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>AI-ML Personalized Diet Plan Report</b>", styles['Title']))
    elements.append(Spacer(1, 15))

    summary_data = [
        ["Glucose (mg/dL)", str(glucose)],
        ["BMI", str(bmi)],
        ["Blood Pressure (mm Hg)", str(bp)],
        ["Diabetes Risk Level", risk_level],
        ["Risk Probability", f"{probability:.2f}"],
        ["Diet Strictness Level", strictness]
    ]

    table = Table(summary_data, colWidths=[220, 220])
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>7-Day Nutritional Plan</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    for day, meals in weekly_plan.items():
        elements.append(Paragraph(f"<b>{day}</b>", styles['Heading3']))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(f"Morning Meal: {meals['Breakfast']}", styles['Normal']))
        elements.append(Paragraph(f"Midday Meal: {meals['Lunch']}", styles['Normal']))
        elements.append(Paragraph(f"Evening Meal: {meals['Dinner']}", styles['Normal']))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return filename


# -------------------------------------------------
# UPLOAD SECTION
# -------------------------------------------------
st.subheader("Upload Medical Report (Optional)")

uploaded_file = st.file_uploader(
    "Upload Report Image (PNG/JPG/JPEG)",
    type=["png", "jpg", "jpeg"]
)

auto_glucose = None
auto_bmi = None
auto_bp = None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Report", width=350)

    results = reader.readtext(np.array(image))
    extracted_text = " ".join([res[1] for res in results])

    with st.expander("View Extracted Text"):
        st.write(extracted_text)

    auto_glucose, auto_bmi, auto_bp = extract_values_from_text(extracted_text)

st.markdown("---")


# -------------------------------------------------
# MANUAL INPUT
# -------------------------------------------------
st.subheader("Enter / Confirm Health Parameters")

col1, col2, col3 = st.columns(3)

glucose = col1.number_input("Glucose (mg/dL)", min_value=0.0, value=float(auto_glucose) if auto_glucose else 0.0)
bmi = col2.number_input("BMI", min_value=0.0, value=float(auto_bmi) if auto_bmi else 0.0)
bp = col3.number_input("Diastolic Blood Pressure (mm Hg)", min_value=0.0, value=float(auto_bp) if auto_bp else 0.0)

st.markdown("---")


# -------------------------------------------------
# GENERATE BUTTON
# -------------------------------------------------
if st.button("Generate Personalized Plan"):

    patient_data = {
        "Glucose": glucose,
        "BMI": bmi,
        "BloodPressure": bp
    }

    alerts = get_health_alerts(patient_data)
    diet_rules = alerts_to_diet_rules(alerts)

    sample_input = [2, glucose, bp, 20, 80, bmi, 0.5, 30]
    prediction, probability = predict_diabetes(sample_input)

    # ---------------- HYBRID STRICTNESS LOGIC ----------------

    if probability >= 0.7:
        strictness = "High"
    elif probability >= 0.4:
        strictness = "Moderate"
    else:
        strictness = "Low"

    # Upgrade strictness if clinical alerts are severe
    for metric, status, message in alerts:
        if status == "Critical":
            strictness = "High"
            break
        elif status == "Warning" and strictness == "Low":
            strictness = "Moderate"

    # ----------------------------------------------------------

    weekly_plan = generate_weekly_plan(diet_rules, strictness)
    insights = generate_insights(alerts, strictness)

    st.session_state.generated = True
    st.session_state.alerts = alerts
    st.session_state.prediction = prediction
    st.session_state.probability = probability
    st.session_state.strictness = strictness
    st.session_state.weekly_plan = weekly_plan
    st.session_state.insights = insights
    st.session_state.current_day_index = 0


# -------------------------------------------------
# DISPLAY RESULTS
# -------------------------------------------------
if "generated" in st.session_state and st.session_state.generated:

    alerts = st.session_state.alerts
    prediction = st.session_state.prediction
    probability = st.session_state.probability
    strictness = st.session_state.strictness
    weekly_plan = st.session_state.weekly_plan
    insights = st.session_state.insights

    day_keys = list(weekly_plan.keys())

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Health Review", "Risk Assessment", "Clinical Insights", "Diet Plan", "Download"]
    )

    with tab1:
        st.subheader("Clinical Health Evaluation")
        for metric, status, message in alerts:
            if status == "Critical":
                st.error(f"{metric}: {message}")
            elif status == "Warning":
                st.warning(f"{metric}: {message}")
            else:
                st.success(f"{metric}: {message}")

    with tab2:
        st.subheader("Predictive Risk Assessment")
        st.write(f"Predicted Diabetes Risk Level: {'High' if prediction == 1 else 'Low'}")
        st.write(f"Model Probability Score: {probability:.2f}")
        st.write(f"Diet Strictness Level: {strictness}")

    with tab3:
        st.subheader("Clinical Insight Summary")
        for insight in insights:
            st.write("•", insight)

    with tab4:
        st.subheader("7-Day Nutritional Plan")

        col_prev, col_mid, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("⬅ Previous"):
                if st.session_state.current_day_index > 0:
                    st.session_state.current_day_index -= 1

        with col_next:
            if st.button("Next ➡"):
                if st.session_state.current_day_index < len(day_keys) - 1:
                    st.session_state.current_day_index += 1

        current_day = day_keys[st.session_state.current_day_index]
        meals = weekly_plan[current_day]

        st.markdown("---")
        st.write(f"### {current_day}")
        st.write(f"Morning Meal: {meals['Breakfast']}")
        st.write(f"Midday Meal: {meals['Lunch']}")
        st.write(f"Evening Meal: {meals['Dinner']}")

    with tab5:
        st.subheader("Export Report")

        pdf_file = create_pdf(
            weekly_plan,
            glucose,
            bmi,
            bp,
            "High" if prediction == 1 else "Low",
            probability,
            strictness
        )

        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name="Personalized_Diet_Plan.pdf",
                mime="application/pdf"
            )

        report_data = {
            "glucose": glucose,
            "bmi": bmi,
            "blood_pressure": bp,
            "risk_level": "High" if prediction == 1 else "Low",
            "probability": probability,
            "strictness": strictness,
            "weekly_plan": weekly_plan
        }

        json_data = json.dumps(report_data, indent=4)

        st.download_button(
            label="Download JSON Report",
            data=json_data,
            file_name="Personalized_Diet_Plan.json",
            mime="application/json"
        )

    st.markdown("---")
    st.caption("Generated using OCR-based extraction, machine learning risk prediction, and rule-based dietary modeling.")