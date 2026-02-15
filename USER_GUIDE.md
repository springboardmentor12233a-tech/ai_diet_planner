# AI NutriCare System - User Guide

## Introduction

Welcome to the AI NutriCare System! This guide will help you use the web interface to process medical reports and generate personalized diet plans.

## Getting Started

### Prerequisites

1. Python 3.8 or higher installed
2. All dependencies installed (see QUICKSTART.md)
3. Required API keys configured (OpenAI, USDA FoodData Central)
4. Encryption key set in environment

### Starting the Application

Open a terminal and run:

```bash
streamlit run ai_diet_planner/ui/app.py
```

The application will open in your web browser at `http://localhost:8501`

---

## Using the Interface

The application has four main pages accessible from the sidebar:

### 1. Upload Page

**Purpose:** Upload medical reports and enter patient information

#### Steps:

1. **Upload Medical Report**
   - Click "Browse files" or drag and drop your medical report
   - Supported formats: PDF, JPEG, PNG, TIFF, TXT
   - Maximum file size: 10MB
   - The system will validate your file automatically

2. **Enter Patient Information**
   - Name: Patient's full name
   - Age: Patient's age in years
   - Gender: Select from dropdown (Male/Female/Other)
   - Height: Enter in centimeters
   - Weight: Enter in kilograms

3. **Enter Dietary Preferences (Optional)**
   - Dietary Preference: Choose from:
     - None
     - Vegetarian
     - Vegan
     - Pescatarian
     - Keto
     - Paleo
     - Mediterranean
   - Cuisine Preferences: Enter preferred cuisines (comma-separated)
     - Example: "Indian, Mediterranean, Asian"
   - Disliked Foods: Enter foods to avoid (comma-separated)
     - Example: "broccoli, mushrooms, olives"

4. **Process Report**
   - Click the "Process Medical Report" button
   - Watch the progress bar as the system:
     - Validates the file
     - Extracts text using OCR
     - Analyzes health metrics
     - Interprets doctor's notes
     - Generates personalized diet plan
     - Creates PDF and JSON reports
     - Saves data securely

5. **View Results**
   - Success message will appear with your unique Patient ID
   - Links to download PDF and JSON reports
   - Navigate to other pages to view detailed information

#### Troubleshooting Upload Issues:

- **"File too large"**: Compress your PDF or use a lower resolution image
- **"Unsupported format"**: Convert your file to PDF, JPEG, or PNG
- **"OCR failed"**: The image quality may be too low. Try:
  - Scanning at higher resolution (300 DPI recommended)
  - Ensuring good lighting and contrast
  - Using the manual data entry option if available

---

### 2. Review Page

**Purpose:** Review extracted health data and detected conditions

#### What You'll See:

1. **Health Metrics Table**
   - All extracted health measurements
   - Values with units
   - Color coding:
     - 🔴 Red: Critical/abnormal values
     - 🟡 Yellow: Warning/borderline values
     - 🟢 Green: Normal values

2. **Detected Health Conditions**
   - List of identified conditions
   - Confidence scores (0-100%)
   - Contributing metrics for each condition

3. **Health Alerts**
   - Prioritized by severity:
     - CRITICAL: Requires immediate attention
     - WARNING: Needs monitoring
     - NORMAL: Informational
   - Recommended actions for each alert

4. **Edit Controls**
   - Correct any misread values
   - Add missing measurements
   - Update and regenerate diet plan if needed

#### Understanding Your Health Data:

**Common Metrics:**
- **Glucose**: Fasting blood sugar level
  - Normal: < 100 mg/dL
  - Prediabetes: 100-125 mg/dL
  - Diabetes: ≥ 126 mg/dL

- **HbA1c**: 3-month average blood sugar
  - Normal: < 5.7%
  - Prediabetes: 5.7-6.4%
  - Diabetes: ≥ 6.5%

