#!/bin/bash
# Quick fix script to install ai_diet_planner package

echo "==================================="
echo "Installing AI NutriCare Package"
echo "==================================="
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Install package in development mode
echo "Installing ai_diet_planner package in development mode..."
pip install -e .

echo ""
echo "==================================="
echo "Installation Complete!"
echo "==================================="
echo ""
echo "You can now run: streamlit run ai_diet_planner/ui/app.py"
echo "Or use: ./start.sh"
echo ""
