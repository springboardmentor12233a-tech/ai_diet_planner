import pandas as pd
import os
import sys

# Add src folder to path (if running directly)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocess import preprocess_text, extract_parameters
from easyocr_extractor import extract_text_from_image

# Path to your single image
image_path = r"C:\Users\parth\Documents\virtual intern\lbmaske\BLR-0425-PA-0039192_05c45741fa5d4b5180df06f200423a00__2_files_merged__26-04-2025_0430-01_PM@E.pdf_page_104.png"

# Extract text using EasyOCR
img_text = extract_text_from_image(image_path)

# Preprocess and extract parameters
records = extract_parameters(preprocess_text(img_text))

# Save results
df = pd.DataFrame(records)
output_file = r"C:\Users\parth\Documents\virtual intern\ai_diet_planner\output\data.csv"
df.to_csv(output_file, index=False)

print(f"Extraction completed. Total tests extracted: {len(df)}")
