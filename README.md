# 🥗 AI-NutriCare: Personalized Diet Plan Generator

AI-NutriCare is an end-to-end AI/ML application that analyzes medical reports (Images/PDFs) to generate personalized 7-day nutritional strategies. By extracting clinical vitals such as **Glucose**, **Hemoglobin**, and **CRP**, the system provides actionable dietary insights tailored to specific health conditions.

---

## 🚀 Key Features

* **AI-Powered OCR:** Uses EasyOCR to extract text from medical lab reports with high accuracy.
* **Clinical Intelligence:** Detects abnormal vitals (Anemia, Diabetes, Hypertension, Inflammation) using custom ML logic and clinical thresholds.
* **Dynamic 7-Day Diet:** Generates a rotation of 21 unique meals per week based on the detected health condition.
* **Medical Dashboard:** A modern React interface for seamless report uploading and visualization.
* **Professional Reports:** Export personalized diet plans and clinical insights directly to PDF.

---

## 📸 Dashboard Preview

<img width="1723" height="895" alt="Dashboard" src="https://github.com/user-attachments/assets/9e1274bd-6bcd-4bf1-a0c5-94eacea18783" />


---

## 📋 Project Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shrey-l/AI_Nutricare.git
cd AI_Nutricare
```

### 2. Backend Setup (FastAPI)

This handles OCR extraction and clinical alert logic.

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

### 3. Frontend Setup (React)

This launches the user dashboard interface.

```bash
# Open a new terminal tab or window
cd frontend
npm install
npm start
```

---

## 🛠️ Tech Stack

| Layer           | Technologies                         |
| --------------- | ------------------------------------ |
| Frontend        | React.js, Tailwind CSS, Lucide-React |
| Backend         | FastAPI (Python), Uvicorn            |
| AI/ML           | EasyOCR, Scikit-learn, OpenCV        |
| Data Processing | Pandas, NumPy, Regex                 |

---

## 📂 Project Structure

* `backend/app.py` — Main FastAPI server and OCR extraction logic
* `backend/train_model.py` — ML model training and clinical alert thresholds
* `backend/milestone3.py` — Diet mapping logic and clinical interpretation
* `frontend/src/App.js` — React dashboard and PDF export functionality

---

## 💡 How It Works

1. **Upload**
   User uploads a medical report (e.g., CBC or Blood Sugar report).

2. **Analyze**
   The system uses OCR to identify keywords like Hemoglobin or RBS and extracts numerical values.

3. **Alert**
   If values are outside the normal range (e.g., Hb < 13.0), a clinical alert is triggered.

4. **Prescribe**
   A condition-specific 7-day diet plan is displayed instantly.
