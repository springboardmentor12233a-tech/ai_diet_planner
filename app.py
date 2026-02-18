
import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import base64
import os
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(page_title="AI Diet Plan Generator", layout="wide", initial_sidebar_state="collapsed")

# ── IMAGE LOADING ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_img_b64(filename):
    for p in [os.path.join(SCRIPT_DIR, filename), os.path.join(os.getcwd(), filename), filename]:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

avoid_b64 = get_img_b64("avoid_food.png")
allowed_b64 = get_img_b64("healthy_food.png")
AVOID_SRC = ("data:image/png;base64," + avoid_b64) if avoid_b64 else "https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=600&h=300&fit=crop"
ALLOWED_SRC = ("data:image/png;base64," + allowed_b64) if allowed_b64 else "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=300&fit=crop"

# ── CACHED OCR ──
@st.cache_resource(show_spinner=False)
def load_ocr():
    return easyocr.Reader(["en"], gpu=False, model_storage_directory=os.path.join(SCRIPT_DIR, ".easyocr_models"), download_enabled=True, verbose=False)

@st.cache_data(show_spinner=False)
def run_ocr(_image_bytes):
    reader = load_ocr()
    img = Image.open(io.BytesIO(_image_bytes))
    MAX_DIM = 1200
    w, h = img.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    result = reader.readtext(np.array(img), detail=0, paragraph=True)
    return " ".join(result).lower()

