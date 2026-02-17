import os
import sys
import ssl
from pathlib import Path

# Fix SSL certificate issues for model downloads
ssl._create_default_https_context = ssl._create_unverified_context

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.ocr_service import OCRService
import random

def test_real_images():
    image_dir = Path("lbmaske")
    images = list(image_dir.glob("*.png"))
    
    if not images:
        print("❌ No images found in lbmaske folder")
        return

    print(f"📁 Found {len(images)} real images. Testing 3 random samples...")
    
    samples = random.sample(images, 3)
    ocr = OCRService()
    
    for img_path in samples:
        print(f"\n🔍 Testing: {img_path.name}")
        try:
            # We want to see the text extracted
            # ocr_service.extract_text usually calls EasyOCR/Tesseract
            text = ocr.extract_text(str(img_path))
            print(f"📝 Extracted Text Preview (First 200 chars):\n {text[:200]}...")
            
            # Check for keywords
            keywords = ["Glucose", "Sugar", "BP", "BMI", "Cholesterol", "mg/dl"]
            found = [k for k in keywords if k.lower() in text.lower()]
            if found:
                print(f"✅ Found Keywords: {', '.join(found)}")
            else:
                print("⚠️  No medical keywords found in this sample.")
                
        except Exception as e:
            print(f"❌ OCR Error for {img_path.name}: {e}")

if __name__ == "__main__":
    test_real_images()
