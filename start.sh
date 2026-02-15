#!/bin/bash
# AI NutriCare System - Startup Script for Linux/Mac

set -e

echo "==================================="
echo "AI NutriCare System - Starting"
echo "==================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using .env.example as template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env file. Please edit it with your API keys."
        exit 1
    else
        echo "Error: .env.example not found"
        exit 1
    fi
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo "Error: Please set OPENAI_API_KEY in .env file"
    exit 1
fi

if [ -z "$USDA_API_KEY" ] || [ "$USDA_API_KEY" = "your-usda-api-key-here" ]; then
    echo "Error: Please set USDA_API_KEY in .env file"
    exit 1
fi

if [ -z "$NUTRICARE_ENCRYPTION_KEY" ] || [ "$NUTRICARE_ENCRYPTION_KEY" = "your-32-character-encryption-key-here" ]; then
    echo "Generating encryption key..."
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    sed -i "s/NUTRICARE_ENCRYPTION_KEY=.*/NUTRICARE_ENCRYPTION_KEY=$NEW_KEY/" .env
    export NUTRICARE_ENCRYPTION_KEY=$NEW_KEY
    echo "Generated new encryption key"
fi

# Create necessary directories
mkdir -p data models exports logs

# Run database migrations
echo "Running database migrations..."
python3 migrations/migrate.py --db-path ${NUTRICARE_DB_PATH:-data/nutricare.db}
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "Installing ai_diet_planner package in development mode..."
    pip install -e .
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# Install package in development mode if not already installed
python3 -c "import ai_diet_planner" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing ai_diet_planner package in development mode..."
    pip install -e .
fi

# Start the application
echo "Starting AI NutriCare System..."
echo "Access the application at: http://localhost:8501"
echo ""
streamlit run ai_diet_planner/ui/app.py