# ── CSS ──
CSS = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800;900&display=swap');"
    "html,body,[class*='css']{font-family:'Nunito',sans-serif;}"
    "#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}"
    "[data-testid='block-container']{padding-top:1rem;max-width:1200px;margin:auto;}"
    ".stApp{background:linear-gradient(160deg,#e8f4fd 0%,#d6eaff 40%,#e4f5ec 100%);min-height:100vh;}"
    ".hero-banner{background:linear-gradient(135deg,#1a73e8 0%,#0d9e6e 100%);"
    "border-radius:24px;padding:42px 50px 38px;margin-bottom:30px;text-align:center;"
    "box-shadow:0 12px 40px rgba(26,115,232,.3);position:relative;overflow:hidden;}"
    ".hero-emoji{font-size:3.2rem;display:block;margin-bottom:10px;}"
    ".hero-title{font-family:'Poppins',sans-serif;font-size:2.6rem;font-weight:800;color:white;margin:0 0 10px;}"
    ".hero-sub{font-size:1.05rem;color:rgba(255,255,255,.88);margin:0;}"
    ".upload-card{background:white;border-radius:20px;padding:28px 32px;box-shadow:0 6px 30px rgba(0,0,0,.08);margin-bottom:28px;}"
    ".upload-title{font-size:1.2rem;font-weight:800;color:#1a73e8;margin-bottom:4px;}"
    ".upload-hint{font-size:.88rem;color:#888;margin-bottom:12px;}"
    ".cond-wrap{text-align:center;margin:8px 0 28px;}"
    ".cond-badge{display:inline-block;background:linear-gradient(135deg,#1a73e8,#0d9e6e);"
    "color:white;padding:12px 32px;border-radius:50px;font-size:1.1rem;font-weight:700;box-shadow:0 4px 18px rgba(26,115,232,.3);}"
    ".stat-card{background:white;border-radius:18px;padding:20px 16px 16px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.07);margin-bottom:24px;}"
    ".stat-num{font-family:'Poppins';font-size:1.9rem;font-weight:800;color:#1a73e8;}"
    ".stat-lbl{font-size:.82rem;color:#666;font-weight:700;margin-top:4px;text-transform:uppercase;}"
    ".sec-title{font-family:'Poppins';font-size:1.55rem;font-weight:800;text-align:center;color:#1a2a40;margin:8px 0 22px;}"
    ".food-card{background:white;border-radius:24px;padding:0 0 24px;box-shadow:0 8px 32px rgba(0,0,0,.10);overflow:hidden;height:100%;}"
    ".fc-img{width:100%;height:200px;object-fit:cover;display:block;}"
    ".fc-body{padding:0 22px;}"
    ".fc-head{font-family:'Poppins';font-size:1.2rem;font-weight:800;text-align:center;padding:18px 0 14px;margin:0;}"
    ".avoid-head{color:#e53935;}.allowed-head{color:#1a73e8;}"
    ".food-list{list-style:none;padding:0;margin:0;}"
    ".food-list li{font-size:.97rem;font-weight:600;padding:9px 4px;border-bottom:1px solid #f3f3f3;}"
    ".food-list li:last-child{border-bottom:none;}"
    ".avoid-li{color:#c62828;}.allow-li{color:#1565c0;}"
    ".tip-card{background:linear-gradient(135deg,#fff9e6,#fff3cc);border-left:5px solid #f5a623;"
    "border-radius:14px;padding:16px 20px;margin-top:20px;margin-bottom:8px;font-size:.95rem;color:#5a3e00;font-weight:600;}"
    ".week-hdr{font-family:'Poppins';font-size:1.9rem;font-weight:900;text-align:center;"
    "color:white;background:linear-gradient(135deg,#1b4332,#40916c);padding:24px 0;"
    "border-radius:20px 20px 0 0;text-transform:uppercase;margin-top:32px;}"
    ".week-wrap{background:white;border-radius:0 0 20px 20px;overflow:hidden;box-shadow:0 12px 48px rgba(0,0,0,.12);margin-bottom:32px;}"
    ".wtbl{width:100%;border-collapse:collapse;}"
    ".wtbl thead th{background:#1b4332;color:white;font-family:'Poppins';font-size:.82rem;font-weight:700;padding:14px 8px;text-align:center;text-transform:uppercase;}"
    ".wtbl thead th.th-day{width:72px;background:#081c15;}"
    ".wtbl tbody td{padding:13px 10px;text-align:center;font-size:.84rem;color:#2d3748;border-bottom:1px solid #e8f5ee;vertical-align:top;background:white;}"
    ".wtbl tbody tr:nth-child(even) td{background:#f0faf5;}"
    ".wtbl tbody tr:hover td{background:#d8f3dc !important;}"
    ".wtbl tbody td.td-day{font-family:'Poppins';font-weight:800;color:white !important;background:#2d6a4f !important;font-size:.82rem;text-transform:uppercase;width:72px;}"
    ".wtbl tbody tr:nth-child(even) td.td-day{background:#40916c !important;}"
    ".mi{font-size:1.15rem;display:block;}"
    ".mm{font-weight:700;font-size:.85rem;color:#1b4332;display:block;}"
    ".md{font-size:.75rem;color:#52796f;margin-top:2px;display:block;}"
    ".motiv{background:linear-gradient(135deg,#2d6a4f,#52b788);color:white;border-radius:20px;padding:26px 36px;"
    "text-align:center;font-family:'Poppins';font-size:1.35rem;font-weight:800;text-transform:uppercase;margin:10px 0 20px;}"
    ".pdf-section{background:white;border-radius:20px;padding:28px 32px;box-shadow:0 6px 30px rgba(0,0,0,.08);margin:16px 0 30px;text-align:center;}"
    ".pdf-title{font-family:'Poppins';font-size:1.15rem;font-weight:700;color:#1a2a40;margin-bottom:6px;}"
    ".pdf-sub{font-size:.88rem;color:#666;margin-bottom:16px;}"
    ".ph-wrap{text-align:center;padding:60px 20px 50px;color:#5a7a9a;}"
    ".ph-icon{font-size:5rem;display:block;margin-bottom:18px;}"
    ".ph-title{font-family:'Poppins';color:#1a73e8;font-size:1.55rem;font-weight:700;margin-bottom:10px;}"
    ".ph-sub{font-size:.97rem;color:#666;max-width:480px;margin:0 auto 32px;}"
    ".chips{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;}"
    ".chip{background:white;border-radius:16px;padding:16px 20px;box-shadow:0 4px 16px rgba(0,0,0,.08);min-width:110px;}"
    ".chip-icon{font-size:1.9rem;display:block;margin-bottom:6px;}"
    ".chip-name{font-size:.8rem;color:#444;font-weight:700;}"
    "</style>"
)
st.markdown(CSS, unsafe_allow_html=True)

