# AI NutriCare System 🥗

An intelligent medical report analysis system that generates personalized diet plans based on health data extraction and ML-powered health condition detection.

## Features

- 📄 **Medical Report Processing**: Upload PDF, images, or text files
- 🔍 **OCR Text Extraction**: Automatic text extraction from scanned documents
- 📊 **Health Data Extraction**: Extract metrics like glucose, cholesterol, blood pressure
- 🤖 **ML Health Analysis**: Detect conditions like diabetes, hypertension, obesity
- 💬 **NLP Analysis**: Interpret doctor's notes using Groq AI (free!)
- 🍽️ **Diet Plan Generation**: Personalized meal plans with nutritional breakdown
- 📥 **Export Options**: Download as PDF or JSON
- 🔒 **Secure Storage**: Encrypted patient data storage

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Tesseract OCR (for document scanning)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/springboardmentor12233a-tech/ai_diet_planner.git
cd ai_diet_planner

# Install the package
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
# Groq API (FREE) - Get from https://console.groq.com/keys
GROQ_API_KEY=your-groq-api-key-here

# USDA Food Database (FREE) - Get from https://fdc.nal.usda.gov/api-key-signup.html
USDA_API_KEY=your-usda-api-key-here

# Encryption Key - Generate with: python -c "import secrets; print(secrets.token_hex(16))"
NUTRICARE_ENCRYPTION_KEY=your-32-character-hex-key-here
```

### 4. Run the Application

```bash
# Windows
start.bat

# Or directly with Python
streamlit run ai_diet_planner/ui/app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Upload Report**: Drag and drop a medical report (PDF, image, or text)
2. **Add Patient Info** (optional): Age, gender, height, weight, activity level
3. **Set Preferences** (optional): Dietary style, allergies, foods to avoid
4. **Process**: Click "Process Report" and wait for analysis
5. **Review**: Navigate to "Review" page to see extracted health data
6. **Diet Plan**: Navigate to "Diet Plan" page to see personalized recommendations
7. **Export**: Download your diet plan as PDF or JSON

## Project Structure

```
ai_diet_planner/
├── extraction/      # Data extraction from text
├── export/          # PDF/JSON export functionality
├── generation/      # Diet plan generation
├── ml/              # Machine learning health analysis
├── models/          # Data models and enums
├── nlp/             # Natural language processing
├── ocr/             # OCR text extraction
├── processor/       # Report processing pipeline
├── storage/         # Database and data storage
├── ui/              # Streamlit web interface
└── utils/           # Utility functions
```

## API Keys Setup

### Groq API (Recommended - FREE)

1. Visit https://console.groq.com/keys
2. Sign up for a free account
3. Create a new API key
4. Add to `.env` file

### USDA FoodData Central (FREE)

1. Visit https://fdc.nal.usda.gov/api-key-signup.html
2. Sign up for a free API key
3. Add to `.env` file

## Configuration Options

Edit `.env` to customize:

```bash
# NLP Model (groq, gpt-4, gpt-3.5-turbo, bert)
NUTRICARE_NLP_MODEL=groq

# OCR Backend (tesseract, easyocr)
NUTRICARE_OCR_BACKEND=tesseract

# ML Model (xgboost, lightgbm, random_forest)
NUTRICARE_ML_MODEL=xgboost

# Logging Level
NUTRICARE_LOG_LEVEL=INFO
```

## Troubleshooting

### Import Error: No module named 'ai_diet_planner'

```bash
# Make sure you're in the project root directory
cd path/to/ai_diet_planner
pip install -e .
```

### Groq API Key Not Detected

Make sure:
1. `.env` file exists in the project root
2. `GROQ_API_KEY` is set correctly
3. No extra spaces or quotes around the key

### OCR Not Working

Install Tesseract OCR:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Security

- ✅ API keys stored in `.env` (not committed to Git)
- ✅ Patient data encrypted in database
- ✅ Sensitive files excluded via `.gitignore`
- ✅ No hardcoded credentials

See [SECURITY.md](SECURITY.md) for more details.

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest ai_diet_planner/test_main_orchestrator.py

# Run with coverage
pytest --cov=ai_diet_planner
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Check [GROQ_SETUP.md](GROQ_SETUP.md) for Groq-specific help
- Open an issue on GitHub

## Acknowledgments

- Groq for free, fast LLM API
- USDA for FoodData Central API
- Streamlit for the web framework
- All open-source contributors

---

Made with ❤️ for better health and nutrition
