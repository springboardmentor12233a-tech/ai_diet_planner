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