# ── DIET DATA ──
DIET = {
    "High Blood Pressure": {
        "emoji": "🫀", "calories": "1800-2200", "water": "2.5-3 L",
        "avoid": ["Excess Salt / Sodium", "Processed & Canned Foods", "Red & High-Fat Meats", "Saturated & Trans Fats", "Added Sugars", "Alcohol & Caffeine"],
        "allowed": ["Non-Starchy Vegetables", "Potassium-Rich Fruits", "Whole Grains", "Lean Proteins (Fish, Chicken)", "Low-Fat Dairy", "Healthy Fats (Nuts, Avocado)"],
        "tip": "Limit sodium under 2,300 mg/day. Follow DASH diet. Drink 8-10 glasses of water daily.",
        "week": {
            "Mon": [("Oatmeal + Berries", "Low-fat milk, 1 banana"), ("Brown Rice + Dal", "Spinach sabzi + salad"), ("Veg Soup + Grilled Chicken", "Steamed broccoli"), ("Walnuts + Green Tea", "1 orange")],
            "Tue": [("Egg White Omelette", "Wheat toast + apple"), ("2 Chapati + Dal", "Mixed veg curry"), ("Baked Salmon", "Green salad + lemon"), ("Fruit Salad", "Low-fat yogurt")],
            "Wed": [("Muesli + Skim Milk", "1 pear + chia seeds"), ("Quinoa Khichdi", "Raita + cucumber salad"), ("Grilled Paneer", "Stir-fried veggies"), ("Carrot Sticks", "Hummus dip")],
            "Thu": [("Banana Smoothie", "Flaxseeds + oats"), ("Chicken Rice Bowl", "Tomato soup + salad"), ("Veg Stew + Brown Rice", "Steamed green beans"), ("Blueberries + Almonds", "Herbal tea")],
            "Fri": [("Wheat Dosa + Sambar", "1 apple + green tea"), ("Tuna Salad Wrap", "Low-sodium soup"), ("Moong Dal Khichdi", "Stir-fried zucchini"), ("Apple + Peanut Butter", "Low-fat milk")],
            "Sat": [("Overnight Oats", "Berries + pumpkin seeds"), ("Chickpea Salad Bowl", "Whole grain pita"), ("Baked Chicken Tikka", "Mint chutney + salad"), ("Mixed Nuts", "1 banana")],
            "Sun": [("Veggie Upma", "Low-fat buttermilk"), ("Rajma Chawal", "Onion salad + yogurt"), ("Grilled Fish + Salad", "Vegetable soup"), ("Orange + Dates", "Herbal tea")],
        }
    },
    "Diabetes": {
        "emoji": "🩸", "calories": "1600-2000", "water": "2.5-3 L",
        "avoid": ["White Rice / Maida", "Sugary Drinks & Juices", "Sweets & Desserts", "Processed Snacks", "Deep Fried Foods", "Full-Fat Dairy"],
        "allowed": ["Leafy Green Vegetables", "Low-GI Fruits (Berries, Apple)", "Whole Grains & Millets", "Legumes & Lentils", "Lean Protein (Fish, Eggs)", "Healthy Fats (Nuts, Seeds)"],
        "tip": "Eat small frequent meals every 2-3 hours. Monitor blood sugar before meals. Never skip breakfast.",
        "week": {
            "Mon": [("Steel-Cut Oats", "Cinnamon + walnuts"), ("Methi Chapati + Dal", "Cucumber raita"), ("Baked Fish + Quinoa", "Stir-fried veggies"), ("Almonds + Herbal Tea", "1 small apple")],
            "Tue": [("Egg Bhurji (2 eggs)", "Wheat toast + tea"), ("Brown Rice + Sambar", "Mixed veg sabzi"), ("Chicken Soup + Salad", "Wheat chapati"), ("Blueberries + Seeds", "Low-fat yogurt")],
            "Wed": [("Besan Chilla", "Mint chutney + orange"), ("Grilled Chicken + Millet", "Tomato soup"), ("Paneer Bhurji", "Salad + 1 chapati"), ("Carrot Sticks + Hummus", "Herbal tea")],
            "Thu": [("Ragi Porridge", "Skimmed milk + chia"), ("Rajma + Quinoa", "Onion salad + lassi"), ("Baked Salmon", "Stir-fried spinach"), ("Walnuts + 1 Pear", "Green tea")],
            "Fri": [("Poha + Sprouts", "1 cup tea no sugar"), ("Lentil Soup + Chapati", "Cucumber salad"), ("Tofu Stir-Fry", "Brown rice + greens"), ("Strawberries + Flax", "Low-fat milk")],
            "Sat": [("Idli (3) + Sambar", "Coconut chutney + tea"), ("Grilled Fish + Salad", "Whole grain bread"), ("Mixed Dal Khichdi", "Stir-fried beans"), ("Peanuts + Apple", "Herbal tea")],
            "Sun": [("Millet Upma", "Vegetables + green tea"), ("Chickpea Curry", "Brown rice + salad"), ("Moong Soup + Chapati", "Stir-fried broccoli"), ("Mixed Berries", "Yogurt parfait")],
        }
    },
    "General Healthy Diet": {
        "emoji": "🌿", "calories": "2000-2400", "water": "2.5-3 L",
        "avoid": ["Junk Food & Fast Food", "Sugary Drinks & Sodas", "Processed & Packaged Foods", "Excessive Salt", "Refined Carbohydrates", "Excessive Alcohol"],
        "allowed": ["Colourful Fruits & Vegetables", "Whole Grains & Millets", "Lean Protein (Fish, Eggs)", "Healthy Fats (Nuts, Olive Oil)", "Low-Fat Dairy", "Legumes & Pulses"],
        "tip": "Eat the rainbow - different coloured veggies give different nutrients. Practice mindful eating daily.",
        "week": {
            "Mon": [("Oatmeal + Berries", "Low-fat milk + banana"), ("Rice + Dal + Sabzi", "Salad + buttermilk"), ("Grilled Chicken Salad", "Whole grain bread"), ("Mixed Nuts + Tea", "1 fruit")],
            "Tue": [("Idli (3) + Sambar", "Coconut chutney + tea"), ("Fish Curry + Rice", "Cucumber salad"), ("Lentil Soup", "Whole wheat chapati"), ("Fruit Salad", "Yogurt")],
            "Wed": [("Egg Paratha", "Mint chutney + lassi"), ("Quinoa Bowl", "Roasted veggies"), ("Rajma + Chapati", "Onion salad"), ("Veggie Sticks + Dip", "Herbal tea")],
            "Thu": [("Poha + Sprouts", "Green tea + fruit"), ("Chicken Wrap", "Whole wheat + salad"), ("Stir-Fried Tofu", "Brown rice + greens"), ("Berries + Almonds", "Low-fat milk")],
            "Fri": [("Wheat Dosa", "Sambar + green tea"), ("Chickpea Salad", "Olive oil dressing"), ("Baked Salmon", "Sweet potato + salad"), ("Apple + Peanut Butter", "Herbal tea")],
            "Sat": [("Veggie Omelette", "Whole toast + OJ"), ("Mixed Dal + Millet", "Salad + yogurt"), ("Paneer Tikka", "Quinoa + grilled veggies"), ("Trail Mix", "Warm lemon water")],
            "Sun": [("Muesli + Milk", "Fresh fruit salad"), ("Biryani (brown rice)", "Raita + salad"), ("Vegetable Khichdi", "Papad + pickle"), ("Seasonal Fruits", "Nuts + tea")],
        }
    },
}

