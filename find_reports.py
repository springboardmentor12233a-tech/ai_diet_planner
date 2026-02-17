import os
import sys
import ssl
from pathlib import Path

# Fix SSL certificate issues for model downloads
ssl._create_default_https_context = ssl._create_unverified_context

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))
from app.services.ocr_service import OCRService

def find_medical_reports():
    image_dir = Path("lbmaske")
    images = list(image_dir.glob("*.png"))
    
    if not images:
        print("❌ No images found")
        return

    ocr = OCRService()
    found_reports = []
    
    # Keyword set
    keywords = ["Glucose", "Sugar", "Blood Sugar", "Insulin", "HbA1c", "BMI", "Blood Pressure"]
    
    print(f"🔍 Scanning {len(images)} images for medical keywords...")
    
    # Scan in chunks to avoid timeout, let's try a larger set but stop once we find 10 good ones
    for img_path in images:
        try:
            text = ocr.extract_text(str(img_path))
            matches = [k for k in keywords if k.lower() in text.lower()]
            if matches:
                print(f"✅ Found {len(matches)} matches in {img_path.name}: {', '.join(matches)}")
                found_reports.append(img_path.name)
                if len(found_reports) >= 10:
                    break
        except Exception:
            continue

    print(f"\n📂 Identified {len(found_reports)} potential lab reports.")
    print(found_reports)

if __name__ == "__main__":
    find_medical_reports()
