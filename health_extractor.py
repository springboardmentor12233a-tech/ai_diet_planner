import pytesseract
import cv2
import re
from PIL import Image


# Change path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_health_values(image_file):

    img = Image.open(image_file)

    # Convert to text
    text = pytesseract.image_to_string(img)
    text = text.lower()

    print("Extracted Text:", text)

    values = {
        "glucose": None,
        "bmi": None,
        "diabetes": "Not Detected",
        "bp": None
    }

    # -------------------
    # Extract Glucose
    # -------------------
    g = re.search(r"glucose[:\s]*(\d+)", text)
    if g:
        values["glucose"] = int(g.group(1))

    # -------------------
    # Extract BMI
    # -------------------
    b = re.search(r"bmi[:\s]*(\d+\.?\d*)", text)
    if b:
        values["bmi"] = float(b.group(1))

    # -------------------
    # Detect Diabetes
    # -------------------
    if "diabetes" in text or "diabetic" in text:
        values["diabetes"] = "Detected"

    # -------------------
    # Extract BP
    # -------------------
    bp = re.search(r"(\d{2,3}/\d{2,3})", text)
    if bp:
        values["bp"] = bp.group(1)

    return values
