import pandas as pd
import cv2
import easyocr
import os
csv_path = "data/diabetes.csv"

if not os.path.exists(csv_path):
    print(" diabetes.csv not found in data folder")
else:
    df = pd.read_csv(csv_path)
    print("First 5 rows of dataset:\n")
    print(df.head())
    print("\nDataset Info:\n")
    print(df.info())


print("\n OCR TEXT EXTRACTION \n")

image_path = "reports/sample_report.png"
# Check if image exists
if not os.path.exists(image_path):
    print(" Image not found in reports folder")
else:
    image = cv2.imread(image_path)

    # Check if image loaded
    if image is None:
        print(" Image failed to load (corrupt or unsupported)")
    else:
        print(" Image loaded successfully")
        print("Image shape:", image.shape)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(gray)

        if len(results) == 0:
            print("\n No text detected by OCR")
        else:
            print("\nExtracted Text:\n")
            for bbox, text, confidence in results:
                print(f"{text}  (Confidence: {confidence:.2f})")

