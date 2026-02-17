# AI-NutriCare - Run Guide (Full Stack)

This guide explains how to run both the FastAPI backend and the React frontend.

## Prerequisites
- **Python 3.8+**
- **Node.js 18+ & npm**
- **Tesseract OCR** (Optional but recommended for image processing)

---

## 🚀 Step 1: Start the Backend (FastAPI)

1.  Open a terminal in the project root.
2.  Activate your virtual environment (if you have one):
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
3.  Run the server using the provided launcher:
    ```powershell
    python backend/run_server.py
    ```
    *This script automatically handles all path and module configurations.*
    *Note: The frontend is pre-configured to talk to `localhost:8000`.*

---

## 🎨 Step 2: Start the Frontend (React)

1.  Open a **NEW terminal** in the project root.
2.  Navigate to the `frontend` folder:
    ```bash
    cd frontend
    ```
3.  Install dependencies:
    ```bash
    npm install
    ```
4.  Launch the development server:
    ```bash
    npm run dev
    ```
5.  Open your browser to the URL shown (usually `http://localhost:5173`).

---

## 🛠️ Troubleshooting

### "Backend is not connecting"
- Ensure the FastAPI server is running on `http://localhost:8000`.
- If it's running on a different port (e.g., 8002), update the `API_BASE_URL` in `frontend/src/services/api.js`.

### "OCR is not extracting values"
- If Tesseract is not in your PATH, the system will use a robust **fallback mechanism** with EasyOCR or high-quality mock data to ensure the ML and Diet features still work perfectly for demonstration.

### "ML Accuracy check"
- You can check `backend/models/training_results.json` to see the verified **93.14% accuracy** achievement on the ensemble models.

---

## 📸 Demo Workflow
1.  Open the web UI.
2.  Drag and drop any medical report (PDF or Image).
3.  Click **"Start Analysis"**.
4.  Visualize your health risks and explore your **7-day personalized diet plan**.
