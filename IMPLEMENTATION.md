# AI NutriCare System - Implementation Documentation

## Overview

AI NutriCare System is an intelligent health report analysis and personalized diet planning application. It processes medical reports (PDF/images), extracts health metrics, analyzes health conditions, and generates customized diet plans with nutritional recommendations.

## System Architecture

### Core Components

```
ai_diet_planner/
├── main.py                 # Main orchestrator coordinating all components
├── ui/                     # Streamlit web interface
├── ocr/                    # Document text extraction
├── extraction/             # Health data extraction from text
├── nlp/                    # Natural language processing for dietary rules
├── ml/                     # Machine learning health analysis
├── generation/             # Diet plan generation
├── export/                 # Report export (PDF/JSON)
├── storage/                # SQLite database management
├── processor/              # Report processing pipeline
├── models/                 # Data models and enums
└── utils/                  # Security, error handling, fallback utilities
```

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary programming language
- **Streamlit**: Web UI framework
- **SQLite**: Local database for patient data and diet plans
- **Groq API**: Free LLM for NLP tasks (llama-3.3-70b-versatile model)
- **Tesseract OCR**: Text extraction from images
- **PyMuPDF (fitz)**: PDF text extraction
- **Pillow**: Image processing
- **Scikit-learn**: Machine learning for health analysis
- **ReportLab**: PDF generation

### Key Libraries
```
streamlit>=1.28.0
groq>=0.4.0
pytesseract>=0.3.10
PyMuPDF>=1.23.0
Pillow>=10.0.0
scikit-learn>=1.3.0
reportlab>=4.0.0
python-dotenv>=1.0.0
cryptography>=41.0.0
```

## Module Details

### 1. Main Orchestrator (`main.py`)

**Purpose**: Coordinates all system components and manages the complete workflow.

**Key Features**:
- Initializes all subsystems (OCR, NLP, ML, storage, etc.)
- Processes uploaded health reports end-to-end
- Handles patient profile creation with unique IDs
- Manages error handling and fallback mechanisms
- Coordinates data flow between components

**Main Methods**:
- `process_report()`: Complete pipeline from upload to diet plan generation
- `_initialize_components()`: Sets up all system modules
- `_extract_text()`: Extracts text from PDF/image files
- `_analyze_health()`: Performs health condition analysis
- `_generate_diet_plan()`: Creates personalized diet recommendations

### 2. User Interface (`ui/app.py`)

**Purpose**: Streamlit-based web interface for user interaction.

**Pages**:
1. **Upload**: File upload, patient info, dietary preferences
2. **Review**: Display extracted health metrics, conditions, and alerts
3. **Diet Plan**: Show personalized meal plans with nutritional breakdown
4. **History**: View past reports and diet plans

**Key Features**:
- Multi-page navigation with session state management
- File validation (PDF/image, max 10MB)
- Real-time processing status updates
- Interactive data visualization with pandas DataFrames
- PDF and JSON export functionality
- Color-coded health alerts and confidence levels

### 3. OCR Engine (`ocr/ocr_engine.py`)

**Purpose**: Extract text from medical documents.

**Supported Formats**:
- PDF files (using PyMuPDF)
- Images: PNG, JPG, JPEG, TIFF (using Tesseract OCR)

**Features**:
- Automatic format detection
- Image preprocessing for better OCR accuracy
- Multi-page PDF support
- Error handling for corrupted files

### 4. Data Extraction (`extraction/data_extractor.py`)

**Purpose**: Parse extracted text to identify health metrics and values.

**Extraction Capabilities**:
- Blood glucose levels (mg/dL, mmol/L)
- Blood pressure (systolic/diastolic)
- Cholesterol (total, LDL, HDL, triglycerides)
- BMI and weight
- HbA1c levels
- Kidney function (creatinine, eGFR)
- Liver function (ALT, AST)
- Thyroid markers (TSH, T3, T4)

**Pattern Matching**:
- Regex-based metric identification
- Unit conversion support
- Handles various report formats
- Extracts ranges and reference values

### 5. NLP Text Interpreter (`nlp/text_interpreter.py`)

**Purpose**: Convert natural language dietary instructions into structured rules.

**NLP Backends**:
- **Groq** (default, free): Uses llama-3.3-70b-versatile model
- **OpenAI**: GPT-4 support (requires API key)
- **BERT**: Local fallback (biomedical-ner-all model)

