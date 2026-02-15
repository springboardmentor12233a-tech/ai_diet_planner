# AI NutriCare System - API Documentation

## Overview

This document provides comprehensive API documentation for all components of the AI NutriCare System.

## Table of Contents

1. [Main Orchestrator](#main-orchestrator)
2. [Medical Report Processor](#medical-report-processor)
3. [OCR Engine](#ocr-engine)
4. [Data Extractor](#data-extractor)
5. [ML Health Analyzer](#ml-health-analyzer)
6. [NLP Text Interpreter](#nlp-text-interpreter)
7. [Diet Plan Generator](#diet-plan-generator)
8. [Report Exporter](#report-exporter)
9. [Data Store](#data-store)
10. [Error Handling](#error-handling)

---

## Main Orchestrator

**Module:** `ai_diet_planner.main`

### AINutriCareOrchestrator

Main orchestrator that wires all components together.

#### Constructor

```python
AINutriCareOrchestrator(
    ocr_backend: str = "tesseract",
    ml_model_type: str = "xgboost",
    enable_storage: bool = True,
    encryption_key: Optional[str] = None
)
```

**Parameters:**
- `ocr_backend`: OCR engine to use ("tesseract" or "easyocr")
- `ml_model_type`: ML model type ("xgboost", "lightgbm", "random_forest", "logistic_regression")
- `enable_storage`: Whether to enable data persistence
- `encryption_key`: Encryption key for sensitive data (uses env var if not provided)

#### Methods

##### process_medical_report

```python
process_medical_report(
    file_path: str,
    patient_profile: PatientProfile,
    user_preferences: Optional[UserPreferences] = None
) -> PipelineResult
```

Process a medical report through the complete pipeline.

**Parameters:**
- `file_path`: Path to medical report file (PDF, JPEG, PNG, TIFF, or TXT)
- `patient_profile`: Patient demographic information
- `user_preferences`: Optional dietary preferences

**Returns:** `PipelineResult` object containing:
- `success`: Whether processing succeeded
- `patient_id`: Unique patient identifier
- `extracted_data`: Structured health data
- `health_conditions`: Detected health conditions
- `alerts`: Health alerts
- `diet_rules`: Extracted diet rules
- `diet_plan`: Generated diet plan
- `pdf_path`: Path to exported PDF report
- `json_path`: Path to exported JSON data
- `error`: Error message if failed

**Example:**
```python
from ai_diet_planner.main import AINutriCareOrchestrator
from ai_diet_planner.models import PatientProfile, UserPreferences

orchestrator = AINutriCareOrchestrator()

patient = PatientProfile(
    name="John Doe",
    age=45,
    gender="male",
    height_cm=175,
    weight_kg=80
)

preferences = UserPreferences(
    dietary_preference="vegetarian",
    cuisine_preferences=["indian", "mediterranean"]
)

result = orchestrator.process_medical_report(
    "path/to/report.pdf",
    patient,
    preferences
)

if result.success:
    print(f"Patient ID: {result.patient_id}")
    print(f"PDF Report: {result.pdf_path}")
else:
    print(f"Error: {result.error}")
```

---

## Medical Report Processor

**Module:** `ai_diet_planner.processor.report_processor`

### MedicalReportProcessor

Validates and processes medical report files.

#### Methods

##### validate_file

```python
validate_file(file_path: str) -> tuple[bool, str]
```

Validate file format and size.

**Parameters:**
- `file_path`: Path to file

**Returns:** Tuple of (is_valid, error_message)

**Supported Formats:** PDF, JPEG, PNG, TIFF, TXT
**Max Size:** 10MB

---

## OCR Engine

**Module:** `ai_diet_planner.ocr.ocr_engine`

### OCREngine

Optical Character Recognition engine with preprocessing.

#### Constructor

```python
OCREngine(backend: str = "tesseract")
```

**Parameters:**
- `backend`: OCR backend ("tesseract" or "easyocr")

#### Methods

##### process_image

```python
process_image(image_path: str) -> OCRResult
```

Extract text from image with preprocessing.

**Parameters:**
- `image_path`: Path to image file

**Returns:** `OCRResult` with text and confidence score

##### process_pdf

```python
process_pdf(pdf_path: str) -> OCRResult
```

Extract text from PDF document.

**Parameters:**
- `pdf_path`: Path to PDF file

**Returns:** `OCRResult` with combined text from all pages

---

## Data Extractor

**Module:** `ai_diet_planner.extraction.data_extractor`

### DataExtractor

Extracts structured health metrics and textual notes from OCR text.

#### Methods

##### extract

```python
extract(text: str) -> StructuredHealthData
```

Extract health metrics and notes from text.

**Parameters:**
- `text`: OCR extracted text

**Returns:** `StructuredHealthData` containing:
- `metrics`: List of HealthMetric objects
- `textual_notes`: List of TextualNote objects

**Supported Metrics:**
- Glucose (mg/dL)
- Cholesterol (Total, LDL, HDL) (mg/dL)
- Triglycerides (mg/dL)
- BMI (kg/m²)
- Blood Pressure (mmHg)
- Hemoglobin (g/dL)
- HbA1c (%)

---

## ML Health Analyzer

**Module:** `ai_diet_planner.ml.health_analyzer`

### MLHealthAnalyzer

Machine learning-based health condition classification and alert generation.

#### Constructor

```python
MLHealthAnalyzer(model_type: str = "xgboost")
```

**Parameters:**
- `model_type`: ML model ("xgboost", "lightgbm", "random_forest", "logistic_regression")

#### Methods

##### analyze

```python
analyze(metrics: List[HealthMetric]) -> tuple[List[HealthCondition], List[Alert]]
```

Analyze health metrics to detect conditions and generate alerts.

**Parameters:**
- `metrics`: List of health metrics

**Returns:** Tuple of (health_conditions, alerts)

**Detected Conditions:**
- Diabetes (Type 1, Type 2, Prediabetes)
- Hypertension (Stage 1, Stage 2)
- Hyperlipidemia
- Obesity (Class I, II, III)
- Anemia

---

## NLP Text Interpreter

**Module:** `ai_diet_planner.nlp.text_interpreter`

### NLPTextInterpreter

Natural language processing for extracting dietary rules from doctor's notes.

#### Constructor

```python
NLPTextInterpreter(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key`: OpenAI API key (uses env var OPENAI_API_KEY if not provided)

#### Methods

##### interpret

```python
interpret(notes: List[TextualNote]) -> List[DietRule]
```

Extract dietary rules from textual notes.

**Parameters:**
- `notes`: List of textual notes

**Returns:** List of DietRule objects with priorities

---

## Diet Plan Generator

**Module:** `ai_diet_planner.generation.diet_planner`

### DietPlanGenerator

Generates personalized diet plans based on health analysis and dietary rules.

#### Constructor

```python
DietPlanGenerator(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key`: USDA FoodData Central API key (uses env var USDA_API_KEY if not provided)

#### Methods

##### generate_plan

```python
generate_plan(
    patient_profile: PatientProfile,
    health_conditions: List[HealthCondition],
    diet_rules: List[DietRule],
    user_preferences: Optional[UserPreferences] = None
) -> DietPlan
```

Generate personalized diet plan.

**Parameters:**
- `patient_profile`: Patient demographics
- `health_conditions`: Detected health conditions
- `diet_rules`: Dietary restrictions and recommendations
- `user_preferences`: Optional user preferences

**Returns:** `DietPlan` with meals for breakfast, lunch, snack, and dinner

**Meal Distribution:**
- Breakfast: 25% of daily calories
- Lunch: 35% of daily calories
- Snack: 10% of daily calories
- Dinner: 30% of daily calories

---

## Report Exporter

**Module:** `ai_diet_planner.export.report_exporter`

### ReportExporter

Exports diet plans to PDF and JSON formats.

#### Methods

##### export_to_pdf

```python
export_to_pdf(
    diet_plan: DietPlan,
    patient_profile: PatientProfile,
    health_summary: Dict[str, Any],
    output_path: str
) -> str
```

Export diet plan to PDF report.

**Parameters:**
- `diet_plan`: Generated diet plan
- `patient_profile`: Patient information
- `health_summary`: Health conditions and alerts
- `output_path`: Output file path

**Returns:** Path to generated PDF

##### export_to_json

```python
export_to_json(
    diet_plan: DietPlan,
    output_path: str
) -> str
```

Export diet plan to JSON format.

**Parameters:**
- `diet_plan`: Generated diet plan
- `output_path`: Output file path

**Returns:** Path to generated JSON file

---

## Data Store

**Module:** `ai_diet_planner.storage.data_store`

### DataStore

Secure data persistence with encryption.

#### Constructor

```python
DataStore(
    db_path: str = "nutricare.db",
    encryption_key: Optional[str] = None
)
```

**Parameters:**
- `db_path`: Path to SQLite database
- `encryption_key`: Encryption key (uses env var NUTRICARE_ENCRYPTION_KEY if not provided)

#### Methods

##### save_patient_data

```python
save_patient_data(
    patient_profile: PatientProfile,
    extracted_data: StructuredHealthData,
    diet_plan: DietPlan
) -> str
```

Save patient data with encryption.

**Parameters:**
- `patient_profile`: Patient information
- `extracted_data`: Extracted health data
- `diet_plan`: Generated diet plan

**Returns:** Unique patient ID

##### get_patient_history

```python
get_patient_history(patient_id: str) -> List[Dict[str, Any]]
```

Retrieve patient history.

**Parameters:**
- `patient_id`: Patient identifier

**Returns:** List of historical records

##### delete_patient_data

```python
delete_patient_data(patient_id: str) -> bool
```

Permanently delete patient data.

**Parameters:**
- `patient_id`: Patient identifier

**Returns:** True if successful

---

## Error Handling

**Module:** `ai_diet_planner.utils.error_handler`

### Error Classes

#### NutriCareError

Base exception for all system errors.

```python
NutriCareError(
    message: str,
    category: ErrorCategory,
    context: Optional[Dict[str, Any]] = None,
    user_message: Optional[str] = None
)
```

#### InputValidationError

Raised for invalid input data.

#### ProcessingError

Raised during data processing failures.

#### DataError

Raised for data storage/retrieval errors.

#### SystemError

Raised for system-level errors.

### ErrorHandler

Centralized error handling with logging.

```python
handler = ErrorHandler()
handler.log_error(error, context={'file': 'report.pdf'})
user_msg = handler.get_user_message(error)
```

### Retry Decorator

```python
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def unstable_operation():
    # Operation that might fail transiently
    pass
```

---

## Environment Variables

Required environment variables:

```bash
# OpenAI API for NLP
OPENAI_API_KEY=your_openai_key

# USDA FoodData Central API
USDA_API_KEY=your_usda_key

# Encryption key for sensitive data
NUTRICARE_ENCRYPTION_KEY=your_32_byte_key
```

---

## Data Models

All data models are defined in `ai_diet_planner.models`:

- `PatientProfile`: Patient demographics
- `UserPreferences`: Dietary preferences
- `HealthMetric`: Individual health measurement
- `StructuredHealthData`: Collection of metrics and notes
- `HealthCondition`: Detected health condition
- `Alert`: Health alert with severity
- `DietRule`: Dietary restriction or recommendation
- `Food`: Food item with nutritional info
- `Portion`: Food portion with quantity
- `Meal`: Collection of food portions
- `DietPlan`: Complete diet plan with all meals

See `ai_diet_planner/models/` for detailed model definitions.
