import streamlit as st
import pytesseract
from PIL import Image
import re
from fpdf import FPDF
import json

# ----------------------------
# CONFIGURATION
# ----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
st.set_page_config(page_title="AI Health Challenge", layout="wide")

# ----------------------------
# CUSTOM CSS
# ----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #dfe9f3, #ffffff);
}

.main-title {
    font-size:40px;
    font-weight:bold;
    text-align:center;
    color:#154360;
}

.section-title {
    font-size:24px;
    font-weight:bold;
    margin-top:20px;
    color:#1B4F72;
}

.high-risk {
    background-color:#FADBD8;
    padding:12px;
    border-radius:12px;
    color:#922B21;
    font-weight:bold;
}

.normal-risk {
    background-color:#D5F5E3;
    padding:12px;
    border-radius:12px;
    color:#196F3D;
    font-weight:bold;
}

.small-image {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 300px;
    border-radius: 15px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.15);
}

.stButton>button {
    background-color:#1ABC9C;
    color:white;
    border-radius:10px;
    font-weight:bold;
}

.stDownloadButton>button {
    background-color:#5DADE2;
    color:white;
    border-radius:10px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎮 AI Health Challenge Dashboard</div>', unsafe_allow_html=True)

# ----------------------------
# SIDEBAR - PROFILE
# ----------------------------
st.sidebar.header("🧍 Personal Profile")

gender = st.sidebar.selectbox("Select Gender", ["Male", "Female", "Other"])
age = st.sidebar.slider("Select Age", 10, 80, 25)
serious = st.sidebar.radio("Are you serious about following diet?",
                           ["Yes 💪", "Maybe 🤔", "No 😅"])
water = st.sidebar.slider("Daily Water Intake (Litres)", 1, 5, 2)

st.sidebar.markdown("---")
st.sidebar.header("📤 Upload Medical Report")
uploaded_file = st.sidebar.file_uploader("Upload Image", type=["png","jpg","jpeg"])

# ----------------------------
# FUNCTIONS
# ----------------------------

def extract_values(text):
    glucose = re.search(r'Glucose.*?(\d+)', text, re.IGNORECASE)
    cholesterol = re.search(r'Cholesterol.*?(\d+)', text, re.IGNORECASE)
    hemoglobin = re.search(r'Hemoglobin.*?(\d+\.?\d*)', text, re.IGNORECASE)

    return {
        "glucose": int(glucose.group(1)) if glucose else 0,
        "cholesterol": int(cholesterol.group(1)) if cholesterol else 0,
        "hemoglobin": float(hemoglobin.group(1)) if hemoglobin else 0
    }

def analyze_health(values):
    return {
        "Diabetes": "High" if values["glucose"] > 140 else "Normal",
        "Cholesterol": "High" if values["cholesterol"] > 200 else "Normal",
        "Anemia": "High" if values["hemoglobin"] < 12 else "Normal"
    }

def generate_diet(risks):
    diet = {
        "Monday": {"Breakfast": "Oats + Almonds + Banana",
                   "Lunch": "Brown Rice + Rajma + Spinach + Curd",
                   "Dinner": "Grilled Paneer/Chicken + Veg Salad"},
        "Tuesday": {"Breakfast": "Boiled Eggs/Sprouts + Orange",
                    "Lunch": "Millet Roti + Mixed Veg + Dal",
                    "Dinner": "Vegetable Soup + Multigrain Chapati"},
        "Wednesday": {"Breakfast": "Milk Smoothie + Peanut Butter",
                      "Lunch": "Quinoa + Chickpea Curry + Salad",
                      "Dinner": "Palak Dal + Brown Rice"},
        "Thursday": {"Breakfast": "Vegetable Upma + Nuts",
                     "Lunch": "Grilled Fish/Tofu + Steamed Veggies",
                     "Dinner": "Vegetable Khichdi + Salad"},
        "Friday": {"Breakfast": "Whole Wheat Toast + Peanut Butter + Apple",
                   "Lunch": "Chole + Brown Rice + Salad",
                   "Dinner": "Stir Fry Veg + Roti + Yogurt"},
        "Saturday": {"Breakfast": "Idli + Sambar",
                     "Lunch": "Paneer/Chicken Tikka + Dal + Salad",
                     "Dinner": "Tomato Soup + Chapati + Beetroot"},
        "Sunday": {"Breakfast": "Fruit Bowl + Greek Yogurt + Seeds",
                   "Lunch": "Veg Pulao + Raita + Lentil Soup",
                   "Dinner": "Light Salad + Moong Dal Soup"}
    }

    if risks["Diabetes"] == "High":
        for day in diet:
            diet[day]["Breakfast"] = "Millets/Oats + Nuts (Low GI)"

    if risks["Cholesterol"] == "High":
        for day in diet:
            diet[day]["Lunch"] = "Brown Rice + Steamed Veggies + Dal (Low Fat)"

    if risks["Anemia"] == "High":
        for day in diet:
            diet[day]["Dinner"] = "Spinach + Beetroot + Lentils (Iron Rich)"

    return diet

def calculate_score(risks):
    score = 100
    for value in risks.values():
        if value == "High":
            score -= 20
    if serious == "No 😅":
        score -= 10
    if water < 2:
        score -= 10
    return max(score, 0)

def create_pdf(diet):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "7-Day Personalized Diet Plan", ln=True)
    pdf.ln(5)

    for day, meals in diet.items():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(200, 8, day, ln=True)
        pdf.set_font("Arial", size=10)
        for meal, food in meals.items():
            pdf.cell(200, 8, f"{meal}: {food}", ln=True)
        pdf.ln(3)

    return pdf.output(dest="S").encode("latin-1")

