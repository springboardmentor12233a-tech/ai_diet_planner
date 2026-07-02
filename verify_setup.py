#!/usr/bin/env python

import sys
import os

print("=" * 60)
print("AI Diet Planner - Verification Script")
print("=" * 60)
print()

# Track results
results = []

print("Checking Python Version...")
if sys.version_info >= (3, 8):
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK")
    results.append(True)
else:
    print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} - Requires 3.8+")
    results.append(False)

print()
print("Checking Required Packages...")

packages_to_check = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("numpy", "NumPy"),
    ("xgboost", "XGBoost"),
    ("pydantic", "Pydantic"),
    ("PIL", "Pillow"),
    ("cv2", "OpenCV"),
    ("sklearn", "scikit-learn"),
    ("reportlab", "ReportLab"),
    ("openai", "OpenAI"),
    ("dotenv", "python-dotenv"),
    ("imblearn", "imbalanced-learn"),
    ("pandas", "Pandas"),
]

missing_packages = []

for package, name in packages_to_check:
    try:
        __import__(package)
        print(f"✓ {name:20} installed")
        results.append(True)
    except ImportError:
        print(f"✗ {name:20} NOT installed")
        missing_packages.append(name)
        results.append(False)

if missing_packages:
    print()
    print("Missing packages detected!")
    print("Install with: pip install -r backend/requirements.txt")
    print()

print()
print("Checking Project Structure...")

required_dirs = [
    "backend",
    "frontend",
    "data",
    "backend/model",
    "backend/uploads",
    "backend/exports"
]

for dir_path in required_dirs:
    if os.path.isdir(dir_path):
        print(f"✓ {dir_path:30} exists")
        results.append(True)
    else:
        print(f"✗ {dir_path:30} missing")
        results.append(False)

print()
print("Checking Required Files...")

required_files = [
    "backend/main.py",
    "backend/ai_interpreter.py",
    "backend/meal_planner.py",
    "backend/nlp_utils.py",
    "backend/ocr_utils.py",
    "backend/requirements.txt",
    "frontend/src/App.js",
    "frontend/package.json",
    "data/diabetes.csv",
    ".env.example"
]

for file_path in required_files:
    if os.path.isfile(file_path):
        print(f"✓ {file_path:40} exists")
        results.append(True)
    else:
        print(f"✗ {file_path:40} missing")
        results.append(False)

print()
print("Checking Model File...")

if os.path.isfile("backend/model/diabetes_xgb.json"):
    print(f"✓ XGBoost model installed")
    results.append(True)
else:
    print(f"⚠ XGBoost model not found")
    print("  Run: python train_model.py")
    results.append(False)

print()
print("=" * 60)

passed = sum(results)
total = len(results)
percentage = (passed / total * 100) if total > 0 else 0

print(f"Verification: {passed}/{total} checks passed ({percentage:.1f}%)")
print("=" * 60)

if percentage == 100:
    print()
    print("✓ All checks passed! Your setup is ready.")
    print()
    print("Next steps:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your OpenAI API key to .env")
    print("  3. Run: python backend/main.py")
    print("  4. In another terminal: cd frontend && npm start")
    print()
    sys.exit(0)
elif percentage >= 80:
    print()
    print("⚠ Most checks passed. Check missing files/packages above.")
    print()
    sys.exit(1)
else:
    print()
    print("✗ Multiple issues detected. Please fix above before continuing.")
    print()
    sys.exit(1)
