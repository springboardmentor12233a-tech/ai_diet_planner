import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.utils.pdf_parser import PDFParser

class TestPDFParser:
    """Test cases for PDF parser"""
    
    @pytest.fixture
    def pdf_parser(self):
        return PDFParser()
    
    def test_pdf_parser_initialization(self, pdf_parser):
        """Test PDF parser initialization"""
        assert pdf_parser is not None
        assert hasattr(pdf_parser, 'extract_text')
    
    # Note: Actual PDF file tests would require sample PDF files
    # These are skipped in basic test setup
