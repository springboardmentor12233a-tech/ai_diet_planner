# import json
# import re
# import requests

# # ─── LLM BACKEND ────────────────────────────────────────────────────────────

# RECOMMENDED_MODELS = [
#     "gemma3:1b", "qwen2.5:0.5b", "qwen2.5:1.5b",
#     "gemma3:4b", "phi3:mini", "phi3.5:mini", "mistral", "llama3",
# ]


# def call_ollama(prompt: str, model: str = "gemma3:1b", system: str = "", timeout: int = 90) -> str:
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "system": system,
#         "stream": False,
#         "options": {
#             "temperature": 0.1,
#             "num_predict": 800,   # Key: limit tokens per call for speed
#             "top_p": 0.9,
#             "repeat_penalty": 1.1,
#             "num_ctx": 2048,      # Smaller context = much faster inference
#         }
#     }
#     try:
#         resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=timeout)
#         resp.raise_for_status()
#         return resp.json().get("response", "").strip()
#     except requests.exceptions.Timeout:
#         raise RuntimeError(
#             f"Model '{model}' timed out after {timeout}s.\n"
#             f"Recommended fast models: gemma3:1b, qwen2.5:1.5b\n"
#             f"Pull with: ollama pull gemma3:1b"
#         )
#     except requests.exceptions.ConnectionError:
#         raise RuntimeError("Cannot connect to Ollama. Run: ollama serve")
#     except Exception as e:
#         raise RuntimeError(f"Ollama error: {e}")


# def get_available_models() -> list:
#     try:
#         resp = requests.get("http://localhost:11434/api/tags", timeout=5)
#         models = [m["name"] for m in resp.json().get("models", [])]
#         return models if models else RECOMMENDED_MODELS
#     except:
#         return RECOMMENDED_MODELS


# def test_ollama_connection(model: str) -> tuple:
#     try:
#         result = call_ollama("Reply with just: OK", model=model, timeout=30)
#         return True, f"Connected! Model '{model}' is ready."
#     except RuntimeError as e:
#         return False, str(e)


# # ─── JSON HELPER ─────────────────────────────────────────────────────────────

# def safe_parse_json(text: str) -> dict:
#     text = text.strip()
#     text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
#     text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
#     try:
#         return json.loads(text)
#     except:
#         pass
#     match = re.search(r'\{.*\}', text, re.DOTALL)
#     if match:
#         try:
#             return json.loads(match.group())
#         except:
#             cleaned = re.sub(r',\s*([}\]])', r'\1', match.group())
#             try:
#                 return json.loads(cleaned)
#             except:
#                 pass
#     return {}


# # ─── METRIC EXTRACTION ───────────────────────────────────────────────────────

# def extract_text_from_pdf(pdf_file) -> str:
#     try:
#         import pdfplumber, io
#         with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
#             return "\n".join(page.extract_text() or "" for page in pdf.pages)
#     except ImportError:
#         try:
#             import pypdf, io
#             reader = pypdf.PdfReader(io.BytesIO(pdf_file.read()))
#             return "\n".join(page.extract_text() or "" for page in reader.pages)
#         except ImportError:
#             raise RuntimeError("Install pdfplumber: pip install pdfplumber")


# def extract_text_from_image(image_file) -> str:
#     try:
#         import pytesseract
#         from PIL import Image
#         import io
#         img = Image.open(io.BytesIO(image_file.read()))
#         return pytesseract.image_to_string(img)
#     except ImportError:
#         raise RuntimeError("Install pytesseract: pip install pytesseract pillow")


# def extract_metrics_with_llm(raw_text: str, model: str) -> dict:
#     text = raw_text[:1200]
#     prompt = f"""Extract medical values from this report. Return ONLY a JSON object.
# Keys: glucose_fasting, glucose_postprandial, hba1c, systolic_bp, diastolic_bp,
# total_cholesterol, ldl, hdl, triglycerides, bmi, weight_kg, height_cm,
# creatinine, hemoglobin, iron, vitamin_d, thyroid_tsh
# Use null for missing values.

# Report: {text}

# JSON:"""
#     response = call_ollama(prompt, model=model,
#                            system="Extract medical data, return only JSON.",
#                            timeout=60)
#     result = safe_parse_json(response)
#     cleaned = {}
#     for k, v in result.items():
#         if v is None or v == "null":
#             cleaned[k] = None
#         else:
#             try:
#                 cleaned[k] = float(str(v).replace(",", "").strip())
#             except:
#                 cleaned[k] = None
#     return cleaned


# # ─── CONDITION ANALYSIS (Rule-based — instant) ───────────────────────────────

# def analyze_conditions(metrics: dict, doctor_notes: str = "") -> dict:
#     conditions = []
#     severity = {}

#     g = metrics.get("glucose_fasting")
#     hba1c = metrics.get("hba1c")
#     sbp = metrics.get("systolic_bp")
#     dbp = metrics.get("diastolic_bp")
#     bmi = metrics.get("bmi")
#     chol = metrics.get("total_cholesterol")
#     ldl = metrics.get("ldl")
#     trig = metrics.get("triglycerides")
#     hgb = metrics.get("hemoglobin")
#     tsh = metrics.get("thyroid_tsh")
#     cr = metrics.get("creatinine")

#     if (g and g >= 126) or (hba1c and hba1c >= 6.5):
#         conditions.append("Type 2 Diabetes")
#         severity["diabetes"] = "high" if (g and g >= 200) or (hba1c and hba1c >= 8) else "moderate"
#     elif (g and 100 <= g < 126) or (hba1c and 5.7 <= hba1c < 6.5):
#         conditions.append("Prediabetes")
#         severity["diabetes"] = "low"

#     if sbp and dbp:
#         if sbp >= 140 or dbp >= 90:
#             conditions.append("Hypertension")
#             severity["hypertension"] = "high" if sbp >= 160 else "moderate"
#         elif sbp >= 130 or dbp >= 80:
#             conditions.append("Elevated Blood Pressure")
#             severity["hypertension"] = "low"

#     if (chol and chol >= 240) or (ldl and ldl >= 160) or (trig and trig >= 200):
#         conditions.append("High Cholesterol")
#         severity["cholesterol"] = "high" if (ldl and ldl >= 190) else "moderate"
#     elif (chol and chol >= 200) or (ldl and ldl >= 130):
#         conditions.append("Borderline High Cholesterol")
#         severity["cholesterol"] = "low"

#     if bmi:
#         if bmi >= 30:
#             conditions.append("Obesity")
#             severity["weight"] = "high" if bmi >= 35 else "moderate"
#         elif bmi >= 25:
#             conditions.append("Overweight")
#             severity["weight"] = "low"

#     if hgb:
#         gender = metrics.get("gender", "").lower()
#         threshold = 12 if gender == "female" else 13
#         if hgb < threshold:
#             conditions.append("Anemia")
#             severity["anemia"] = "high" if hgb < 10 else "low"

#     if tsh:
#         if tsh > 4.5:
#             conditions.append("Hypothyroidism")
#         elif tsh < 0.4:
#             conditions.append("Hyperthyroidism")

#     if cr and cr > 1.3:
#         conditions.append("Elevated Creatinine (Kidney)")

#     notes = (doctor_notes or "").lower()
#     note_map = {
#         "iron": "Iron Deficiency", "anaemia": "Anemia", "anemia": "Anemia",
#         "thyroid": "Thyroid Disorder", "hypothyroid": "Hypothyroidism",
#         "kidney": "Kidney Issue", "renal": "Kidney Issue",
#         "uric acid": "High Uric Acid", "gout": "High Uric Acid / Gout",
#         "pcod": "PCOD/PCOS", "pcos": "PCOD/PCOS",
#         "fatty liver": "Fatty Liver", "vitamin d": "Vitamin D Deficiency",
#         "b12": "Vitamin B12 Deficiency",
#     }
#     for keyword, condition in note_map.items():
#         if keyword in notes and condition not in conditions:
#             conditions.append(condition)

#     return {"conditions": conditions, "severity": severity}


# # ─── DIET RULES (instant, no LLM) ────────────────────────────────────────────

# CONDITION_RULES = {
#     "diabetes": "Low GI only. No sugar/white rice/maida/sweet fruits/juices. Use brown rice, multigrain roti, oats, methi, bitter gourd. Small frequent meals.",
#     "hypertension": "Low sodium. No pickles/papad/canned foods. Include banana, spinach, garlic, flaxseeds.",
#     "cholesterol": "No fried food/ghee/butter. Include oats, flaxseeds, walnuts. Use mustard oil.",
#     "weight": "Calorie deficit. High fiber, high protein. No junk/fried food. Large vegetable portions.",
#     "anemia": "Iron-rich: spinach, beetroot, dates, rajma, jaggery. Add Vit C for absorption. Cook in iron kadhai.",
#     "kidney": "Low potassium/phosphorus. Limit: banana, tomato, potato, dairy. Small protein portions.",
#     "thyroid": "Iodized salt. Selenium-rich foods. Avoid excess raw cruciferous vegetables.",
# }

# _SEVERITY_KEY_MAP = {
#     "type 2 diabetes": "diabetes", "prediabetes": "diabetes",
#     "hypertension": "hypertension", "elevated blood pressure": "hypertension",
#     "high cholesterol": "cholesterol", "borderline high cholesterol": "cholesterol",
#     "obesity": "weight", "overweight": "weight",
#     "anemia": "anemia", "iron deficiency": "anemia",
#     "kidney issue": "kidney", "elevated creatinine (kidney)": "kidney",
#     "hypothyroidism": "thyroid", "hyperthyroidism": "thyroid",
# }

# VEG_FOODS = "Indian vegetarian: dal, paneer, tofu, sprouts, chana, rajma, sabzi, curd, buttermilk, multigrain roti, brown rice, oats, poha, idli, upma, sambar, methi, palak."
# NONVEG_FOODS = "Indian: grilled/boiled chicken, eggs, fish (rohu/surmai), along with dal, sabzi, curd, multigrain roti, brown rice, oats, poha."


# def _get_condition_rules(conditions: list) -> str:
#     seen = set()
#     rules = []
#     for c in conditions:
#         key = _SEVERITY_KEY_MAP.get(c.lower())
#         if key and key not in seen and key in CONDITION_RULES:
#             rules.append(CONDITION_RULES[key])
#             seen.add(key)
#     return " | ".join(rules) if rules else "Balanced healthy Indian diet."


# def _recs_and_avoid(conditions: list, diet_type: str):
#     recs = [
#         "Drink 8-10 glasses of water daily",
#         "Eat every 3-4 hours — no skipping meals",
#         "Include fiber-rich food in every meal",
#         "Use small plates to control portions",
#     ]
#     avoid = ["Processed/packaged foods", "Excess oil & fried foods", "Late night eating"]

