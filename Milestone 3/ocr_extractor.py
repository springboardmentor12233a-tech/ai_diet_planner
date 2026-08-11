import pytesseract
from PIL import Image
import os

# Windows path example, change if using Linux/Mac
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text
