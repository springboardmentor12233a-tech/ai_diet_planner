# 🥗 AI/ML-Based Personalized Diet Plan Generator from Medical Reports

**Project Name:** AI-NutriCare (AI Diet Planner)  
**Status:** Under Development  
**Author:** Tanishq Chauhan  

---

## 📌 Overview

AI-NutriCare is an intelligent AI/ML-based system designed to generate **personalized diet plans** by analyzing **medical reports and health data**.  
Medical reports often contain complex numerical values and unstructured doctor notes that are difficult for patients to interpret. This project aims to simplify that process by using **OCR, Machine Learning, and NLP techniques** to extract meaningful insights and recommend suitable diet plans.

The system processes **CSV-based medical datasets**, **scanned medical report images**, and **nutrition datasets** to understand a user’s health condition and generate tailored dietary recommendations.

---

## 🎯 Objectives

- Parse medical reports (CSV, scanned images)
- Extract numeric lab values and textual doctor notes
- Analyze medical data for health conditions (e.g., diabetes)
- Generate AI-driven personalized diet recommendations
- Convert unstructured medical data into structured formats
- Lay the foundation for future ML/NLP-based diet planning

---

## ✨ Key Features

- Medical report analysis using OCR  
- Extraction of lab values with confidence scores   
- Personalized diet recommendation framework  
- Simple and user-friendly approach
- AI-based health recommendations

---

## 📊 Datasets Used

### 1️⃣ Pima Indians Diabetes Database  
**Type:** CSV (Structured Medical Data)  
**Source:** Kaggle  
**Link:**  
https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database  

**Purpose:**  
- Used to analyze numeric medical parameters such as glucose, BMI, insulin, age, etc.
- Acts as a benchmark dataset for diabetes risk prediction and health analysis.

**Key Columns:**  
Pregnancies, Glucose, BloodPressure, Insulin, BMI, Age, Outcome

---

### 2️⃣ Medical Lab Report Dataset  
**Type:** Image Dataset (Scanned Medical Reports)  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/dikshaasinghhh/bajaj

**Purpose:**  
- Used to implement OCR on real-world medical reports
- Enables extraction of both numeric lab values and textual doctor notes
- Core dataset for unstructured data processing

**Data Size:**  
426 scanned medical report images

---

### 3️⃣ Food Nutrition Dataset  
**Type:** CSV (Nutrition Data)  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/utsavdey1410/food-nutrition-dataset

**Files:**  
- FOOD-DATA-GROUP1.csv  
- FOOD-DATA-GROUP2.csv  
- FOOD-DATA-GROUP3.csv  
- FOOD-DATA-GROUP4.csv  
- FOOD-DATA-GROUP5.csv  

**Purpose:**  
- Provides detailed macro- and micro-nutrient information
- Used as the primary nutrition intelligence source
- Supports diet planning for diabetes, hypertension, and general health

**Key Information:**  
Calories, fats, carbohydrates, proteins, vitamins, minerals, sodium, cholesterol, nutrition density

---

### 4️⃣ Diet Recommendations Dataset  
**Type:** CSV (Health Profile → Diet Mapping)  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/ziya07/diet-recommendations-dataset

**Purpose:**  
- Maps patient health profiles to diet recommendations
- Contains disease type, severity, allergies, preferences, and target diet
- Acts as ground truth for supervised diet recommendation logic

**Target Column:**  
Diet_Recommendation (Low_Carb, Low_Sodium, Balanced)

---

## 🧠 OCR Integration

OCR is implemented using **EasyOCR** to extract text from scanned medical report images.

### OCR Capabilities:
- Extracts raw text from medical reports
- Provides **confidence score for each extracted text segment**
- Converts unstructured image data into structured JSON output
- Displays image and extracted text side-by-side for validation

---

## 🧱 Project Structure

AI-DIET-PLANNER/
│
├── data/
│ ├── medical_reports_images/
│ ├── food_nutrition/
│ ├── pima_diabetes.csv
│ ├── diet_recommendations.csv
│ └── healthy_eating.csv
│
├── src/
│ ├── ocr_easyocr.py
│ ├── load_csv_datasets.py
│ └── utils.py
│
├── outputs/
│ └── ocr_results.json
│
├── notebooks/
│ └── (Google Colab notebooks)
│
├── requirements.txt
└── README.md


---

## ✅ Milestone-1 (Weeks 1–2): Data Collection & Preprocessing

### Completed Tasks

- ✔ Collected structured and unstructured medical datasets  
- ✔ Loaded and explored all CSV datasets  
- ✔ Implemented OCR on scanned medical reports using EasyOCR  
- ✔ Extracted numeric lab values and textual doctor notes  
- ✔ Generated confidence scores for OCR output  
- ✔ Converted extracted data into structured formats (JSON / DataFrame)  

### Milestone Outcome

> Successfully extracted structured numeric and textual data from sample medical reports, forming a solid foundation for further ML and NLP-based analysis.

---

## 🛠️ Technology Stack

- **Programming Language:** Python  
- **Libraries:**  
  - Pandas  
  - NumPy  
  - EasyOCR  
  - OpenCV  
  - Matplotlib  
- **Development Platforms:**  
  - Google Colab  
  - VS Code  
- **Data Source:** Kaggle  

---

## 🔮 Future Enhancements

- NLP-based interpretation of doctor notes
- Disease risk classification models
- Constraint-based diet plan generation
- PDF/HTML diet plan export
- Allergy- and preference-aware personalization
- Web or mobile application interface

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!

