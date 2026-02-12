# 🥗 AI Diet Planner

**Project Name:** AI Diet Planner  
**Author:** Sabiha Anjum  
**Status:** ✅ Weeks 5-8 Complete - Advanced Features Implemented  

---

## 📌 Overview
AI Diet Planner is an intelligent system designed to generate **personalized diet plans** by analyzing **medical data and reports** using **Artificial Intelligence (AI)** and **Machine Learning (ML)** techniques.

The system processes both **structured medical datasets (CSV)** and **unstructured medical reports (images)** using **OCR** and **AI-powered text interpretation**, enabling accurate health analysis and condition-based dietary recommendations with detailed meal plans.

---

## 🎯 Objectives
- Analyze medical report data (numerical and textual)
- Detect health conditions such as **diabetes, hypertension, sepsis, pneumonia**
- Provide AI-driven, personalized diet recommendations with **breakfast, lunch, and dinner** plans
- Convert doctor notes into **actionable diet rules** using AI (OpenAI GPT)
- Export meal plans in **PDF and JSON** formats
- Simplify complex medical data interpretation for users

---

## ✨ Key Features

### 🔥 NEW - Week 5-8 Enhancements
- **🤖 AI-Powered Text Interpretation**: GPT-based intelligent analysis of doctor notes and prescriptions
- **🍽️ Comprehensive Meal Plans**: Detailed breakfast, lunch, and dinner recommendations
- **📊 Nutritional Information**: Calories, protein, carbs for each meal
- **🥤 Snack Recommendations**: Healthy snack options throughout the day
- **📄 PDF Export**: Professional meal plan reports
- **💾 JSON Export**: Structured data export for integration
- **📈 Daily Nutritional Summary**: Complete overview of daily intake
- **💧 Hydration Guidelines**: Water intake recommendations
- **⚠️ Important Notes**: Personalized dietary guidelines and tips

### Core Features
- Personalized diet planning based on health conditions
- AI-based health risk prediction (diabetes, hypertension, obesity)
- ML-powered diabetes detection using XGBoost
- Medical report analysis using OCR + AI interpretation
- Dataset-driven predictions with high accuracy
- Modern, responsive UI with React
- RESTful API with FastAPI

---

## 🏗️ Project Milestones

### ✅ Week 5-6: NLP/AI Text Interpretation
- ✅ Integrated OpenAI GPT for intelligent prescription analysis
- ✅ Rule-based fallback system for robust interpretation
- ✅ Maps textual instructions to actionable diet guidelines
- ✅ Achieves 80%+ accuracy in converting notes to diet rules
- ✅ Detects: diabetes, hypertension, sepsis, pneumonia, obesity, gastric issues

### ✅ Week 7-8: Diet Plan Generation & UI Integration
- ✅ Comprehensive meal plan generator with breakfast, lunch, dinner
- ✅ Combined ML diabetes prediction + AI diet recommendations
- ✅ Modern React UI with meal cards and nutritional info
- ✅ PDF export with professional formatting (reportlab)
- ✅ JSON export for data portability
- ✅ Fully functional end-to-end prototype
- ✅ Tested with sample medical reports

---

## 📊 Datasets Used

### 1️⃣ CSV Dataset (Structured Medical Data)
- **Dataset:** Pima Indians Diabetes Database  
- **Source:** Kaggle  
- **Link:**  
  https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database  

**Purpose:**  
Used to predict diabetes risk and analyze patient health parameters such as:
- Glucose level  
- BMI  
- Insulin  
- Blood pressure  
- Age  

---

### 2️⃣ Image Dataset (Unstructured Data)
- **Dataset:** Bajaj Dataset  
- **Source:** Kaggle  
- **Link:**  
  https://www.kaggle.com/datasets/dikshaasinghhh/bajaj  

**Purpose:**  
Used to simulate scanned medical reports and experiment with OCR-based text extraction workflows.

---

## 🧾 OCR Integration
Optical Character Recognition (OCR) is implemented to extract textual and numerical data from scanned medical reports.

**Capabilities:**
- Extracts text from medical images
- Preprocesses and cleans OCR output
- Converts unstructured data into ML-ready format

**Tools Used:**
- OpenCV
- Tesseract OCR
- Python

---

## 🧠 Machine Learning Approach
- Binary classification for diabetes prediction
- Models experimented:
  - Logistic Regression
  - Random Forest
  - Support Vector Machine (SVM)
  - XGBoost (Final Model)
- Performance evaluated using:
  - Accuracy
  - ROC-AUC score
  - Cross-validation

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI
- **ML/AI:** 
  - XGBoost (Diabetes Prediction)
  - OpenAI GPT-3.5 (Text Interpretation)
  - Scikit-learn (Data Processing)
- **OCR:** Tesseract, OpenCV, Pillow
- **Export:** ReportLab (PDF), JSON

### Frontend
- **Framework:** React 19
- **Styling:** Custom CSS with responsive design
- **Features:** Dynamic meal cards, export buttons, real-time updates

### Data & Models
- **Language:** Python 3.13
- **Libraries:** Pandas, NumPy
- **Model:** XGBoost (ROC-AUC: 0.81)
- **Platform:** VS Code, Google Colab
- **Data Source:** Kaggle

---

## 🚀 API Endpoints

### 1. Diabetes Risk Prediction
```http
POST /predict
Content-Type: application/json

{
  "pregnancies": 1,
  "glucose": 120,
  "blood_pressure": 70,
  "skin_thickness": 20,
  "insulin": 80,
  "bmi": 25.5,
  "dpf": 0.5,
  "age": 30
}
```

