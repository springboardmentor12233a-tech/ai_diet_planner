AI/ML-Based Personalized Diet Plan Generator from Medical Reports

About the Project

AI NutriCare is a smart web application that analyzes medical lab reports and generates a personalized 7-day diet plan.

Users can upload a lab report image, and the system automatically:

Extracts health parameters using OCR

Identifies health conditions (Diabetes, Cholesterol, BP, BMI)

Recommends healthy foods

Suggests foods to avoid

Generates a weekly meal plan

Allows downloading the plan as PDF or JSON

The goal of this project is to simplify diet planning using Artificial Intelligence


🎯 Problem Statement

Many people receive lab reports but do not clearly understand:

Whether their values are normal or high

What foods they should eat

What foods they should avoid

AI NutriCare bridges this gap by automatically analyzing reports and providing clear, easy-to-follow diet recommendations.


⚙️ How It Works

User uploads a lab report image (PNG/JPG)

EasyOCR extracts text from the image

System detects health values:

Glucose

Cholesterol

Blood Pressure

BMI

Insulin

Health conditions are classified:

Normal

Elevated / Pre-stage

High

Diet engine generates:

Main recommended foods

Foods to avoid

7-day personalized meal plan

User can download the plan as PDF or JSON

🏗️ System Architecture

Lab Report Image
        ↓
     EasyOCR
        ↓
  Value Extraction
        ↓
 Health Classification
        ↓
 Diet Recommendation Engine
        ↓
 Weekly Plan Generation
        ↓
   PDF / JSON Export


| Category             | Technology    |
| -------------------- | ------------- |
| Frontend             | Streamlit     |
| OCR                  | EasyOCR       |
| Machine Learning     | Scikit-learn  |
| Data Processing      | Pandas, NumPy |
| Model Saving         | Joblib        |
| PDF Generation       | ReportLab     |
| Programming Language | Python        |

✨ Key Features

✔ Upload medical lab report image
✔ Automatic value extraction
✔ Health status detection (Normal / Pre / High)
✔ Recommended foods list
✔ Foods to avoid list
✔ 7-day personalized weekly plan
✔ Download as:

PDF

JSON

📂 Project Structure
AI_NutriCare/
│
├── app.py
├── models/
│   ├── best_model.pkl
│   └── scaler.pkl
├── data/
├── notebooks/
├── requirements.txt
└── README.md


🚀 How to Run the Project
Step 1: Clone Repository
git clone https://github.com/your-username/AI-NutriCare.git
cd AI-NutriCare

Step 2: Create Environment
conda create -n nutricare python=3.9
conda activate nutricare

Step 3: Install Dependencies
pip install -r requirements.txt

Step 4: Run Application
streamlit run app.py


Open in browser:

http://localhost:8501

📊 Sample Output

The system displays:

Health Status Summary

Main Recommended Foods

Foods to Avoid

7-Day Weekly Diet Plan

Downloadable PDF Report

🔮 Future Improvements

Calorie-based personalized plans

User login system

Cloud deployment

Mobile app version

Real-time nutrition tracking

