# AI NutriCare System - Troubleshooting Guide

## Common Issues and Solutions

### Issue: "No module named 'ai_diet_planner'"

**Symptom:** When you upload a file in the Streamlit UI, you get an error:
```
An error occurred: No module named 'ai_diet_planner'
```

**Cause:** The `ai_diet_planner` package is not installed in your Python environment.

**Solution:**

1. **Quick Fix - Run the install script:**

   **Windows:**
   ```cmd
   install_package.bat
   ```

   **Linux/Mac:**
   ```bash
   chmod +x install_package.sh
   ./install_package.sh
   ```

2. **Manual Fix:**

   Make sure you're in the project root directory and run:

   **Windows:**
   ```cmd
   # Activate your virtual environment first
   venv\Scripts\activate
   
   # Install the package in development mode
   pip install -e .
   ```

   **Linux/Mac:**
   ```bash
   # Activate your virtual environment first
   source venv/bin/activate
   
   # Install the package in development mode
   pip install -e .
   ```

3. **Verify Installation:**

   After installation, verify it worked:
   ```bash
   python -c "import ai_diet_planner; print('Success!')"
   ```

   You should see "Success!" printed.

4. **Restart Streamlit:**

   After installing the package, restart the Streamlit app:
   ```bash
   # Stop the current app (Ctrl+C)
   # Then restart:
   streamlit run ai_diet_planner/ui/app.py
   ```

---

### Issue: "ModuleNotFoundError" for other packages

**Symptom:** Errors like:
```
ModuleNotFoundError: No module named 'streamlit'
ModuleNotFoundError: No module named 'pytesseract'
```

**Solution:**

1. Make sure you've installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Verify your virtual environment is activated:
   - Windows: You should see `(venv)` at the start of your command prompt
   - Linux/Mac: You should see `(venv)` at the start of your terminal prompt

3. If issues persist, recreate the virtual environment:
   ```bash
   # Remove old environment
   rm -rf venv  # Linux/Mac
   rmdir /s venv  # Windows
   
   # Create new environment
   python -m venv venv
   
   # Activate it
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   
   # Install everything
   pip install -r requirements.txt
   pip install -e .
   ```

---

### Issue: "Tesseract not found"

**Symptom:**
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Solution:**

Tesseract OCR needs to be installed separately:

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to PATH or set in code:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

---

### Issue: "OpenAI API key not found"

**Symptom:**
```
Error: OpenAI API key not configured
```

**Solution:**

1. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   USDA_API_KEY=your-usda-key-here
   NUTRICARE_ENCRYPTION_KEY=your-encryption-key-here
   ```

3. Generate encryption key if needed:
   ```bash
   python -c "import secrets; print(secrets.token_hex(16))"
   ```

4. Restart the application.

---

### Issue: "Database locked" or "Unable to open database"

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**

1. Close all other instances of the application
2. Delete the lock file:
   ```bash
   rm data/nutricare.db-journal  # Linux/Mac
   del data\nutricare.db-journal  # Windows
   ```
3. If problem persists, backup and recreate database:
   ```bash
   # Backup
   cp data/nutricare.db data/nutricare.db.backup
   
   # Recreate
   rm data/nutricare.db
   python migrations/migrate.py
   ```

---

### Issue: Streamlit app won't start

**Symptom:**
```
streamlit: command not found
```

**Solution:**

1. Make sure Streamlit is installed:
   ```bash
   pip install streamlit
   ```

2. Verify virtual environment is activated

3. Try running with full path:
   ```bash
   python -m streamlit run ai_diet_planner/ui/app.py
   ```

---

### Issue: File upload fails with "File too large"

**Symptom:**
```
File size exceeds 10 MB limit
```

**Solution:**

1. Compress your PDF:
   - Use online tools like SmallPDF
   - Reduce image quality in scanned documents
   - Split multi-page documents

2. For images, reduce resolution:
   - Recommended: 300 DPI
   - Maximum: 600 DPI
   - Use JPEG instead of PNG for smaller size

---

### Issue: OCR accuracy is poor

**Symptom:** Extracted text is incorrect or incomplete

**Solution:**

1. **Improve document quality:**
   - Scan at 300 DPI or higher
   - Ensure good lighting
   - Avoid shadows and glare
   - Keep text straight (not skewed)

2. **Try different OCR backend:**
   
   Set in `.env`:
   ```
   NUTRICARE_OCR_BACKEND=easyocr
   ```
   
   Install EasyOCR:
   ```bash
   pip install easyocr
   ```

3. **Preprocess images:**
   - Convert to grayscale
   - Increase contrast
   - Remove noise

---

### Issue: Diet plan generation fails

**Symptom:**
```
Error generating diet plan
```

**Solution:**

1. **Check USDA API key:**
   - Verify key is correct in `.env`
   - Check API quota hasn't been exceeded
   - Get new key at: https://fdc.nal.usda.gov/api-key-signup.html

2. **Check internet connection:**
   - USDA API requires internet access
   - Check firewall settings

3. **Use fallback:**
   - System will use cached food database if API fails
   - Check logs for specific error

---

### Issue: PDF export fails

**Symptom:**
```
Error exporting to PDF
```

**Solution:**

1. **Check disk space:**
   - Ensure enough space in `exports/` directory

2. **Check permissions:**
   ```bash
   # Linux/Mac
   chmod 755 exports/
   
   # Windows - run as administrator if needed
   ```

3. **Install ReportLab:**
   ```bash
   pip install reportlab
   ```

---

### Issue: Slow performance

**Symptom:** Processing takes too long

**Solution:**

1. **Enable caching:**
   
   In `.env`:
   ```
   NUTRICARE_ENABLE_CACHE=true
   ```

2. **Use faster OCR backend:**
   ```
   NUTRICARE_OCR_BACKEND=tesseract
   ```

3. **Reduce image size:**
   - Compress images before upload
   - Use lower resolution (300 DPI is sufficient)

4. **Use faster ML model:**
   ```
   NUTRICARE_ML_MODEL=logistic_regression
   ```

---

### Issue: Memory errors

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Solution:**

1. **Process smaller files:**
   - Split large PDFs
   - Reduce image resolution

2. **Increase available memory:**
   - Close other applications
   - Restart Python process

3. **Use pagination for large documents:**
   - Process pages individually
   - Implemented automatically for PDFs

---

## Getting More Help

### Check Logs

Logs are stored in `logs/` directory. Check them for detailed error messages:

```bash
# View recent logs
tail -f logs/nutricare.log  # Linux/Mac
type logs\nutricare.log  # Windows
```

### Enable Debug Mode

For more detailed logging, set in `.env`:
```
NUTRICARE_LOG_LEVEL=DEBUG
```

### Run Tests

Verify system components are working:

```bash
# Run all tests
pytest

# Run specific component tests
pytest ai_diet_planner/ocr/test_ocr_engine.py
pytest ai_diet_planner/extraction/test_data_extractor.py
```

### System Information

Collect system info for support:

```bash
# Python version
python --version

# Installed packages
pip list

# System info
python -c "import platform; print(platform.platform())"
```

---

## Still Having Issues?

1. **Check Documentation:**
   - `README.md` - System overview
   - `QUICKSTART.md` - Installation guide
   - `USER_GUIDE.md` - Usage instructions
   - `API_DOCUMENTATION.md` - Technical details
   - `CONFIGURATION.md` - Configuration options

2. **Review Error Messages:**
   - Read the full error message
   - Check the "Error Details" expander in the UI
   - Look for specific file/line numbers

3. **Search Issues:**
   - Check if others have reported similar issues
   - Look for solutions in documentation

4. **Contact Support:**
   - Provide error messages
   - Include system information
   - Describe steps to reproduce

---

## Prevention Tips

1. **Always activate virtual environment** before running commands
2. **Keep dependencies updated:** `pip install --upgrade -r requirements.txt`
3. **Backup database regularly:** `cp data/nutricare.db data/backup.db`
4. **Use high-quality scans** for best OCR results
5. **Monitor API usage** to avoid quota limits
6. **Check logs regularly** for warnings
7. **Test with sample data** before using real medical reports

---

Last Updated: 2026-02-15