#     cl = [c.lower() for c in conditions]
#     if any("diabetes" in c for c in cl):
#         recs += ["Low GI foods only", "Include methi/karela/cinnamon", "Walk 15 min after meals"]
#         avoid += ["Sugar, sweets, cold drinks", "White rice, maida, bread", "Sweet fruits & juices"]
#     if any("hypertension" in c or "blood pressure" in c for c in cl):
#         recs += ["Use sendha namak / low sodium salt", "Include potassium-rich foods"]
#         avoid += ["Pickles, papad, achaar", "Extra salt at table"]
#     if any("cholesterol" in c for c in cl):
#         recs += ["Oats daily for breakfast", "Include flaxseeds & walnuts"]
#         avoid += ["Ghee, butter, cream", "Full cream dairy, red meat"]
#     if any("obes" in c or "overweight" in c for c in cl):
#         recs += ["High protein breakfast", "30 min walk daily"]
#         avoid += ["Fried snacks, desserts", "Sugary beverages"]
#     if any("anemia" in c or "iron" in c for c in cl):
#         recs += ["Spinach, dates, beetroot daily", "Lemon/amla with iron-rich meals"]
#         avoid += ["Tea/coffee right after meals", "Excess calcium with iron meals"]
#     if diet_type == "Vegetarian":
#         recs += ["Dal or legumes twice daily for protein"]
#     else:
#         recs += ["Prefer grilled/boiled over fried protein", "Fish 2-3x/week for omega-3"]
#     return recs[:8], avoid[:8]


# def _general_tips(conditions: list) -> list:
#     tips = [
#         "Sleep 7-8 hours — poor sleep worsens blood sugar & weight",
#         "Manage stress: yoga, meditation, or 10 min deep breathing daily",
#         "Cook at home as much as possible",
#         "Don't skip meals — it leads to overeating",
#         "Read food labels — watch for hidden sugar and sodium",
#     ]
#     cl = [c.lower() for c in conditions]
#     if any("diabetes" in c for c in cl):
#         tips.append("Keep a food diary to track blood sugar responses to meals")
#     if any("hypertension" in c or "blood pressure" in c for c in cl):
#         tips.append("Monitor BP at the same time each morning")
#     if any("obes" in c or "overweight" in c for c in cl):
#         tips.append("Weigh yourself weekly (same time, same conditions)")
#     return tips


# def _foods_to_avoid(conditions: list) -> list:
#     avoid = ["Maida products (bread, biscuits, naan)", "Packaged chips & namkeen",
#              "Cold drinks & soda", "Excess oil & butter"]
#     cl = [c.lower() for c in conditions]
#     if any("diabetes" in c for c in cl):
#         avoid += ["White rice (or max ½ cup)", "Sugar, jaggery excess", "Mango, banana, grapes, chikoo, fruit juice"]
#     if any("cholesterol" in c for c in cl):
#         avoid += ["Vanaspati, coconut oil", "Red meat, organ meats"]
#     if any("hypertension" in c or "blood pressure" in c for c in cl):
#         avoid += ["Pickles, canned/preserved foods", "High-sodium sauces"]
#     return avoid


# # ─── FALLBACK MEALS ──────────────────────────────────────────────────────────

# def _fallback_day(day: int, diet_type: str, calories: int, conditions: list) -> dict:
#     is_diabetic = any("diabetes" in c.lower() for c in conditions)
#     rice = "Brown rice (½ cup)" if is_diabetic else "Rice (¾ cup)"

#     veg_days = [
#         {"breakfast": {"name": "Oats Upma", "items": ["Oats upma (1 bowl)", "Sprouts (½ cup)", "Green tea"], "calories": 280, "protein": "10g", "carbs": "38g", "fat": "6g"},
#          "mid_morning": {"name": "Fruit & Nuts", "items": ["Apple (1)", "Walnuts (4-5)"], "calories": 150},
#          "lunch": {"name": "Dal Rice & Sabzi", "items": ["Moong dal (1 cup)", rice, "Mixed sabzi (1 cup)", "Curd (½ cup)"], "calories": 420, "protein": "18g", "carbs": "62g", "fat": "8g"},
#          "evening": {"name": "Buttermilk & Chana", "items": ["Buttermilk (1 glass)", "Roasted chana (30g)"], "calories": 130},
#          "dinner": {"name": "Roti & Paneer Sabzi", "items": ["Multigrain roti (2)", "Paneer sabzi (1 cup)", "Salad"], "calories": 380, "protein": "20g", "carbs": "45g", "fat": "12g"}},
#         {"breakfast": {"name": "Methi Paratha & Curd", "items": ["Methi paratha (2 small)", "Low-fat curd (1 cup)", "Cucumber"], "calories": 300, "protein": "12g", "carbs": "42g", "fat": "8g"},
#          "mid_morning": {"name": "Coconut Water & Almonds", "items": ["Coconut water (1 glass)", "Almonds (6)"], "calories": 120},
#          "lunch": {"name": "Rajma Chawal", "items": ["Rajma (1 cup)", rice, "Onion salad", "Buttermilk"], "calories": 440, "protein": "20g", "carbs": "65g", "fat": "6g"},
#          "evening": {"name": "Sprouts Chaat", "items": ["Mixed sprouts (1 cup)", "Lemon juice", "Coriander"], "calories": 140},
#          "dinner": {"name": "Palak Dal & Roti", "items": ["Palak dal (1 cup)", "Multigrain roti (2)", "Salad"], "calories": 360, "protein": "18g", "carbs": "50g", "fat": "8g"}},
#         {"breakfast": {"name": "Vegetable Poha", "items": ["Poha with veggies (1 bowl)", "Sprouts (¼ cup)", "Lemon tea"], "calories": 270, "protein": "8g", "carbs": "44g", "fat": "5g"},
#          "mid_morning": {"name": "Guava & Seeds", "items": ["Guava (1)", "Pumpkin seeds (1 tbsp)"], "calories": 110},
#          "lunch": {"name": "Chana Dal Thali", "items": ["Chana dal (1 cup)", "Multigrain roti (2)", "Sabzi (1 cup)", "Salad"], "calories": 430, "protein": "20g", "carbs": "60g", "fat": "7g"},
#          "evening": {"name": "Roasted Makhana", "items": ["Roasted makhana (30g)", "Herbal tea"], "calories": 120},
#          "dinner": {"name": "Mixed Dal & Roti", "items": ["Mixed dal (1 cup)", "Roti (2)", "Stir-fry veggies (1 cup)"], "calories": 370, "protein": "19g", "carbs": "50g", "fat": "8g"}},
#         {"breakfast": {"name": "Idli Sambar", "items": ["Steamed idli (3)", "Sambar (1 cup)", "Coconut chutney (1 tbsp)"], "calories": 290, "protein": "10g", "carbs": "48g", "fat": "5g"},
#          "mid_morning": {"name": "Orange & Walnuts", "items": ["Orange (1)", "Walnuts (4)"], "calories": 130},
#          "lunch": {"name": "Palak Paneer & Rice", "items": ["Palak paneer (1 cup)", rice, "Salad", "Curd (½ cup)"], "calories": 450, "protein": "22g", "carbs": "56g", "fat": "14g"},
#          "evening": {"name": "Chana Chaat", "items": ["Boiled chana (½ cup)", "Onion, tomato, lemon"], "calories": 140},
#          "dinner": {"name": "Moong Dal Khichdi", "items": ["Moong dal khichdi (1.5 cups)", "Curd (½ cup)", "Pickle (1 tsp)"], "calories": 360, "protein": "16g", "carbs": "52g", "fat": "6g"}},
#         {"breakfast": {"name": "Besan Chilla", "items": ["Besan chilla (2)", "Mint chutney", "Green tea"], "calories": 260, "protein": "14g", "carbs": "30g", "fat": "8g"},
#          "mid_morning": {"name": "Pomegranate", "items": ["Pomegranate (½ cup)", "Flaxseeds (1 tsp)"], "calories": 100},
#          "lunch": {"name": "Lobia Dal Roti", "items": ["Lobia (black-eyed peas) (1 cup)", "Multigrain roti (2)", "Salad"], "calories": 400, "protein": "18g", "carbs": "58g", "fat": "6g"},
#          "evening": {"name": "Curd with Seeds", "items": ["Low-fat curd (1 cup)", "Chia seeds (1 tsp)"], "calories": 120},
#          "dinner": {"name": "Tofu Bhurji & Roti", "items": ["Tofu bhurji (1 cup)", "Roti (2)", "Stir-fry veggies"], "calories": 380, "protein": "22g", "carbs": "44g", "fat": "12g"}},
#         {"breakfast": {"name": "Dalia (Broken Wheat) Upma", "items": ["Dalia upma (1 bowl)", "Boiled egg / paneer (50g)", "Green tea"], "calories": 285, "protein": "12g", "carbs": "40g", "fat": "6g"},
#          "mid_morning": {"name": "Pear & Almonds", "items": ["Pear (1)", "Almonds (6)"], "calories": 130},
#          "lunch": {"name": "Toor Dal & Sabzi", "items": ["Toor dal (1 cup)", rice, "Bhindi/any sabzi (1 cup)", "Curd"], "calories": 420, "protein": "18g", "carbs": "60g", "fat": "7g"},
#          "evening": {"name": "Roasted Chana & Amla", "items": ["Roasted chana (30g)", "Amla juice (small)"], "calories": 130},
#          "dinner": {"name": "Vegetable Khichdi", "items": ["Moong-rice khichdi (1.5 cup)", "Curd (½ cup)", "Papad (1, roasted)"], "calories": 350, "protein": "15g", "carbs": "50g", "fat": "6g"}},
#         {"breakfast": {"name": "Rava Upma", "items": ["Rava upma with veggies (1 bowl)", "Sprouts (¼ cup)", "Lemon water"], "calories": 270, "protein": "9g", "carbs": "42g", "fat": "6g"},
#          "mid_morning": {"name": "Banana Lassi (small)", "items": ["Banana (½)", "Low-fat curd lassi (1 cup, no sugar)"], "calories": 140},
#          "lunch": {"name": "Masoor Dal Thali", "items": ["Masoor dal (1 cup)", "Multigrain roti (2)", "Salad", "Sabzi (1 cup)"], "calories": 430, "protein": "19g", "carbs": "60g", "fat": "7g"},
#          "evening": {"name": "Makhana & Herbal Tea", "items": ["Roasted makhana (25g)", "Herbal tea (1 cup)"], "calories": 110},
#          "dinner": {"name": "Paneer Stir-fry & Roti", "items": ["Paneer stir-fry (100g paneer)", "Roti (2)", "Salad"], "calories": 390, "protein": "24g", "carbs": "40g", "fat": "14g"}},
#     ]

