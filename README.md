# ai_diet_planner

# 🥗 AI/ML-Based Personalized Diet Plan Generator from Medical Reports

**Project Name:** AI-NutriCare (AI Diet Planner)  
**Status:** Under Development  
**Author:** Nikhita.B

---

## 📌 Overview
AI-NutriCare is an AI/ML-based system that generates **personalized diet plans** by analyzing medical reports and patient health data.  

Medical reports contain **numerical lab values** (blood sugar, cholesterol, BMI) and **doctor notes/prescriptions** that are difficult to interpret.  
This system uses **OCR, Machine Learning, and NLP models** to extract key information and create diet recommendations tailored to each patient’s **health conditions, allergies, and dietary preferences**.

It can handle **PDFs, text files, and scanned medical images**, making it practical for real-world applications.

---

## 🎯 Objectives
- Extract structured data from medical reports (PDF, text, scanned images)  
- Analyze numeric lab results to detect health conditions (e.g., diabetes, high cholesterol)  
- Interpret textual doctor notes using AI/NLP techniques  
- Generate **daily personalized diet plans** based on the patient’s health profile  
- Provide outputs in **PDF, HTML, or JSON formats**  

---

## ✨ Key Features
- OCR-based extraction of numeric and textual medical data  
- ML models to detect health risks from lab results  
- NLP/AI analysis of doctor notes and prescriptions  
- Personalized diet plan generation considering **health, allergies, and preferences**  
- Exportable diet plans in **PDF or JSON**  
- User-friendly interface for report upload and diet visualization  

---

## 🧠 OCR Integration
OCR (Optical Character Recognition) is used to extract text from scanned medical reports and images.  

**Capabilities:**  
- Extract numeric lab values and doctor notes from reports  
- Clean and structure unstructured text into JSON/DataFrames  
- Provide confidence scores for extracted data  
- Prepare data for ML/NLP models  
- Supports multiple formats: PDF, image, and text files  

---

## 📊 Expected Outcomes
- Automatic detection of **critical health metrics** from medical reports  
- Generation of **personalized diet plans** tailored to each patient  
- Exportable diet plans in **PDF/JSON** format  
- Easy-to-understand dashboard to **visualize diet recommendations**  

---

## 🛠️ Technology Stack

**Programming Language:** Python 3  

**Libraries & Tools:**  
- **ML:** scikit-learn, XGBoost, LightGBM  
- **AI/NLP:** GPT-4/GPT-5, BERT  
- **OCR:** Tesseract OCR, EasyOCR  
- **Data Processing:** Pandas, NumPy  
- **Computer Vision:** OpenCV  
- **Visualization & Frontend:** Streamlit, React  
- **Database:** PostgreSQL / SQLite  
- **Export Formats:** PDF (ReportLab), JSON  

**Platform:** Google Colab / VS Code  
**Data Source:** Kaggle  

---

## 🔮 Future Enhancements
- NLP-based interpretation of doctor notes for better recommendations  
- Advanced disease risk prediction using ML/Deep Learning models  
- Constraint-based diet plan generation considering preferences & allergies  
- PDF/HTML diet plan export  
- Web or mobile application interface for easier access  
- Integration with hospital systems for automatic report input  

---

## 📊 Datasets Used

### CSV Dataset (Medical Data)
**Pima Indians Diabetes Database**  
Source: Kaggle  
https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database  

**Purpose:** Used to analyze and predict diabetes risk using medical parameters such as glucose, BMI, insulin levels, and age.

---

### Image Dataset (Medical Reports)
**Bajaj Dataset**  
Source: Kaggle  
https://www.kaggle.com/datasets/dikshaasinghhh/bajaj  

**Purpose:** Used for experimenting with image-based medical reports and OCR workflows.

---
