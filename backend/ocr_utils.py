import cv2
import os
import logging

logger = logging.getLogger(__name__)

def run_ocr(image_path: str) -> str:
    """Extract text from image using OCR. Handles missing Tesseract gracefully."""
    try:
        import pytesseract
        
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return ""
        
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Could not read image: {image_path}")
            return ""
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text
        
    except Exception as e:
        error_msg = str(e).lower()
        if "tesseract" in error_msg or "not installed" in error_msg:
            logger.warning("Tesseract OCR not available. Using fallback mode.")
            return "[OCR_UNAVAILABLE] Automatic text extraction is not available. Please use manual entry to input your health data."
        else:
            logger.error(f"OCR error: {str(e)}")
            return ""
