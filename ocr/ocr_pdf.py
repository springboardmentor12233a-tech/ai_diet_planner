from pathlib import Path
import pytesseract as tess
from pdf2image import convert_from_path


base_dir = Path(__file__).resolve().parents[1]  # Get the base directory two levels up
pdf_dir = base_dir / "datasets" / "pdfs"  # Directory containing PDFs

for pdf_path in pdf_dir.iterdir():
    if pdf_path.suffix.lower() == ".pdf":
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        print(f"\n--- {pdf_path.name} ---")
        print(f"Total pages: {len(images)}")
        
        # OCR each page
        for i, img in enumerate(images):
            text = tess.image_to_string(img)
            print(f"\n--- Page {i+1} ---")
            print(text)
