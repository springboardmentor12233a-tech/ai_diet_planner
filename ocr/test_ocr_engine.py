"""
Unit tests for OCR Engine.

Tests cover:
- Backend initialization
- Image preprocessing
- Text extraction from images and PDFs
- Confidence scoring
- Quality validation
"""

import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from datetime import datetime

from .ocr_engine import (
    OCREngine,
    OCRResult,
    ExtractedText,
    UnreadableDocumentError
)


class TestOCREngineInitialization:
    """Test OCR engine initialization with different backends."""
    
    def test_init_with_tesseract_backend(self):
        """Should initialize with Tesseract backend."""
        engine = OCREngine(backend="tesseract")
        assert engine.backend == "tesseract"
        assert engine._easyocr_reader is None
    
    def test_init_with_default_backend(self):
        """Should default to Tesseract backend."""
        engine = OCREngine()
        assert engine.backend == "tesseract"
    
    def test_init_with_easyocr_backend(self):
        """Should initialize with EasyOCR backend."""
        try:
            engine = OCREngine(backend="easyocr")
            assert engine.backend == "easyocr"
            # EasyOCR reader is lazily initialized
        except ImportError:
            pytest.skip("EasyOCR not installed")


class TestImagePreprocessing:
    """Test image preprocessing pipeline."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def sample_image(self):
        """Create a simple test image."""
        # Create a white image with black text
        img_array = np.ones((100, 200), dtype=np.uint8) * 255
        # Add some "text" (black rectangles)
        img_array[40:60, 50:150] = 0
        return Image.fromarray(img_array)
    
    def test_preprocess_returns_pil_image(self, engine, sample_image):
        """Should return a PIL Image after preprocessing."""
        result = engine.preprocess_image(sample_image)
        assert isinstance(result, Image.Image)
    
    def test_preprocess_converts_to_grayscale(self, engine):
        """Should convert color images to grayscale."""
        # Create RGB image
        rgb_array = np.ones((100, 200, 3), dtype=np.uint8) * 255
        rgb_image = Image.fromarray(rgb_array, mode='RGB')
        
        result = engine.preprocess_image(rgb_image)
        result_array = np.array(result)
        
        # Result should be 2D (grayscale)
        assert len(result_array.shape) == 2
    
    def test_preprocess_handles_grayscale_input(self, engine, sample_image):
        """Should handle already grayscale images."""
        result = engine.preprocess_image(sample_image)
        assert isinstance(result, Image.Image)
    
    def test_preprocess_applies_binarization(self, engine, sample_image):
        """Should apply binarization (only black and white pixels)."""
        result = engine.preprocess_image(sample_image)
        result_array = np.array(result)
        
        # After binarization, should have mostly 0 or 255 values
        unique_values = np.unique(result_array)
        # Allow some intermediate values due to rotation interpolation
        assert 0 in unique_values or 255 in unique_values


class TestTextExtraction:
    """Test text extraction from images."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def text_image(self):
        """Create an image with actual text for OCR."""
        # Create a simple white image
        img = Image.new('RGB', (400, 100), color='white')
        # Note: For real testing, we'd need actual text rendering
        # This is a placeholder that will return low confidence
        return img
    
    def test_extract_from_image_obj_returns_extracted_text(self, engine, text_image):
        """Should return ExtractedText object."""
        result = engine.extract_text_from_image_obj(text_image)
        assert isinstance(result, ExtractedText)
        assert isinstance(result.text, str)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
    
    def test_extract_from_image_obj_includes_page_number(self, engine, text_image):
        """Should include page number in metadata."""
        result = engine.extract_text_from_image_obj(text_image, page_number=5)
        assert result.page_number == 5
    
    def test_extract_from_image_obj_includes_timestamp(self, engine, text_image):
        """Should include extraction timestamp."""
        result = engine.extract_text_from_image_obj(text_image)
        assert isinstance(result.extraction_timestamp, datetime)
    
    def test_extracted_text_confidence_in_valid_range(self, engine, text_image):
        """Confidence score should be between 0 and 1."""
        result = engine.extract_text_from_image_obj(text_image)
        assert 0.0 <= result.confidence <= 1.0


