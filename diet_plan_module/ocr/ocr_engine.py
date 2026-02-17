import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path

def extract_text_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Improve handwriting OCR
        gray = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        gray = cv2.medianBlur(gray, 3)

        text = pytesseract.image_to_string(
            gray,
            config="--psm 6"
        )
        return text

    except Exception as e:
        return ""

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        pages = convert_from_path(pdf_path)
        for page in pages:
            text += pytesseract.image_to_string(page)
    except Exception as e:
        pass
    return text



