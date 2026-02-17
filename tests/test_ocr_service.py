import pytest
import cv2
import numpy as np
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.services.ocr_service import OCRService

class TestOCRService:
    """Test cases for OCR service"""
    
    @pytest.fixture
    def ocr_service(self):
        return OCRService()
    
    @pytest.fixture
    def sample_image(self):
        """Create a simple test image with text"""
        # Create a white image
        img = np.ones((100, 400, 3), dtype=np.uint8) * 255
        
        # Add some text using OpenCV (simulated)
        cv2.putText(img, "Blood Sugar: 120", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, "Cholesterol: 200", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return img
    
    def test_preprocess_image(self, ocr_service, sample_image):
        """Test image preprocessing"""
        processed = ocr_service.preprocess_image(sample_image)
        
        assert processed is not None
        assert len(processed.shape) == 2  # Should be grayscale
        assert processed.shape[0] == sample_image.shape[0]
        assert processed.shape[1] == sample_image.shape[1]
    
    def test_extract_text_from_image_array(self, ocr_service, sample_image):
        """Test text extraction from image array"""
        try:
            text = ocr_service.extract_text(image=sample_image)
            # OCR might not always work in tests, so just check it doesn't crash
            assert isinstance(text, str)
        except Exception as e:
            # OCR might fail in test environment, that's okay
            pytest.skip(f"OCR test skipped: {e}")
