import os
import logging
import base64
import requests

logger = logging.getLogger(__name__)

# OCR.space free API key (get yours at https://ocr.space/ocrapi/freekey)
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "K85676270788957")  # Free tier key

def run_ocr_cloud(image_path: str) -> str:
    """Extract text using OCR.space cloud API (free tier: 25k requests/month)."""
    try:
        # Read and encode image as base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Determine file type
        ext = image_path.split(".")[-1].lower()
        if ext in ["jpg", "jpeg"]:
            file_type = "image/jpeg"
        elif ext == "png":
            file_type = "image/png"
        elif ext == "pdf":
            file_type = "application/pdf"
        else:
            file_type = "image/png"
        
        # Call OCR.space API
        response = requests.post(
            "https://api.ocr.space/parse/image",
            data={
                "base64Image": f"data:{file_type};base64,{image_data}",
                "apikey": OCR_SPACE_API_KEY,
                "language": "eng",
                "isOverlayRequired": False,
                "detectOrientation": True,
                "scale": True,
                "OCREngine": 2,  # More accurate engine
            },
            timeout=30
        )
        
        result = response.json()
        
        if result.get("IsErroredOnProcessing"):
            error_msg = result.get("ErrorMessage", ["Unknown error"])[0]
            logger.error(f"OCR.space error: {error_msg}")
            return ""
        
        # Extract text from all parsed results
        parsed_results = result.get("ParsedResults", [])
        if parsed_results:
            text = "\n".join([r.get("ParsedText", "") for r in parsed_results])
            logger.info(f"OCR.space extracted {len(text)} characters")
            return text.strip()
        
        return ""
        
    except requests.Timeout:
        logger.error("OCR.space API timeout")
        return ""
    except Exception as e:
        logger.error(f"OCR.space error: {str(e)}")
        return ""

def run_ocr_local(image_path: str) -> str:
    """Extract text using local Tesseract OCR."""
    try:
        import cv2
        import pytesseract
        
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
            return ""
        logger.error(f"Local OCR error: {str(e)}")
        return ""

def run_ocr(image_path: str) -> str:
    """Extract text from image. Uses cloud API first, falls back to local Tesseract."""
    logger.info(f"Running OCR on: {image_path}")
    
    # Try cloud OCR first (works on Render free tier)
    text = run_ocr_cloud(image_path)
    if text:
        logger.info("Successfully extracted text using cloud OCR")
        return text
    
    # Fall back to local Tesseract (for local development)
    logger.info("Trying local Tesseract OCR...")
    text = run_ocr_local(image_path)
    if text:
        logger.info("Successfully extracted text using local Tesseract")
        return text
    
    logger.warning("OCR failed to extract text")
    return ""
