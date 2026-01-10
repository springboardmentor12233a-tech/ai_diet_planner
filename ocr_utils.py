import easyocr
import cv2
import os
import re
import pandas as pd

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(img_path):
    # Read image
    img = cv2.imread(img_path)
    if img is None:
        print(f"ERROR: Failed to load {img_path}")
        return None

    # Convert to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # OCR
    results = reader.readtext(img)
    text = " ".join([t for _, t, _ in results])
    return text

def clean_text(raw_text):
    # basic cleanup
    text = re.sub(r'[^A-Za-z0-9₹\s:.]', '', raw_text)
    text = re.sub(r'\s+', ' ', text)
    return text

def images_to_csv(folder_path, output_csv="ocr_output.csv"):
    rows = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        text = extract_text_from_image(file_path)
        if text:
            cleaned = clean_text(text)
            rows.append({"image": filename, "raw_text": text, "clean_text": cleaned})

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"OCR results saved to {output_csv}")
