FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Tesseract OCR and OpenCV deps
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/

# Create necessary directories
RUN mkdir -p /app/uploads /app/exports

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BACKEND_HOST=0.0.0.0

# Run the application with uvicorn (uses PORT env var from Render, defaults to 8000)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