# ── PDF GENERATOR ──
def generate_pdf(condition, d):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm, leftMargin=15*mm, rightMargin=15*mm)

    GREEN_DARK = colors.HexColor("#1b4332")
    GREEN_MID = colors.HexColor("#2d6a4f")
    WHITE = colors.white
    GREY_LIGHT = colors.HexColor("#f0faf5")
    AMBER_LIGHT = colors.HexColor("#fff9e6")
    AMBER = colors.HexColor("#f5a623")
    DARK = colors.HexColor("#1a2a40")

    story = []

    # Header
    header_data = [[Paragraph(
        f'<font size="22"><b>AI Diet Plan Generator</b></font><br/>'
        f'<font size="10">Condition: {condition} | Generated: {date.today().strftime("%d %B %Y")}</font>',
        ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=22, textColor=WHITE, alignment=TA_CENTER)
    )]]
    header_table = Table(header_data, colWidths=[180*mm])
    header_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), GREEN_DARK), ("TOPPADDING", (0,0), (-1,-1), 14), ("BOTTOMPADDING", (0,0), (-1,-1), 14)]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Stats
    stats = [("7 Days", "Meal Plan"), (d["calories"].split("-")[0]+" kcal", "Min Daily"), ("4 Meals", "Per Day"), (d["water"], "Daily Water")]
    stat_cells = [Paragraph(f'<b><font size="13" color="#1a73e8">{v}</font></b><br/><font size="8">{l}</font>', 
                           ParagraphStyle("sc", fontName="Helvetica", alignment=TA_CENTER)) for v, l in stats]
    stat_table = Table([stat_cells], colWidths=[44*mm]*4)
    stat_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), WHITE), ("BOX", (0,0), (-1,-1), 0.5, colors.grey), ("TOPPADDING", (0,0), (-1,-1), 10)]))
    story.append(stat_table)
    story.append(Spacer(1, 10))

    # Foods
    avoid_paras = [Paragraph('<b><font color="#c62828">Foods to Avoid</font></b>', ParagraphStyle("fh", fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER))]
    for f in d["avoid"]:
        avoid_paras.append(Paragraph(f'<font color="#c62828">✗ {f}</font>', ParagraphStyle("body", fontName="Helvetica", fontSize=9)))

    allow_paras = [Paragraph('<b><font color="#1a73e8">Foods Allowed</font></b>', ParagraphStyle("fh2", fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER))]
    for f in d["allowed"]:
        allow_paras.append(Paragraph(f'<font color="#1565c0">✓ {f}</font>', ParagraphStyle("body", fontName="Helvetica", fontSize=9)))

    food_table = Table([[avoid_paras, allow_paras]], colWidths=[88*mm, 88*mm])
    food_table.setStyle(TableStyle([("BACKGROUND", (0,0), (0,-1), colors.HexColor("#fff5f5")), ("BACKGROUND", (1,0), (1,-1), colors.HexColor("#f0f7ff")), ("TOPPADDING", (0,0), (-1,-1), 10)]))
    story.append(food_table)
    story.append(Spacer(1, 8))

    # Tip
    tip_data = [[Paragraph(f'<b>Expert Tip: </b>{d["tip"]}', ParagraphStyle("tip", fontName="Helvetica", fontSize=9))]]
    tip_table = Table(tip_data, colWidths=[180*mm])
    tip_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), AMBER_LIGHT), ("LEFTPADDING", (0,0), (-1,-1), 14), ("TOPPADDING", (0,0), (-1,-1), 10)]))
    story.append(tip_table)
    story.append(Spacer(1, 12))

    # Weekly table
    week_title_data = [[Paragraph("MY DAILY FOOD PLAN — 7-DAY SCHEDULE", ParagraphStyle("wt", fontName="Helvetica-Bold", fontSize=13, textColor=WHITE, alignment=TA_CENTER))]]
    week_title_tbl = Table(week_title_data, colWidths=[180*mm])
    week_title_tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), GREEN_DARK), ("TOPPADDING", (0,0), (-1,-1), 10)]))
    story.append(week_title_tbl)

    DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    MEALS = ["Breakfast","Lunch","Dinner","Snacks"]
    hdr_row = [Paragraph("<b>DAY</b>", ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER))]
    hdr_row += [Paragraph(m.upper(), ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER)) for m in MEALS]
    table_data = [hdr_row]

    for day in DAYS:
        row = [Paragraph(f"<b>{day.upper()}</b>", ParagraphStyle("day", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, alignment=TA_CENTER))]
        for idx in range(4):
            main, detail = d["week"][day][idx]
            row.append(Paragraph(f'<b>{main}</b><br/><font size="7">{detail}</font>', ParagraphStyle("mc", fontName="Helvetica", fontSize=8, alignment=TA_CENTER)))
        table_data.append(row)

    week_table = Table(table_data, colWidths=[18*mm, 40*mm, 40*mm, 40*mm, 36*mm])
    week_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN_DARK),
        ("BACKGROUND", (0,1), (0,-1), GREEN_MID),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#c8e6c9")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GREY_LIGHT]),
    ]))
    story.append(week_table)
    story.append(Spacer(1, 14))

    # Footer
    motiv_data = [[Paragraph('<b><font color="white" size="12">I CAN DO IT — Your Health Journey Starts Today!</font></b>', ParagraphStyle("mv", fontName="Helvetica-Bold", alignment=TA_CENTER))]]
    motiv_table = Table(motiv_data, colWidths=[180*mm])
    motiv_table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), GREEN_MID), ("TOPPADDING", (0,0), (-1,-1), 12)]))
    story.append(motiv_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ── CONDITION DETECTION ──
def detect(text):
    t = text.lower()
    if any(k in t for k in ["diabetes","diabetic","blood sugar","glucose","insulin","hba1c"]):
        return "Diabetes"
    if any(k in t for k in ["bp","blood pressure","hypertension"]):
        return "High Blood Pressure"
    return "General Healthy Diet"

# ── CONSTANTS ──
DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
MEALS = ["Breakfast","Lunch","Dinner","Snacks"]
ICONS = {"Breakfast":"🌅","Lunch":"☀️","Dinner":"🌙","Snacks":"🍎"}
M_HDR = {"Breakfast":"BREAKFAST","Lunch":"LUNCH","Dinner":"DINNER","Snacks":"SNACKS"}

# ── HERO ──
st.markdown('<div class="hero-banner"><span class="hero-emoji">🥗</span>'
            '<p class="hero-title">AI Diet Plan Generator</p>'
            '<p class="hero-sub">Upload your prescription — get a personalised 7-day meal plan instantly</p></div>',
            unsafe_allow_html=True)

# ── UPLOAD ──
st.markdown('<div class="upload-card"><p class="upload-title">📄 Upload Prescription / Health Report</p>'
            '<p class="upload-hint">JPG, JPEG or PNG — AI OCR detects your condition automatically</p>',
            unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN ──
if uploaded_file:
    img = Image.open(uploaded_file)
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        st.image(img, caption="Uploaded Prescription", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    uploaded_file.seek(0)
    img_bytes = uploaded_file.read()

    with st.spinner("🔍 Analysing prescription... (first run loads model ~20 sec)"):
        extracted = run_ocr(img_bytes)

    condition = detect(extracted)
    d = DIET[condition]

    # Condition badge
    st.markdown(f'<div class="cond-wrap"><span class="cond-badge">{d["emoji"]} Detected Condition: {condition}</span></div>', unsafe_allow_html=True)

    # Stats
    stats = [("7","Day Meal Plan"), (d["calories"].split("-")[0],"Min Daily kcal"), ("4","Meals Per Day"), (d["water"],"Daily Water Goal")]
    for col, (num, lbl) in zip(st.columns(4), stats):
        col.markdown(f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sec-title">🥦 Your Personalised Food Guide</p>', unsafe_allow_html=True)

    # Food cards
    col_av, col_al = st.columns(2)
    with col_av:
        li = "".join(f'<li class="avoid-li">❌ {f}</li>' for f in d["avoid"])
        st.markdown(f'<div class="food-card"><img class="fc-img" src="{AVOID_SRC}" alt="Foods to Avoid"/>'
                    f'<div class="fc-body"><p class="fc-head avoid-head">🚫 Foods to Avoid</p><ul class="food-list">{li}</ul></div></div>', unsafe_allow_html=True)
    with col_al:
        li = "".join(f'<li class="allow-li">✅ {f}</li>' for f in d["allowed"])
        st.markdown(f'<div class="food-card"><img class="fc-img" src="{ALLOWED_SRC}" alt="Foods Allowed"/>'
                    f'<div class="fc-body"><p class="fc-head allowed-head">✔️ Foods Allowed</p><ul class="food-list">{li}</ul></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="tip-card">💡 <strong>Expert Tip:</strong> {d["tip"]}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Weekly table
    st.markdown('<div class="week-hdr">🍽️ My Daily Food Plan — 7-Day Schedule</div>', unsafe_allow_html=True)
    thead = '<thead><tr><th class="th-day">DAY</th>' + "".join(f'<th>{ICONS[m]} {M_HDR[m]}</th>' for m in MEALS) + '</tr></thead>'
    tbody = "<tbody>"
    for day in DAYS:
        cells = "".join(f'<td><span class="mi">{ICONS[m]}</span><span class="mm">{d["week"][day][i][0]}</span>'
                       f'<span class="md">{d["week"][day][i][1]}</span></td>' for i, m in enumerate(MEALS))
        tbody += f'<tr><td class="td-day">{day.upper()}</td>{cells}</tr>'
    tbody += "</tbody>"
    st.markdown(f'<div class="week-wrap"><table class="wtbl">{thead}{tbody}</table></div>', unsafe_allow_html=True)

    st.markdown('<div class="motiv">💪 I CAN DO IT — Your Health Journey Starts Today! 🌱</div>', unsafe_allow_html=True)

    # PDF download
    st.markdown('<div class="pdf-section"><p class="pdf-title">📥 Download Your Full Diet Plan</p>'
                '<p class="pdf-sub">Get a beautifully formatted PDF with your 7-day meal plan</p>', unsafe_allow_html=True)

    pdf_bytes = generate_pdf(condition, d)
    filename = f"Diet_Plan_{condition.replace(' ','_')}.pdf"

    st.download_button(label="⬇️ Download Diet Plan as PDF", data=pdf_bytes, file_name=filename, 
                      mime="application/pdf", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="ph-wrap"><span class="ph-icon">📋</span>'
                '<p class="ph-title">Upload your prescription to get started</p>'
                '<p class="ph-sub">Our AI reads your prescription and builds a personalised 7-day diet plan automatically.</p>'
                '<div class="chips">'
                '<div class="chip"><span class="chip-icon">🫀</span><span class="chip-name">Blood Pressure</span></div>'
                '<div class="chip"><span class="chip-icon">🩸</span><span class="chip-name">Diabetes</span></div>'
                '<div class="chip"><span class="chip-icon">🌿</span><span class="chip-name">Healthy Diet</span></div>'
                '</div></div>', unsafe_allow_html=True)
