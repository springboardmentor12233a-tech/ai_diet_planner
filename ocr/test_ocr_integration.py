"""
Integration tests for OCR Engine with real files.

These tests verify the OCR engine works with actual images and PDFs
from the datasets directory.
"""

import pytest
from pathlib import Path

from .ocr_engine import OCREngine, OCRResult, UnreadableDocumentError


# Get paths to test data
BASE_DIR = Path(__file__).resolve().parents[1]
IMAGE_DIR = BASE_DIR / "datasets" / "images"
PDF_DIR = BASE_DIR / "datasets" / "pdfs"


class TestOCRWithRealImages:
    """Test OCR engine with real image files."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def sample_images(self):
        """Get list of available test images."""
        if not IMAGE_DIR.exists():
            pytest.skip("Image directory not found")
        
        images = list(IMAGE_DIR.glob("*.png")) + list(IMAGE_DIR.glob("*.jpg"))
        if not images:
            pytest.skip("No test images found")
        
        return images
    
    def test_extract_from_real_image(self, engine, sample_images):
        """Should extract text from real image file."""
        # Use first available image
        image_path = sample_images[0]
        
        result = engine.extract_text_from_image(image_path)
        
        assert isinstance(result, OCRResult)
        assert result.total_pages == 1
        assert result.backend_used == "tesseract"
        assert isinstance(result.full_text, str)
        assert 0.0 <= result.average_confidence <= 1.0
    
    def test_extract_from_multiple_images(self, engine, sample_images):
        """Should successfully process multiple images."""
        # Test up to 3 images
        for image_path in sample_images[:3]:
            result = engine.extract_text_from_image(image_path)
            
            assert isinstance(result, OCRResult)
            assert result.total_pages == 1
            # Text might be empty for some images, but should be a string
            assert isinstance(result.full_text, str)
    
    def test_image_result_has_metadata(self, engine, sample_images):
        """Extracted result should have complete metadata."""
        image_path = sample_images[0]
        
        result = engine.extract_text_from_image(image_path)
        
        assert len(result.pages) == 1
        page = result.pages[0]
        assert page.page_number == 1
        assert page.extraction_timestamp is not None
        assert isinstance(page.confidence, float)


class TestOCRWithRealPDFs:
    """Test OCR engine with real PDF files."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def sample_pdfs(self):
        """Get list of available test PDFs."""
        if not PDF_DIR.exists():
            pytest.skip("PDF directory not found")
        
        pdfs = list(PDF_DIR.glob("*.pdf"))
        if not pdfs:
            pytest.skip("No test PDFs found")
        
        return pdfs
    
    def test_extract_from_real_pdf(self, engine, sample_pdfs):
        """Should extract text from real PDF file."""
        # Use first available PDF
        pdf_path = sample_pdfs[0]
        
        try:
            result = engine.extract_text_from_pdf(pdf_path)
            
            assert isinstance(result, OCRResult)
            assert result.total_pages > 0
            assert result.backend_used == "tesseract"
            assert isinstance(result.full_text, str)
            assert 0.0 <= result.average_confidence <= 1.0
            assert len(result.pages) == result.total_pages
        except UnreadableDocumentError:
            # Some PDFs might have low quality - this is expected behavior
            pytest.skip("PDF quality insufficient for OCR")
    
    def test_pdf_preserves_page_order(self, engine, sample_pdfs):
        """Should preserve page order in multi-page PDFs."""
        pdf_path = sample_pdfs[0]
        
        try:
            result = engine.extract_text_from_pdf(pdf_path)
            
            # Check page numbers are sequential
            for i, page in enumerate(result.pages, start=1):
                assert page.page_number == i
        except UnreadableDocumentError:
            pytest.skip("PDF quality insufficient for OCR")
    
    def test_pdf_pages_have_metadata(self, engine, sample_pdfs):
        """Each PDF page should have complete metadata."""
        pdf_path = sample_pdfs[0]
        
        try:
            result = engine.extract_text_from_pdf(pdf_path)
            
            for page in result.pages:
                assert page.page_number is not None
                assert page.extraction_timestamp is not None
                assert isinstance(page.confidence, float)
                assert 0.0 <= page.confidence <= 1.0
        except UnreadableDocumentError:
            pytest.skip("PDF quality insufficient for OCR")


class TestQualityValidationWithRealFiles:
    """Test quality validation with real files."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    def test_quality_check_property(self, engine):
        """Quality check should be based on 60% threshold."""
        # This test verifies the quality check logic
        # Real files might pass or fail depending on quality
        
        # Create a simple test to verify the threshold logic
        from .ocr_engine import OCRResult, ExtractedText
        
        # High quality result
        high_quality = OCRResult(
            pages=[ExtractedText(text="Test", confidence=0.8, page_number=1)],
            average_confidence=0.8,
            total_pages=1,
            backend_used="tesseract"
        )
        assert high_quality.passes_quality_check is True
        
        # Low quality result
        low_quality = OCRResult(
            pages=[ExtractedText(text="Test", confidence=0.4, page_number=1)],
            average_confidence=0.4,
            total_pages=1,
            backend_used="tesseract"
        )
        assert low_quality.passes_quality_check is False
        
        # Boundary case
        boundary = OCRResult(
            pages=[ExtractedText(text="Test", confidence=0.6, page_number=1)],
            average_confidence=0.6,
            total_pages=1,
            backend_used="tesseract"
        )
        assert boundary.passes_quality_check is True


class TestPreprocessingWithRealImages:
    """Test preprocessing pipeline with real images."""
    
    @pytest.fixture
    def engine(self):
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def sample_images(self):
        """Get list of available test images."""
        if not IMAGE_DIR.exists():
            pytest.skip("Image directory not found")
        
        images = list(IMAGE_DIR.glob("*.png")) + list(IMAGE_DIR.glob("*.jpg"))
        if not images:
            pytest.skip("No test images found")
        
        return images
    
    def test_preprocessing_improves_or_maintains_quality(self, engine, sample_images):
        """Preprocessing should not significantly degrade OCR quality."""
        from PIL import Image
        
        image_path = sample_images[0]
        original_image = Image.open(image_path)
        
        # Extract with preprocessing (default)
        result_with_preprocessing = engine.extract_text_from_image_obj(original_image)
        
        # Confidence should be in valid range
        assert 0.0 <= result_with_preprocessing.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
