# AI NutriCare System - Configuration Guide

## Overview

This guide covers all configuration options for the AI NutriCare System.

## Environment Variables

### Required Variables

#### OpenAI API Key
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```
- **Purpose**: NLP text interpretation for doctor's notes
- **Get Key**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (typically $0.01-0.05 per report)

#### USDA FoodData Central API Key
```bash
USDA_API_KEY=your-usda-api-key-here
```
- **Purpose**: Food database for diet plan generation
- **Get Key**: https://fdc.nal.usda.gov/api-key-signup.html
- **Cost**: Free

#### Encryption Key
```bash
NUTRICARE_ENCRYPTION_KEY=your-32-byte-encryption-key-here
```
- **Purpose**: Encrypt sensitive patient data at rest
- **Generate**: `python -c "import secrets; print(secrets.token_hex(16))"`
- **Important**: Keep this key secure! Loss means data cannot be decrypted

### Optional Variables

#### Database Path
```bash
NUTRICARE_DB_PATH=./data/nutricare.db
```
- **Default**: `nutricare.db` in current directory
- **Purpose**: Location of SQLite database

#### Log Level
```bash
NUTRICARE_LOG_LEVEL=INFO
```
- **Options**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Default**: INFO

#### OCR Backend
```bash
NUTRICARE_OCR_BACKEND=tesseract
```
- **Options**: tesseract, easyocr
- **Default**: tesseract
- **Note**: EasyOCR requires GPU for best performance

#### ML Model Type
```bash
NUTRICARE_ML_MODEL=xgboost
```
- **Options**: xgboost, lightgbm, random_forest, logistic_regression
- **Default**: xgboost

---

## Setting Environment Variables

### Windows (CMD)

```cmd
set OPENAI_API_KEY=your-key-here
set USDA_API_KEY=your-key-here
set NUTRICARE_ENCRYPTION_KEY=your-key-here
```

### Windows (PowerShell)

```powershell
$env:OPENAI_API_KEY="your-key-here"
$env:USDA_API_KEY="your-key-here"
$env:NUTRICARE_ENCRYPTION_KEY="your-key-here"
```

### Linux/Mac

```bash
export OPENAI_API_KEY=your-key-here
export USDA_API_KEY=your-key-here
export NUTRICARE_ENCRYPTION_KEY=your-key-here
```

### Permanent Configuration

#### Windows

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-key-here
USDA_API_KEY=your-key-here
NUTRICARE_ENCRYPTION_KEY=your-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

#### Linux/Mac

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export OPENAI_API_KEY=your-key-here
export USDA_API_KEY=your-key-here
export NUTRICARE_ENCRYPTION_KEY=your-key-here
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

## Component Configuration

### OCR Engine

#### Tesseract Configuration

**Installation:**
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

**Language Data:**
```bash
# Install additional languages
# Windows: Download from GitHub and place in tessdata folder
# Linux: sudo apt-get install tesseract-ocr-[lang]
# Mac: brew install tesseract-lang
```

**Custom Configuration:**
```python
from ai_diet_planner.ocr import OCREngine

engine = OCREngine(
    backend="tesseract",
    config="--psm 6 --oem 3"  # Page segmentation and OCR engine mode
)
```

#### EasyOCR Configuration

**Installation:**
```bash
pip install easyocr
```

**GPU Support:**
```bash
# Install CUDA toolkit for GPU acceleration
# See: https://pytorch.org/get-started/locally/
```

**Custom Configuration:**
```python
from ai_diet_planner.ocr import OCREngine

engine = OCREngine(
    backend="easyocr",
    gpu=True,  # Use GPU if available
    languages=['en']  # Supported languages
)
```

---

### ML Health Analyzer

#### Model Selection

**XGBoost (Default - Recommended)**
- Best accuracy for health condition classification
- Fast inference
- Handles missing values well

**LightGBM**
- Faster training than XGBoost
- Lower memory usage
- Good for large datasets

**Random Forest**
- Interpretable results
- Robust to outliers
- No hyperparameter tuning needed

**Logistic Regression**
- Fastest inference
- Most interpretable
- Good for simple cases

#### Model Training

```python
from ai_diet_planner.ml import MLHealthAnalyzer

