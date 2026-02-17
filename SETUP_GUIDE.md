# Quick Setup Guide
## AI-NutriCare - Installation and Testing

**By:** Sai Nikhil

---

## Quick Installation (5 Minutes)

### 1. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install all Python packages
pip install -r requirements.txt
```

**Note:** First-time installation may take 5-10 minutes due to ML libraries.

### 2. Setup Environment

```bash
# Copy environment template (if .env doesn't exist)
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Linux/Mac
```

Default SQLite database will be created automatically - no configuration needed for basic testing.

### 3. Initialize Database

```bash
python -c "from app.models.database import init_db; init_db()"
```

You should see: `✓ Database initialized`

### 4. Create Test Files

```bash
# From project root
python tests/create_test_files.py
```

This creates sample medical reports for testing.

### 5. Run Quick Test

```bash
# From project root
python test_extraction_standalone.py
```

Expected output:
```
============================================================
Data Extraction Test - Standalone
============================================================
[OK] Loaded test file: tests\test_data\sample_medical_report.txt
[OK] Text length: 1007 characters

EXTRACTED NUMERIC DATA:
{
  "cholesterol": 220.0,
  "bmi": 26.5
  ...
}

[PASS] Data extraction test PASSED!
```

---

## Running the API Server

### Option 1: Simple Start

```bash
cd backend
python app/main.py
```

### Option 2: Using Uvicorn (Recommended)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Verify Server is Running

Open browser: http://localhost:8000

You should see:
```json
{
  "message": "AI-NutriCare API",
  "version": "1.0.0",
  "status": "running"
}
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Upload Test Report

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/upload-report" ^
  -F "file=@tests/test_data/sample_medical_report.txt"
```

**Using Python:**
```python
import requests

with open('tests/test_data/sample_medical_report.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload-report',
        files={'file': f}
    )
    print(response.json())
```

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Click on `POST /api/upload-report`
3. Click "Try it out"
4. Upload a file
5. Click "Execute"

### 3. Get Report

```bash
curl http://localhost:8000/api/reports/1
```

---

## Running Full Test Suite

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_data_extraction.py -v

# Run with coverage
pytest tests/ --cov=backend/app --cov-report=html
```

---

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure you're in the correct directory and virtual environment is activated.

```bash
# Activate venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies again
pip install -r backend/requirements.txt
```

### Issue: EasyOCR not working

**Solution:** EasyOCR downloads models on first use. If it fails:
1. Check internet connection
2. Try installing Tesseract as fallback:
   ```bash
   # Windows: Download from GitHub
   # Linux: sudo apt-get install tesseract-ocr
   # Mac: brew install tesseract
   ```

### Issue: Database errors

**Solution:** Delete existing database and reinitialize:

```bash
# Delete database
rm backend/ainutricare.db  # Linux/Mac
del backend\ainutricare.db  # Windows

# Reinitialize
python -c "from app.models.database import init_db; init_db()"
```

### Issue: Port already in use

**Solution:** Use a different port:

```bash
uvicorn app.main:app --port 8001
```

---

## Verification Checklist

After setup, verify:

- [ ] `python test_extraction_standalone.py` runs successfully
- [ ] Database file `ainutricare.db` exists in `backend/` directory
- [ ] Server starts without errors
- [ ] http://localhost:8000 shows API response
- [ ] http://localhost:8000/docs shows Swagger UI
- [ ] Can upload test file via API
- [ ] Can retrieve uploaded report

---

## Next Steps

1. **Test with Real Medical Reports**: Upload actual PDF/image reports
2. **Week 3-4**: Implement ML models for health analysis
3. **Week 5-6**: Add NLP/AI interpretation
4. **Week 7-8**: Build React frontend and diet plan generator

---

## Need Help?

- Check `Milestone_Reports/` for detailed documentation
- Review `README.md` for full documentation
- Check API docs at http://localhost:8000/docs

---

**Setup Guide by:** Sai Nikhil  
**Last Updated:** January 2024
