# 🥗 AI Diet Planner

**Project Name:** AI Diet Planner  
**Author:** Sabiha Anjum  
**Status:** 🚧 Under Development  

---

## 📌 Overview
AI Diet Planner is an intelligent system designed to generate **personalized diet plans** by analyzing **medical data and reports** using **Artificial Intelligence (AI)** and **Machine Learning (ML)** techniques.

The system processes both **structured medical datasets (CSV)** and **unstructured medical reports (images)** using **OCR**, enabling accurate health analysis and condition-based dietary recommendations.

---

## 🎯 Objectives
- Analyze medical report data (numerical and textual)
- Detect health conditions such as **diabetes**
- Provide AI-driven, personalized diet recommendations
- Simplify complex medical data interpretation for users

---

## ✨ Key Features
- Personalized diet planning  
- AI-based health risk prediction  
- Diabetes detection using ML models  
- Medical report analysis using OCR  
- Dataset-driven predictions  
- Simple, user-friendly workflow  

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
- **Programming Language:** Python  
- **Libraries & Frameworks:**
  - Pandas
  - NumPy
  - Scikit-learn
  - XGBoost
  - OpenCV
  - Tesseract OCR
- **Backend:** FastAPI  
- **Frontend:** React (UI Integration)  
- **Platform:** Google Colab, VS Code  
- **Data Source:** Kaggle  

---

## 🚀 Future Enhancements
- Integration with real-world medical reports (PDF / Image)
- Full web or mobile application
- Advanced Deep Learning models
- Personalized diet plan generation (PDF)
- Allergy and food preference customization
- User authentication and history tracking

---

## ⭐ Acknowledgements
- Kaggle for providing open medical datasets
- Open-source AI/ML community

---

### 🌟 If you like this project, consider giving it a ⭐ on GitHub!