- **Blood Pressure**: Systolic/Diastolic
  - Normal: < 120/80 mmHg
  - Elevated: 120-129/<80 mmHg
  - Hypertension Stage 1: 130-139/80-89 mmHg
  - Hypertension Stage 2: ≥ 140/90 mmHg

- **Cholesterol**:
  - Total: < 200 mg/dL (desirable)
  - LDL: < 100 mg/dL (optimal)
  - HDL: ≥ 60 mg/dL (protective)

- **BMI**: Body Mass Index
  - Underweight: < 18.5
  - Normal: 18.5-24.9
  - Overweight: 25-29.9
  - Obese: ≥ 30

---

### 3. Diet Plan Page

**Purpose:** View your personalized diet plan

#### What You'll See:

1. **Daily Nutritional Summary**
   - Total daily calories
   - Macronutrient breakdown:
     - Carbohydrates (grams and %)
     - Proteins (grams and %)
     - Fats (grams and %)
   - Visual pie chart of macronutrient distribution

2. **Meal Plans**
   
   **Breakfast (25% of daily calories)**
   - Food items with portions
   - Nutritional information per item
   - Preparation suggestions
   
   **Lunch (35% of daily calories)**
   - Main dishes
   - Side dishes
   - Nutritional breakdown
   
   **Snack (10% of daily calories)**
   - Healthy snack options
   - Portion sizes
   
   **Dinner (30% of daily calories)**
   - Evening meal components
   - Balanced nutrition

3. **Dietary Restrictions**
   - Medical restrictions (REQUIRED)
   - Food allergies and intolerances
   - Doctor's recommendations
   - User preferences

4. **Special Considerations**
   - Health condition-specific guidelines
   - Meal timing recommendations
   - Hydration guidelines
   - Physical activity suggestions

5. **Export Options**
   - **Download PDF**: Printable diet plan report
   - **Download JSON**: Machine-readable data for apps

#### Understanding Your Diet Plan:

**Calorie Calculation:**
The system uses the Mifflin-St Jeor equation to calculate your daily caloric needs based on:
- Age, gender, height, weight
- Activity level (assumed moderate)
- Health conditions (adjusted for weight management goals)

**Macronutrient Targets:**
Adjusted based on health conditions:
- **Diabetes**: Lower carbs (40%), higher protein (25%), moderate fat (35%)
- **Hypertension**: Balanced with sodium restriction
- **Hyperlipidemia**: Lower saturated fats, higher fiber
- **Obesity**: Caloric deficit with adequate protein

**Food Selection:**
- Excludes all allergies and intolerances (REQUIRED)
- Follows medical dietary restrictions (REQUIRED)
- Incorporates doctor's recommendations (RECOMMENDED)
- Considers user preferences when possible (OPTIONAL)
- Ensures variety and nutritional balance

---

### 4. History Page

**Purpose:** Access past medical reports and diet plans

#### Features:

1. **Patient Records List**
   - All your previous reports
   - Sorted by date (newest first)
   - Patient ID for each record

2. **Filtering Options**
   - Filter by date range
   - Search by patient ID
   - Sort by various criteria

3. **View Previous Plans**
   - Click on any record to view details
   - See historical health data
   - Compare diet plans over time

4. **Re-export Reports**
   - Download previous PDF reports
   - Export historical data to JSON
   - Share with healthcare providers

---

## Tips for Best Results

### Medical Report Quality

1. **Scan Quality**
   - Use 300 DPI or higher
   - Ensure good lighting
   - Avoid shadows and glare
   - Keep text straight (not skewed)

2. **File Format**
   - PDF is preferred for multi-page reports
   - JPEG/PNG for single-page reports
   - Ensure text is readable

3. **Report Content**
   - Include lab results section
   - Include doctor's notes if available
   - Ensure all values are visible
   - Include units of measurement

### Entering Patient Information

1. **Accurate Measurements**
   - Use recent height and weight
   - Be honest about age and gender
   - These affect calorie calculations

2. **Dietary Preferences**
   - Be specific about allergies (life-critical!)
   - List all food intolerances
   - Mention cultural/religious restrictions
   - Note strong dislikes