analyzer = MLHealthAnalyzer(model_type="xgboost")

# Train on custom dataset
analyzer.train(
    X_train, y_train,
    cv_folds=5,
    use_smote=True
)

# Save trained model
analyzer.save_model("models/custom_model.pkl")

# Load trained model
analyzer.load_model("models/custom_model.pkl")
```

#### Model Registry

Models are stored in `models/` directory with metadata:

```
models/
├── xgboost_v1.pkl
├── xgboost_v1_metadata.json
├── lightgbm_v1.pkl
└── lightgbm_v1_metadata.json
```

Metadata includes:
- Model version
- Training date
- Accuracy metrics
- Feature list
- Hyperparameters

---

### NLP Text Interpreter

#### OpenAI Configuration

**Model Selection:**
```python
from ai_diet_planner.nlp import NLPTextInterpreter

interpreter = NLPTextInterpreter(
    model="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.3,  # Lower = more consistent
    max_tokens=500
)
```

**Cost Optimization:**
- Use GPT-3.5-turbo for lower costs
- Enable caching for repeated patterns
- Batch process multiple notes

**Fallback to BERT:**
```python
interpreter = NLPTextInterpreter(
    use_fallback=True,  # Enable BERT fallback
    fallback_model="bert-base-uncased"
)
```

---

### Diet Plan Generator

#### USDA FoodData Central

**API Configuration:**
```python
from ai_diet_planner.generation import DietPlanGenerator

generator = DietPlanGenerator(
    api_key="your-usda-key",
    cache_ttl=86400,  # Cache for 24 hours
    max_retries=3
)
```

**Custom Food Database:**
```python
# Use custom food database instead of USDA
generator = DietPlanGenerator(
    use_custom_db=True,
    custom_db_path="data/custom_foods.json"
)
```

**Meal Generation Parameters:**
```python
diet_plan = generator.generate_plan(
    patient_profile,
    health_conditions,
    diet_rules,
    user_preferences,
    meal_distribution={
        'breakfast': 0.25,
        'lunch': 0.35,
        'snack': 0.10,
        'dinner': 0.30
    },
    variety_weight=0.3,  # How much to prioritize variety
    preference_weight=0.2  # How much to prioritize user preferences
)
```

---

### Data Store

#### Database Configuration

**SQLite (Default):**
```python
from ai_diet_planner.storage import DataStore

store = DataStore(
    db_path="data/nutricare.db",
    encryption_key="your-key"
)
```

**PostgreSQL (Production):**
```python
store = DataStore(
    db_type="postgresql",
    db_config={
        'host': 'localhost',
        'port': 5432,
        'database': 'nutricare',
        'user': 'nutricare_user',
        'password': 'secure_password'
    },
    encryption_key="your-key",
    use_tls=True
)
```

#### Encryption Configuration

**Key Management:**
```python
# Generate new encryption key
import secrets
key = secrets.token_hex(16)
print(f"New encryption key: {key}")

# Rotate encryption key
store.rotate_encryption_key(
    old_key="old-key",
    new_key="new-key"
)
```

**Encrypted Fields:**
- Patient name
- Medical report content
- Doctor's notes
- Diet plan details

**Unencrypted Fields:**
- Patient ID (indexed)
- Timestamps (indexed)
- Metric types (for queries)

---

### Report Exporter

#### PDF Configuration

**Template Customization:**
```python
from ai_diet_planner.export import ReportExporter

exporter = ReportExporter(
    template="custom_template.html",
    logo_path="assets/logo.png",
    font_family="Arial",
    color_scheme={
        'primary': '#2E7D32',
        'secondary': '#1976D2',
        'accent': '#F57C00'
    }
)
```

**Performance Tuning:**
```python
exporter = ReportExporter(
    enable_compression=True,
    image_quality=85,  # 0-100
    cache_templates=True
)
```

#### JSON Configuration

**Schema Validation:**
```python
exporter = ReportExporter(
    validate_json=True,
    json_schema_path="schemas/diet_plan_schema.json"
)
```

---

## Performance Tuning

### Caching

**Redis Configuration (Optional):**
```bash
pip install redis
```

```python
from ai_diet_planner.utils import CacheManager

