"""
OCR Engine for extracting text from medical reports.

This module provides a unified OCR interface supporting multiple backends
(Tesseract, EasyOCR) with image preprocessing and quality validation.
"""

from pathlib import Path
from typing import List, Literal, Optional
from dataclasses import dataclass
from datetime import datetime
from PIL import Image
import numpy as np
import cv2
import pytesseract as tess
from pdf2image import convert_from_path


OCRBackend = Literal["tesseract", "easyocr"]


@dataclass
class ExtractedText:
    """Container for OCR extraction results."""
    text: str
    confidence: float
    page_number: Optional[int] = None
    extraction_timestamp: datetime = None
    
    def __post_init__(self):
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()


@dataclass
class OCRResult:
    """Complete OCR result with metadata."""
    pages: List[ExtractedText]
    average_confidence: float
    total_pages: int
    backend_used: str
    
    @property
    def full_text(self) -> str:
        """Concatenate all page texts preserving order."""
        return "\n\n".join(page.text for page in self.pages)
    
    @property
    def passes_quality_check(self) -> bool:
        """Check if result meets minimum confidence threshold."""
        return self.average_confidence >= 0.60


class UnreadableDocumentError(Exception):
    """Raised when document quality is insufficient for OCR."""
    pass


class OCREngine:
    """
    Unified OCR engine with configurable backend and preprocessing.
    
    Supports:
    - Multiple OCR backends (Tesseract, EasyOCR)
    - Image preprocessing pipeline
    - Confidence scoring
    - Quality validation
    """
    
    MINIMUM_CONFIDENCE = 0.60
    PDF_DPI = 300
    
    def __init__(self, backend: OCRBackend = "tesseract"):
        """
        Initialize OCR engine with specified backend.
        
        Args:
            backend: OCR backend to use ("tesseract" or "easyocr")
        """
        self.backend = backend
        self._easyocr_reader = None
        
        if backend == "easyocr":
            self._initialize_easyocr()
    
    def _initialize_easyocr(self):
        """Lazy initialization of EasyOCR reader."""
        try:
            import easyocr
            self._easyocr_reader = easyocr.Reader(['en'])
        except ImportError:
            raise ImportError(
                "EasyOCR backend requires 'easyocr' package. "
                "Install with: pip install easyocr"
            )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> OCRResult:
        """
        Extract text from PDF document.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            OCRResult with extracted text and metadata
            
        Raises:
            UnreadableDocumentError: If document quality insufficient
        """
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=self.PDF_DPI)
        
        # Process each page
        extracted_pages = []
        for page_num, img in enumerate(images, start=1):
            extracted_text = self.extract_text_from_image_obj(img, page_number=page_num)
            extracted_pages.append(extracted_text)
        
        # Calculate average confidence
        avg_confidence = sum(page.confidence for page in extracted_pages) / len(extracted_pages)
        
        result = OCRResult(
            pages=extracted_pages,
            average_confidence=avg_confidence,
            total_pages=len(images),
            backend_used=self.backend
        )
        
        # Quality check
        if not result.passes_quality_check:
            raise UnreadableDocumentError(
                f"Document quality insufficient. Average confidence: {avg_confidence:.2%}, "
                f"minimum required: {self.MINIMUM_CONFIDENCE:.2%}"
            )
        
        return result
    
    def extract_text_from_image(self, image_path: Path) -> OCRResult:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to image file (JPEG, PNG, TIFF)
            
        Returns:
            OCRResult with extracted text and metadata
            
        Raises:
            UnreadableDocumentError: If image quality insufficient
        """
        img = Image.open(image_path)
        extracted_text = self.extract_text_from_image_obj(img, page_number=1)
        
        result = OCRResult(
            pages=[extracted_text],
            average_confidence=extracted_text.confidence,
            total_pages=1,
            backend_used=self.backend
        )
        
        # Quality check
        if not result.passes_quality_check:
            raise UnreadableDocumentError(
                f"Image quality insufficient. Confidence: {extracted_text.confidence:.2%}, "
                f"minimum required: {self.MINIMUM_CONFIDENCE:.2%}"
            )
        
        return result
    
    def extract_text_from_image_obj(
        self, 
        image: Image.Image, 
        page_number: Optional[int] = None
    ) -> ExtractedText:
        """
        Extract text from PIL Image object.
        
        Args:
            image: PIL Image object
            page_number: Optional page number for metadata
            
        Returns:
            ExtractedText with text and confidence score
        """
        # Preprocess image
        preprocessed = self.preprocess_image(image)
        
        # Extract text based on backend
        if self.backend == "tesseract":
            text, confidence = self._extract_with_tesseract(preprocessed)
        elif self.backend == "easyocr":
            text, confidence = self._extract_with_easyocr(preprocessed)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
        
        return ExtractedText(
            text=text,
            confidence=confidence,
            page_number=page_number
        )
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply preprocessing pipeline to improve OCR accuracy.
        
        Pipeline steps:
        1. Grayscale conversion
        2. Noise reduction (Gaussian blur)
        3. Contrast enhancement (CLAHE)
        4. Binarization (Otsu's method)
        5. Deskewing (Hough transform)
        
        Args:
            image: Input PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        
        # 1. Grayscale conversion
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # 2. Noise reduction
        denoised = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 3. Contrast enhancement using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 4. Binarization using Otsu's method
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 5. Deskewing
        deskewed = self._deskew_image(binary)
        
        # Convert back to PIL Image
        return Image.fromarray(deskewed)
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew image using Hough transform.
        
        Args:
            image: Grayscale image as numpy array
            
        Returns:
            Deskewed image as numpy array
        """
        # Detect edges
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            return image
        
        # Calculate average angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            angles.append(angle)
        
        if not angles:
            return image
        
        median_angle = np.median(angles)
        
        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(median_angle) < 0.5:
            return image
        
        # Rotate image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def _extract_with_tesseract(self, image: Image.Image) -> tuple[str, float]:
        """
        Extract text using Tesseract OCR.
        
        Args:
            image: Preprocessed PIL Image
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        # Get detailed OCR data for confidence scoring
        data = tess.image_to_data(image, output_type=tess.Output.DICT)
        
        # Extract text
        text = tess.image_to_string(image)
        
        # Calculate average confidence (excluding -1 values which indicate no text)
        confidences = [
            float(conf) for conf in data['conf'] 
            if conf != -1 and str(conf) != '-1'
        ]
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences) / 100.0  # Convert to 0-1 scale
        else:
            avg_confidence = 0.0
        
        return text, avg_confidence
    
    def _extract_with_easyocr(self, image: Image.Image) -> tuple[str, float]:
        """
        Extract text using EasyOCR.
        
        Args:
            image: Preprocessed PIL Image
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if self._easyocr_reader is None:
            self._initialize_easyocr()
        
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Perform OCR
        results = self._easyocr_reader.readtext(img_array)
        
        if not results:
            return "", 0.0
        
        # Extract text and confidence
        texts = []
        confidences = []
        
        for (bbox, text, conf) in results:
            texts.append(text)
            confidences.append(conf)
        
        # Combine text with spaces
        full_text = " ".join(texts)
        
        # Calculate average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return full_text, avg_confidence