### Using the Diet Plan

1. **Follow Medical Restrictions**
   - REQUIRED rules must be followed
   - These are based on your health conditions
   - Consult your doctor before changes

2. **Adapt to Your Lifestyle**
   - Meal times are flexible
   - Substitute similar foods if needed
   - Maintain overall calorie and macro targets

3. **Monitor Progress**
   - Track your adherence
   - Note how you feel
   - Upload new reports to track changes

---

## Privacy and Security

### Data Protection

1. **Encryption**
   - All sensitive data is encrypted at rest
   - AES-256 encryption standard
   - Secure key management

2. **Data Storage**
   - Local database (not cloud)
   - You control your data
   - Can delete anytime

3. **Data Deletion**
   - Use History page to delete records
   - Permanent deletion with verification
   - Audit trail maintained

### Best Practices

1. **Protect Your Patient ID**
   - Keep it confidential
   - Use it to access your records
   - Don't share publicly

2. **Secure Your Environment**
   - Run on trusted computers
   - Use secure networks
   - Log out when done

3. **API Keys**
   - Keep API keys private
   - Don't share in screenshots
   - Rotate keys periodically

---

## Frequently Asked Questions

### Q: How accurate is the OCR?

A: The system achieves 90%+ accuracy on clear, well-scanned documents. Always review extracted data on the Review page.

### Q: Can I edit extracted values?

A: Yes! Use the edit controls on the Review page to correct any misread values.

### Q: What if my medical report is in a different language?

A: Currently, the system works best with English reports. Multi-language support is planned.

### Q: How are diet plans personalized?

A: Plans are based on:
- Your health metrics and conditions
- Doctor's dietary recommendations
- Medical restrictions (allergies, intolerances)
- Your dietary preferences
- Nutritional science and medical guidelines

### Q: Can I use this instead of seeing a doctor?

A: **NO!** This system is a tool to help implement your doctor's recommendations. Always consult healthcare professionals for medical advice.

### Q: What if I have multiple health conditions?

A: The system handles multiple conditions and prioritizes medical requirements. Conflicting rules are resolved using medical priority hierarchies.

### Q: Can I share my diet plan with my doctor?

A: Yes! Export the PDF report and share it with your healthcare provider.

### Q: How often should I update my medical report?

A: Upload new reports whenever you have updated lab results, typically every 3-6 months or as recommended by your doctor.

### Q: What if the system can't process my report?

A: The system will offer fallback options:
- Manual data entry for health metrics
- Manual entry for dietary restrictions
- Contact support if issues persist

---

## Getting Help

### Technical Issues

1. Check QUICKSTART.md for setup issues
2. Review error messages carefully
3. Check logs in the terminal
4. Ensure all dependencies are installed
5. Verify API keys are configured

### Medical Questions

1. Consult your healthcare provider
2. This system is not a substitute for medical advice
3. Use generated plans as a starting point
4. Discuss with a registered dietitian

### Feature Requests

1. Submit feedback through the interface
2. Check documentation for existing features
3. Review the roadmap in README.md

---

## Keyboard Shortcuts

- `Ctrl + R`: Refresh page
- `Ctrl + S`: Save current state
- `Esc`: Close modals/dialogs

---

## Next Steps

1. **First Time Users**
   - Upload a sample medical report
   - Explore all four pages
   - Download the PDF report
   - Review the diet plan

2. **Regular Users**
   - Upload new medical reports as available
   - Track changes in health metrics
   - Adjust dietary preferences as needed
   - Monitor progress over time

3. **Advanced Users**
   - Use JSON exports for integration
   - Analyze historical trends
   - Customize meal plans
   - Share with healthcare team

---

## Support

For additional help:
- Review API_DOCUMENTATION.md for technical details
- Check README.md for system overview
- See QUICKSTART.md for setup instructions

**Remember:** This system is a tool to support your health journey. Always work with qualified healthcare professionals for medical decisions.