cache = CacheManager(
    backend="redis",
    host="localhost",
    port=6379,
    ttl=86400  # 24 hours
)
```

**In-Memory Caching:**
```python
cache = CacheManager(
    backend="memory",
    max_size=1000,  # Max cached items
    ttl=3600  # 1 hour
)
```

### Parallel Processing

**Multi-page OCR:**
```python
from ai_diet_planner.ocr import OCREngine

engine = OCREngine(
    backend="tesseract",
    parallel=True,
    max_workers=4  # Number of parallel workers
)
```

### Database Optimization

**Indexes:**
```sql
CREATE INDEX idx_patient_id ON patients(patient_id);
CREATE INDEX idx_created_at ON medical_reports(created_at);
CREATE INDEX idx_metric_type ON health_metrics(metric_type);
```

**Connection Pooling:**
```python
store = DataStore(
    db_path="nutricare.db",
    pool_size=10,
    max_overflow=20
)
```

---

## Security Configuration

### Authentication

**API Key Authentication:**
```python
from ai_diet_planner.utils import AuthManager

auth = AuthManager(
    api_key_header="X-API-Key",
    api_keys=["key1", "key2"]
)
```

### Rate Limiting

```python
from ai_diet_planner.utils import RateLimiter

limiter = RateLimiter(
    max_requests=100,
    time_window=3600  # 1 hour
)
```

### Input Sanitization

```python
from ai_diet_planner.utils import InputSanitizer

sanitizer = InputSanitizer(
    max_file_size=10 * 1024 * 1024,  # 10MB
    allowed_extensions=['.pdf', '.jpg', '.png'],
    scan_for_malware=True
)
```

---

## Logging Configuration

### Log Levels

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nutricare.log'),
        logging.StreamHandler()
    ]
)
```

### Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
```

---

## Deployment Configuration

### Docker

See `docker-compose.yml` for container configuration.

### Production Settings

```python
# config/production.py
SETTINGS = {
    'debug': False,
    'log_level': 'WARNING',
    'enable_caching': True,
    'use_tls': True,
    'rate_limiting': True,
    'max_file_size': 10 * 1024 * 1024,
    'session_timeout': 3600,
    'cors_origins': ['https://yourdomain.com']
}
```

---

## Troubleshooting

### Common Issues

**Issue: "Encryption key not found"**
```bash
# Solution: Set environment variable
export NUTRICARE_ENCRYPTION_KEY=$(python -c "import secrets; print(secrets.token_hex(16))")
```

**Issue: "OpenAI API rate limit exceeded"**
```python
# Solution: Enable caching and reduce requests
interpreter = NLPTextInterpreter(
    enable_cache=True,
    cache_ttl=86400,
    max_retries=5,
    retry_delay=60
)
```

**Issue: "OCR accuracy too low"**
```python
# Solution: Improve preprocessing
engine = OCREngine(
    backend="tesseract",
    preprocess=True,
    denoise=True,
    deskew=True,
    enhance_contrast=True
)
```

---

## Best Practices

1. **Security**
   - Rotate encryption keys regularly
   - Use strong API keys
   - Enable TLS in production
   - Implement rate limiting

2. **Performance**
   - Enable caching for repeated operations
   - Use connection pooling for databases
   - Optimize OCR preprocessing
   - Monitor API usage

3. **Reliability**
   - Implement retry logic with backoff
   - Use fallback mechanisms
   - Log all errors with context
   - Monitor system health

4. **Maintenance**
   - Regular database backups
   - Monitor model accuracy
   - Update dependencies
   - Review logs periodically

---

## Support

For configuration issues:
- Check logs for detailed error messages
- Review API_DOCUMENTATION.md for component details
- See QUICKSTART.md for setup instructions
- Consult README.md for system overview