#     nonveg_days = [
#         {"breakfast": {"name": "Egg Veggie Scramble", "items": ["Scrambled eggs (2)", "Brown bread (2 slices)", "Green tea"], "calories": 300, "protein": "16g", "carbs": "30g", "fat": "10g"},
#          "mid_morning": {"name": "Fruit & Nuts", "items": ["Guava (1)", "Almonds (6)"], "calories": 140},
#          "lunch": {"name": "Chicken Dal Thali", "items": ["Grilled chicken (100g)", "Dal (1 cup)", rice, "Salad"], "calories": 450, "protein": "35g", "carbs": "50g", "fat": "8g"},
#          "evening": {"name": "Buttermilk & Makhana", "items": ["Buttermilk (1 glass)", "Roasted makhana (25g)"], "calories": 130},
#          "dinner": {"name": "Fish Curry & Roti", "items": ["Fish curry (100g fish)", "Multigrain roti (2)", "Sabzi (1 cup)"], "calories": 390, "protein": "28g", "carbs": "42g", "fat": "10g"}},
#         {"breakfast": {"name": "Poha with Egg", "items": ["Poha (1 bowl)", "Boiled egg (1)", "Green tea"], "calories": 290, "protein": "14g", "carbs": "40g", "fat": "7g"},
#          "mid_morning": {"name": "Coconut Water & Nuts", "items": ["Coconut water (1 glass)", "Walnuts (4)"], "calories": 130},
#          "lunch": {"name": "Chicken Roti Bowl", "items": ["Grilled chicken (100g)", "Multigrain roti (2)", "Dal (½ cup)", "Salad"], "calories": 430, "protein": "32g", "carbs": "46g", "fat": "9g"},
#          "evening": {"name": "Sprouts Chaat", "items": ["Sprouts (1 cup)", "Lemon juice"], "calories": 140},
#          "dinner": {"name": "Egg Curry & Roti", "items": ["Egg curry (2 eggs)", "Roti (2)", "Sabzi (1 cup)"], "calories": 380, "protein": "22g", "carbs": "44g", "fat": "12g"}},
#         {"breakfast": {"name": "Egg Oats Bowl", "items": ["Oats (½ cup)", "Boiled egg (2)", "Lemon tea"], "calories": 310, "protein": "18g", "carbs": "36g", "fat": "10g"},
#          "mid_morning": {"name": "Apple & Almonds", "items": ["Apple (1)", "Almonds (6)"], "calories": 140},
#          "lunch": {"name": "Fish Curry & Rice", "items": ["Fish curry (100g)", rice, "Sabzi (1 cup)", "Salad"], "calories": 440, "protein": "30g", "carbs": "52g", "fat": "10g"},
#          "evening": {"name": "Roasted Chana", "items": ["Roasted chana (30g)", "Herbal tea"], "calories": 120},
#          "dinner": {"name": "Chicken Sabzi & Roti", "items": ["Chicken sabzi (100g)", "Multigrain roti (2)", "Salad"], "calories": 390, "protein": "30g", "carbs": "40g", "fat": "12g"}},
#         {"breakfast": {"name": "Egg Besan Chilla", "items": ["Besan chilla (2) with egg", "Mint chutney", "Green tea"], "calories": 290, "protein": "16g", "carbs": "28g", "fat": "10g"},
#          "mid_morning": {"name": "Pomegranate", "items": ["Pomegranate (½ cup)", "Pumpkin seeds (1 tsp)"], "calories": 110},
#          "lunch": {"name": "Mutton Curry & Roti", "items": ["Lean mutton curry (80g)", "Multigrain roti (2)", "Dal (½ cup)", "Salad"], "calories": 460, "protein": "32g", "carbs": "44g", "fat": "14g"},
#          "evening": {"name": "Buttermilk", "items": ["Buttermilk (1 glass)", "Roasted makhana (20g)"], "calories": 110},
#          "dinner": {"name": "Prawn Stir-fry & Rice", "items": ["Prawn stir-fry (100g)", rice, "Stir-fry veggies (1 cup)"], "calories": 380, "protein": "28g", "carbs": "42g", "fat": "8g"}},
#         {"breakfast": {"name": "Omelette & Toast", "items": ["Veggie omelette (2 eggs)", "Brown bread (1 slice)", "Green tea"], "calories": 280, "protein": "18g", "carbs": "22g", "fat": "12g"},
#          "mid_morning": {"name": "Orange & Walnuts", "items": ["Orange (1)", "Walnuts (4)"], "calories": 120},
#          "lunch": {"name": "Grilled Fish Thali", "items": ["Grilled fish (120g)", "Multigrain roti (2)", "Dal (½ cup)", "Salad"], "calories": 440, "protein": "34g", "carbs": "46g", "fat": "10g"},
#          "evening": {"name": "Sprouts", "items": ["Mixed sprouts (1 cup)", "Lemon juice, black pepper"], "calories": 130},
#          "dinner": {"name": "Chicken Daliya", "items": ["Chicken daliya porridge (1.5 cup)", "Salad", "Curd (½ cup)"], "calories": 380, "protein": "28g", "carbs": "42g", "fat": "8g"}},
#         {"breakfast": {"name": "Egg Dalia Upma", "items": ["Dalia upma (1 bowl)", "Boiled egg (1)", "Lemon tea"], "calories": 290, "protein": "14g", "carbs": "40g", "fat": "7g"},
#          "mid_morning": {"name": "Pear & Seeds", "items": ["Pear (1)", "Flaxseeds (1 tsp)"], "calories": 120},
#          "lunch": {"name": "Egg Curry & Rice", "items": ["Egg curry (2 eggs)", rice, "Sabzi (1 cup)", "Salad"], "calories": 420, "protein": "22g", "carbs": "52g", "fat": "12g"},
#          "evening": {"name": "Chana & Amla", "items": ["Roasted chana (30g)", "Amla juice (small)"], "calories": 130},
#          "dinner": {"name": "Chicken Soup & Roti", "items": ["Chicken clear soup (1 bowl)", "Multigrain roti (2)", "Stir-fry veggies (1 cup)"], "calories": 360, "protein": "28g", "carbs": "38g", "fat": "8g"}},
#         {"breakfast": {"name": "Idli with Egg", "items": ["Idli (2)", "Boiled egg (1)", "Sambar (½ cup)", "Green tea"], "calories": 280, "protein": "14g", "carbs": "40g", "fat": "6g"},
#          "mid_morning": {"name": "Coconut Water", "items": ["Coconut water (1 glass)", "Almonds (5)"], "calories": 120},
#          "lunch": {"name": "Fish Dal Thali", "items": ["Grilled fish (100g)", "Dal (1 cup)", rice, "Salad"], "calories": 440, "protein": "32g", "carbs": "50g", "fat": "9g"},
#          "evening": {"name": "Curd & Seeds", "items": ["Low-fat curd (1 cup)", "Chia seeds (1 tsp)"], "calories": 110},
#          "dinner": {"name": "Chicken Palak & Roti", "items": ["Chicken palak (100g chicken)", "Multigrain roti (2)", "Salad"], "calories": 390, "protein": "30g", "carbs": "42g", "fat": "12g"}},
#     ]

#     pool = veg_days if diet_type == "Vegetarian" else nonveg_days
#     meal = pool[(day - 1) % len(pool)]
#     total = sum(m.get("calories", 0) for m in meal.values())
#     return {**meal, "total_calories": total, "tip": "Eat slowly, chew well, and stay hydrated."}


# # ─── DIET PLAN GENERATION ────────────────────────────────────────────────────

# def generate_diet_plan(
#     metrics: dict,
#     conditions: list,
#     severity: dict,
#     doctor_notes: str,
#     diet_type: str,
#     days: int,
#     patient_name: str,
#     model: str,
#     progress_callback=None
# ) -> dict:

#     # Calculate calorie target
#     weight = float(metrics.get("weight_kg") or 70)
#     age = float(metrics.get("age") or 40)
#     gender = str(metrics.get("gender") or "Male")
#     height = float(metrics.get("height_cm") or 165)

#     try:
#         if gender == "Female":
#             bmr = 10 * weight + 6.25 * height - 5 * age - 161
#         else:
#             bmr = 10 * weight + 6.25 * height - 5 * age + 5
#         calorie_target = int(bmr * 1.4)
#     except:
#         calorie_target = 1800

#     cl = [c.lower() for c in conditions]
#     if any("obes" in c or "overweight" in c for c in cl):
#         calorie_target = max(1400, calorie_target - 500)
#     if any("diabetes" in c for c in cl):
#         calorie_target = min(calorie_target, 1800)

#     # Quick summary (one small LLM call)
#     try:
#         summary = call_ollama(
#             f"Patient has: {', '.join(conditions) or 'no specific conditions'}. Write 2 sentences of dietary strategy. Be specific. No extra text.",
#             model=model,
#             system="You are a dietitian. Be brief and specific.",
#             timeout=40
#         )
#         if not summary or len(summary) < 20:
#             raise ValueError("empty")
#     except:
#         cond_str = ", ".join(conditions) if conditions else "general health"
#         summary = (f"This diet plan is tailored for {cond_str} with a daily calorie target of {calorie_target} kcal. "
#                    f"Focus on whole foods, controlled portions, and regular meal timings.")

#     key_recs, key_avoid = _recs_and_avoid(conditions, diet_type)
#     condition_rules = _get_condition_rules(conditions)
#     food_context = VEG_FOODS if diet_type == "Vegetarian" else NONVEG_FOODS
#     notes_short = (doctor_notes or "")[:150]

#     day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#     all_days = []
#     previous_meal_names = []

#     for day_num in range(1, days + 1):
#         if progress_callback:
#             progress_callback(day_num, days)

#         prev_str = f"Avoid repeating: {', '.join(previous_meal_names[-4:])}" if previous_meal_names else ""
#         notes_str = f"Doctor notes: {notes_short}" if notes_short else ""

#         prompt = f"""Day {day_num} Indian meal plan. Conditions: {', '.join(conditions) or 'healthy'}. {diet_type}. ~{calorie_target} kcal.
# Rules: {condition_rules}
# Foods: {food_context}
# {notes_str} {prev_str}

# Return ONLY JSON (no extra text):
# {{
#   "breakfast": {{"name": "...", "items": ["item (qty)"], "calories": 0, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}},
#   "mid_morning": {{"name": "...", "items": ["item (qty)"], "calories": 0}},
#   "lunch": {{"name": "...", "items": ["item (qty)"], "calories": 0, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}},
#   "evening": {{"name": "...", "items": ["item (qty)"], "calories": 0}},
#   "dinner": {{"name": "...", "items": ["item (qty)"], "calories": 0, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}},
#   "total_calories": 0,
#   "tip": "one short tip"
# }}"""

