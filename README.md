# AI Diet Planner

An intelligent system for generating personalized diet plans by analyzing medical data and reports using AI and Machine Learning.

## Overview

AI Diet Planner processes structured medical datasets (CSV) and unstructured medical reports (images) using OCR and AI-powered text interpretation. It provides accurate health analysis and condition-based dietary recommendations with detailed 7-day meal plans.

## Features

- **Diabetes Risk Prediction**: XGBoost ML model with 81% ROC-AUC accuracy
- **7-Day Meal Planning**: Personalized breakfast, lunch, snack, and dinner recommendations
- **Medical Report Analysis**: OCR + AI interpretation of prescriptions
- **Export Options**: PDF and JSON export for meal plans
- **Health Condition Detection**: Diabetes, hypertension, obesity, and more
- **Nutritional Information**: Calories, protein, and carbs for each meal

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.8+ |
| Frontend | React 19 |
| ML Model | XGBoost |
| OCR | Tesseract |
| AI | OpenAI GPT (optional) |
| PDF Generation | ReportLab |

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Tesseract OCR (optional, for prescription scanning)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Diabetes risk prediction |
| `/generate-meal-plan` | POST | Generate 7-day meal plan |
| `/upload-prescription` | POST | Upload and analyze prescription |
| `/export-pdf` | POST | Export meal plan as PDF |
| `/export-json` | POST | Export meal plan as JSON |

## Project Structure

```
AI Diet Planner/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── meal_planner.py      # Meal plan generator
│   ├── ai_interpreter.py    # AI text interpretation
│   ├── ocr_utils.py         # OCR functionality
│   ├── model/               # Trained ML model
│   ├── uploads/             # Uploaded files
│   └── exports/             # Generated exports
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   └── App.css          # Styling
│   └── package.json
├── data/
│   ├── diabetes.csv         # Training dataset
│   └── image/               # Sample images
└── train_model.py           # Model training script
```

## Datasets

1. **Pima Indians Diabetes Database** (Kaggle)
   - Used for diabetes risk prediction model training

2. **Medical Report Images**
   - Used for OCR text extraction testing

## Usage

1. **Health Assessment**: Enter health parameters (glucose, BMI, blood pressure) to get diabetes risk prediction
2. **Meal Plan Generation**: Click "Generate Full Meal Plan" for personalized 7-day meal schedules
3. **Prescription Upload**: Upload medical prescription images for automatic health parameter extraction
4. **Export**: Download meal plans as PDF or JSON

## Development

### Train Model
```bash
python train_model.py
```

### Run Tests
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Author

**Sabiha Anjum**

Springboard Mentorship Program - AI/ML Project

## License

Educational use only.
