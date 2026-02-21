import streamlit as st
import textwrap
import copy
import io
import json
import hashlib
import random

# Note: Ensure these are available in your directory
from health_extractor import extract_health_values
from diet_generator import generate_diet_plan

# PDF generation imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Diet Plan Generator", page_icon="🥗", layout="wide")

# --- SVG ICONS ---
ICON_HEALTH = """<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>"""
ICON_CALENDAR = """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>"""

# --- CUSTOM CSS FOR RICH UI ---
# Initialize theme
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'
theme = st.session_state.get('theme', 'light')
if theme == 'dark':
    accent1 = '#2563eb'
    accent2 = '#0891b2'
    muted = '#94a3b8'
    body_bg = '#0f172a'
    text_color = '#e6eef9'
else:
    accent1 = '#3b82f6'
    accent2 = '#06b6d4'
    muted = '#64748b'
    body_bg = '#ffffff'
    text_color = '#0f172a'

theme_vars = f":root {{ --accent1: {accent1}; --accent2: {accent2}; --muted: {muted}; --body-bg: {body_bg}; --text-color: {text_color}; }}"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
{theme_vars}
    html, body, [class*="css"] {{ font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background: var(--body-bg); color: var(--text-color); }}
    .hero-container {{
        background: linear-gradient(135deg, var(--accent1) 0%, #60a5fa 60%);
        padding: 28px 26px;
        border-radius: 14px;
        color: white;
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(59,130,246,0.12);
        align-items:center;
    }}
    .hero-container h1 {{
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
        color: white;
    }}
    .hero-container p {{
        margin: 5px 0 0 0;
        opacity: 0.95;
        font-size: 0.98rem;
    }}

    /* Custom Metric Cards */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(160px, 1fr));
        gap: 18px;
        margin-bottom: 28px;
    }}
    .metric-card {{
        background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
        border: none;
        border-radius: 12px;
        padding: 18px 16px;
        text-align: left;
        box-shadow: 0 6px 18px rgba(2,6,23,0.04);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 18px 40px rgba(2,6,23,0.06);
    }}
    .metric-title {{
        color: var(--muted);
        font-size: 0.86rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }}
    .metric-value {{
        color: var(--text-color);
        font-size: 1.5rem;
        font-weight: 800;
    }}
    
    /* Meal Card (Inside Tabs) */
    .meal-card {{
        background-color: #ffffff;
        border-left: 4px solid var(--accent1);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.03);
        transition: transform .14s ease, box-shadow .14s ease;
    }}
    .meal-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 18px 40px rgba(2,6,23,0.06);
    }}
    .meal-label {{
        color: var(--accent1);
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .meal-cal {{
        background: #e2e8f0;
        color: #475569;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }}
    .meal-desc {{
        color: #334155;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.5;
        margin-top: 10px;
    }}
    
    /* Streamlit overrides */
    div[data-testid="stTabs"] button {{
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        padding: 10px 18px !important;
        border-radius: 999px !important;
        background: transparent !important;
        border: 1px solid rgba(15,23,42,0.04) !important;
        color: var(--text-color) !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        background: linear-gradient(90deg,var(--accent2),var(--accent1)) !important;
        color: white !important;
        box-shadow: 0 8px 30px rgba(59,130,246,0.12) !important;
    }}
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(90deg,var(--accent2),var(--accent1)) !important;
        color: white !important;
        border: none !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        box-shadow: 0 6px 18px rgba(59,130,246,0.12) !important;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
    }}
    .preview-card {{
        background: #fff; border: 1px solid #e6eef9; padding: 16px; border-radius: 10px; box-shadow: 0 6px 18px rgba(2,6,23,0.03);
        animation: slideUpFade .35s ease both;
        transition: transform .18s ease, box-shadow .18s ease;
    }}
    .preview-title {{ font-weight:700; color:var(--text-color); margin-bottom:8px; }}
    .small-muted {{ color:#6b7280; font-size:0.9rem }}
    @keyframes slideUpFade {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
</style>
""", unsafe_allow_html=True)

# --- HELPER: PDF GENERATION ---
def create_pdf_bytes(export_data: dict, uploaded_file) -> bytes:
    buffer = io.BytesIO()
    page_size = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size

    # Header accent bar + title
    try:
        if st.session_state.get('theme', 'light') == 'dark':
            accent = (0.09, 0.48, 0.78)
        else:
            accent = (0.152, 0.514, 0.961)
    except Exception:
        accent = (0.152, 0.514, 0.961)
    c.setFillColorRGB(*accent)
    header_h = 56
    c.rect(0, height - header_h, width, header_h, fill=1, stroke=0)
    c.setFillColorRGB(1,1,1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 40, "AI Personalised Diet Plan")

    # Health summary
    c.setFont("Helvetica", 12)
    health = export_data.get("health", {})
    c.setFillColorRGB(0,0,0)
    c.drawString(40, height - 92, f"Glucose: {health.get('glucose', 'N/A')} mg/dL")
    c.drawString(220, height - 92, f"BMI: {health.get('bmi', 'N/A')}")
    c.drawString(340, height - 92, f"Status: {health.get('status', 'N/A')}")
    c.drawString(480, height - 92, f"Risk Level: {health.get('risk_level', 'N/A')}")

    y = height - 110
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "7-Day Meal Plan")
    y -= 20
    c.setFont("Helvetica", 10)

    diet_plan = export_data.get("diet_plan", {})
    for day, meals in diet_plan.items():
        if y < 120:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 10)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, str(day))
        y -= 16
        c.setFont("Helvetica", 10)
        for meal_name, text_desc in meals.items():
            lines = textwrap.wrap(f"{meal_name}: {text_desc}", width=90)
            for line in lines:
                c.drawString(50, y, line)
                y -= 12
                if y < 80:
                    c.showPage()
                    y = height - 60
                    c.setFont("Helvetica", 10)
        y -= 8

    # Process uploaded image
    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            pil_img = Image.open(uploaded_file).convert("RGB")
            max_w = width / 3
            max_h = height / 3
            img_w, img_h = pil_img.size
            ratio = min(max_w / img_w, max_h / img_h, 1)
            new_w, new_h = int(img_w * ratio), int(img_h * ratio)
            img_reader = ImageReader(pil_img.resize((new_w, new_h)))
            c.drawImage(img_reader, width - new_w - 40, 40, width=new_w, height=new_h)
        except Exception:
            pass

    c.save()
    buffer.seek(0)
    return buffer.read()

# --- HERO HEADER ---
st.markdown(f"""
    <div class="hero-container">
        <div>{ICON_HEALTH}</div>
        <div>
            <h1>AI Personalised Diet Plan</h1>
            <p>Upload your medical data and let AI craft your optimal nutrition strategy.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Top navigation: compact with avatar and theme toggle
nav_left, nav_right = st.columns([9,1])
with nav_left:
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
with nav_right:
    if st.button('Toggle Theme'):
        st.session_state['theme'] = 'dark' if st.session_state.get('theme','light') == 'light' else 'light'
        st.experimental_rerun()
    # avatar
    st.markdown("""
        <div style='display:flex; align-items:center; justify-content:flex-end; gap:8px;'>
            <div style='text-align:right;'>
                <div style='font-weight:700;'>You</div>
                <div style='font-size:0.8rem; color: #64748b;'>Premium</div>
            </div>
            <div style='width:40px;height:40px;border-radius:999px;background:linear-gradient(90deg,var(--accent2),var(--accent1));display:flex;align-items:center;justify-content:center;color:white;font-weight:700;'>U</div>
        </div>
    """, unsafe_allow_html=True)

# --- UPLOAD SECTION ---
st.markdown("### 📄 1. Upload Prescription")
uploaded_file = st.file_uploader("Upload Doctor Prescription (JPG, PNG)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    # Sidebar: quick tips and sample
    st.sidebar.title("How to use")
    st.sidebar.markdown("""
    - Upload a clear photo of the prescription.
    - Click **Analyze & Generate** to extract health values and create a 7-day plan.
    - Use the swap controls to swap Monday with another day.
    - Use the alternative selector to preview and apply a new plan for any day.
    """)
    st.sidebar.markdown("---")
    st.sidebar.markdown("Need help? Share the screenshot or open issues in the repo.")
    col_img, col_info = st.columns([1, 2], gap="large")
    
    with col_img:
        # THE FIX: Removed 'border=True' from this line
        st.image(uploaded_file, caption="Prescription Preview", use_container_width=True)
    
    with col_info:
        st.info("File uploaded successfully. Ready to analyze your health markers.")

        if st.button("🚀 Analyze & Generate My Diet Plan", use_container_width=True, type="primary"):
            # --- EXECUTE REAL BACKEND LOGIC ---
            with st.spinner("Processing medical data and generating plan..."):
                try:
                    uploaded_file.seek(0)
                except Exception:
                    pass

                img_bytes = uploaded_file.read() or b""

                img_hash = hashlib.sha256(img_bytes).hexdigest()
                seed = int(img_hash[:16], 16)
                random.seed(seed)

                try:
                    img_io_for_extract = io.BytesIO(img_bytes)
                    health_data = extract_health_values(img_io_for_extract) or {}
                except Exception:
                    health_data = {}

                def _to_float(val, fallback):
                    try:
                        return float(val)
                    except Exception:
                        try:
                            num = ''.join(c for c in str(val) if (c.isdigit() or c=='.' or c=='-'))
                            return float(num) if num not in ('', '.', '-') else fallback
                        except Exception:
                            return fallback

                base_glucose = _to_float(health_data.get('glucose'), 120.0)
                base_bmi = _to_float(health_data.get('bmi'), 25.0)
                base_diabetes = str(health_data.get('diabetes', '')).strip()

                g_var = (seed % 21) - 10
                b_var = ((seed >> 16) % 11) - 5

                glucose = max(50, min(300, int(round(base_glucose + g_var))))
                bmi = max(12, min(60, round(base_bmi + b_var, 1)))

                if base_diabetes and base_diabetes.lower() not in ('', 'n/a', 'none'):
                    diabetes_status = base_diabetes
                else:
                    if glucose >= 126:
                        diabetes_status = 'Detected'
                    elif glucose >= 100:
                        diabetes_status = 'Pre-diabetic'
                    else:
                        diabetes_status = 'Not Detected'

                if glucose >= 140 or bmi >= 35:
                    risk_level = 'High Risk'
                elif glucose >= 126 or bmi >= 30:
                    risk_level = 'Elevated Risk'
                elif glucose >= 100 or bmi >= 25:
                    risk_level = 'Low Risk'
                else:
                    risk_level = 'Normal'

                result = generate_diet_plan(glucose, bmi)

                try:
                    original_plan = result.get("Diet Plan", {})
                    days = list(original_plan.keys())
                    if days:
                        n = len(days)
                        offset = seed % n
                        meals_list = [original_plan[d] for d in days]
                        rotated_meals = meals_list[offset:] + meals_list[:offset]
                        new_plan = {}
                        for day_name, meals in zip(days, rotated_meals):
                            meal_items = list(meals.items())
                            if meal_items:
                                m_offset = (seed >> 8) % len(meal_items)
                                rotated_meal_items = meal_items[m_offset:] + meal_items[:m_offset]
                                new_meals = {k: v for k, v in rotated_meal_items}
                            else:
                                new_meals = meals
                            new_plan[day_name] = new_meals
                        result["Diet Plan"] = new_plan
                except Exception:
                    pass

                # persist results and uploaded bytes for later rendering
                st.session_state['diet_plan'] = result.get("Diet Plan", {})
                st.session_state['seed'] = seed
                st.session_state['glucose'] = glucose
                st.session_state['bmi'] = bmi
                st.session_state['risk_level'] = risk_level
                st.session_state['diabetes_status'] = diabetes_status
                st.session_state['uploaded_bytes'] = img_bytes

            st.success("Health analysis complete — plan saved below.")

    # End with col_info

    # If a plan exists in session_state, render it (this keeps UI available across reruns)
    if st.session_state.get('diet_plan'):
        result = {"Diet Plan": st.session_state['diet_plan']}
        glucose = st.session_state.get('glucose', 120)
        bmi = st.session_state.get('bmi', 25)
        diabetes_status = st.session_state.get('diabetes_status', 'N/A')
        risk_level = st.session_state.get('risk_level', 'Normal')

        st.divider()
        st.markdown("### 📊 2. Health Profile Overview")
        metrics_html = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-title">🩸 Fasting Glucose</div>
                <div class="metric-value">{glucose} <span style="font-size:1rem;color:#94a3b8;">mg/dL</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-title">⚖️ BMI</div>
                <div class="metric-value">{bmi}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">🩺 Diabetes Status</div>
                <div class="metric-value">{diabetes_status}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">⚠️ Risk Level</div>
                <div class="metric-value" style="color: {'#ef4444' if risk_level != 'Normal' else '#10b981'};">{risk_level}</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # Meal plan tabs
        st.markdown(textwrap.dedent(f"""
            <div style="display:flex; align-items:center; gap:12px; margin: 30px 0 20px 0;">
                {ICON_CALENDAR}
                <h2 style="margin:0; color: #1e3a8a;">Customised 7-Day Meal Plan</h2>
            </div>
        """), unsafe_allow_html=True)

        diet_plan = st.session_state.get('diet_plan', {})
        days = list(diet_plan.keys())
        if not days:
            st.warning("No diet plan data found.")
        else:
            tabs = st.tabs([day.upper() for day in days])
            for i, tab in enumerate(tabs):
                with tab:
                    meals = diet_plan[days[i]]
                    total_cal = 0
                    st.write("")
                    for meal_name, food_description in meals.items():
                        cal_val = 450 if meal_name.lower() in ['lunch', 'dinner'] else 300
                        total_cal += cal_val
                        meal_card_html = f"""
                            <div class="meal-card">
                                <div class="meal-label">
                                    <span>🍽️ {meal_name}</span>
                                    <span class="meal-cal">{cal_val} kcal</span>
                                </div>
                                <div class="meal-desc">{food_description}</div>
                            </div>
                        """
                        st.markdown(textwrap.dedent(meal_card_html), unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:right; font-weight:800; color:#1e3a8a; font-size:1.1rem; padding-top: 10px;'>🔥 Daily Total: ~{total_cal} kcal</div>", unsafe_allow_html=True)

            # Swap / alternative UI
            day_map = {d.upper(): d for d in days}
            monday_key = day_map.get('MONDAY')
            if monday_key:
                other_days = [d for d in days if d != monday_key]
                st.markdown("---")
                st.markdown("### ⚡ Can't eat Monday? Swap or regenerate it")
                cols_swap = st.columns([3,2,2])
                with cols_swap[0]:
                    swap_with = st.selectbox("Swap Monday with", options=other_days, key='swap_select')
                    alt_day = st.selectbox("Select day to generate alternative for", options=days, key='alt_select')
                with cols_swap[1]:
                    # swap icon + button
                    swap_svg = """
                    <div style='display:flex; align-items:center; gap:8px;'>
                      <svg width='28' height='28' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>
                        <path d='M21 16V12' stroke='var(--accent1)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/>
                        <path d='M3 8V12' stroke='var(--accent1)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/>
                        <path d='M21 12H3' stroke='var(--accent1)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/>
                      </svg>
                    </div>
                    """
                    st.markdown(swap_svg, unsafe_allow_html=True)
                    if st.button("Swap Selected Day with Monday"):
                        try:
                            dp = st.session_state.get('diet_plan', {})
                            # save previous for undo
                            st.session_state['previous_plan'] = copy.deepcopy(dp)
                            dp[monday_key], dp[swap_with] = dp[swap_with], dp[monday_key]
                            st.session_state['diet_plan'] = dp
                            st.success(f"Swapped {monday_key} with {swap_with}")
                        except Exception:
                            st.error("Swap failed — please try again.")
                with cols_swap[2]:
                    if st.button("Generate Alternative for Selected Day"):
                        try:
                            selected_day = st.session_state.get('alt_select', monday_key)
                            alt_seed = st.session_state.get('seed', 0) + 1
                            random.seed(alt_seed)
                            alt_result = generate_diet_plan(st.session_state.get('glucose', glucose), st.session_state.get('bmi', bmi))
                            original_plan_alt = alt_result.get("Diet Plan", {})
                            alt_days = list(original_plan_alt.keys())
                            if alt_days:
                                n_alt = len(alt_days)
                                offset_alt = alt_seed % n_alt
                                meals_list_alt = [original_plan_alt[d] for d in alt_days]
                                rotated_meals_alt = meals_list_alt[offset_alt:] + meals_list_alt[:offset_alt]
                                new_plan_alt = {}
                                for day_name, meals in zip(alt_days, rotated_meals_alt):
                                    meal_items = list(meals.items())
                                    if meal_items:
                                        m_offset = (alt_seed >> 8) % len(meal_items)
                                        rotated_meal_items = meal_items[m_offset:] + meal_items[:m_offset]
                                        new_meals = {k: v for k, v in rotated_meal_items}
                                    else:
                                        new_meals = meals
                                    new_plan_alt[day_name] = new_meals
                                if selected_day in new_plan_alt:
                                    # store as pending alternative for preview/confirm
                                    st.session_state['pending_alt'] = {
                                        'day': selected_day,
                                        'meals': new_plan_alt[selected_day],
                                        'seed': alt_seed,
                                        'full_plan': new_plan_alt
                                    }
                                    st.success(f'Generated alternative preview for {selected_day}')
                                else:
                                    st.warning(f'Alternative plan generation returned no entry for {selected_day}.')
                            else:
                                st.warning('Alternative plan generation returned no days.')
                        except Exception:
                            st.error('Failed to generate alternative plan.')

            # Export
            # If a pending alternative exists, show preview and confirm controls
            pending = st.session_state.get('pending_alt')
            if pending:
                st.markdown("---")
                st.markdown("### 🔍 Preview Alternative")
                left, right = st.columns(2)
                cur_day = pending['day']
                with left:
                    cur_meals = st.session_state.get('diet_plan', {}).get(cur_day, {})
                    total_cur = sum(450 if m.lower() in ['lunch', 'dinner'] else 300 for m in cur_meals.keys())
                    st.markdown(f"<div class='preview-card'><div class='preview-title'>Current: {cur_day} <span class='small-muted' style='float:right;'>{total_cur} kcal</span></div>", unsafe_allow_html=True)
                    for m, desc in cur_meals.items():
                        st.markdown(f"**{m}**: {desc}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with right:
                    prop_meals = pending['meals']
                    total_prop = sum(450 if m.lower() in ['lunch', 'dinner'] else 300 for m in prop_meals.keys())
                    st.markdown(f"<div class='preview-card'><div class='preview-title'>Proposed Alternative: {cur_day} <span class='small-muted' style='float:right;'>{total_prop} kcal</span></div>", unsafe_allow_html=True)
                    for m, desc in prop_meals.items():
                        st.markdown(f"**{m}**: {desc}")
                    st.markdown("</div>", unsafe_allow_html=True)
                c1, c2 = st.columns([1,1])
                with c1:
                    apply_svg = """
                    <div style='display:flex; align-items:center; gap:8px; margin-bottom:6px;'>
                        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>
                            <path d='M20 6L9 17l-5-5' stroke='green' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/>
                        </svg>
                    </div>
                    """
                    st.markdown(apply_svg, unsafe_allow_html=True)
                    if st.button('Apply Alternative'):
                        try:
                            dp = st.session_state.get('diet_plan', {})
                            # save previous for undo
                            st.session_state['previous_plan'] = copy.deepcopy(dp)
                            dp[cur_day] = pending['meals']
                            st.session_state['diet_plan'] = dp
                            st.session_state['seed'] = pending.get('seed', st.session_state.get('seed', 0))
                            del st.session_state['pending_alt']
                            st.success(f'Applied alternative for {cur_day}')
                        except Exception:
                            st.error('Failed to apply alternative.')
                with c2:
                    discard_svg = """
                    <div style='display:flex; align-items:center; gap:8px; margin-bottom:6px;'>
                        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>
                            <path d='M18 6L6 18M6 6l12 12' stroke='#ef4444' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/>
                        </svg>
                    </div>
                    """
                    st.markdown(discard_svg, unsafe_allow_html=True)
                    if st.button('Discard Alternative'):
                        if 'pending_alt' in st.session_state:
                            del st.session_state['pending_alt']
                        st.info('Discarded alternative preview')

            # Undo support with icon
            if st.session_state.get('previous_plan'):
                undo_svg = """
                <div style='display:flex; align-items:center; gap:8px; margin-bottom:6px;'>
                  <svg width='20' height='20' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>
                    <path d='M3 7v6h6' stroke='var(--accent1)' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/>
                    <path d='M20 17A8 8 0 1 0 12 5' stroke='var(--accent1)' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/>
                  </svg>
                </div>
                """
                st.markdown(undo_svg, unsafe_allow_html=True)
                if st.button('Undo Last Change'):
                    try:
                        st.session_state['diet_plan'] = copy.deepcopy(st.session_state['previous_plan'])
                        del st.session_state['previous_plan']
                        st.success('Reverted last change')
                    except Exception:
                        st.error('Undo failed')
            export_data = {
                "health": {
                    "glucose": glucose,
                    "bmi": bmi,
                    "status": diabetes_status,
                    "risk_level": risk_level
                },
                "diet_plan": st.session_state.get('diet_plan', {})
            }
            json_bytes = json.dumps(export_data, indent=2).encode("utf-8")
            try:
                pdf_src_bytes = st.session_state.get('uploaded_bytes')
                pdf_src = io.BytesIO(pdf_src_bytes) if pdf_src_bytes is not None else uploaded_file
                pdf_src.seek(0)
            except Exception:
                pdf_src = uploaded_file
            pdf_bytes = create_pdf_bytes(export_data, pdf_src)

            st.markdown("### 💾 3. Export Plan")
            cols_export = st.columns([1,1,2])
            with cols_export[0]:
                st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name="diet-plan.pdf", mime="application/pdf")
            with cols_export[1]:
                st.download_button(label="📊 Download JSON", data=json_bytes, file_name="diet-plan.json", mime="application/json")

# --- FOOTER ---
st.markdown("<br><hr><div style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>Disclaimer: This AI-generated plan is for informational purposes. Please consult your doctor before starting any new diet.</div>", unsafe_allow_html=True)