#         day_data = None
#         for attempt in range(2):
#             try:
#                 response = call_ollama(
#                     prompt, model=model,
#                     system="Dietitian AI. Return only valid JSON.",
#                     timeout=90
#                 )
#                 parsed = safe_parse_json(response)
#                 if parsed and "breakfast" in parsed and isinstance(parsed["breakfast"], dict):
#                     day_data = parsed
#                     break
#             except Exception:
#                 if attempt == 1:
#                     day_data = None

#         if not day_data:
#             day_data = _fallback_day(day_num, diet_type, calorie_target, conditions)

#         # Collect meal names for variety tracking
#         for mk in ["breakfast", "lunch", "dinner"]:
#             meal = day_data.get(mk, {})
#             if isinstance(meal, dict) and meal.get("name"):
#                 previous_meal_names.append(meal["name"])

#         all_days.append({
#             "day": day_num,
#             "day_name": f"Day {day_num} — {day_names[(day_num-1) % 7]}",
#             "meals": {
#                 "breakfast": day_data.get("breakfast", {}),
#                 "mid_morning_snack": day_data.get("mid_morning", {}),
#                 "lunch": day_data.get("lunch", {}),
#                 "evening_snack": day_data.get("evening", {}),
#                 "dinner": day_data.get("dinner", {})
#             },
#             "total_calories": day_data.get("total_calories", calorie_target),
#             "water_intake": "8-10 glasses",
#             "daily_tip": day_data.get("tip", "Eat mindfully and stay hydrated.")
#         })

#     return {
#         "patient_name": patient_name,
#         "summary": summary,
#         "daily_calories": calorie_target,
#         "diet_type": diet_type,
#         "days": days,
#         "key_recommendations": key_recs,
#         "key_restrictions": key_avoid,
#         "meal_plan": all_days,
#         "general_tips": _general_tips(conditions),
#         "foods_to_avoid": _foods_to_avoid(conditions),
#     }


# # ─── PDF EXPORT ──────────────────────────────────────────────────────────────

# def generate_pdf_report(patient_name, conditions, metrics, diet_plan, diet_type, days):
#     try:
#         from reportlab.lib.pagesizes import A4
#         from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#         from reportlab.lib.units import cm
#         from reportlab.lib import colors
#         from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
#         from reportlab.lib.enums import TA_CENTER
#         import io

#         buffer = io.BytesIO()
#         doc = SimpleDocTemplate(buffer, pagesize=A4,
#                                 leftMargin=2*cm, rightMargin=2*cm,
#                                 topMargin=2*cm, bottomMargin=2*cm)
#         styles = getSampleStyleSheet()

#         GREEN = colors.HexColor('#0d4a2e')
#         MID_GREEN = colors.HexColor('#1a7a4a')
#         GOLD = colors.HexColor('#d4a843')
#         MUTED = colors.HexColor('#5d6d7e')
#         RED = colors.HexColor('#c0392b')

#         def sty(name, **kw):
#             return ParagraphStyle(name, parent=styles['Normal'], **kw)

#         title_s = sty('T', fontSize=20, textColor=GREEN, alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')
#         sub_s = sty('S', fontSize=9.5, textColor=MUTED, alignment=TA_CENTER, spaceAfter=12)
#         h2_s = sty('H2', fontSize=13, textColor=GREEN, spaceBefore=10, spaceAfter=5, fontName='Helvetica-Bold')
#         h3_s = sty('H3', fontSize=10.5, textColor=MID_GREEN, spaceBefore=7, spaceAfter=3, fontName='Helvetica-Bold')
#         body_s = sty('B', fontSize=9, leading=13, spaceAfter=3)
#         green_s = sty('G', fontSize=9, leading=13, textColor=colors.HexColor('#1e8449'))
#         red_s = sty('R', fontSize=9, leading=13, textColor=RED)
#         gold_s = sty('Go', fontSize=8.5, textColor=GOLD, fontName='Helvetica-Oblique')
#         nut_s = sty('N', fontSize=8, textColor=MID_GREEN, leading=12)
#         dis_s = sty('D', fontSize=7.5, textColor=MUTED, alignment=TA_CENTER)

#         story = []
#         story.append(Paragraph("Personalized Diet Plan", title_s))
#         story.append(Paragraph(
#             f"Patient: {patient_name or 'Patient'}  |  {diet_type}  |  {days}-Day Plan  |  {diet_plan.get('daily_calories', '')} kcal/day",
#             sub_s))
#         story.append(HRFlowable(width="100%", thickness=2, color=GREEN))
#         story.append(Spacer(1, 8))

#         if conditions:
#             story.append(Paragraph("Medical Conditions", h2_s))
#             story.append(Paragraph("  |  ".join(f"• {c}" for c in conditions),
#                                    sty('Cond', fontSize=9, textColor=colors.HexColor('#7d3c98'))))
#             story.append(Spacer(1, 6))

#         if diet_plan.get("summary"):
#             story.append(Paragraph("Dietary Strategy", h2_s))
#             story.append(Paragraph(diet_plan["summary"], body_s))
#             story.append(Spacer(1, 8))

#         recs = diet_plan.get("key_recommendations", [])
#         avoid = diet_plan.get("key_restrictions", [])
#         if recs or avoid:
#             mx = max(len(recs), len(avoid), 1)
#             rows = [[Paragraph("Recommended", sty('TH', textColor=colors.white, fontName='Helvetica-Bold', fontSize=9)),
#                      Paragraph("Avoid", sty('TH2', textColor=colors.white, fontName='Helvetica-Bold', fontSize=9))]]
#             for i in range(mx):
#                 r = Paragraph(f"• {recs[i]}", green_s) if i < len(recs) else Paragraph("", body_s)
#                 a = Paragraph(f"• {avoid[i]}", red_s) if i < len(avoid) else Paragraph("", body_s)
#                 rows.append([r, a])
#             t = Table(rows, colWidths=[8.5*cm, 8.5*cm])
#             t.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), GREEN),
#                 ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d5d8dc')),
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                 ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf4fb')]),
#                 ('PADDING', (0, 0), (-1, -1), 5),
#             ]))
#             story.append(t)
#             story.append(Spacer(1, 12))

#         meal_labels = {
#             "breakfast": "Breakfast", "mid_morning_snack": "Mid-Morning Snack",
#             "lunch": "Lunch", "evening_snack": "Evening Snack", "dinner": "Dinner"
#         }

#         for day_data in diet_plan.get("meal_plan", []):
#             story.append(Paragraph(f"📅 {day_data.get('day_name', '')}", h2_s))
#             story.append(Paragraph(
#                 f"Total Calories: {day_data.get('total_calories', '')} kcal  |  Water: {day_data.get('water_intake', '8-10 glasses')}",
#                 sty('DI', fontSize=8.5, textColor=MUTED)))
#             if day_data.get("daily_tip"):
#                 story.append(Paragraph(f"Tip: {day_data['daily_tip']}", gold_s))
#             story.append(Spacer(1, 4))

#             for mk, ml in meal_labels.items():
#                 meal = day_data.get("meals", {}).get(mk, {})
#                 if not meal:
#                     continue
#                 name = meal.get("name", "")
#                 cal = meal.get("calories", "")
#                 items = meal.get("items", [])
#                 story.append(Paragraph(f"• {ml} — {name}  [{cal} kcal]", h3_s))
#                 if items:
#                     story.append(Paragraph("  |  ".join(items), body_s))
#                 p = meal.get("protein", "")
#                 c = meal.get("carbs", "")
#                 f = meal.get("fat", "")
#                 if p or c or f:
#                     story.append(Paragraph(f"Protein: {p}  |  Carbs: {c}  |  Fat: {f}", nut_s))
#                 story.append(Spacer(1, 3))

#             story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor('#d5d8dc')))
#             story.append(Spacer(1, 8))

#         if diet_plan.get("general_tips"):
#             story.append(Paragraph("General Health Tips", h2_s))
#             for tip in diet_plan["general_tips"]:
#                 story.append(Paragraph(f"• {tip}", body_s))
#             story.append(Spacer(1, 6))

#         if diet_plan.get("foods_to_avoid"):
#             story.append(Paragraph("Foods to Strictly Avoid", h2_s))
#             story.append(Paragraph("  |  ".join(diet_plan["foods_to_avoid"]), red_s))

#         story.append(Spacer(1, 16))
#         story.append(HRFlowable(width="100%", thickness=1, color=GREEN))
#         story.append(Paragraph(
#             "Disclaimer: This AI-generated diet plan is for guidance only. Consult your doctor or registered dietitian before making significant dietary changes.",
#             dis_s))

#         doc.build(story)
#         return buffer.getvalue()

#     except ImportError:
#         raise RuntimeError("Install reportlab: pip install reportlab")


import json
import re
import requests

# ─── LLM BACKEND ────────────────────────────────────────────────────────────

RECOMMENDED_MODELS = [
    "gemma3:1b", "qwen2.5:0.5b", "qwen2.5:1.5b",
    "gemma3:4b", "phi3:mini", "phi3.5:mini", "mistral", "llama3",
]


def call_ollama(prompt: str, model: str = "gemma3:1b", system: str = "", timeout: int = 90) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 800,   # Key: limit tokens per call for speed
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_ctx": 2048,      # Smaller context = much faster inference
        }
    }
    try:
        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Model '{model}' timed out after {timeout}s.\n"
            f"Recommended fast models: gemma3:1b, qwen2.5:1.5b\n"
            f"Pull with: ollama pull gemma3:1b"
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Ollama. Run: ollama serve")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")


def get_available_models() -> list:
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        return models if models else RECOMMENDED_MODELS
    except:
        return RECOMMENDED_MODELS


def test_ollama_connection(model: str) -> tuple:
    try:
        result = call_ollama("Reply with just: OK", model=model, timeout=30)
        return True, f"Connected! Model '{model}' is ready."
    except RuntimeError as e:
        return False, str(e)


# ─── JSON HELPER ─────────────────────────────────────────────────────────────

def safe_parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except:
        pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            cleaned = re.sub(r',\s*([}\]])', r'\1', match.group())
            try:
                return json.loads(cleaned)
            except:
                pass
    return {}


# ─── MEAL DATA SANITIZER ─────────────────────────────────────────────────────

def _item_to_str(x) -> str:
    """Convert any LLM item output to a plain string."""
    if isinstance(x, str):
        return x.strip()
    if isinstance(x, dict):
        # Try common key names the LLM might use
        name = ""
        for k in ["item", "name", "food", "description", "ingredient"]:
            if k in x:
                name = str(x[k])
                break
        qty = ""
        for k in ["qty", "quantity", "amount", "portion", "serving"]:
            if k in x:
                qty = f"({x[k]})"
                break
        result = f"{name} {qty}".strip()
        return result if result else str(x)
    if isinstance(x, (list, tuple)):
        return ", ".join(_item_to_str(i) for i in x)
    return str(x)