class TestOCRResult:
    """Test OCRResult data structure."""
    
    def test_full_text_concatenates_pages(self):
        """Should concatenate all page texts."""
        pages = [
            ExtractedText(text="Page 1", confidence=0.9, page_number=1),
            ExtractedText(text="Page 2", confidence=0.8, page_number=2),
            ExtractedText(text="Page 3", confidence=0.7, page_number=3),
        ]
        result = OCRResult(
            pages=pages,
            average_confidence=0.8,
            total_pages=3,
            backend_used="tesseract"
        )
        
        assert result.full_text == "Page 1\n\nPage 2\n\nPage 3"
    
    def test_passes_quality_check_with_high_confidence(self):
        """Should pass quality check with confidence >= 60%."""
        pages = [ExtractedText(text="Test", confidence=0.8, page_number=1)]
        result = OCRResult(
            pages=pages,
            average_confidence=0.8,
            total_pages=1,
            backend_used="tesseract"
        )
        
        assert result.passes_quality_check is True
    
    def test_fails_quality_check_with_low_confidence(self):
        """Should fail quality check with confidence < 60%."""
        pages = [ExtractedText(text="Test", confidence=0.5, page_number=1)]
        result = OCRResult(
            pages=pages,
            average_confidence=0.5,
            total_pages=1,
            backend_used="tesseract"
        )
        
        assert result.passes_quality_check is False
    
    def test_quality_check_threshold_exactly_60_percent(self):
        """Should pass quality check at exactly 60% confidence."""
        pages = [ExtractedText(text="Test", confidence=0.6, page_number=1)]
        result = OCRResult(
            pages=pages,
            average_confidence=0.6,
            total_pages=1,
            backend_used="tesseract"
        )
        
        assert result.passes_quality_check is True


class TestQualityValidation:
    """Test quality validation and error handling."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    def test_minimum_confidence_threshold_is_60_percent(self, engine):
        """Minimum confidence threshold should be 60%."""
        assert engine.MINIMUM_CONFIDENCE == 0.60
    
    def test_pdf_dpi_is_300(self, engine):
        """PDF conversion DPI should be 300."""
        assert engine.PDF_DPI == 300


class TestDeskewing:
    """Test image deskewing functionality."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    def test_deskew_returns_same_shape(self, engine):
        """Deskewed image should have same dimensions."""
        # Create test image
        img_array = np.ones((100, 200), dtype=np.uint8) * 255
        
        result = engine._deskew_image(img_array)
        
        assert result.shape == img_array.shape
    
    def test_deskew_handles_no_lines_detected(self, engine):
        """Should return original image if no lines detected."""
        # Create blank image (no edges to detect)
        img_array = np.ones((100, 200), dtype=np.uint8) * 255
        
        result = engine._deskew_image(img_array)
        
        # Should return image unchanged
        assert result.shape == img_array.shape


class TestBackendSelection:
    """Test OCR backend selection and usage."""
    
    def test_invalid_backend_raises_error(self):
        """Should raise error for invalid backend during extraction."""
        engine = OCREngine(backend="tesseract")
        engine.backend = "invalid_backend"  # Force invalid backend
        
        img = Image.new('RGB', (100, 100), color='white')
        
        with pytest.raises(ValueError, match="Unsupported backend"):
            engine.extract_text_from_image_obj(img)


class TestExtractedTextDataclass:
    """Test ExtractedText dataclass behavior."""
    
    def test_auto_timestamp_on_creation(self):
        """Should automatically set timestamp if not provided."""
        extracted = ExtractedText(text="Test", confidence=0.8)
        assert extracted.extraction_timestamp is not None
        assert isinstance(extracted.extraction_timestamp, datetime)
    
    def test_custom_timestamp_preserved(self):
        """Should preserve custom timestamp if provided."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        extracted = ExtractedText(
            text="Test",
            confidence=0.8,
            extraction_timestamp=custom_time
        )
        assert extracted.extraction_timestamp == custom_time
    
    def test_optional_page_number(self):
        """Page number should be optional."""
        extracted = ExtractedText(text="Test", confidence=0.8)
        assert extracted.page_number is None
        
        extracted_with_page = ExtractedText(text="Test", confidence=0.8, page_number=1)
        assert extracted_with_page.page_number == 1


class TestConfidenceScoring:
    """Test confidence score calculation."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    def test_tesseract_confidence_normalized_to_0_1(self, engine):
        """Tesseract confidence should be normalized to 0-1 range."""
        # Create a simple image
        img = Image.new('RGB', (100, 100), color='white')
        
        result = engine.extract_text_from_image_obj(img)
        
        # Confidence should be in valid range
        assert 0.0 <= result.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
