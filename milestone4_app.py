import streamlit as st
from milestone_utils import predict_diabetes, extract_rules, generate_weekly_plan, ocr_extract_text
import io
import json

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="AI-Weekly Diet Planner", layout="wide", initial_sidebar_state="expanded")

st.title("🩺 AI-Weekly Diet Planner")

#Sidebar Inputs
st.sidebar.header("👤 Your Health Metrics")

gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
age = st.sidebar.number_input("Age", 1, 120, 30)
glucose = st.sidebar.number_input("Glucose (mg/dL)", 40, 500, 100)
bmi = st.sidebar.number_input("BMI", 10.0, 60.0, 25.0)
blood_pressure = st.sidebar.number_input("Blood Pressure (mmHg)", 40, 200, 70)
insulin = st.sidebar.number_input("Insulin (μIU/mL)", 0, 900, 80)
dpf = st.sidebar.number_input("Diabetes Pedigree Function (DPF)", 0.0, 2.5, 0.47)
pregnancies = st.sidebar.number_input("Pregnancies", 0, 20, 0) if gender == "Female" else 0

input_features = {
    "Pregnancies": pregnancies,
    "Glucose": glucose,
    "BloodPressure": blood_pressure,
    "SkinThickness": 20,
    "Insulin": insulin,
    "BMI": bmi,
    "DPF": dpf,
    "Age": age
}

#Health Alerts
st.header("Health Alerts")
diabetic_status = 0

if glucose >= 126:
    st.error("❌ High Glucose (Diabetic Range)")
    diabetic_status = 2
elif glucose >= 100:
    st.warning("⚠️ Elevated Glucose (Pre-diabetic Range)")
    diabetic_status = 1
else:
    st.success("✅ Glucose Normal")

if bmi >= 30:
    st.error("❌ Obesity Detected")
elif bmi >= 25:
    st.warning("⚠️ Overweight")
else:
    st.success("✅ BMI Normal")

if blood_pressure >= 90:
    st.error("❌ High Blood Pressure")
else:
    st.success("✅ Blood Pressure Normal")

#ML Prediction
if st.button("Predict Diabetes"):
    ml_pred = predict_diabetes(input_features)
    st.info(f"ML Model Prediction: {'Diabetic' if ml_pred else 'Non-diabetic'}")

#Prescription Input
st.header("Step 2: Prescription Text / Upload")

prescription_text = st.text_area("Paste prescription text")
uploaded_file = st.file_uploader("Upload prescription image (optional)", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    extracted_text = ocr_extract_text(uploaded_file)
    prescription_text += " " + extracted_text
    st.success("✅ Prescription image processed successfully.")

#Generate Diet Plan
st.header("Step 3: Generate Weekly Diet Plan")

if st.button("Generate Diet Plan"):

    if not prescription_text.strip():
        st.warning("Please paste text or upload a prescription.")

    else:
        rules = extract_rules(prescription_text)

        if not rules:
            st.warning("⚠️ No diet rules detected from prescription.")

        else:
            weekly_plan = generate_weekly_plan(rules, diabetic_status)

            st.subheader("📅 Weekly Diet Plan (Sunday → Saturday)")

            for day, meals in weekly_plan.items():
                with st.expander(day):
                    for meal, items in meals.items():
                        st.write(f"**{meal}:** {', '.join(items)}")

            #JSON Download
            json_buffer = io.StringIO()
            json.dump(weekly_plan, json_buffer, indent=4)

            st.download_button(
                "📄 Download JSON",
                json_buffer.getvalue(),
                "weekly_diet_plan.json"
            )

            #PDF Export
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer)

            elements = []

            title_style = ParagraphStyle(name="Title", fontSize=18, spaceAfter=20, alignment=1)
            day_style = ParagraphStyle(name="Day", fontSize=14, spaceAfter=10)
            cell_style = ParagraphStyle(name="Cell", fontSize=10, leading=14)

            elements.append(Paragraph("<b>AI-Weekly Diet Plan</b>", title_style))
            elements.append(Spacer(1, 12))

            for day, meals in weekly_plan.items():

                elements.append(Paragraph(f"<b>{day}</b>", day_style))
                elements.append(Spacer(1, 6))

                table_data = [
                    ["Meal", "Food Items"],
                    ["Morning", Paragraph(", ".join(meals["Morning"]), cell_style)],
                    ["Lunch", Paragraph(", ".join(meals["Lunch"]), cell_style)],
                    ["Evening", Paragraph(", ".join(meals["Evening"]), cell_style)],
                    ["Night", Paragraph(", ".join(meals["Night"]), cell_style)],
                ]

                table = Table(table_data, colWidths=[100, 380], repeatRows=1)

                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('PADDING', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))

                elements.append(table)
                elements.append(Spacer(1, 18))  

            doc.build(elements)

            pdf_buffer.seek(0)

            st.download_button(
                "📄 Download PDF",
                pdf_buffer,
                "weekly_diet_plan.pdf"
            )