def sanitize_meal(meal: dict) -> dict:
    """Ensure meal dict has clean string items regardless of LLM output format."""
    if not isinstance(meal, dict):
        return {}
    result = dict(meal)
    # Fix items list
    items = result.get("items", [])
    if isinstance(items, list):
        result["items"] = [_item_to_str(it) for it in items if it]
    elif isinstance(items, str):
        result["items"] = [items]
    else:
        result["items"] = []
    # Ensure calories is int
    try:
        result["calories"] = int(str(result.get("calories", 0)).replace("kcal", "").strip())
    except:
        result["calories"] = 0
    # Ensure name is string
    result["name"] = str(result.get("name", "")).strip()
    return result


def sanitize_day(day_data: dict) -> dict:
    """Sanitize all meals in a day."""
    if not isinstance(day_data, dict):
        return {}
    meals = day_data.get("meals", {})
    if isinstance(meals, dict):
        day_data["meals"] = {k: sanitize_meal(v) for k, v in meals.items() if isinstance(v, dict)}
    return day_data


# ─── METRIC EXTRACTION ───────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_file) -> str:
    try:
        import pdfplumber, io
        with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        try:
            import pypdf, io
            reader = pypdf.PdfReader(io.BytesIO(pdf_file.read()))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise RuntimeError("Install pdfplumber: pip install pdfplumber")


def extract_text_from_image(image_file) -> str:
    try:
        import pytesseract
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_file.read()))
        return pytesseract.image_to_string(img)
    except ImportError:
        raise RuntimeError("Install pytesseract: pip install pytesseract pillow")


def _regex_extract_metrics(text: str) -> dict:
    """
    Regex-based metric extractor — works instantly on any structured lab report.
    Looks for patterns like: 'Fasting Glucose 180 mg/dL' or 'Systolic BP 140 mmHg'
    Returns only non-zero, non-null values.
    """
    # Each entry: (result_key, list of regex patterns to try)
    PATTERNS = {
        "glucose_fasting": [
            r"fasting\s*(?:glucose|blood\s*sugar)[^\d]*(\d+\.?\d*)",
            r"glucose[,\s]*fasting[^\d]*(\d+\.?\d*)",
            r"FBS[^\d]*(\d+\.?\d*)",
            r"fasting[^\d]{0,10}(\d{2,3})\s*mg",
        ],
        "glucose_postprandial": [
            r"post[\s\-]*prandial[^\d]*(\d+\.?\d*)",
            r"pp\s*(?:glucose|blood\s*sugar)[^\d]*(\d+\.?\d*)",
            r"2\s*h(?:r|our)?\s*(?:pp|glucose)[^\d]*(\d+\.?\d*)",
            r"PPBS[^\d]*(\d+\.?\d*)",
        ],
        "hba1c": [
            r"hb\s*a1c[^\d]*(\d+\.?\d*)",
            r"glycated\s*hemo[^\d]*(\d+\.?\d*)",
            r"a1c[^\d]*(\d+\.?\d*)",
            r"HbA1c[^\d]*(\d+\.?\d*)",
        ],
        "systolic_bp": [
            r"systolic[^\d]*(\d+\.?\d*)",
            r"bp[^\d]*(\d{2,3})\s*/",
            r"blood\s*pressure[^\d]*(\d{2,3})\s*/",
            r"SBP[^\d]*(\d+\.?\d*)",
        ],
        "diastolic_bp": [
            r"diastolic[^\d]*(\d+\.?\d*)",
            r"bp[^\d]*\d+\s*/\s*(\d{2,3})",
            r"blood\s*pressure[^\d]*\d+\s*/\s*(\d{2,3})",
            r"DBP[^\d]*(\d+\.?\d*)",
        ],
        "total_cholesterol": [
            r"total\s*cholesterol[^\d]*(\d+\.?\d*)",
            r"cholesterol[,\s]*total[^\d]*(\d+\.?\d*)",
            r"T\.?CHOL[^\d]*(\d+\.?\d*)",
        ],
        "ldl": [
            r"ldl[^\d]*(\d+\.?\d*)",
            r"low\s*density[^\d]*(\d+\.?\d*)",
            r"LDL[\s\-]*C[^\d]*(\d+\.?\d*)",
        ],
        "hdl": [
            r"hdl[^\d]*(\d+\.?\d*)",
            r"high\s*density[^\d]*(\d+\.?\d*)",
            r"HDL[\s\-]*C[^\d]*(\d+\.?\d*)",
        ],
        "triglycerides": [
            r"triglycerides?[^\d]*(\d+\.?\d*)",
            r"TRIG[^\d]*(\d+\.?\d*)",
            r"TG[^\d]*(\d+\.?\d*)",
        ],
        "bmi": [
            r"bmi[^\d]*(\d+\.?\d*)",
            r"body\s*mass\s*index[^\d]*(\d+\.?\d*)",
            r"calculated\s*bmi[^\d]*(\d+\.?\d*)",
        ],
        "weight_kg": [
            r"weight[^\d]*(\d+\.?\d*)\s*kg",
            r"(\d+\.?\d*)\s*kg\s*(?:weight|wt)",
            r"wt[^\d]*(\d+\.?\d*)\s*kg",
        ],
        "height_cm": [
            r"height[^\d]*(\d+\.?\d*)\s*cm",
            r"(\d+\.?\d*)\s*cm\s*(?:height|ht)",
            r"ht[^\d]*(\d+\.?\d*)\s*cm",
        ],
        "hemoglobin": [
            r"hemo?globin[^\d]*(\d+\.?\d*)",
            r"\bHb\b[^\d]*(\d+\.?\d*)",
            r"Hgb[^\d]*(\d+\.?\d*)",
        ],
        "iron": [
            r"serum\s*iron[^\d]*(\d+\.?\d*)",
            r"ferritin[^\d]*(\d+\.?\d*)",
            r"iron[^\d]*(\d+\.?\d*)",
        ],
        "vitamin_d": [
            r"vitamin\s*d[^\d]*(\d+\.?\d*)",
            r"25[\s\-]*oh[\s\-]*d[^\d]*(\d+\.?\d*)",
            r"Vit\.?\s*D[^\d]*(\d+\.?\d*)",
        ],
        "thyroid_tsh": [
            r"tsh[^\d]*(\d+\.?\d*)",
            r"thyroid\s*(?:stimulating\s*)?hormone[^\d]*(\d+\.?\d*)",
            r"T\.?S\.?H[^\d]*(\d+\.?\d*)",
        ],
        "creatinine": [
            r"creatinine[^\d]*(\d+\.?\d*)",
            r"CREAT[^\d]*(\d+\.?\d*)",
            r"S\.?\s*Creatinine[^\d]*(\d+\.?\d*)",
        ],
    }

    text_lower = text.lower()
    result = {}

    for key, patterns in PATTERNS.items():
        for pattern in patterns:
            try:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    val = float(match.group(1))
                    if val > 0:  # 0 = not tested, skip
                        result[key] = val
                        break
            except:
                continue

    return result


def extract_metrics_with_llm(raw_text: str, model: str) -> dict:
    """
    Extract metrics using regex first (fast, accurate for structured reports).
    Falls back to LLM only if regex finds fewer than 3 metrics.
    """
    # Step 1: Try regex — works perfectly for standard lab report formats
    regex_result = _regex_extract_metrics(raw_text)

    if len(regex_result) >= 3:
        # Regex found enough — no LLM call needed, instant result
        return regex_result

    # Step 2: Fallback to LLM for non-standard / narrative reports
    text = raw_text[:1200]
    prompt = f"""Extract medical values from this report. Return ONLY a JSON object.
Keys: glucose_fasting, glucose_postprandial, hba1c, systolic_bp, diastolic_bp,
total_cholesterol, ldl, hdl, triglycerides, bmi, weight_kg, height_cm,
creatinine, hemoglobin, iron, vitamin_d, thyroid_tsh
Use null for missing values.

Report: {text}

JSON:"""
    try:
        response = call_ollama(prompt, model=model,
                               system="Extract medical data, return only JSON.",
                               timeout=60)
        result = safe_parse_json(response)
        cleaned = {}
        for k, v in result.items():
            if v is None or v == "null" or v == "":
                cleaned[k] = None
            else:
                try:
                    num = float(str(v).replace(",", "").strip())
                    cleaned[k] = None if num == 0 else num
                except:
                    cleaned[k] = None
        # Merge: regex takes priority, LLM fills gaps
        return {**cleaned, **regex_result}
    except:
        return regex_result

# ─── CONDITION ANALYSIS (Rule-based — instant) ───────────────────────────────

def analyze_conditions(metrics: dict, doctor_notes: str = "") -> dict:
    conditions = []
    severity = {}

    g = metrics.get("glucose_fasting")
    hba1c = metrics.get("hba1c")
    sbp = metrics.get("systolic_bp")
    dbp = metrics.get("diastolic_bp")
    bmi = metrics.get("bmi")
    chol = metrics.get("total_cholesterol")
    ldl = metrics.get("ldl")
    trig = metrics.get("triglycerides")
    hgb = metrics.get("hemoglobin")
    tsh = metrics.get("thyroid_tsh")
    cr = metrics.get("creatinine")

    if (g and g >= 126) or (hba1c and hba1c >= 6.5):
        conditions.append("Type 2 Diabetes")
        severity["diabetes"] = "high" if (g and g >= 200) or (hba1c and hba1c >= 8) else "moderate"
    elif (g and 100 <= g < 126) or (hba1c and 5.7 <= hba1c < 6.5):
        conditions.append("Prediabetes")
        severity["diabetes"] = "low"

    if sbp and dbp:
        if sbp >= 140 or dbp >= 90:
            conditions.append("Hypertension")
            severity["hypertension"] = "high" if sbp >= 160 else "moderate"
        elif sbp >= 130 or dbp >= 80:
            conditions.append("Elevated Blood Pressure")
            severity["hypertension"] = "low"

    if (chol and chol >= 240) or (ldl and ldl >= 160) or (trig and trig >= 200):
        conditions.append("High Cholesterol")
        severity["cholesterol"] = "high" if (ldl and ldl >= 190) else "moderate"
    elif (chol and chol >= 200) or (ldl and ldl >= 130):
        conditions.append("Borderline High Cholesterol")
        severity["cholesterol"] = "low"

    if bmi:
        if bmi >= 30:
            conditions.append("Obesity")
            severity["weight"] = "high" if bmi >= 35 else "moderate"
        elif bmi >= 25:
            conditions.append("Overweight")
            severity["weight"] = "low"

    if hgb:
        gender = metrics.get("gender", "").lower()
        threshold = 12 if gender == "female" else 13
        if hgb < threshold:
            conditions.append("Anemia")
            severity["anemia"] = "high" if hgb < 10 else "low"

    if tsh:
        if tsh > 4.5:
            conditions.append("Hypothyroidism")
        elif tsh < 0.4:
            conditions.append("Hyperthyroidism")

    if cr and cr > 1.3:
        conditions.append("Elevated Creatinine (Kidney)")

    notes = (doctor_notes or "").lower()
    note_map = {
        "iron": "Iron Deficiency", "anaemia": "Anemia", "anemia": "Anemia",
        "thyroid": "Thyroid Disorder", "hypothyroid": "Hypothyroidism",
        "kidney": "Kidney Issue", "renal": "Kidney Issue",
        "uric acid": "High Uric Acid", "gout": "High Uric Acid / Gout",
        "pcod": "PCOD/PCOS", "pcos": "PCOD/PCOS",
        "fatty liver": "Fatty Liver", "vitamin d": "Vitamin D Deficiency",
        "b12": "Vitamin B12 Deficiency",
    }
    for keyword, condition in note_map.items():
        if keyword in notes and condition not in conditions:
            conditions.append(condition)

    return {"conditions": conditions, "severity": severity}


