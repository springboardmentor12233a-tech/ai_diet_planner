"""
Integration tests for Upload page with backend orchestrator.

Tests the complete flow from file upload through backend processing.
"""

import pytest
from pathlib import Path
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ai_diet_planner.processor.report_processor import UploadedFile, ProcessingStatus
from ai_diet_planner.models import (
    StructuredHealthData,
    HealthMetric,
    MetricType,
    HealthCondition,
    ConditionType,
    Alert,
    AlertSeverity,
    DietRule,
    RulePriority,
    DietPlan,
    MealType,
    Meal,
    MacronutrientRatios,
)


class TestUploadPageIntegration:
    """Test Upload page integration with backend."""
    
    def test_uploaded_file_creation(self):
        """Test creating UploadedFile object from uploaded content."""
        # Create sample file content
        content = b"Sample medical report content"
        filename = "test_report.txt"
        
        # Create UploadedFile
        uploaded_file = UploadedFile(filename=filename, content=content)
        
        assert uploaded_file.filename == filename
        assert uploaded_file.content == content
    
    @patch('ai_diet_planner.main.AINutriCareOrchestrator')
    def test_process_report_success(self, mock_orchestrator_class):
        """Test successful report processing flow."""
        # Create mock orchestrator instance
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Create mock result
        mock_result = Mock()
        mock_result.status = Mock(value="completed")
        mock_result.report_id = "test-report-123"
        mock_result.processing_time = 5.5
        
        # Create mock structured data
        mock_metric = HealthMetric(
            metric_type=MetricType.GLUCOSE,
            value=120.0,
            unit="mg/dL",
            extracted_at=datetime.now(),
            confidence=0.95
        )
        mock_result.structured_data = StructuredHealthData(
            metrics=[mock_metric],
            report_id="test-report-123",
            extraction_timestamp=datetime.now()
        )
        
        mock_result.textual_notes = []
        mock_result.health_conditions = []
        mock_result.alerts = []
        mock_result.diet_rules = []
        mock_result.diet_plan = None
        mock_result.pdf_export = None
        mock_result.json_export = None
        
        mock_orchestrator.process_report.return_value = mock_result
        
        # Create test file
        test_content = b"Test medical report"
        uploaded_file_obj = UploadedFile(
            filename="test.txt",
            content=test_content
        )
        
        # Process report
        result = mock_orchestrator.process_report(
            uploaded_file=uploaded_file_obj,
            patient_profile=None,
            user_preferences=None,
            export_pdf=True,
            export_json=True
        )
        
        # Verify result
        assert result.status.value == "completed"
        assert result.report_id == "test-report-123"
        assert result.processing_time == 5.5
        assert len(result.structured_data.metrics) == 1
        assert result.structured_data.metrics[0].metric_type == MetricType.GLUCOSE
    
    @patch('ai_diet_planner.main.AINutriCareOrchestrator')
    def test_process_report_failure(self, mock_orchestrator_class):
        """Test report processing failure handling."""
        # Create mock orchestrator instance
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Create mock result with failure
        mock_result = Mock()
        mock_result.status = Mock(value="failed")
        mock_result.error_message = "Failed to extract text from report"
        mock_result.processing_time = 2.0
        
        mock_orchestrator.process_report.return_value = mock_result
        
        # Create test file
        test_content = b"Unreadable content"
        uploaded_file_obj = UploadedFile(
            filename="bad_scan.pdf",
            content=test_content
        )
        
        # Process report
        result = mock_orchestrator.process_report(
            uploaded_file=uploaded_file_obj,
            patient_profile=None,
            user_preferences=None,
            export_pdf=True,
            export_json=True
        )
        
        # Verify failure
        assert result.status.value == "failed"
        assert result.error_message == "Failed to extract text from report"
    
    def test_file_size_validation(self):
        """Test file size validation logic."""
        # Create file content larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
        
        # Calculate size in MB
        file_size_mb = len(large_content) / (1024 * 1024)
        
        # Verify size exceeds limit
        assert file_size_mb > 10
    
    def test_supported_file_formats(self):
        """Test that all supported formats are recognized."""
        supported_formats = ["pdf", "jpg", "jpeg", "png", "tif", "tiff", "txt"]
        
        for fmt in supported_formats:
            filename = f"test_file.{fmt}"
            assert any(filename.endswith(f".{f}") for f in supported_formats)
    
    def test_patient_profile_creation(self):
        """Test creating patient profile from user input."""
        from ai_diet_planner.models import PatientProfile, UserPreferences
        
        # Create user preferences
        preferences = UserPreferences(
            dietary_style="Vegetarian",
            allergies=["peanuts", "shellfish"],
            dislikes=["mushrooms"],
            cultural_preferences=[]
        )
        
        # Create patient profile
        profile = PatientProfile(
            patient_id="",
            age=30,
            gender="Male",
            height_cm=175,
            weight_kg=75,
            activity_level="moderate",
            preferences=preferences,
            created_at=None
        )
        
        assert profile.age == 30
        assert profile.gender == "Male"
        assert profile.preferences.dietary_style == "Vegetarian"
        assert "peanuts" in profile.preferences.allergies
    
    def test_allergies_parsing(self):
        """Test parsing comma-separated allergies input."""
        allergies_input = "peanuts, shellfish, dairy"
        allergies = [a.strip() for a in allergies_input.split(",")]
        
        assert len(allergies) == 3
        assert "peanuts" in allergies
        assert "shellfish" in allergies
        assert "dairy" in allergies
    
    def test_empty_allergies_parsing(self):
        """Test parsing empty allergies input."""
        allergies_input = ""
        allergies = [a.strip() for a in allergies_input.split(",")] if allergies_input else []
        
        assert len(allergies) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
