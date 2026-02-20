import easyocr
from PIL import Image
import numpy as np
from src.model_loader import load_model
from src.gpt_diet import generate_7_day_diet
import numpy as np
import streamlit as st
import re

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
import tempfile

def create_pdf(diet_text):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name)
    styles = getSampleStyleSheet()
    elements = []

    for line in diet_text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return temp_file.name


model = load_model()

def extract_text_from_image(uploaded_file):
    reader = easyocr.Reader(['en'], gpu=False)
    image = Image.open(uploaded_file)
    image_np = np.array(image)
    results = reader.readtext(image_np)

    extracted_text = ""
    for (bbox, text, prob) in results:
        extracted_text += text + " "

    return extracted_text


def extract_values_from_text(text):
    # Default values (demo safe defaults)
    pregnancies = 0
    skin_thickness = 20
    insulin = 80
    dpf = 0.5
    age = 45
    bmi = 28.0
    glucose = 120
    blood_pressure = 80

    # Extract Glucose
    glucose_match = re.search(r'glucose[:\s]*([\d.]+)', text, re.IGNORECASE)
    if glucose_match:
        glucose = float(glucose_match.group(1))

    # Extract Blood Pressure (take systolic value only)
    bp_match = re.search(r'blood pressure[:\s]*([\d]+)', text, re.IGNORECASE)
    if bp_match:
        blood_pressure = float(bp_match.group(1))

    # Extract BMI
    bmi_match = re.search(r'bmi[:\s]*([\d.]+)', text, re.IGNORECASE)
    if bmi_match:
        bmi = float(bmi_match.group(1))

    # Extract Age
    age_match = re.search(r'age[:\s]*([\d.]+)', text, re.IGNORECASE)
    if age_match:
        age = float(age_match.group(1))

    return np.array([[pregnancies,
                      glucose,
                      blood_pressure,
                      skin_thickness,
                      insulin,
                      bmi,
                      dpf,
                      age]])


st.set_page_config(page_title="AI Diet Planner", layout="wide")
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #F8FAFC;
}

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
}

.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    height: 3.2em;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #1E40AF;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; font-size:42px;'>
AI-Powered Diabetes Diet Planner
</h1>
<p style='text-align: center; font-size:20px; color:#475569; margin-top:-10px;'>
Upload your prescription or enter health metrics to generate a personalized 7-day clinical diet plan.
</p>
""", unsafe_allow_html=True)
st.divider()

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Prescription (Image)",
            type=["png", "jpg", "jpeg"]
        )

    with col2:
        manual_text = st.text_area(
            "Or Enter Health Metrics Manually",
            height=150
        )

    st.markdown("<br>", unsafe_allow_html=True)
    generate = st.button("Generate Diet Plan", use_container_width=True)

if generate:

    if uploaded_file is None and manual_text.strip() == "":
        st.warning("Please upload a prescription image or paste medical values.")
        st.stop()

    st.info("Processing...")

    if uploaded_file is not None:
        extracted_text = extract_text_from_image(uploaded_file)
        model_input = extract_values_from_text(extracted_text)
    else:
        model_input = extract_values_from_text(manual_text)

    prediction = model.predict(model_input)

    if prediction[0] == 1:
        risk_level = "High Risk"
        risk_color = "#DC2626"
        risk_bg = "#FEE2E2"
    else:
        risk_level = "Low Risk"
        risk_color = "#065F46"
        risk_bg = "#D1FAE5"

    st.markdown(f"""
    <div style="
    background-color:{risk_bg};
    padding:20px;
    border-radius:16px;
    text-align:center;
    font-size:20px;
    font-weight:600;
    color:{risk_color};
    box-shadow: 0px 4px 14px rgba(0,0,0,0.05);">
    Diabetes Risk Assessment: {risk_level}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    glucose = model_input[0][1]
    bp = model_input[0][2]
    bmi = model_input[0][5]

    diet_plan = generate_7_day_diet(glucose, bp, bmi)
    # Split explanation from diet
    parts = diet_plan.split("Why This Diet Was Chosen")

    main_content = parts[0]
    explanation = parts[1] if len(parts) > 1 else ""

    # Split days
    days = main_content.split("Day ")

    st.subheader("7-Day Personalized Diet Plan")
    st.markdown(days[0])

    for day in days[1:]:
        day_number = day.split(":")[0].strip()
        day_content = day.split(":", 1)[1]

        formatted_day_content = day_content.replace("\n", "<br>")

        with st.container():
            card_html = f"""
                <div style="
                background-color:rgb(38 73 144);
                padding:20px;
                border-radius:14px;
                border:1px solid #E5E7EB;
                margin-bottom:20px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
                <h4>Day {day_number}</h4>
                {formatted_day_content}
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    
    if explanation.strip():
        st.markdown("### 📌 Why This Diet Was Chosen")
        st.markdown(explanation.strip())

    if glucose > 180:
        st.write("- Reduced simple carbohydrates to help control high blood sugar levels.")

    if bp > 140:
        st.write("- Limited sodium intake to support blood pressure management.")

    if bmi > 30:
        st.write("- Included calorie-controlled meals to promote healthy weight reduction.")

    if glucose <= 180 and bp <= 140 and bmi <= 30:
        st.write("- Balanced macronutrient distribution for preventive health maintenance.")


    pdf_file = create_pdf(diet_plan)

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download Diet Plan as PDF",
            data=f,
            file_name="7_day_diet_plan.pdf",
            mime="application/pdf"
        )