# ─── DIET RULES (instant, no LLM) ────────────────────────────────────────────

CONDITION_RULES = {
    "diabetes": "Low GI only. No sugar/white rice/maida/sweet fruits/juices. Use brown rice, multigrain roti, oats, methi, bitter gourd. Small frequent meals.",
    "hypertension": "Low sodium. No pickles/papad/canned foods. Include banana, spinach, garlic, flaxseeds.",
    "cholesterol": "No fried food/ghee/butter. Include oats, flaxseeds, walnuts. Use mustard oil.",
    "weight": "Calorie deficit. High fiber, high protein. No junk/fried food. Large vegetable portions.",
    "anemia": "Iron-rich: spinach, beetroot, dates, rajma, jaggery. Add Vit C for absorption. Cook in iron kadhai.",
    "kidney": "Low potassium/phosphorus. Limit: banana, tomato, potato, dairy. Small protein portions.",
    "thyroid": "Iodized salt. Selenium-rich foods. Avoid excess raw cruciferous vegetables.",
}

_SEVERITY_KEY_MAP = {
    "type 2 diabetes": "diabetes", "prediabetes": "diabetes",
    "hypertension": "hypertension", "elevated blood pressure": "hypertension",
    "high cholesterol": "cholesterol", "borderline high cholesterol": "cholesterol",
    "obesity": "weight", "overweight": "weight",
    "anemia": "anemia", "iron deficiency": "anemia",
    "kidney issue": "kidney", "elevated creatinine (kidney)": "kidney",
    "hypothyroidism": "thyroid", "hyperthyroidism": "thyroid",
}

VEG_FOODS = "Indian vegetarian: dal, paneer, tofu, sprouts, chana, rajma, sabzi, curd, buttermilk, multigrain roti, brown rice, oats, poha, idli, upma, sambar, methi, palak."
NONVEG_FOODS = "Indian: grilled/boiled chicken, eggs, fish (rohu/surmai), along with dal, sabzi, curd, multigrain roti, brown rice, oats, poha."


def _get_condition_rules(conditions: list) -> str:
    seen = set()
    rules = []
    for c in conditions:
        key = _SEVERITY_KEY_MAP.get(c.lower())
        if key and key not in seen and key in CONDITION_RULES:
            rules.append(CONDITION_RULES[key])
            seen.add(key)
    return " | ".join(rules) if rules else "Balanced healthy Indian diet."


def _recs_and_avoid(conditions: list, diet_type: str):
    recs = [
        "Drink 8-10 glasses of water daily",
        "Eat every 3-4 hours — no skipping meals",
        "Include fiber-rich food in every meal",
        "Use small plates to control portions",
    ]
    avoid = ["Processed/packaged foods", "Excess oil & fried foods", "Late night eating"]

    cl = [c.lower() for c in conditions]
    if any("diabetes" in c for c in cl):
        recs += ["Low GI foods only", "Include methi/karela/cinnamon", "Walk 15 min after meals"]
        avoid += ["Sugar, sweets, cold drinks", "White rice, maida, bread", "Sweet fruits & juices"]
    if any("hypertension" in c or "blood pressure" in c for c in cl):
        recs += ["Use sendha namak / low sodium salt", "Include potassium-rich foods"]
        avoid += ["Pickles, papad, achaar", "Extra salt at table"]
    if any("cholesterol" in c for c in cl):
        recs += ["Oats daily for breakfast", "Include flaxseeds & walnuts"]
        avoid += ["Ghee, butter, cream", "Full cream dairy, red meat"]
    if any("obes" in c or "overweight" in c for c in cl):
        recs += ["High protein breakfast", "30 min walk daily"]
        avoid += ["Fried snacks, desserts", "Sugary beverages"]
    if any("anemia" in c or "iron" in c for c in cl):
        recs += ["Spinach, dates, beetroot daily", "Lemon/amla with iron-rich meals"]
        avoid += ["Tea/coffee right after meals", "Excess calcium with iron meals"]
    if diet_type == "Vegetarian":
        recs += ["Dal or legumes twice daily for protein"]
    else:
        recs += ["Prefer grilled/boiled over fried protein", "Fish 2-3x/week for omega-3"]
    return recs[:8], avoid[:8]


def _general_tips(conditions: list) -> list:
    tips = [
        "Sleep 7-8 hours — poor sleep worsens blood sugar & weight",
        "Manage stress: yoga, meditation, or 10 min deep breathing daily",
        "Cook at home as much as possible",
        "Don't skip meals — it leads to overeating",
        "Read food labels — watch for hidden sugar and sodium",
    ]
    cl = [c.lower() for c in conditions]
    if any("diabetes" in c for c in cl):
        tips.append("Keep a food diary to track blood sugar responses to meals")
    if any("hypertension" in c or "blood pressure" in c for c in cl):
        tips.append("Monitor BP at the same time each morning")
    if any("obes" in c or "overweight" in c for c in cl):
        tips.append("Weigh yourself weekly (same time, same conditions)")
    return tips


def _foods_to_avoid(conditions: list) -> list:
    avoid = ["Maida products (bread, biscuits, naan)", "Packaged chips & namkeen",
             "Cold drinks & soda", "Excess oil & butter"]
    cl = [c.lower() for c in conditions]
    if any("diabetes" in c for c in cl):
        avoid += ["White rice (or max ½ cup)", "Sugar, jaggery excess", "Mango, banana, grapes, chikoo, fruit juice"]
    if any("cholesterol" in c for c in cl):
        avoid += ["Vanaspati, coconut oil", "Red meat, organ meats"]
    if any("hypertension" in c or "blood pressure" in c for c in cl):
        avoid += ["Pickles, canned/preserved foods", "High-sodium sauces"]
    return avoid


# ─── FALLBACK MEALS ──────────────────────────────────────────────────────────

