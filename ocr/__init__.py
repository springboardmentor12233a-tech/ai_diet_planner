"""
OCR module for AI NutriCare System.

This module provides unified OCR functionality for extracting text
from medical reports in various formats (images and PDFs).
"""

from .ocr_engine import (
    OCREngine,
    OCRResult,
    ExtractedText,
    UnreadableDocumentError,
    OCRBackend
)

__all__ = [
    "OCREngine",
    "OCRResult",
    "ExtractedText",
    "UnreadableDocumentError",
    "OCRBackend"
]