**Features**:
- Extracts food items, portions, and restrictions
- Identifies meal timing and frequency
- Detects dietary constraints (allergies, preferences)
- Converts unstructured text to structured `DietaryRule` objects

**Rule Mapping** (`nlp/rules_mapping.py`):
- Maps health conditions to dietary recommendations
- Provides evidence-based nutrition guidelines
- Supports diabetes, hypertension, kidney disease, etc.

### 6. Health Analyzer (`ml/health_analyzer.py`)

**Purpose**: ML-based health condition detection and risk assessment.

**Analysis Types**:
1. **Diabetes Detection**: Based on glucose, HbA1c, BMI
2. **Hypertension Detection**: Blood pressure analysis
3. **Cholesterol Risk**: Lipid profile evaluation
4. **Kidney Disease Risk**: Creatinine and eGFR assessment
5. **Liver Function**: ALT/AST analysis
6. **Thyroid Disorders**: TSH level evaluation

**Features**:
- Confidence scoring for each condition
- Severity classification (mild, moderate, severe)
- Health alerts with actionable recommendations
- Risk factor identification

### 7. Diet Plan Generator (`generation/diet_planner.py`)

**Purpose**: Create personalized meal plans based on health analysis.

**Generation Process**:
1. Calculate daily caloric needs (Harris-Benedict equation)
2. Determine macronutrient ratios based on health conditions
3. Generate 4 meals per day (breakfast, lunch, dinner, snack)
4. Apply dietary restrictions and preferences
5. Ensure nutritional balance and variety

**Meal Planning**:
- Food database with 100+ items
- Portion size calculations
- Calorie and macro tracking
- Meal timing recommendations
- Hydration guidelines

**Customization**:
- Vegetarian/vegan options
- Allergen exclusions
- Cultural food preferences
- Activity level adjustments

### 8. Report Exporter (`export/report_exporter.py`)

**Purpose**: Generate downloadable reports in multiple formats.

**Export Formats**:
1. **PDF**: Professional formatted report with:
   - Patient information
   - Health metrics summary
   - Detected conditions
   - Complete diet plan with meals
   - Nutritional breakdown
   - Dietary recommendations

2. **JSON**: Structured data export for:
   - API integration
   - Data analysis
   - System interoperability

**Features**:
- ReportLab-based PDF generation
- Custom styling and branding
- Table formatting for metrics
- Section organization
- Timestamp and metadata

### 9. Data Storage (`storage/data_store.py`)

**Purpose**: SQLite database management for persistent data.

**Database Schema**:
- **patients**: Patient profiles and demographics
- **health_metrics**: Extracted health measurements
- **health_conditions**: Detected conditions with confidence
- **diet_plans**: Generated meal plans
- **meals**: Individual meal details
- **food_items**: Food items with nutritional info
- **dietary_rules**: Applied dietary recommendations
- **health_alerts**: Generated health warnings

**Features**:
- CRUD operations for all entities
- Relationship management
- Query optimization
- Data encryption for sensitive fields
- Automatic timestamp tracking
- Duplicate prevention

### 10. Security & Utilities

**Security** (`utils/security.py`):
- AES encryption for sensitive data
- Fernet-based encryption key management
- Environment variable protection
- Secure data storage

**Error Handling** (`utils/error_handler.py`):
- Centralized exception management
- User-friendly error messages
- Logging and debugging support
- Graceful degradation

**Fallback Mechanisms** (`utils/fallback.py`):
- Default values for missing data
- Alternative processing paths
- Resilient system behavior

## Data Models

### Core Models (`models/`)

**PatientProfile**:
- Demographics (name, age, gender, height, weight)
- Contact information
- Medical history
- Dietary preferences and restrictions

**HealthMetrics**:
- Metric name and value
- Unit of measurement
- Reference ranges
- Measurement timestamp

**HealthCondition**:
- Condition name and severity
- Confidence score
- Detection timestamp
- Supporting evidence

**DietPlan**:
- Daily caloric target
- Macronutrient distribution
- Meal collection
- Dietary rules
- Generation timestamp

**Meal**:
- Meal type (breakfast, lunch, dinner, snack)
- Food items with portions
- Total calories and macros
- Timing recommendations

**DietaryRule**:
- Rule type (include, exclude, limit, timing)
- Target foods
- Portions and frequencies
- Rationale

## Configuration

### Environment Variables (`.env`)

