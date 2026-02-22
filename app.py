import streamlit as st
from PIL import Image
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import ListFlowable
from reportlab.platypus import ListItem
from reportlab.platypus import KeepTogether
from reportlab.platypus import PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import HRFlowable
from reportlab.platypus import FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageTemplate
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import Flowable
from reportlab.platypus import XPreformatted
from reportlab.platypus import Preformatted
from reportlab.platypus import CondPageBreak
from reportlab.platypus import BalancedColumns
from PIL import Image as PILImage
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="AI-NutriCare", layout="wide")

st.title("🥗 AI-NutriCare: Personalized Diet Plan Generator")

# ----------------------------
# IMAGE UPLOAD
# ----------------------------
st.subheader("Upload Medical Report Image")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = PILImage.open(uploaded_file)
    st.image(image, caption="Uploaded Medical Report", use_column_width=True)

# ----------------------------
# USER INPUT
# ----------------------------
st.subheader("Enter Health Details")

name = st.text_input("Name")
age = st.number_input("Age", min_value=1, max_value=100)
height = st.number_input("Height (in meters)", min_value=1.0, max_value=2.5)
weight = st.number_input("Weight (in kg)", min_value=30.0, max_value=200.0)
sugar = st.number_input("Blood Sugar Level (mg/dL)")
cholesterol = st.number_input("Cholesterol Level (mg/dL)")
preference = st.selectbox("Food Preference", ["Vegetarian", "Non-Vegetarian"])

# ----------------------------
# BMI CALCULATION
# ----------------------------
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

# ----------------------------
# DIET GENERATION LOGIC
# ----------------------------
def generate_diet(bmi, sugar, cholesterol, preference):
    diet = {}

    # Breakfast
    if sugar > 140:
        diet["Breakfast"] = "Oatmeal with skim milk, boiled eggs"
    else:
        diet["Breakfast"] = "Vegetable sandwich, green tea"

    # Lunch
    if cholesterol > 200:
        diet["Lunch"] = "Grilled chicken salad with olive oil" if preference == "Non-Vegetarian" else "Quinoa salad with legumes"
    else:
        diet["Lunch"] = "Brown rice with dal and vegetables"

    # Dinner
    if bmi > 25:
        diet["Dinner"] = "Grilled vegetables with paneer/tofu"
    else:
        diet["Dinner"] = "Chapati with vegetable curry"

    return diet

# ----------------------------
# GENERATE BUTTON
# ----------------------------
if st.button("Generate Diet Plan"):

    bmi = calculate_bmi(weight, height)
    diet_plan = generate_diet(bmi, sugar, cholesterol, preference)

    st.success(f"Your BMI is {bmi}")

    st.subheader("Personalized Diet Plan")
    for meal, item in diet_plan.items():
        st.write(f"**{meal}:** {item}")

    # ----------------------------
    # DOWNLOAD JSON
    # ----------------------------
    json_data = {
        "Name": name,
        "Age": age,
        "BMI": bmi,
        "Sugar Level": sugar,
        "Cholesterol": cholesterol,
        "Diet Plan": diet_plan
    }

    st.download_button(
        label="Download as JSON",
        data=json.dumps(json_data, indent=4),
        file_name="diet_plan.json",
        mime="application/json"
    )

    # ----------------------------
    # CREATE PDF
    # ----------------------------
    pdf_filename = "diet_plan.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("AI-NutriCare Personalized Diet Plan", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"Name: {name}", styles["Normal"]))
    elements.append(Paragraph(f"Age: {age}", styles["Normal"]))
    elements.append(Paragraph(f"BMI: {bmi}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    for meal, item in diet_plan.items():
        elements.append(Paragraph(f"{meal}: {item}", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)

    with open(pdf_filename, "rb") as f:
        st.download_button(
            label="Download as PDF",
            data=f,
            file_name="diet_plan.pdf",
            mime="application/pdf"
        )