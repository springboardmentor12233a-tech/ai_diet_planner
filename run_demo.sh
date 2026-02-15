#!/bin/bash
# AI NutriCare System - Demo Runner for Linux/Mac
# This script runs the interactive demonstration

echo ""
echo "========================================"
echo "  AI NutriCare System - Demo Runner"
echo "========================================"
echo ""

# Set encryption key for demo
export NUTRICARE_ENCRYPTION_KEY="demo-encryption-key-for-testing"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo ""

# Run the demo
echo "Starting demo..."
echo ""
python3 demo.py

echo ""
echo "Demo completed!"
echo ""
