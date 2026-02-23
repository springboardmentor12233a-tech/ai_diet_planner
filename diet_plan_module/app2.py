import streamlit as st
import json
from diet_engine import (
    extract_text_from_pdf, extract_text_from_image,
    extract_metrics_with_llm, analyze_conditions,
    generate_diet_plan, generate_pdf_report,
    get_available_models, test_ollama_connection,
    RECOMMENDED_MODELS,
)

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --gd: #0d4a2e; --gm: #1a7a4a; --gl: #52c27d;
    --gold: #d4a843; --cream: #faf7f0;
    --surface: #ffffff; --text: #1c2a1e;
    --muted: #6b7c6d; --border: #d8e8dc;
    --danger: #c0392b; --warn: #e67e22;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--text); }
.stApp { background: linear-gradient(135deg, #f0f7f2 0%, #faf7f0 50%, #f0f5f7 100%); }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--gd) 0%, #0a3d25 100%) !important;
    border-right: 3px solid var(--gl);
}
section[data-testid="stSidebar"] * { color: #e8f5ec !important; }
section[data-testid="stSidebar"] label { color: #b8dfc4 !important; font-size: 0.85rem !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: var(--gold) !important; }

h1 { font-family: 'Playfair Display', serif !important; color: var(--gd) !important; }
h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--gm) !important; }

.hero {
    background: linear-gradient(135deg, var(--gd) 0%, var(--gm) 60%, #2ecc71 100%);
    border-radius: 20px; padding: 36px 44px; margin-bottom: 24px; position: relative; overflow: hidden;
}
.hero::before { content: '🥗'; position: absolute; right: 40px; top: 50%; transform: translateY(-50%); font-size: 5rem; opacity: 0.15; }
.hero h1 { color: white !important; font-size: 2.2rem; margin: 0; }
.hero p { color: rgba(255,255,255,0.85); font-size: 1rem; margin: 8px 0 0; }

.step-badge { background: var(--gm); color: white; border-radius: 50%; width: 28px; height: 28px;
    display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 8px; font-size: 0.85rem; }

.metric-card { background: linear-gradient(135deg, var(--gd), var(--gm)); border-radius: 12px;
    padding: 14px 16px; color: white !important; text-align: center; margin: 4px; }
.metric-card .val { font-size: 1.6rem; font-weight: 700; color: var(--gold) !important; }
.metric-card .lbl { font-size: 0.75rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px; }

.badge-d { background: #fdecea; color: #c0392b; border: 1px solid #f5b7b1; border-radius: 20px; padding: 3px 10px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin: 3px; }
.badge-w { background: #fef9e7; color: #d68910; border: 1px solid #f9e79f; border-radius: 20px; padding: 3px 10px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin: 3px; }
.badge-i { background: #eaf2ff; color: #1a5276; border: 1px solid #aed6f1; border-radius: 20px; padding: 3px 10px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin: 3px; }

.meal-box { background: #f7fdf9; border-left: 4px solid var(--gl); border-radius: 0 10px 10px 0; padding: 14px 18px; margin: 8px 0; }
.meal-title { font-weight: 700; color: var(--gd); font-size: 1rem; }
.meal-items { color: var(--muted); font-size: 0.88rem; margin: 4px 0; }
.nut-chip { background: var(--gd); color: white; border-radius: 6px; padding: 2px 8px; font-size: 0.78rem; display: inline-block; margin: 2px; }
.cal-badge { background: var(--gold); color: var(--gd); border-radius: 16px; padding: 2px 9px; font-size: 0.75rem; font-weight: 700; margin-left: 6px; }
.tip-text { color: var(--warn); font-size: 0.83rem; font-style: italic; margin-top: 5px; }

.divider { height: 2px; background: linear-gradient(90deg, var(--gl), transparent); margin: 20px 0; border-radius: 2px; }

.stButton > button { background: linear-gradient(135deg, var(--gm), var(--gd)) !important; color: white !important;
    border: none !important; border-radius: 10px !important; font-weight: 600 !important;
    padding: 10px 24px !important; transition: all 0.2s !important; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(13,74,46,0.3) !important; }
.stDownloadButton > button { background: linear-gradient(135deg, var(--gold), #e8b84b) !important;
    color: var(--gd) !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; }

.stTabs [data-baseweb="tab"][aria-selected="true"] { color: var(--gm) !important; border-bottom: 3px solid var(--gm) !important; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE INIT ──────────────────────────────────────────────────────
_defaults = {
    "metrics": {},
    "conditions": [],
    "severity": {},
    "diet_plan": None,
    "doctor_notes_text": "",
    "extracted_raw": "",
    "pdf_bytes": None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ AI Engine Settings")
    st.markdown("---")
    st.markdown("**Backend: Ollama (Local)**")
    st.caption("Your data stays private on your machine.")

    # Get installed models
    available = get_available_models()
    # Put recommended fast models at top
    fast_first = [m for m in ["gemma3:1b", "qwen2.5:1.5b", "qwen2.5:0.5b", "gemma3:4b", "phi3.5:mini"] if m in available]
    rest = [m for m in available if m not in fast_first]
    model_list = fast_first + rest if fast_first else available

    ollama_model = st.selectbox(
        "Model",
        model_list,
        help="gemma3:1b and qwen2.5:1.5b are fastest (5-12s per day)"
    )

    if st.button("🔍 Test Connection", use_container_width=True):
        with st.spinner("Testing..."):
            ok, msg = test_ollama_connection(ollama_model)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    st.markdown("---")
    st.markdown("### ⚡ Speed Tips")
    st.markdown("""
<div style='font-size:0.78rem; color:#b8dfc4; line-height:1.7;'>
<b>Fastest models:</b><br>
🥇 gemma3:1b (~5s/day)<br>
🥈 qwen2.5:1.5b (~8s/day)<br>
🥉 gemma3:4b (~12s/day)<br><br>
<b>Pull fast models:</b><br>
<code>ollama pull gemma3:1b</code><br>
<code>ollama pull qwen2.5:1.5b</code>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Plan Settings")
    diet_type = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian"], horizontal=True)
    plan_days = st.select_slider("Plan Duration (days)", options=[3, 5, 7], value=7)

    st.markdown("---")
    st.markdown("""
<div style='font-size:0.78rem; color:#b8dfc4; line-height:1.7;'>
<b>Conditions covered:</b><br>
🩸 Diabetes / Prediabetes<br>
💓 Hypertension<br>
🫀 High Cholesterol<br>
⚖️ Overweight / Obesity<br>
🔴 Anemia / Iron Deficiency<br>
🦋 Thyroid Disorders<br>
🫘 Kidney Issues<br>
+ More from doctor notes
</div>
""", unsafe_allow_html=True)


# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>AI-Powered Diet Planner</h1>
    <p>Personalized therapeutic meal plans based on your medical reports & health metrics</p>
</div>
""", unsafe_allow_html=True)


# ─── STEP 1: PATIENT INFO ────────────────────────────────────────────────────
st.markdown('<span class="step-badge">1</span> **Patient Information**', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    patient_name = st.text_input("Patient Name", placeholder="e.g. Rahul Sharma")
with c2:
    patient_age = st.number_input("Age", min_value=1, max_value=120, value=45)
with c3:
    patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─── STEP 2: HEALTH METRICS ──────────────────────────────────────────────────
st.markdown('<span class="step-badge">2</span> **Health Metrics**', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📄 Upload Report (PDF/Image)", "✏️ Enter Manually", "📊 View Current Metrics"])

with t1:
    uploaded_report = st.file_uploader(
        "Upload Medical Report", type=["pdf", "png", "jpg", "jpeg"],
        help="PDF or image of blood test / lab report",
        label_visibility="collapsed"
    )
    if uploaded_report:
        if st.button("🔍 Extract Metrics from Report", use_container_width=True):
            with st.spinner("Extracting text from file..."):
                try:
                    uploaded_report.seek(0)
                    if "pdf" in uploaded_report.type:
                        raw_text = extract_text_from_pdf(uploaded_report)
                    else:
                        raw_text = extract_text_from_image(uploaded_report)
                    st.session_state["extracted_raw"] = raw_text

                    if not raw_text.strip():
                        st.warning("⚠️ Could not extract text. Please enter metrics manually.")
                    else:
                        with st.expander("📄 Extracted text (preview)"):
                            st.text(raw_text[:800])
                        with st.spinner("Analyzing metrics with AI..."):
                            extracted = extract_metrics_with_llm(raw_text, ollama_model)
                        for k, v in extracted.items():
                            # Skip None and 0 (0 = not tested in lab reports)
                            if v is not None and v != 0:
                                st.session_state["metrics"][k] = v
                        found = sum(1 for v in extracted.values() if v is not None and v != 0)
                        st.success(f"✅ Extracted {found} metrics from report!")

                        # ── AUTO-EXTRACT DOCTOR NOTES from same report file ──
                        # Many lab reports include doctor notes at the bottom
                        # We pull any notes section automatically so user doesn't need to re-upload
                        notes_keywords = [
                            "doctor", "note", "advice", "recommend", "avoid",
                            "elevated", "high", "low", "diet", "reduce", "advised",
                            "physical", "activity", "sodium", "sugar", "weight"
                        ]
                        lines = raw_text.split("\n")
                        auto_notes_lines = []
                        capture = False
                        for line in lines:
                            line_lower = line.lower().strip()
                            # Start capturing after "doctor" or "note" heading
                            if any(kw in line_lower for kw in ["doctor", "notes", "advice", "recommendation"]):
                                capture = True
                            if capture and line.strip():
                                auto_notes_lines.append(line.strip("•● ").strip())
                            # Also capture any line that contains diet/health advice keywords
                            elif not capture and any(kw in line_lower for kw in notes_keywords[3:]):
                                auto_notes_lines.append(line.strip("•● ").strip())

                        if auto_notes_lines:
                            auto_notes_text = " ".join(auto_notes_lines)
                            existing = st.session_state.get("doctor_notes_text", "")
                            if auto_notes_text not in existing:
                                st.session_state["doctor_notes_text"] = (existing + " " + auto_notes_text).strip()
                            st.info(f"📋 Also found doctor notes in the report — auto-filled in Step 3!")
                except Exception as e:
                    st.error(f"❌ {e}")

with t2:
    st.markdown("Enter your values (leave at 0 if unknown):")
    ca, cb, cc = st.columns(3)
    with ca:
        st.markdown("**🩸 Blood Sugar**")
        g_fast = st.number_input("Fasting Glucose (mg/dL)", 0.0, 600.0, 0.0, 1.0)
        g_post = st.number_input("Post-Prandial Glucose (mg/dL)", 0.0, 600.0, 0.0, 1.0)
        hba1c = st.number_input("HbA1c (%)", 0.0, 20.0, 0.0, 0.1)
    with cb:
        st.markdown("**💓 Heart & BP**")
        sbp = st.number_input("Systolic BP (mmHg)", 0.0, 300.0, 0.0, 1.0)
        dbp = st.number_input("Diastolic BP (mmHg)", 0.0, 200.0, 0.0, 1.0)
        chol = st.number_input("Total Cholesterol (mg/dL)", 0.0, 600.0, 0.0, 1.0)
        ldl = st.number_input("LDL (mg/dL)", 0.0, 400.0, 0.0, 1.0)
        hdl = st.number_input("HDL (mg/dL)", 0.0, 200.0, 0.0, 1.0)
        trig = st.number_input("Triglycerides (mg/dL)", 0.0, 1000.0, 0.0, 1.0)
    with cc:
        st.markdown("**⚖️ Body & Others**")
        weight = st.number_input("Weight (kg)", 0.0, 250.0, 0.0, 0.5)
        height = st.number_input("Height (cm)", 0.0, 250.0, 0.0, 0.5)
        bmi_v = st.number_input("BMI (if known)", 0.0, 70.0, 0.0, 0.1)
        hgb = st.number_input("Hemoglobin (g/dL)", 0.0, 25.0, 0.0, 0.1)
        iron = st.number_input("Serum Iron / Ferritin", 0.0, 500.0, 0.0, 1.0)
        tsh = st.number_input("Thyroid TSH (mIU/L)", 0.0, 50.0, 0.0, 0.01)
        creat = st.number_input("Creatinine (mg/dL)", 0.0, 20.0, 0.0, 0.01)

    if st.button("💾 Save Metrics", use_container_width=True):
        manual = {
            "glucose_fasting": g_fast or None, "glucose_postprandial": g_post or None,
            "hba1c": hba1c or None, "systolic_bp": sbp or None, "diastolic_bp": dbp or None,
            "total_cholesterol": chol or None, "ldl": ldl or None, "hdl": hdl or None,
            "triglycerides": trig or None, "weight_kg": weight or None,
            "height_cm": height or None, "bmi": bmi_v or None, "hemoglobin": hgb or None,
            "iron": iron or None, "thyroid_tsh": tsh or None, "creatinine": creat or None,
        }
        for k, v in manual.items():
            if v:
                st.session_state["metrics"][k] = v
        if weight > 0 and height > 0 and not bmi_v:
            st.session_state["metrics"]["bmi"] = round(weight / ((height / 100) ** 2), 1)
        n = sum(1 for v in manual.values() if v)
        st.success(f"✅ Saved {n} metrics!")

with t3:
    m = st.session_state.get("metrics", {})
    display_map = {
        "glucose_fasting": ("Fasting Glucose", "mg/dL"), "hba1c": ("HbA1c", "%"),
        "systolic_bp": ("Systolic BP", "mmHg"), "diastolic_bp": ("Diastolic BP", "mmHg"),
        "bmi": ("BMI", ""), "total_cholesterol": ("Cholesterol", "mg/dL"),
        "hemoglobin": ("Hemoglobin", "g/dL"), "weight_kg": ("Weight", "kg"),
        "ldl": ("LDL", "mg/dL"), "hdl": ("HDL", "mg/dL"),
        "triglycerides": ("Triglycerides", "mg/dL"), "thyroid_tsh": ("TSH", "mIU/L"),
    }
    if m:
        cols = st.columns(4)
        i = 0
        for key, (lbl, unit) in display_map.items():
            val = m.get(key)
            if val is not None:
                with cols[i % 4]:
                    st.markdown(f"""<div class="metric-card">
                        <div class="val">{val}</div>
                        <div class="lbl">{lbl}{' ' + unit if unit else ''}</div>
                    </div>""", unsafe_allow_html=True)
                i += 1
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All Metrics"):
            st.session_state["metrics"] = {}
            st.rerun()
    else:
        st.info("No metrics entered yet. Upload a report or enter manually above.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─── STEP 3: DOCTOR NOTES ────────────────────────────────────────────────────
st.markdown('<span class="step-badge">3</span> **Doctor\'s Notes & Recommendations**', unsafe_allow_html=True)

nt1, nt2 = st.tabs(["✏️ Type Notes", "📄 Upload Notes (PDF/Image)"])
with nt1:
    doctor_notes_typed = st.text_area(
        "Doctor Notes", label_visibility="collapsed",
        placeholder="e.g. High blood pressure. Glucose is elevated. Iron diet recommended. Avoid sugar and refined carbs. Low sodium diet required...",
        height=110
    )
with nt2:
    notes_file = st.file_uploader("Upload prescription/notes", type=["pdf", "png", "jpg", "jpeg"],
                                   key="notes_up", label_visibility="collapsed")
    if notes_file:
        if st.button("📖 Extract Notes"):
            with st.spinner("Extracting..."):
                try:
                    notes_file.seek(0)
                    if "pdf" in notes_file.type:
                        nt = extract_text_from_pdf(notes_file)
                    else:
                        nt = extract_text_from_image(notes_file)
                    st.session_state["doctor_notes_text"] = str(nt)
                    st.success("✅ Extracted!")
                    st.text(nt[:400])
                except Exception as e:
                    st.error(f"❌ {e}")

# Always a clean string merge
_typed = str(doctor_notes_typed or "")
_uploaded = str(st.session_state.get("doctor_notes_text") or "")
final_notes = (_typed + " " + _uploaded).strip()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─── STEP 4: GENERATE ────────────────────────────────────────────────────────
st.markdown('<span class="step-badge">4</span> **Generate Diet Plan**', unsafe_allow_html=True)

metrics_now = st.session_state.get("metrics", {})
if metrics_now or final_notes:
    analysis = analyze_conditions(metrics_now, final_notes)
    conds_found = analysis["conditions"]
    if conds_found:
        st.markdown("**Identified Conditions:**")
        badges = ""
        for c in conds_found:
            cl = c.lower()
            if any(x in cl for x in ["diabetes", "hypertension", "obesity", "high cholesterol", "anemia"]):
                badges += f'<span class="badge-d">⚠️ {c}</span>'
            elif any(x in cl for x in ["borderline", "elevated", "prediabetes", "overweight"]):
                badges += f'<span class="badge-w">⚡ {c}</span>'
            else:
                badges += f'<span class="badge-i">ℹ️ {c}</span>'
        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.info("No conditions detected yet. Add metrics or doctor notes to identify conditions.")

est_time = plan_days * 12  # ~12s per day for small models
st.caption(f"⏱️ Estimated time with {ollama_model}: ~{est_time//60}m {est_time%60}s for {plan_days} days")

gen_col, _ = st.columns([2, 1])
with gen_col:
    generate_btn = st.button(
        f"🚀 Generate {plan_days}-Day {diet_type} Diet Plan",
        use_container_width=True, type="primary"
    )

if generate_btn:
    if not metrics_now and not final_notes:
        st.error("❌ Please add health metrics or doctor notes first!")
    else:
        metrics_now["gender"] = patient_gender
        metrics_now["age"] = patient_age
        analysis = analyze_conditions(metrics_now, final_notes)

        st.markdown("---")
        status_text = st.empty()
        progress_bar = st.progress(0)

        def on_progress(day, total):
            pct = int((day - 1) / total * 100)
            progress_bar.progress(pct)
            status_text.markdown(f"⏳ Generating Day {day} of {total}... please wait")

        try:
            diet_plan = generate_diet_plan(
                metrics=metrics_now,
                conditions=analysis["conditions"],
                severity=analysis["severity"],
                doctor_notes=final_notes,
                diet_type=diet_type,
                days=plan_days,
                patient_name=patient_name,
                model=ollama_model,
                progress_callback=on_progress
            )
            progress_bar.progress(100)
            status_text.markdown("✅ **Diet plan generated successfully!**")

            st.session_state["diet_plan"] = diet_plan
            st.session_state["conditions"] = analysis["conditions"]
            st.session_state["severity"] = analysis["severity"]
            st.rerun()

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            err = str(e)
            st.error(f"❌ {err}")
            if "timed out" in err.lower() or "timeout" in err.lower():
                st.info("💡 **To fix timeout:**\n"
                        "1. Pull a faster model: `ollama pull gemma3:1b`\n"
                        "2. Select it in the sidebar\n"
                        "3. Try again")
            elif "cannot connect" in err.lower():
                st.info("💡 Start Ollama: run `ollama serve` in a terminal")


# ─── DISPLAY DIET PLAN ───────────────────────────────────────────────────────
diet_plan = st.session_state.get("diet_plan")

if diet_plan:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📋 Your Personalized Diet Plan")

    mc1, mc2, mc3, mc4 = st.columns(4)
    meta = [
        (diet_plan.get("daily_calories", "—"), "Daily Calories (kcal)"),
        (plan_days, "Days Planned"),
        ("5", "Meals Per Day"),
        (len(st.session_state.get("conditions", [])), "Conditions Addressed"),
    ]
    for col, (val, lbl) in zip([mc1, mc2, mc3, mc4], meta):
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="val">{val}</div><div class="lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if diet_plan.get("summary"):
        st.info(f"📌 **Dietary Strategy:** {diet_plan['summary']}")

    rc, ac = st.columns(2)
    with rc:
        if diet_plan.get("key_recommendations"):
            st.markdown("**✅ Recommended**")
            for r in diet_plan["key_recommendations"]:
                st.markdown(f"• {r}")
    with ac:
        if diet_plan.get("key_restrictions"):
            st.markdown("**🚫 Avoid**")
            for a in diet_plan["key_restrictions"]:
                st.markdown(f"• {a}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Day tabs
    meal_plan = diet_plan.get("meal_plan", [])
    if meal_plan:
        day_tabs = st.tabs([d.get("day_name", f"Day {d['day']}") for d in meal_plan])

        meal_icons = {
            "breakfast": "🌅", "mid_morning_snack": "🍎",
            "lunch": "🍽️", "evening_snack": "☕", "dinner": "🌙"
        }
        meal_labels = {
            "breakfast": "Breakfast", "mid_morning_snack": "Mid-Morning Snack",
            "lunch": "Lunch", "evening_snack": "Evening Snack", "dinner": "Dinner"
        }

        for tab, day_data in zip(day_tabs, meal_plan):
            with tab:
                total_cal = day_data.get("total_calories", "")
                water = day_data.get("water_intake", "8-10 glasses")
                tip = day_data.get("daily_tip", "")

                st.markdown(f"""
                <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:10px;">
                    <span style="background:#1a7a4a; color:white; padding:3px 12px; border-radius:16px; font-size:0.85rem;">🔥 {total_cal} kcal</span>
                    <span style="background:#2e86c1; color:white; padding:3px 12px; border-radius:16px; font-size:0.85rem;">💧 {water}</span>
                    {f'<span style="background:#f39c12; color:white; padding:3px 12px; border-radius:16px; font-size:0.85rem;">💡 {tip}</span>' if tip else ''}
                </div>
                """, unsafe_allow_html=True)

                meals = day_data.get("meals", {})
                for mk, icon in meal_icons.items():
                    meal = meals.get(mk)
                    if not meal or not isinstance(meal, dict):
                        continue

                    name = meal.get("name", "")
                    cal = meal.get("calories", "")
                    items = meal.get("items", [])
                    protein = meal.get("protein", "")
                    carbs = meal.get("carbs", "")
                    fat = meal.get("fat", "")

                    # Sanitize items — LLM may return dicts, nested lists, etc.
                    def _item_to_str(x):
                        if isinstance(x, str):
                            return x
                        if isinstance(x, dict):
                            # e.g. {"item": "Oats", "qty": "1 bowl"} or {"name": "Apple", "quantity": "1"}
                            parts = []
                            for key in ["item", "name", "food", "description"]:
                                if key in x:
                                    parts.append(str(x[key]))
                                    break
                            for key in ["qty", "quantity", "amount", "portion"]:
                                if key in x:
                                    parts.append(f"({x[key]})")
                                    break
                            return " ".join(parts) if parts else str(x)
                        return str(x)
                    safe_items = [_item_to_str(it) for it in items] if items else []
                    items_str = " &nbsp;|&nbsp; ".join(safe_items) if safe_items else ""
                    nut_html = ""
                    if protein:
                        nut_html += f'<span class="nut-chip">Protein: {protein}</span>'
                    if carbs:
                        nut_html += f'<span class="nut-chip">Carbs: {carbs}</span>'
                    if fat:
                        nut_html += f'<span class="nut-chip">Fat: {fat}</span>'

                    st.markdown(f"""
                    <div class="meal-box">
                        <div class="meal-title">{icon} {meal_labels[mk]} — {name}
                            <span class="cal-badge">🔥 {cal} kcal</span>
                        </div>
                        <div class="meal-items">{items_str}</div>
                        {f'<div style="margin-top:6px;">{nut_html}</div>' if nut_html else ''}
                    </div>
                    """, unsafe_allow_html=True)

    # Tips & Avoid
    tc, av = st.columns(2)
    with tc:
        if diet_plan.get("general_tips"):
            st.markdown("### 💡 Health Tips")
            for t in diet_plan["general_tips"]:
                st.markdown(f"• {t}")
    with av:
        if diet_plan.get("foods_to_avoid"):
            st.markdown("### 🚫 Strictly Avoid")
            for f in diet_plan["foods_to_avoid"]:
                st.markdown(f"• {f}")

    # ─── DOWNLOAD ────────────────────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📥 Download Your Diet Plan")

    dl1, dl2 = st.columns(2)
    with dl1:
        json_str = json.dumps(diet_plan, indent=2, ensure_ascii=False)
        st.download_button(
            "⬇️ Download JSON",
            data=json_str,
            file_name=f"diet_plan_{(patient_name or 'patient').replace(' ','_')}_{plan_days}days.json",
            mime="application/json",
            use_container_width=True
        )
    with dl2:
        if st.button("📄 Generate PDF", use_container_width=True, key="gen_pdf"):
            with st.spinner("Building PDF..."):
                try:
                    pdf = generate_pdf_report(
                        patient_name=patient_name,
                        conditions=st.session_state.get("conditions", []),
                        metrics=st.session_state.get("metrics", {}),
                        diet_plan=diet_plan,
                        diet_type=diet_type,
                        days=plan_days
                    )
                    st.session_state["pdf_bytes"] = pdf
                    st.success("✅ PDF ready to download!")
                except Exception as e:
                    st.error(f"❌ {e}")

    if st.session_state.get("pdf_bytes"):
        st.download_button(
            "⬇️ Download PDF Diet Plan",
            data=st.session_state["pdf_bytes"],
            file_name=f"diet_plan_{(patient_name or 'patient').replace(' ','_')}_{plan_days}days.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_pdf"
        )

    if st.button("🔄 Generate New Plan", key="regen"):
        st.session_state["diet_plan"] = None
        st.session_state["pdf_bytes"] = None
        st.rerun()

    st.markdown("""<br>
    <div style="text-align:center; color:#6b7c6d; font-size:0.8rem; padding:14px;
        background:#f8fdf9; border-radius:10px; border:1px solid #d8e8dc;">
        ⚠️ <b>Medical Disclaimer:</b> This AI-generated diet plan is for general guidance only.
        Always consult your doctor or registered dietitian before making significant dietary changes.
    </div>""", unsafe_allow_html=True)