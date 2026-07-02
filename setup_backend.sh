#!/bin/bash

# AI Diet Planner - Backend Setup Script for Linux/Mac

echo "========================================"
echo "AI Diet Planner - Backend Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created successfully!"
else
    echo "Virtual environment already exists."
fi

echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo ""
echo "Step 4: Creating .env file from template..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created. Please update it with your OpenAI API key!"
else
    echo ".env file already exists."
fi

echo ""
echo "Step 5: Creating necessary directories..."
mkdir -p backend/uploads backend/exports backend/model
echo "Directories created successfully!"

echo ""
echo "========================================"
echo "Backend setup complete!"
echo "========================================"
echo ""
echo "To start the backend:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python backend/main.py"
echo ""
