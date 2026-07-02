#!/bin/bash

# AI Diet Planner - Frontend Setup Script for Linux/Mac

echo "========================================"
echo "AI Diet Planner - Frontend Setup"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

cd frontend

echo ""
echo "Step 1: Installing dependencies..."
npm install

echo ""
echo "Step 2: Creating .env file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
REACT_APP_API_URL=http://127.0.0.1:8000
EOF
    echo ".env file created successfully!"
else
    echo ".env file already exists."
fi

echo ""
echo "========================================"
echo "Frontend setup complete!"
echo "========================================"
echo ""
echo "To start the frontend:"
echo "  1. Navigate to frontend directory: cd frontend"
echo "  2. Run: npm start"
echo ""
