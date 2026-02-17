import pdfplumber
import PyPDF2
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from PIL import Image
import io
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from typing import List, Dict
try:
    from app.services.ocr_service import ocr_service
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

class PDFParser:
    def __init__(self):
        self.text_extraction_methods = ["pdfplumber", "pymupdf", "pypdf2"]
    
    def extract_text_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (best for structured data)"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber extraction error: {e}")
        return text
    
    def extract_text_pymupdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF (fast)"""
        if not HAS_PYMUPDF:
            return ""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
        except Exception as e:
            print(f"PyMuPDF extraction error: {e}")
        return text
    
    def extract_text_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2 (fallback)"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
        return text
    
    def extract_images_from_pdf(self, file_path: str) -> List:
        """Extract images from PDF for OCR processing"""
        if not HAS_PYMUPDF:
            return []
        images = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    images.append(image)
            doc.close()
        except Exception as e:
            print(f"Image extraction error: {e}")
        return images
    
    def extract_text(self, file_path: str, use_ocr_for_images: bool = True) -> str:
        """Main extraction method with fallback"""
        text = ""
        
        # Try pdfplumber first
        text = self.extract_text_pdfplumber(file_path)
        if len(text.strip()) > 100:  # If sufficient text extracted
            return text
        
        # Try PyMuPDF
        text = self.extract_text_pymupdf(file_path)
        if len(text.strip()) > 100:
            return text
        
        # Try PyPDF2
        text = self.extract_text_pypdf2(file_path)
        if len(text.strip()) > 100:
            return text
        
        # If text extraction fails, try OCR on images
        if use_ocr_for_images and HAS_OCR and HAS_CV2:
            try:
                images = self.extract_images_from_pdf(file_path)
                if images:
                    for image in images:
                        # Convert PIL Image to numpy array
                        img_array = np.array(image)
                        if len(img_array.shape) == 2:  # Grayscale
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
                        elif len(img_array.shape) == 3 and img_array.shape[2] == 4:  # RGBA
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                        ocr_text = ocr_service.extract_text(image=img_array)
                        if ocr_text:
                            text += ocr_text + "\n"
            except Exception as e:
                print(f"OCR extraction from images failed: {e}")
        
        return text

pdf_parser = PDFParser()
