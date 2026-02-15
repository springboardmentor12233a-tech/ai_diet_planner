"""
Example usage of the unified OCR Engine.

This script demonstrates how to use the OCREngine class to extract
text from images and PDFs.
"""

from pathlib import Path
from .ocr_engine import OCREngine, UnreadableDocumentError


def main():
    # Initialize OCR engine with Tesseract backend
    engine = OCREngine(backend="tesseract")
    
    # Get paths to datasets
    base_dir = Path(__file__).resolve().parents[1]
    image_dir = base_dir / "datasets" / "images"
    pdf_dir = base_dir / "datasets" / "pdfs"
    
    print("=" * 70)
    print("OCR Engine Example Usage")
    print("=" * 70)
    
    # Process images
    print("\n--- Processing Images ---\n")
    if image_dir.exists():
        for img_path in list(image_dir.iterdir())[:2]:  # Process first 2 images
            if img_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                print(f"Processing: {img_path.name}")
                try:
                    result = engine.extract_text_from_image(img_path)
                    print(f"  Backend: {result.backend_used}")
                    print(f"  Confidence: {result.average_confidence:.2%}")
                    print(f"  Quality Check: {'PASS' if result.passes_quality_check else 'FAIL'}")
                    print(f"  Text Preview: {result.full_text[:100]}...")
                except UnreadableDocumentError as e:
                    print(f"  Error: {e}")
                print()
    
    # Process PDFs
    print("\n--- Processing PDFs ---\n")
    if pdf_dir.exists():
        for pdf_path in list(pdf_dir.iterdir())[:1]:  # Process first PDF
            if pdf_path.suffix.lower() == ".pdf":
                print(f"Processing: {pdf_path.name}")
                try:
                    result = engine.extract_text_from_pdf(pdf_path)
                    print(f"  Backend: {result.backend_used}")
                    print(f"  Total Pages: {result.total_pages}")
                    print(f"  Average Confidence: {result.average_confidence:.2%}")
                    print(f"  Quality Check: {'PASS' if result.passes_quality_check else 'FAIL'}")
                    
                    # Show confidence for each page
                    print(f"  Page Confidences:")
                    for page in result.pages:
                        print(f"    Page {page.page_number}: {page.confidence:.2%}")
                    
                    print(f"  Text Preview: {result.full_text[:200]}...")
                except UnreadableDocumentError as e:
                    print(f"  Error: {e}")
                print()
    
    print("=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
