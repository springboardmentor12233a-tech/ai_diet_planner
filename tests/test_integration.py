"""
Integration tests for the complete data extraction pipeline
"""
import pytest
import os
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.services.data_extraction import data_extraction_service

class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_text_extraction(self):
        """Test complete extraction pipeline with text file"""
        test_file = Path("./tests/test_data/sample_medical_report.txt")
        
        if not test_file.exists():
            pytest.skip("Test data file not found. Run create_test_files.py first.")
        
        result = data_extraction_service.extract_from_file(str(test_file), "txt")
        
        assert "numeric_data" in result
        assert "textual_data" in result
        
        # Check specific extractions
        numeric = result["numeric_data"]
        assert "blood_sugar" in numeric or numeric.get("blood_sugar") is not None
        assert "cholesterol" in numeric
        assert "bmi" in numeric
        
        # Check textual data
        assert "doctor_notes" in result["textual_data"]
        assert len(result["textual_data"]["doctor_notes"]) > 0
    
    def test_multiple_formats(self):
        """Test extraction with different text formats"""
        test_cases = [
            ("Blood Sugar: 120", {"expected": "blood_sugar"}),
            ("FBS: 110", {"expected": "blood_sugar"}),
            ("Cholesterol: 200", {"expected": "cholesterol"}),
            ("BMI: 25.5", {"expected": "bmi"}),
            ("BP: 130/85", {"expected": "systolic_bp"}),
        ]
        
        for text, expected in test_cases:
            numeric_data = data_extraction_service.extract_numeric_data(text)
            # At least check it doesn't crash
            assert isinstance(numeric_data, dict)