def _fallback_day(day: int, diet_type: str, calories: int, conditions: list) -> dict:
    is_diabetic = any("diabetes" in c.lower() for c in conditions)
    rice = "Brown rice (½ cup)" if is_diabetic else "Rice (¾ cup)"

    veg_days = [
        {"breakfast": {"name": "Oats Upma", "items": ["Oats upma (1 bowl)", "Sprouts (½ cup)", "Green tea"], "calories": 280, "protein": "10g", "carbs": "38g", "fat": "6g"},
         "mid_morning": {"name": "Fruit & Nuts", "items": ["Apple (1)", "Walnuts (4-5)"], "calories": 150},
         "lunch": {"name": "Dal Rice & Sabzi", "items": ["Moong dal (1 cup)", rice, "Mixed sabzi (1 cup)", "Curd (½ cup)"], "calories": 420, "protein": "18g", "carbs": "62g", "fat": "8g"},
         "evening": {"name": "Buttermilk & Chana", "items": ["Buttermilk (1 glass)", "Roasted chana (30g)"], "calories": 130},
         "dinner": {"name": "Roti & Paneer Sabzi", "items": ["Multigrain roti (2)", "Paneer sabzi (1 cup)", "Salad"], "calories": 380, "protein": "20g", "carbs": "45g", "fat": "12g"}},
        {"breakfast": {"name": "Methi Paratha & Curd", "items": ["Methi paratha (2 small)", "Low-fat curd (1 cup)", "Cucumber"], "calories": 300, "protein": "12g", "carbs": "42g", "fat": "8g"},
         "mid_morning": {"name": "Coconut Water & Almonds", "items": ["Coconut water (1 glass)", "Almonds (6)"], "calories": 120},
         "lunch": {"name": "Rajma Chawal", "items": ["Rajma (1 cup)", rice, "Onion salad", "Buttermilk"], "calories": 440, "protein": "20g", "carbs": "65g", "fat": "6g"},
         "evening": {"name": "Sprouts Chaat", "items": ["Mixed sprouts (1 cup)", "Lemon juice", "Coriander"], "calories": 140},
         "dinner": {"name": "Palak Dal & Roti", "items": ["Palak dal (1 cup)", "Multigrain roti (2)", "Salad"], "calories": 360, "protein": "18g", "carbs": "50g", "fat": "8g"}},
        {"breakfast": {"name": "Vegetable Poha", "items": ["Poha with veggies (1 bowl)", "Sprouts (¼ cup)", "Lemon tea"], "calories": 270, "protein": "8g", "carbs": "44g", "fat": "5g"},
         "mid_morning": {"name": "Guava & Seeds", "items": ["Guava (1)", "Pumpkin seeds (1 tbsp)"], "calories": 110},
         "lunch": {"name": "Chana Dal Thali", "items": ["Chana dal (1 cup)", "Multigrain roti (2)", "Sabzi (1 cup)", "Salad"], "calories": 430, "protein": "20g", "carbs": "60g", "fat": "7g"},
         "evening": {"name": "Roasted Makhana", "items": ["Roasted makhana (30g)", "Herbal tea"], "calories": 120},
         "dinner": {"name": "Mixed Dal & Roti", "items": ["Mixed dal (1 cup)", "Roti (2)", "Stir-fry veggies (1 cup)"], "calories": 370, "protein": "19g", "carbs": "50g", "fat": "8g"}},
        {"breakfast": {"name": "Idli Sambar", "items": ["Steamed idli (3)", "Sambar (1 cup)", "Coconut chutney (1 tbsp)"], "calories": 290, "protein": "10g", "carbs": "48g", "fat": "5g"},
         "mid_morning": {"name": "Orange & Walnuts", "items": ["Orange (1)", "Walnuts (4)"], "calories": 130},
         "lunch": {"name": "Palak Paneer & Rice", "items": ["Palak paneer (1 cup)", rice, "Salad", "Curd (½ cup)"], "calories": 450, "protein": "22g", "carbs": "56g", "fat": "14g"},
         "evening": {"name": "Chana Chaat", "items": ["Boiled chana (½ cup)", "Onion, tomato, lemon"], "calories": 140},
         "dinner": {"name": "Moong Dal Khichdi", "items": ["Moong dal khichdi (1.5 cups)", "Curd (½ cup)", "Pickle (1 tsp)"], "calories": 360, "protein": "16g", "carbs": "52g", "fat": "6g"}},
        {"breakfast": {"name": "Besan Chilla", "items": ["Besan chilla (2)", "Mint chutney", "Green tea"], "calories": 260, "protein": "14g", "carbs": "30g", "fat": "8g"},
         "mid_morning": {"name": "Pomegranate", "items": ["Pomegranate (½ cup)", "Flaxseeds (1 tsp)"], "calories": 100},
         "lunch": {"name": "Lobia Dal Roti", "items": ["Lobia (black-eyed peas) (1 cup)", "Multigrain roti (2)", "Salad"], "calories": 400, "protein": "18g", "carbs": "58g", "fat": "6g"},
         "evening": {"name": "Curd with Seeds", "items": ["Low-fat curd (1 cup)", "Chia seeds (1 tsp)"], "calories": 120},
         "dinner": {"name": "Tofu Bhurji & Roti", "items": ["Tofu bhurji (1 cup)", "Roti (2)", "Stir-fry veggies"], "calories": 380, "protein": "22g", "carbs": "44g", "fat": "12g"}},
        {"breakfast": {"name": "Dalia (Broken Wheat) Upma", "items": ["Dalia upma (1 bowl)", "Boiled egg / paneer (50g)", "Green tea"], "calories": 285, "protein": "12g", "carbs": "40g", "fat": "6g"},
         "mid_morning": {"name": "Pear & Almonds", "items": ["Pear (1)", "Almonds (6)"], "calories": 130},
         "lunch": {"name": "Toor Dal & Sabzi", "items": ["Toor dal (1 cup)", rice, "Bhindi/any sabzi (1 cup)", "Curd"], "calories": 420, "protein": "18g", "carbs": "60g", "fat": "7g"},
         "evening": {"name": "Roasted Chana & Amla", "items": ["Roasted chana (30g)", "Amla juice (small)"], "calories": 130},
         "dinner": {"name": "Vegetable Khichdi", "items": ["Moong-rice khichdi (1.5 cup)", "Curd (½ cup)", "Papad (1, roasted)"], "calories": 350, "protein": "15g", "carbs": "50g", "fat": "6g"}},
        {"breakfast": {"name": "Rava Upma", "items": ["Rava upma with veggies (1 bowl)", "Sprouts (¼ cup)", "Lemon water"], "calories": 270, "protein": "9g", "carbs": "42g", "fat": "6g"},
         "mid_morning": {"name": "Banana Lassi (small)", "items": ["Banana (½)", "Low-fat curd lassi (1 cup, no sugar)"], "calories": 140},
         "lunch": {"name": "Masoor Dal Thali", "items": ["Masoor dal (1 cup)", "Multigrain roti (2)", "Salad", "Sabzi (1 cup)"], "calories": 430, "protein": "19g", "carbs": "60g", "fat": "7g"},
         "evening": {"name": "Makhana & Herbal Tea", "items": ["Roasted makhana (25g)", "Herbal tea (1 cup)"], "calories": 110},
         "dinner": {"name": "Paneer Stir-fry & Roti", "items": ["Paneer stir-fry (100g paneer)", "Roti (2)", "Salad"], "calories": 390, "protein": "24g", "carbs": "40g", "fat": "14g"}},
    ]

    nonveg_days = [
        {"breakfast": {"name": "Egg Veggie Scramble", "items": ["Scrambled eggs (2)", "Brown bread (2 slices)", "Green tea"], "calories": 300, "protein": "16g", "carbs": "30g", "fat": "10g"},
         "mid_morning": {"name": "Fruit & Nuts", "items": ["Guava (1)", "Almonds (6)"], "calories": 140},
         "lunch": {"name": "Chicken Dal Thali", "items": ["Grilled chicken (100g)", "Dal (1 cup)", rice, "Salad"], "calories": 450, "protein": "35g", "carbs": "50g", "fat": "8g"},
         "evening": {"name": "Buttermilk & Makhana", "items": ["Buttermilk (1 glass)", "Roasted makhana (25g)"], "calories": 130},
         "dinner": {"name": "Fish Curry & Roti", "items": ["Fish curry (100g fish)", "Multigrain roti (2)", "Sabzi (1 cup)"], "calories": 390, "protein": "28g", "carbs": "42g", "fat": "10g"}},
        {"breakfast": {"name": "Poha with Egg", "items": ["Poha (1 bowl)", "Boiled egg (1)", "Green tea"], "calories": 290, "protein": "14g", "carbs": "40g", "fat": "7g"},
         "mid_morning": {"name": "Coconut Water & Nuts", "items": ["Coconut water (1 glass)", "Walnuts (4)"], "calories": 130},
         "lunch": {"name": "Chicken Roti Bowl", "items": ["Grilled chicken (100g)", "Multigrain roti (2)", "Dal (½ cup)", "Salad"], "calories": 430, "protein": "32g", "carbs": "46g", "fat": "9g"},
         "evening": {"name": "Sprouts Chaat", "items": ["Sprouts (1 cup)", "Lemon juice"], "calories": 140},
         "dinner": {"name": "Egg Curry & Roti", "items": ["Egg curry (2 eggs)", "Roti (2)", "Sabzi (1 cup)"], "calories": 380, "protein": "22g", "carbs": "44g", "fat": "12g"}},
        {"breakfast": {"name": "Egg Oats Bowl", "items": ["Oats (½ cup)", "Boiled egg (2)", "Lemon tea"], "calories": 310, "protein": "18g", "carbs": "36g", "fat": "10g"},
         "mid_morning": {"name": "Apple & Almonds", "items": ["Apple (1)", "Almonds (6)"], "calories": 140},
         "lunch": {"name": "Fish Curry & Rice", "items": ["Fish curry (100g)", rice, "Sabzi (1 cup)", "Salad"], "calories": 440, "protein": "30g", "carbs": "52g", "fat": "10g"},
         "evening": {"name": "Roasted Chana", "items": ["Roasted chana (30g)", "Herbal tea"], "calories": 120},
         "dinner": {"name": "Chicken Sabzi & Roti", "items": ["Chicken sabzi (100g)", "Multigrain roti (2)", "Salad"], "calories": 390, "protein": "30g", "carbs": "40g", "fat": "12g"}},
        {"breakfast": {"name": "Egg Besan Chilla", "items": ["Besan chilla (2) with egg", "Mint chutney", "Green tea"], "calories": 290, "protein": "16g", "carbs": "28g", "fat": "10g"},
         "mid_morning": {"name": "Pomegranate", "items": ["Pomegranate (½ cup)", "Pumpkin seeds (1 tsp)"], "calories": 110},
         "lunch": {"name": "Mutton Curry & Roti", "items": ["Lean mutton curry (80g)", "Multigrain roti (2)", "Dal (½ cup)", "Salad"], "calories": 460, "protein": "32g", "carbs": "44g", "fat": "14g"},
         "evening": {"name": "Buttermilk", "items": ["Buttermilk (1 glass)", "Roasted makhana (20g)"], "calories": 110},
         "dinner": {"name": "Prawn Stir-fry & Rice", "items": ["Prawn stir-fry (100g)", rice, "Stir-fry veggies (1 cup)"], "calories": 380, "protein": "28g", "carbs": "42g", "fat": "8g"}},
        {"breakfast": {"name": "Omelette & Toast", "items": ["Veggie omelette (2 eggs)", "Brown bread (1 slice)", "Green tea"], "calories": 280, "protein": "18g", "carbs": "22g", "fat": "12g"},
         "mid_morning": {"name": "Orange & Walnuts", "items": ["Orange (1)", "Walnuts (4)"], "calories": 120},
         "lunch": {"name": "Grilled Fish Thali", "items": ["Grilled fish (120g)", "Multigrain roti (2)", "Dal (½ cup)", "Salad"], "calories": 440, "protein": "34g", "carbs": "46g", "fat": "10g"},
         "evening": {"name": "Sprouts", "items": ["Mixed sprouts (1 cup)", "Lemon juice, black pepper"], "calories": 130},
         "dinner": {"name": "Chicken Daliya", "items": ["Chicken daliya porridge (1.5 cup)", "Salad", "Curd (½ cup)"], "calories": 380, "protein": "28g", "carbs": "42g", "fat": "8g"}},
        {"breakfast": {"name": "Egg Dalia Upma", "items": ["Dalia upma (1 bowl)", "Boiled egg (1)", "Lemon tea"], "calories": 290, "protein": "14g", "carbs": "40g", "fat": "7g"},
         "mid_morning": {"name": "Pear & Seeds", "items": ["Pear (1)", "Flaxseeds (1 tsp)"], "calories": 120},
         "lunch": {"name": "Egg Curry & Rice", "items": ["Egg curry (2 eggs)", rice, "Sabzi (1 cup)", "Salad"], "calories": 420, "protein": "22g", "carbs": "52g", "fat": "12g"},
         "evening": {"name": "Chana & Amla", "items": ["Roasted chana (30g)", "Amla juice (small)"], "calories": 130},
         "dinner": {"name": "Chicken Soup & Roti", "items": ["Chicken clear soup (1 bowl)", "Multigrain roti (2)", "Stir-fry veggies (1 cup)"], "calories": 360, "protein": "28g", "carbs": "38g", "fat": "8g"}},
        {"breakfast": {"name": "Idli with Egg", "items": ["Idli (2)", "Boiled egg (1)", "Sambar (½ cup)", "Green tea"], "calories": 280, "protein": "14g", "carbs": "40g", "fat": "6g"},
         "mid_morning": {"name": "Coconut Water", "items": ["Coconut water (1 glass)", "Almonds (5)"], "calories": 120},
         "lunch": {"name": "Fish Dal Thali", "items": ["Grilled fish (100g)", "Dal (1 cup)", rice, "Salad"], "calories": 440, "protein": "32g", "carbs": "50g", "fat": "9g"},
         "evening": {"name": "Curd & Seeds", "items": ["Low-fat curd (1 cup)", "Chia seeds (1 tsp)"], "calories": 110},
         "dinner": {"name": "Chicken Palak & Roti", "items": ["Chicken palak (100g chicken)", "Multigrain roti (2)", "Salad"], "calories": 390, "protein": "30g", "carbs": "42g", "fat": "12g"}},
    ]

    pool = veg_days if diet_type == "Vegetarian" else nonveg_days
    meal = pool[(day - 1) % len(pool)]
    total = sum(m.get("calories", 0) for m in meal.values())
    return {**meal, "total_calories": total, "tip": "Eat slowly, chew well, and stay hydrated."}


