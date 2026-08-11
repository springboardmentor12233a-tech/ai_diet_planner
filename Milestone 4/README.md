# AI-NutriCare — Personalized Diet Plan Generator

End-to-end AI/ML-based system that accepts medical reports, extracts lab values, analyzes health conditions, interprets doctor notes, and generates a **7-day weekly diet plan** with export to PDF and JSON.

## Features

1. **Medical Report Input** — PDF, JPG, PNG, or TXT upload; OCR (EasyOCR) for images/scanned PDFs
2. **Structured Extraction** — Blood sugar, cholesterol, BMI, blood pressure, doctor notes
3. **Health Analysis** — Threshold-based classification (e.g. blood sugar > 126 → diabetes risk)
4. **NLP Interpretation** — Keyword-based diet rules from doctor notes (e.g. "avoid sugar" → low-sugar)
5. **7-Day Diet Plan** — Breakfast, mid-morning snack, lunch, evening snack, dinner; respects restrictions and allergies
6. **Export** — PDF (ReportLab) and JSON download

## Setup

```bash
cd weeklydietplan
pip install -r requirements.txt
```

- **Windows (PDF OCR):** For scanned PDFs, install [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) and add `bin` to PATH, or use text/PDF with embedded text only.
- **First run:** EasyOCR downloads language data once (~100MB).

## Run

```bash
streamlit run app.py
```

Open the URL shown (e.g. http://localhost:8501).

## Quick Test Without Report

1. Skip upload and click **Generate 7-Day Diet Plan** after filling name, age, weight, height, gender, diet preference, allergies, and health goal.
2. Or upload `sample_report.txt` and click **Extract & Analyze Report**, then fill the form and generate.

## Project Structure

- `app.py` — Streamlit UI and pipeline
- `modules/medical_report_parser.py` — File read + OCR + regex extraction
- `modules/health_analyzer.py` — Threshold-based condition classification
- `modules/nlp_interpreter.py` — Doctor notes → diet rules
- `modules/meal_database.py` — Meals by type and tags
- `modules/diet_plan_generator.py` — User profile, BMI/calories, 7-day plan
- `modules/export_module.py` — PDF and JSON export

## Disclaimer

Academic prototype only. Not a substitute for professional medical or dietary advice.
