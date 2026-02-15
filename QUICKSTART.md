# AI NutriCare System - Quick Start Guide

## 🚀 Getting Started

This guide will help you set up and run the AI NutriCare System in minutes.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2GB free disk space
- Internet connection (for initial setup)

## 🔧 Installation

### Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd ai_diet_planner

# Install required packages
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

```bash
# Windows (Command Prompt)
set NUTRICARE_ENCRYPTION_KEY=your-secure-encryption-key-here

# Windows (PowerShell)
$env:NUTRICARE_ENCRYPTION_KEY="your-secure-encryption-key-here"

# Linux/Mac
export NUTRICARE_ENCRYPTION_KEY="your-secure-encryption-key-here"
```

**Note**: For production, use a secure key management system like AWS KMS or HashiCorp Vault.

## 🎯 Running the Application

### Option 1: Streamlit Web Interface (Recommended)

```bash
# From the ai_diet_planner directory
streamlit run ui/app.py
```

The application will open in your browser at `http://localhost:8501`

### Option 2: Command Line Interface

```bash
# Process a medical report directly
python -m ai_diet_planner.main path/to/medical_report.pdf
```

### Option 3: Python API

```python
from ai_diet_planner.main import process_medical_report
from pathlib import Path

# Process a report
result = process_medical_report(Path("medical_report.txt"))

# Check results
if result.status.value == "completed":
    print(f"✓ Processing completed in {result.processing_time:.1f}s")
    print(f"Health conditions detected: {len(result.health_conditions)}")
    print(f"Alerts generated: {len(result.alerts)}")
    print(f"Diet plan generated: {result.diet_plan is not None}")
else:
    print(f"✗ Processing failed: {result.error_message}")
```

## 📝 Creating a Sample Medical Report

Create a text file named `sample_report.txt` with the following content:

```text
MEDICAL REPORT

Patient: John Doe
Date: 2024-01-15
Age: 45 years
Gender: Male

LAB RESULTS:
- Fasting Blood Glucose: 155 mg/dL (High)
- HbA1c: 7.2% (Elevated)
- Total Cholesterol: 240 mg/dL (High)
- LDL Cholesterol: 160 mg/dL (High)
- HDL Cholesterol: 35 mg/dL (Low)
- Triglycerides: 220 mg/dL (High)
- BMI: 29.5 (Overweight)
- Blood Pressure: 135/85 mmHg (Elevated)
- Hemoglobin: 14.2 g/dL (Normal)

DOCTOR'S NOTES:
Patient shows signs of prediabetes with elevated glucose and HbA1c levels.
Recommend dietary modifications to reduce sugar intake and increase fiber.
Monitor blood glucose levels regularly.
Patient has family history of diabetes.

DIETARY RECOMMENDATIONS:
- Follow a low glycemic index diet
- Reduce processed foods and added sugars
- Increase intake of vegetables and whole grains
- Limit saturated fats
- Avoid sugary beverages
- Increase physical activity to 30 minutes daily

FOLLOW-UP:
Schedule follow-up appointment in 3 months to reassess glucose levels.
```

## 🎬 Step-by-Step Demo

### Using the Web Interface

1. **Start the Application**
   ```bash
   streamlit run ui/app.py
   ```

2. **Upload Page**
   - Click "Browse files" or drag and drop `sample_report.txt`
   - (Optional) Fill in patient information:
     - Age: 45
     - Gender: Male
     - Height: 175 cm
     - Weight: 85 kg
     - Activity Level: Moderate
   - (Optional) Add dietary preferences:
     - Dietary Style: Balanced
     - Allergies: peanuts
     - Foods to Avoid: liver
   - Click "Process Report"
   - Watch the progress bar as the system:
     - Validates the file
     - Extracts text
     - Analyzes health metrics
     - Detects conditions
     - Generates diet plan

3. **Review Page**
   - Navigate to "Review" in the sidebar
   - View extracted health metrics
   - See detected health conditions
   - Review health alerts

4. **Diet Plan Page**
   - Navigate to "Diet Plan" in the sidebar
   - View personalized meal recommendations
   - See nutritional breakdown
   - Export to PDF or JSON

5. **History Page**
   - Navigate to "History" in the sidebar
   - View past reports and diet plans

### Using the Command Line

```bash
# Process the sample report
python -m ai_diet_planner.main sample_report.txt
```

