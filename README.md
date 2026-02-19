AI-NutriCare: Personalized Diet Plan Generator 🥗
AI-NutriCare is an end-to-end AI/ML application that analyzes medical reports (Images/PDFs) to generate personalized 7-day nutritional strategies. By extracting clinical vitals like Glucose, Hemoglobin, and CRP, the system provides actionable dietary insights tailored to specific health conditions.

🚀 Key Features
AI-Powered OCR: Uses EasyOCR to extract text from medical lab reports with high accuracy.

Clinical Intelligence: Detects abnormal vitals (Anemia, Diabetes, Hypertension, Inflammation) using custom ML logic and clinical thresholds.

Dynamic 7-Day Diet: Generates a rotation of 21 unique meals per week based on the detected health condition.

Medical Dashboard: A modern React interface for seamless report uploading and visualization.

Professional Reports: Export your personalized diet plan and clinical insights directly to PDF.

🛠️ Tech Stack
Frontend: React.js, Tailwind CSS, Lucide-React

Backend: FastAPI (Python), Uvicorn

AI/ML: EasyOCR, Scikit-learn (RandomForest, Gradient Boosting), OpenCV

Data Processing: Pandas, Numpy, Regex

📋 Installation & Setup
1. Clone the repository
Bash
git clone https://github.com/your-username/AI_Nutricare.git
cd AI_Nutricare
2. Backend Setup
Bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload
3. Frontend Setup
Bash
cd frontend
npm install
npm start
📂 Project Structure
backend/app.py: Main FastAPI server and OCR logic.

backend/train_model.py: ML model training and clinical alert thresholds.

backend/milestone3.py: Diet mapping logic and clinical interpretation.

frontend/src/App.js: React Dashboard and PDF export functionality.

💡 How It Works
Upload: User uploads a report (e.g., CBC or Blood Sugar report).

Analyze: The system uses OCR to find keywords like "Hemoglobin" or "RBS" and grabs the numerical values.

Alert: If values are outside the normal range (e.g., Hb < 13.0), a clinical alert is triggered.

Prescribe: A condition-specific 7-day diet plan is displayed instantly.
![Dashboard UI](./assets/Dashboard.png)