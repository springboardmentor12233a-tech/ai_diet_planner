
---

# AI-NutriCare  
## AI/ML-Based Personalized Diet Plan Generator from Medical Reports  

**Project Status:** Completed ✅  
**Developed By:** Sai Nikhil  
**Version:** 1.0.0  

---

## 📖 Overview  

AI-NutriCare is an intelligent system that analyzes medical reports (PDF, images, text) to extract health metrics and generate personalized diet plans. It leverages OCR, NLP, and ML technologies to interpret medical data and provide actionable dietary recommendations.  

---

## ✨ Key Features  
- 📄 **Multi-format Support**: PDF, images (JPG, PNG, BMP), and text files  
- 🔍 **Intelligent Extraction**: OCR + pattern matching for medical metrics  
- 🔒 **Secure Storage**: Encrypted storage of sensitive medical data  
- 📊 **Health Analysis**: Automatic detection of health conditions  
- 🍎 **Personalized Diet Plans**: AI-generated diet recommendations  
- 🌐 **REST API**: FastAPI-based backend for easy integration  

---

## 📊 Datasets Used  

This project uses publicly available Kaggle datasets for training and evaluation:  

- **Pima Indians Diabetes Database**  
  [Link](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)  
  - Contains diagnostic measurements for diabetes prediction.  
  - Used for ML model training and health condition detection.  

- **Bajaj Medical Image Dataset**  
  [Link](https://www.kaggle.com/datasets/dikshaasinghhh/bajaj)  
  - Contains medical images for OCR and health metric extraction.  
  - Used to validate OCR pipelines and image-based report analysis.  

---

## 🧠 Technical Architecture  

- **Hybrid ML Intelligence (93.14% Accuracy)**: Random Forest, XGBoost, LightGBM combined via Voting Classifier.  
- **Diet Generation Expert System**: Constraint satisfaction, nutritional calculus, cuisine rotation.  
- **NLP Interpretation**: Biomedical NER + rule-based fallback for allergies/restrictions.  

---

## ⚙️ Installation & Setup  

```bash
# Clone repository
git clone <repository-url>
cd ai_date_plan

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Initialize database
python -c "from app.models.database import init_db; init_db()"
```

---

## 🚀 Running the Application  

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000`  
- API Docs: `http://localhost:8000/docs`  

---

## 🧪 Testing  

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## 📌 Usage Examples  

### Upload a Medical Report (Python)  
```python
import requests

with open('medical_report.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload-report',
        files={'file': f},
        data={'user_id': 1}
    )
    result = response.json()
    print("Report ID:", result['report_id'])
    print("Extracted Data:", result['extracted_data'])
```

### Health Check (cURL)  
```bash
curl http://localhost:8000/health
```

### List Reports (cURL)  
```bash
curl http://localhost:8000/api/reports?user_id=1
```

---

## 🔒 Security Features  
- Encryption at rest (Fernet).  
- PBKDF2 key derivation.  
- Input validation & sanitization.  

---

## 📜 License  
This project is part of an academic/research initiative. Refer to project requirements for licensing.  

---

## 🙏 Acknowledgments  
- OCR: EasyOCR, Tesseract  
- ML: scikit-learn, XGBoost, LightGBM  
- NLP: OpenAI GPT-4, BERT  
- Datasets: Kaggle (Pima Indians Diabetes, Bajaj Medical Images)  

---