### 2. Complete Meal Plan Generation
```http
POST /generate-meal-plan
Content-Type: application/json

{
  "pregnancies": 1,
  "glucose": 140,
  "blood_pressure": 85,
  "skin_thickness": 25,
  "insulin": 90,
  "bmi": 28.0,
  "dpf": 0.6,
  "age": 35
}
```
**Returns:** Diabetes risk + personalized meal plan with breakfast, lunch, dinner

### 3. Prescription Analysis (OCR + AI)
```http
POST /upload-prescription
Content-Type: multipart/form-data

file: [prescription image]
```
**Returns:** Extracted text + AI interpretation + meal plan

### 4. Export to PDF
```http
POST /export-pdf
Content-Type: application/json

{
  "meal_plan": {...},
  "risk_level": "Moderate Risk",
  ...
}
```
**Returns:** PDF file download

### 5. Export to JSON
```http
POST /export-json
Content-Type: application/json

{
  "meal_plan": {...},
  "conditions": [...],
  ...
}
```
**Returns:** JSON file download

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.13+
- Node.js 16+
- Tesseract OCR installed on system
- (Optional) OpenAI API key for GPT integration

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set OpenAI API key for GPT features
set OPENAI_API_KEY=your_api_key_here

# Run backend server
python main.py
```
Backend runs on: http://localhost:8000

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```
Frontend runs on: http://localhost:3000

---

## 🎨 Sample Meal Plan Output

```json
{
  "breakfast": {
    "name": "Oatmeal with berries and nuts",
    "description": "Steel-cut oats with fresh berries, almonds, and cinnamon",
    "calories": 350,
    "protein": "12g",
    "carbs": "45g"
  },
  "lunch": {
    "name": "Grilled chicken salad",
    "description": "Grilled chicken breast with mixed greens, olive oil dressing",
    "calories": 420,
    "protein": "35g",
    "carbs": "20g"
  },
  "dinner": {
    "name": "Baked salmon with steamed vegetables",
    "description": "Herb-crusted salmon with broccoli and cauliflower",
    "calories": 450,
    "protein": "40g",
    "carbs": "25g"
  },
  "snacks": [
    {
      "name": "Greek yogurt",
      "description": "Plain Greek yogurt with berries",
      "calories": 120
    }
  ],
  "daily_summary": {
    "total_calories": "1400-1600",
    "protein": "85-100g",
    "carbs": "150-180g",
    "focus": "Low glycemic index foods"
  }
}
```

---

## 🔬 Machine Learning Model Performance

### XGBoost Diabetes Classifier
- **ROC-AUC Score:** 0.81
- **Optimal Threshold:** 0.18
- **Features:** 8 health parameters
- **Risk Categories:** Low, Moderate, High

### AI Text Interpretation
- **Primary:** OpenAI GPT-3.5 Turbo
- **Fallback:** Enhanced rule-based system
- **Success Rate:** 80%+ accurate diet rule extraction
- **Conditions Detected:** 9+ medical conditions

---

## 🚀 Future Enhancements
- 🔐 User authentication and profile management
- 📱 Mobile application (React Native)
- 🗄️ Database integration for meal plan history
- 🌍 Multi-language support
- 🥗 Recipe suggestions with cooking instructions
- 📊 Progress tracking and health analytics
- 🔔 Meal reminders and notifications
- 🤝 Integration with fitness trackers
- 🧬 Advanced Deep Learning models (BERT, GPT-4)
- 🏥 Integration with Electronic Health Records (EHR)
- 🍎 Allergy and food preference customization
- 📈 Long-term diet plan (weekly/monthly)

---

## 📝 Usage Examples

### Example 1: Diabetes Risk Assessment
1. Enter patient health parameters in the form
2. Click "Predict Risk" to get risk level
3. Click "Generate Full Meal Plan" to get personalized meals
4. Export plan as PDF or JSON

### Example 2: Prescription Analysis
1. Upload a medical prescription image
2. System extracts text using OCR
3. AI interprets medical conditions and recommendations
4. Generates personalized meal plan automatically
5. Export complete analysis

---

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest  # Run unit tests (if implemented)

# Manual API testing
curl http://localhost:8000/
```

### Frontend Testing
```bash
cd frontend
npm test
```

---

## 📄 License
This project is created for educational purposes as part of Springboard mentorship program.

---

## ⭐ Acknowledgements
- **Springboard Mentorship Program** for guidance and support
- **Kaggle** for providing open medical datasets
- **OpenAI** for GPT API access
- **Open-source AI/ML community** for tools and libraries

---

## 👨‍💻 Author
**Sabiha Anjum**
- GitHub: springboardmentor12233a-tech/ai_diet_planner
- Project Status: Active Development
- Current Milestone: Weeks 5-8 Complete ✅

---

## 📊 Project Structure
```
AI Diet Planner/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── ai_interpreter.py       # GPT-based text interpretation
│   ├── meal_planner.py         # Meal plan generator
│   ├── ocr_utils.py           # OCR functionality
│   ├── nlp_utils.py           # NLP utilities
│   ├── train_model.py         # ML model training
│   ├── requirements.txt       # Python dependencies
│   ├── model/
│   │   └── diabetes_xgb.json  # Trained XGBoost model
│   ├── uploads/               # Uploaded prescriptions
│   └── exports/               # Generated PDFs/JSONs
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styling
│   │   └── index.js          # Entry point
│   ├── public/
│   └── package.json          # Node dependencies
├── data/
│   ├── diabetes.csv          # Training dataset
│   └── image/                # Sample medical images
└── README.md                 # Project documentation
```

---

### 🌟 If you like this project, consider giving it a ⭐ on GitHub!

**End-to-end AI-powered diet planning system - From medical data to personalized meal plans in seconds!**