Expected output:
```
Processing medical report: sample_report.txt

✓ Processing completed in 15.3s

Health Conditions Detected: 3
  - prediabetes: 85.2%
  - hypertension_stage1: 78.5%
  - hyperlipidemia: 92.1%

Alerts Generated: 5
  - WARNING: Elevated fasting glucose (155 mg/dL)
  - WARNING: Elevated HbA1c (7.2%)
  - WARNING: High total cholesterol (240 mg/dL)
  - WARNING: High LDL cholesterol (160 mg/dL)
  - CRITICAL: Low HDL cholesterol (35 mg/dL)

Diet Rules Extracted: 6

Diet Plan Generated:
  Daily Calories: 1800
  Meals: 4
```

## 🧪 Running Tests

### Run All Tests
```bash
# From the project root
pytest ai_diet_planner/ -v
```

### Run Specific Test Suites
```bash
# UI tests
pytest ai_diet_planner/ui/test_app.py -v

# Integration tests
pytest ai_diet_planner/test_main_orchestrator.py -v

# Storage tests
pytest ai_diet_planner/storage/test_data_store.py -v
```

## 📊 Example Demonstrations

### Demo 1: Complete Pipeline
```bash
cd ai_diet_planner
python -c "
from main import process_medical_report
from pathlib import Path

# Create sample report
sample_text = '''
LAB RESULTS:
- Glucose: 145 mg/dL
- Cholesterol: 230 mg/dL
- BMI: 28.5
- Blood Pressure: 130/85 mmHg

NOTES: Reduce sugar intake, increase fiber.
'''

Path('demo_report.txt').write_text(sample_text)

# Process it
result = process_medical_report(Path('demo_report.txt'))

print(f'Status: {result.status.value}')
print(f'Time: {result.processing_time:.1f}s')
print(f'Metrics: {len(result.structured_data.metrics) if result.structured_data else 0}')
print(f'Conditions: {len(result.health_conditions)}')
print(f'Alerts: {len(result.alerts)}')
"
```

### Demo 2: Storage System
```bash
cd ai_diet_planner
python storage/example_usage.py
```

### Demo 3: Diet Plan Generation
```bash
cd ai_diet_planner
python generation/example_usage.py
```

### Demo 4: Report Export
```bash
cd ai_diet_planner
python export/example_usage.py
```

## 🔍 Troubleshooting

### Issue: "Module not found" error
**Solution**: Make sure you're in the correct directory and have installed dependencies:
```bash
cd ai_diet_planner
pip install -r requirements.txt
```

### Issue: "Encryption key not provided" error
**Solution**: Set the environment variable:
```bash
# Windows
set NUTRICARE_ENCRYPTION_KEY=test-key

# Linux/Mac
export NUTRICARE_ENCRYPTION_KEY=test-key
```

### Issue: Streamlit won't start
**Solution**: Install Streamlit explicitly:
```bash
pip install streamlit>=1.28.0
```

### Issue: OCR not working
**Solution**: Install Tesseract OCR:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Issue: Low memory
**Solution**: The system requires at least 2GB RAM. Close other applications if needed.

## 📚 Additional Resources

### Documentation
- [UI README](ai_diet_planner/ui/README.md) - Web interface guide
- [Storage README](ai_diet_planner/storage/README.md) - Database and encryption
- [Generation README](ai_diet_planner/generation/README.md) - Diet plan generation
- [Export README](ai_diet_planner/export/README.md) - PDF/JSON export

### Example Scripts
- `ui/example_usage.py` - UI examples
- `storage/example_usage.py` - Storage examples
- `generation/example_usage.py` - Diet plan examples
- `export/example_usage.py` - Export examples

### Test Files
- `test_main_orchestrator.py` - Integration tests
- `ui/test_app.py` - UI tests
- `storage/test_data_store.py` - Storage tests

## 🎓 Next Steps

1. **Try the Web Interface**: Upload your own medical reports
2. **Explore the API**: Integrate with your applications
3. **Customize**: Modify diet rules, add new health conditions
4. **Deploy**: Set up for production use
5. **Contribute**: Add new features or improvements

## 🔒 Security Notes

- Always use strong encryption keys in production
- Never commit encryption keys to version control
- Use HTTPS for web deployment
- Regularly update dependencies
- Follow HIPAA compliance guidelines for healthcare data

## 💡 Tips

- Use high-quality scans (300 DPI) for best OCR results
- Provide patient information for personalized diet plans
- Export diet plans to PDF for easy sharing
- Review extracted data for accuracy
- Keep the system updated with latest dependencies

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the documentation in each module
3. Run the test suite to verify installation
4. Check the example scripts for usage patterns

## 🎉 Success!

You're now ready to use the AI NutriCare System! Start by uploading a medical report and generating your first personalized diet plan.

Happy health planning! 🥗