```bash
# NLP Configuration
NLP_BACKEND=groq
GROQ_API_KEY=your_groq_api_key_here

# Food Database API
USDA_API_KEY=your_usda_api_key_here

# Security
ENCRYPTION_KEY=your_32_byte_encryption_key_here

# Database
DATABASE_PATH=nutricare.db

# Logging
LOG_LEVEL=INFO
```

### API Keys Setup

1. **Groq API** (Free):
   - Visit: https://console.groq.com
   - Create account and generate API key
   - Used for NLP dietary rule extraction

2. **USDA FoodData Central** (Free):
   - Visit: https://fdc.nal.usda.gov/api-key-signup.html
   - Register and get API key
   - Used for food nutritional data

3. **Encryption Key**:
   - Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   - Used for encrypting sensitive patient data

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR installed
- Git

### Installation Steps

1. **Clone Repository**:
```bash
git clone https://github.com/springboardmentor12233a-tech/ai_diet_planner.git
cd ai_diet_planner
```

2. **Install Package**:
```bash
pip install -e .
```

3. **Configure Environment**:
```bash
# Copy example and edit with your API keys
copy .env.example .env
# Edit .env with your actual API keys
```

4. **Run Application**:
```bash
# Windows
start.bat

# Or manually
streamlit run ai_diet_planner/ui/app.py
```

## Usage Workflow

### 1. Upload Report
- Navigate to Upload page
- Select PDF or image file (max 10MB)
- Optionally provide patient information
- Set dietary preferences and restrictions
- Click "Process Report"

### 2. Review Health Data
- System extracts text using OCR
- Identifies health metrics automatically
- Detects health conditions using ML
- Generates health alerts
- Displays results on Review page

### 3. View Diet Plan
- System generates personalized meal plan
- Shows daily nutritional targets
- Displays 4 meals with food items and portions
- Provides dietary recommendations
- Available on Diet Plan page

### 4. Export & Save
- Download PDF report
- Export JSON data
- View in History page
- Access past reports anytime

## Testing

### Test Coverage
- Unit tests for all major components
- Integration tests for pipeline
- OCR accuracy tests
- NLP extraction validation
- ML model performance tests
- Database operations tests
- UI component tests

### Running Tests
```bash
# Run all tests
pytest

# Run specific module tests
pytest ai_diet_planner/ocr/test_ocr_engine.py
pytest ai_diet_planner/nlp/test_text_interpreter.py
pytest ai_diet_planner/ml/test_health_analyzer.py
```

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: BERT model loaded only when needed
2. **Caching**: Streamlit session state for UI data
3. **Database Indexing**: Optimized queries for patient lookup
4. **Batch Processing**: Efficient multi-page PDF handling
5. **API Rate Limiting**: Groq API request management

### Resource Usage
- Memory: ~500MB (without BERT), ~2GB (with BERT)
- Storage: ~50MB base + patient data
- Processing Time: 10-30 seconds per report

## Error Handling

### Common Issues & Solutions

1. **Import Error**: Run `pip install -e .` from project root
2. **API Key Error**: Check `.env` file configuration
3. **OCR Failure**: Ensure Tesseract is installed
4. **Processing Timeout**: Check file size and quality
5. **Database Lock**: Close other connections

## Security Features

1. **Data Encryption**: Sensitive patient data encrypted at rest
2. **Environment Variables**: API keys protected in `.env`
3. **Input Validation**: File type and size checks
4. **SQL Injection Prevention**: Parameterized queries
5. **Error Sanitization**: No sensitive data in error messages

## Future Enhancements

### Planned Features
- Multi-language support
- Mobile app integration
- Wearable device data import
- Meal tracking and logging
- Recipe recommendations
- Grocery list generation
- Nutritionist consultation booking
- Progress tracking and analytics

### Technical Improvements
- Redis caching for performance
- PostgreSQL for production
- Docker containerization
- REST API development
- Cloud deployment (AWS/Azure)
- Real-time notifications
- Advanced ML models

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Standards
- PEP 8 style guide
- Type hints for functions
- Docstrings for classes/methods
- Unit tests for new features
- Integration tests for workflows

## License

This project is developed for educational purposes as part of the Infosys Springboard program.

## Support

For issues or questions:
- GitHub Issues: https://github.com/springboardmentor12233a-tech/ai_diet_planner/issues
- Branch: Ashraya
- Contact: Project mentor

## Acknowledgments

- Infosys Springboard Program
- Groq for free LLM API access
- USDA FoodData Central for nutrition data
- Open source community for libraries and tools

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Status**: Production Ready
