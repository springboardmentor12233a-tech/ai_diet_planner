"""
AI-NutriCare - Personalized Diet Plan Generator
Full end-to-end Streamlit app: Upload → Extract → Analyze → Generate Plan → Display → Export
"""

import streamlit as st
from io import BytesIO

from modules.medical_report_parser import parse_medical_report
from modules.health_analyzer import analyze_medical_data
from modules.nlp_interpreter import interpret_doctor_notes, rules_from_health_conditions, combine_rules
from modules.diet_plan_generator import (
    build_profile,
    generate_weekly_plan,
    calculate_bmi,
    calculate_daily_calories,
    get_meal_explanation,
    estimate_meal_macros,
    swap_meal,
    SLOT_TO_MEAL_KEY,
)
from modules.export_module import export_to_pdf, export_to_json
from modules.risk_summary import get_risk_summary

# Page config
st.set_page_config(page_title="AI-NutriCare", page_icon="🥗", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for cleaner dashboard
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1e88e5; margin-bottom: 0.5rem; }
    .sub-header { color: #546e7a; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
    .condition-high { color: #c62828; font-weight: 600; }
    .condition-moderate { color: #f9a825; font-weight: 600; }
    .condition-normal { color: #2e7d32; font-weight: 600; }
    div[data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 8px; }
    .risk-low { background: #e8f5e9; color: #2e7d32; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .risk-moderate { background: #fff8e1; color: #f9a825; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .risk-high { background: #ffebee; color: #c62828; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .why-meal { font-size: 0.85rem; color: #546e7a; font-style: italic; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# Session state
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "conditions" not in st.session_state:
    st.session_state.conditions = []
if "diet_rules" not in st.session_state:
    st.session_state.diet_rules = []
if "diet_plan" not in st.session_state:
    st.session_state.diet_plan = None
if "patient_name" not in st.session_state:
    st.session_state.patient_name = ""


def run_pipeline(uploaded_file):
    """Parse report -> analyze -> NLP rules."""
    if uploaded_file is None:
        return
    bytes_data = uploaded_file.read()
    filename = uploaded_file.name or "report.pdf"
    result = parse_medical_report(bytes_data, filename)
    if not result["success"]:
        st.error(result["error"])
        return
    data = result["data"]
    st.session_state.report_data = data
    conditions = analyze_medical_data(data)
    st.session_state.conditions = conditions
    nlp_rules = interpret_doctor_notes(data.get("doctor_notes", ""), data.get("raw_text", ""))
    cond_rules = rules_from_health_conditions(conditions)
    st.session_state.diet_rules = combine_rules(nlp_rules, cond_rules)
    uploaded_file.seek(0)


# ----- Header -----
st.markdown('<p class="main-header">🥗 AI-NutriCare</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Personalized 7-Day Diet Plan Generator — Upload medical report, get a structured weekly plan.</p>', unsafe_allow_html=True)

# ----- 1. Medical Report Upload -----
st.header("1️⃣ Medical Report Input")
col_upload, col_info = st.columns([2, 1])
with col_upload:
    uploaded_file = st.file_uploader(
        "Upload medical report (PDF, JPG, PNG, or TXT)",
        type=["pdf", "jpg", "jpeg", "png", "txt"],
        key="report_upload",
    )
with col_info:
    if uploaded_file:
        st.caption(f"File: {uploaded_file.name}")

if st.button("Extract & Analyze Report", type="primary") and uploaded_file:
    with st.spinner("Extracting text and analyzing..."):
        run_pipeline(uploaded_file)
    st.success("Report processed. View extracted data and conditions below.")

# ----- 2. Extracted Data -----
if st.session_state.report_data:
    data = st.session_state.report_data
    st.header("2️⃣ Extracted Numeric Data")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Blood Sugar (mg/dL)", data.get("blood_sugar") or "—")
    with c2:
        st.metric("Cholesterol (mg/dL)", data.get("cholesterol") or "—")
    with c3:
        st.metric("BMI", data.get("bmi") or "—")
    with c4:
        bp_s = data.get("systolic_bp")
        bp_d = data.get("diastolic_bp")
        st.metric("Blood Pressure (mmHg)", f"{bp_s or '—'} / {bp_d or '—'}" if (bp_s or bp_d) else "—")
    with c5:
        st.caption("Doctor notes length: " + str(len(data.get("doctor_notes", "") or "")) + " chars")

    with st.expander("View raw / doctor notes text"):
        st.text_area("", value=(data.get("doctor_notes") or data.get("raw_text", ""))[:3000], height=150, disabled=True)

# ----- 3. Detected Health Conditions -----
if st.session_state.conditions:
    st.header("3️⃣ Detected Health Conditions")
    for c in st.session_state.conditions:
        sev = (c.severity or "").lower()
        cls = "condition-normal" if sev == "normal" else "condition-moderate" if sev == "moderate" else "condition-high"
        val_str = f"{c.value} {c.unit}" if c.value is not None else "—"
        st.markdown(f"- **{c.name}**: {val_str} — <span class='{cls}'>{c.message}</span>", unsafe_allow_html=True)

# ----- 3b. Health Risk Summary -----
risk_summary = get_risk_summary(st.session_state.conditions, st.session_state.report_data)
if risk_summary["has_data"]:
    st.header("📊 Health Risk Summary")
    cols = st.columns(len(risk_summary["items"]) + 1)
    for i, r in enumerate(risk_summary["items"]):
        with cols[i]:
            cls = "risk-low" if r.level == "Low" else "risk-moderate" if r.level == "Moderate" else "risk-high"
            val_str = f"{r.value} {r.unit}" if r.value is not None else r.unit
            st.markdown(f'<span class="{cls}">{r.level}</span>', unsafe_allow_html=True)
            st.caption(f"**{r.category}**")
            st.caption(val_str)
    with cols[-1]:
        overall = risk_summary["overall"]
        cls = "risk-low" if overall == "Low" else "risk-moderate" if overall == "Moderate" else "risk-high"
        st.markdown(f'<span class="{cls}">Overall: {overall}</span>', unsafe_allow_html=True)
        st.caption("Combined risk")
    st.markdown("")

# ----- 4. Interpreted Diet Rules -----
if st.session_state.diet_rules:
    st.header("4️⃣ Interpreted Diet Rules (from report)")
    for r in st.session_state.diet_rules:
        st.markdown(f"- **{r.rule_id}**: {r.description}")

# ----- 5. User Profile & Plan Generator -----
st.header("5️⃣ Your Profile & Weekly Plan")
st.caption("Fill your details. Medical restrictions from the report are applied automatically if you uploaded one.")

with st.form("user_profile_form"):
    name = st.text_input("Full Name", value=st.session_state.get("patient_name", ""), placeholder="Your name")
    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=1.0)
    gender = st.selectbox("Gender", ["Male", "Female"])
    dietary_preference = st.selectbox("Dietary Preference", ["Veg", "Non-Veg"])
    allergies_input = st.text_input("Allergies (comma-separated)", placeholder="e.g. nuts, dairy, gluten")
    health_goal = st.selectbox("Health Goal", ["Weight loss", "Weight gain", "Maintenance"])
    submitted = st.form_submit_button("Generate 7-Day Diet Plan")

    if submitted:
        allergies = [a.strip() for a in (allergies_input or "").split(",") if a.strip()]
        st.session_state.patient_name = name
        profile = build_profile(
            name=name, age=age, weight_kg=weight_kg, height_cm=height_cm,
            gender=gender, dietary_preference=dietary_preference, allergies=allergies,
            health_goal=health_goal, diet_rules=st.session_state.diet_rules,
        )
        daily_cal = calculate_daily_calories(weight_kg, height_cm, age, gender, health_goal)
        plan = generate_weekly_plan(profile, daily_cal)
        st.session_state.diet_plan = plan
        st.session_state.last_profile = profile
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()

# ----- 6. Display 7-Day Diet Plan -----
if st.session_state.diet_plan:
    plan = st.session_state.diet_plan
    profile = st.session_state.get("last_profile")
    diet_rules = st.session_state.diet_rules or []

    st.header("6️⃣ Your 7-Day Weekly Diet Plan")
    st.markdown(f"**Daily calorie target:** {plan['daily_calories']} kcal | **BMI:** {plan['bmi']}")

    # Nutritional Breakdown (aggregate macros from all meals)
    total_carbs = total_protein = total_fat = 0.0
    for day_info in plan["days"]:
        for slot in ["breakfast", "mid_morning_snack", "lunch", "evening_snack", "dinner"]:
            meal = day_info.get(slot) or {}
            tags = meal.get("tags", [])
            cal = meal.get("calories", 0)
            macros = estimate_meal_macros(tags, cal)
            total_carbs += macros["carbs_g"]
            total_protein += macros["protein_g"]
            total_fat += macros["fat_g"]

    with st.expander("📈 Nutritional Breakdown (weekly totals)", expanded=False):
        try:
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Pie(
                labels=["Carbs (g)", "Protein (g)", "Fats (g)"],
                values=[total_carbs, total_protein, total_fat],
                hole=0.4,
                marker_colors=["#64b5f6", "#81c784", "#ffb74d"],
                textinfo="label+value",
            )])
            fig.update_layout(showlegend=True, height=280, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.bar_chart({"Carbs (g)": total_carbs, "Protein (g)": total_protein, "Fats (g)": total_fat})

    tabs = st.tabs([f"Day {d['day']}" for d in plan["days"]])
    for tab, day_info in zip(tabs, plan["days"]):
        with tab:
            for slot in ["breakfast", "mid_morning_snack", "lunch", "evening_snack", "dinner"]:
                meal = day_info.get(slot) or {}
                label = slot.replace("_", " ").title()
                name = meal.get("name", "—")
                cal = meal.get("calories", 0)
                tags = meal.get("tags", [])
                why = get_meal_explanation(tags, diet_rules)

                col_meal, col_swap = st.columns([4, 1])
                with col_meal:
                    st.markdown(f"**{label}** — {name} ({cal} kcal)")
                    st.markdown(f'<p class="why-meal">💡 {why}</p>', unsafe_allow_html=True)
                with col_swap:
                    if profile and name != "No suitable meal (restrictions)":
                        if st.button("🔄 Swap", key=f"swap_{day_info['day']}_{slot}"):
                            used = {day_info.get(s).get("name") for s in ["breakfast", "mid_morning_snack", "lunch", "evening_snack", "dinner"] if day_info.get(s) and day_info.get(s).get("name")}
                            new_meal = swap_meal(profile, SLOT_TO_MEAL_KEY[slot], used)
                            if len(new_meal) >= 2 and new_meal[0] != name:
                                day_info[slot] = {"name": new_meal[0], "calories": new_meal[1], "tags": list(new_meal[2]) if len(new_meal) > 2 else []}
                                st.session_state.diet_plan = plan
                                try:
                                    st.rerun()
                                except Exception:
                                    st.experimental_rerun()

# ----- 7. Export -----
if st.session_state.diet_plan is not None:
    st.header("7️⃣ Export")
    patient_name = st.session_state.get("patient_name", "Patient")
    conditions = st.session_state.conditions or []
    rules = st.session_state.diet_rules or []
    plan = st.session_state.diet_plan

    buf = export_to_pdf(patient_name, conditions, rules, plan)
    json_str = export_to_json(patient_name, conditions, rules, plan)

    col_pdf, col_json = st.columns(2)
    with col_pdf:
        st.download_button(
            "Download PDF",
            data=buf.getvalue(),
            file_name="AI-NutriCare-Diet-Plan.pdf",
            mime="application/pdf",
            key="dl_pdf",
        )
    with col_json:
        st.download_button(
            "Download JSON",
            data=json_str,
            file_name="AI-NutriCare-Diet-Plan.json",
            mime="application/json",
            key="dl_json",
        )

# Sidebar summary
with st.sidebar:
    st.markdown("### Pipeline Status")
    st.markdown("- ✅ Upload: " + ("Done" if st.session_state.report_data else "Pending"))
    st.markdown("- ✅ Extract: " + ("Done" if st.session_state.report_data else "Pending"))
    st.markdown("- ✅ Analyze: " + ("Done" if st.session_state.conditions else "Pending"))
    st.markdown("- ✅ Rules: " + ("Done" if st.session_state.diet_rules else "Pending"))
    st.markdown("- ✅ Plan: " + ("Done" if st.session_state.diet_plan else "Pending"))
    st.markdown("---")
    st.caption("AI-NutriCare — Academic prototype. Not a substitute for professional medical or dietary advice.")