# ─── DIET PLAN GENERATION ────────────────────────────────────────────────────

def generate_diet_plan(
    metrics: dict,
    conditions: list,
    severity: dict,
    doctor_notes: str,
    diet_type: str,
    days: int,
    patient_name: str,
    model: str,
    progress_callback=None
) -> dict:

    # Calculate calorie target
    weight = float(metrics.get("weight_kg") or 70)
    age = float(metrics.get("age") or 40)
    gender = str(metrics.get("gender") or "Male")
    height = float(metrics.get("height_cm") or 165)

    try:
        if gender == "Female":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        calorie_target = int(bmr * 1.4)
    except:
        calorie_target = 1800

    cl = [c.lower() for c in conditions]
    if any("obes" in c or "overweight" in c for c in cl):
        calorie_target = max(1400, calorie_target - 500)
    if any("diabetes" in c for c in cl):
        calorie_target = min(calorie_target, 1800)

    # Quick summary (one small LLM call)
    try:
        summary = call_ollama(
            f"Patient has: {', '.join(conditions) or 'no specific conditions'}. Write 2 sentences of dietary strategy. Be specific. No extra text.",
            model=model,
            system="You are a dietitian. Be brief and specific.",
            timeout=40
        )
        if not summary or len(summary) < 20:
            raise ValueError("empty")
    except:
        cond_str = ", ".join(conditions) if conditions else "general health"
        summary = (f"This diet plan is tailored for {cond_str} with a daily calorie target of {calorie_target} kcal. "
                   f"Focus on whole foods, controlled portions, and regular meal timings.")

    key_recs, key_avoid = _recs_and_avoid(conditions, diet_type)
    condition_rules = _get_condition_rules(conditions)
    food_context = VEG_FOODS if diet_type == "Vegetarian" else NONVEG_FOODS
    notes_short = (doctor_notes or "")[:150]

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    all_days = []
    previous_meal_names = []

    for day_num in range(1, days + 1):
        if progress_callback:
            progress_callback(day_num, days)

        prev_str = f"Avoid repeating: {', '.join(previous_meal_names[-4:])}" if previous_meal_names else ""
        notes_str = f"Doctor notes: {notes_short}" if notes_short else ""

        prompt = f"""Day {day_num} Indian meal plan. Conditions: {', '.join(conditions) or 'healthy'}. {diet_type}. ~{calorie_target} kcal.
Rules: {condition_rules}
Foods: {food_context}
{notes_str} {prev_str}

Return ONLY JSON (no extra text):
{{
  "breakfast": {{"name": "...", "items": ["item (qty)"], "calories": 0, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}},
  "mid_morning": {{"name": "...", "items": ["item (qty)"], "calories": 0}},
  "lunch": {{"name": "...", "items": ["item (qty)"], "calories": 0, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}},
  "evening": {{"name": "...", "items": ["item (qty)"], "calories": 0}},
  "dinner": {{"name": "...", "items": ["item (qty)"], "calories": 0, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}},
  "total_calories": 0,
  "tip": "one short tip"
}}"""

        day_data = None
        for attempt in range(2):
            try:
                response = call_ollama(
                    prompt, model=model,
                    system="Dietitian AI. Return only valid JSON.",
                    timeout=90
                )
                parsed = safe_parse_json(response)
                if parsed and "breakfast" in parsed and isinstance(parsed["breakfast"], dict):
                    day_data = parsed
                    break
            except Exception:
                if attempt == 1:
                    day_data = None

        if not day_data:
            day_data = _fallback_day(day_num, diet_type, calorie_target, conditions)

        # Collect meal names for variety tracking
        for mk in ["breakfast", "lunch", "dinner"]:
            meal = day_data.get(mk, {})
            if isinstance(meal, dict) and meal.get("name"):
                previous_meal_names.append(meal["name"])

        raw_meals = {
            "breakfast": day_data.get("breakfast", {}),
            "mid_morning_snack": day_data.get("mid_morning", {}),
            "lunch": day_data.get("lunch", {}),
            "evening_snack": day_data.get("evening", {}),
            "dinner": day_data.get("dinner", {})
        }
        # Sanitize every meal so items are always plain strings
        clean_meals = {k: sanitize_meal(v) for k, v in raw_meals.items() if isinstance(v, dict)}

        all_days.append({
            "day": day_num,
            "day_name": f"Day {day_num} — {day_names[(day_num-1) % 7]}",
            "meals": clean_meals,
            "total_calories": day_data.get("total_calories", calorie_target),
            "water_intake": "8-10 glasses",
            "daily_tip": str(day_data.get("tip", "Eat mindfully and stay hydrated."))
        })

    return {
        "patient_name": patient_name,
        "summary": summary,
        "daily_calories": calorie_target,
        "diet_type": diet_type,
        "days": days,
        "key_recommendations": key_recs,
        "key_restrictions": key_avoid,
        "meal_plan": all_days,
        "general_tips": _general_tips(conditions),
        "foods_to_avoid": _foods_to_avoid(conditions),
    }


# ─── PDF EXPORT ──────────────────────────────────────────────────────────────

def generate_pdf_report(patient_name, conditions, metrics, diet_plan, diet_type, days):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        GREEN = colors.HexColor('#0d4a2e')
        MID_GREEN = colors.HexColor('#1a7a4a')
        GOLD = colors.HexColor('#d4a843')
        MUTED = colors.HexColor('#5d6d7e')
        RED = colors.HexColor('#c0392b')

        def sty(name, **kw):
            return ParagraphStyle(name, parent=styles['Normal'], **kw)

        title_s = sty('T', fontSize=20, textColor=GREEN, alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')
        sub_s = sty('S', fontSize=9.5, textColor=MUTED, alignment=TA_CENTER, spaceAfter=12)
        h2_s = sty('H2', fontSize=13, textColor=GREEN, spaceBefore=10, spaceAfter=5, fontName='Helvetica-Bold')
        h3_s = sty('H3', fontSize=10.5, textColor=MID_GREEN, spaceBefore=7, spaceAfter=3, fontName='Helvetica-Bold')
        body_s = sty('B', fontSize=9, leading=13, spaceAfter=3)
        green_s = sty('G', fontSize=9, leading=13, textColor=colors.HexColor('#1e8449'))
        red_s = sty('R', fontSize=9, leading=13, textColor=RED)
        gold_s = sty('Go', fontSize=8.5, textColor=GOLD, fontName='Helvetica-Oblique')
        nut_s = sty('N', fontSize=8, textColor=MID_GREEN, leading=12)
        dis_s = sty('D', fontSize=7.5, textColor=MUTED, alignment=TA_CENTER)

        story = []
        story.append(Paragraph("Personalized Diet Plan", title_s))
        story.append(Paragraph(
            f"Patient: {patient_name or 'Patient'}  |  {diet_type}  |  {days}-Day Plan  |  {diet_plan.get('daily_calories', '')} kcal/day",
            sub_s))
        story.append(HRFlowable(width="100%", thickness=2, color=GREEN))
        story.append(Spacer(1, 8))

        if conditions:
            story.append(Paragraph("Medical Conditions", h2_s))
            story.append(Paragraph("  |  ".join(f"• {c}" for c in conditions),
                                   sty('Cond', fontSize=9, textColor=colors.HexColor('#7d3c98'))))
            story.append(Spacer(1, 6))

        if diet_plan.get("summary"):
            story.append(Paragraph("Dietary Strategy", h2_s))
            story.append(Paragraph(diet_plan["summary"], body_s))
            story.append(Spacer(1, 8))

        recs = diet_plan.get("key_recommendations", [])
        avoid = diet_plan.get("key_restrictions", [])
        if recs or avoid:
            mx = max(len(recs), len(avoid), 1)
            rows = [[Paragraph("Recommended", sty('TH', textColor=colors.white, fontName='Helvetica-Bold', fontSize=9)),
                     Paragraph("Avoid", sty('TH2', textColor=colors.white, fontName='Helvetica-Bold', fontSize=9))]]
            for i in range(mx):
                r = Paragraph(f"• {recs[i]}", green_s) if i < len(recs) else Paragraph("", body_s)
                a = Paragraph(f"• {avoid[i]}", red_s) if i < len(avoid) else Paragraph("", body_s)
                rows.append([r, a])
            t = Table(rows, colWidths=[8.5*cm, 8.5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), GREEN),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d5d8dc')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eaf4fb')]),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

        meal_labels = {
            "breakfast": "Breakfast", "mid_morning_snack": "Mid-Morning Snack",
            "lunch": "Lunch", "evening_snack": "Evening Snack", "dinner": "Dinner"
        }

        for day_data in diet_plan.get("meal_plan", []):
            story.append(Paragraph(f"📅 {day_data.get('day_name', '')}", h2_s))
            story.append(Paragraph(
                f"Total Calories: {day_data.get('total_calories', '')} kcal  |  Water: {day_data.get('water_intake', '8-10 glasses')}",
                sty('DI', fontSize=8.5, textColor=MUTED)))
            if day_data.get("daily_tip"):
                story.append(Paragraph(f"Tip: {day_data['daily_tip']}", gold_s))
            story.append(Spacer(1, 4))

            for mk, ml in meal_labels.items():
                meal = day_data.get("meals", {}).get(mk, {})
                if not meal:
                    continue
                name = meal.get("name", "")
                cal = meal.get("calories", "")
                items = meal.get("items", [])
                story.append(Paragraph(f"• {ml} — {name}  [{cal} kcal]", h3_s))
                if items:
                    story.append(Paragraph("  |  ".join(items), body_s))
                p = meal.get("protein", "")
                c = meal.get("carbs", "")
                f = meal.get("fat", "")
                if p or c or f:
                    story.append(Paragraph(f"Protein: {p}  |  Carbs: {c}  |  Fat: {f}", nut_s))
                story.append(Spacer(1, 3))

            story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor('#d5d8dc')))
            story.append(Spacer(1, 8))

        if diet_plan.get("general_tips"):
            story.append(Paragraph("General Health Tips", h2_s))
            for tip in diet_plan["general_tips"]:
                story.append(Paragraph(f"• {tip}", body_s))
            story.append(Spacer(1, 6))

        if diet_plan.get("foods_to_avoid"):
            story.append(Paragraph("Foods to Strictly Avoid", h2_s))
            story.append(Paragraph("  |  ".join(diet_plan["foods_to_avoid"]), red_s))

        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=1, color=GREEN))
        story.append(Paragraph(
            "Disclaimer: This AI-generated diet plan is for guidance only. Consult your doctor or registered dietitian before making significant dietary changes.",
            dis_s))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        raise RuntimeError("Install reportlab: pip install reportlab")