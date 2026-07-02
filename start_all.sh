#!/bin/bash

# AI Diet Planner - Complete Startup Script for Linux/Mac

echo ""
echo "========================================"
echo "AI Diet Planner - Complete Startup"
echo "========================================"
echo ""

# Check if both setups are done
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run: ./setup_backend.sh first"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "Frontend dependencies not installed!"
    echo "Please run: ./setup_frontend.sh first"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env with your OpenAI API key!"
fi

echo ""
echo "========================================"
echo "Starting Backend and Frontend..."
echo "========================================"
echo ""
echo "IMPORTANT:"
echo "- Backend will start on http://127.0.0.1:8000"
echo "- Frontend will start on http://localhost:3000"
echo "- Keep both terminals running!"
echo ""
echo "Press Ctrl+C to stop either service"
echo ""

# Activate virtual environment and start backend in background
source venv/bin/activate
python backend/main.py &
BACKEND_PID=$!

sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
