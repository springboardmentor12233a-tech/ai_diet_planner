# AI NutriCare System - Docker Image

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ai_diet_planner/ ./ai_diet_planner/
COPY demo.py .
COPY README.md .
COPY QUICKSTART.md .
COPY USER_GUIDE.md .
COPY API_DOCUMENTATION.md .
COPY CONFIGURATION.md .

# Create directories for data and models
RUN mkdir -p /app/data /app/models /app/exports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NUTRICARE_DB_PATH=/app/data/nutricare.db
ENV NUTRICARE_LOG_LEVEL=INFO

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')"

# Default command - run Streamlit app
CMD ["streamlit", "run", "ai_diet_planner/ui/app.py", "--server.address", "0.0.0.0"]