# ----------------------------
# MAIN APP
# ----------------------------

if uploaded_file:
    image = Image.open(uploaded_file)

    # SMALL CENTERED IMAGE
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    st.image(image, caption="Uploaded Report", width=300)
    st.markdown('</div>', unsafe_allow_html=True)

    text = pytesseract.image_to_string(image)
    values = extract_values(text)
    risks = analyze_health(values)
    diet_plan = generate_diet(risks)

    # LAB VALUES
    st.markdown('<div class="section-title">📊 Extracted Lab Values</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Glucose (mg/dL)", values["glucose"])
    col2.metric("Cholesterol (mg/dL)", values["cholesterol"])
    col3.metric("Hemoglobin (g/dL)", values["hemoglobin"])

    # RISK
    st.markdown('<div class="section-title">⚠ Risk Analysis</div>', unsafe_allow_html=True)
    for risk, status in risks.items():
        if status == "High":
            st.markdown(f'<div class="high-risk">{risk}: HIGH RISK 🚨</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="normal-risk">{risk}: NORMAL ✅</div>', unsafe_allow_html=True)

    # SCORE
    st.markdown('<div class="section-title">🏆 Health Score</div>', unsafe_allow_html=True)
    score = calculate_score(risks)
    st.progress(score/100)
    st.write(f"### Your Score: {score}/100")

    # DIET
    st.markdown('<div class="section-title">🥗 7-Day Diet Plan</div>', unsafe_allow_html=True)
    for day, meals in diet_plan.items():
        with st.expander(f"📅 {day}"):
            for meal, food in meals.items():
                st.write(f"**{meal}:** {food}")

    # DOWNLOAD
    st.markdown('<div class="section-title">📥 Download Diet Plan</div>', unsafe_allow_html=True)

    pdf_data = create_pdf(diet_plan)
    st.download_button("📄 Download as PDF", pdf_data, "diet_plan.pdf", "application/pdf")

    json_data = json.dumps(diet_plan, indent=4)
    st.download_button("📂 Download as JSON", json_data, "diet_plan.json", "application/json")

else:
    st.info("👈 Upload medical report from sidebar to start!")
