"""
Integration Tests for Main Application Orchestrator

Tests the complete end-to-end pipeline orchestrated by AINutriCareOrchestrator:
- Medical Report Processor → OCR Engine → Data Extractor
- Data Extractor → ML Health Analyzer + NLP Text Interpreter
- Analyzers → Diet Plan Generator → Report Exporter → Data Store

Validates: Requirements 2.4 and all integration requirements
"""

import pytest
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime

from ai_diet_planner.main import (
    AINutriCareOrchestrator,
    PipelineResult,
    process_medical_report,
)
from ai_diet_planner.processor.report_processor import (
    UploadedFile,
    ProcessingStatus,
)
from ai_diet_planner.models import (
    PatientProfile,
    UserPreferences,
)


# Test encryption key for all tests
TEST_ENCRYPTION_KEY = hashlib.sha256(b"test-key-for-testing").digest()


class TestPipelineResult:
    """Test PipelineResult data structure."""
    
    def test_pipeline_result_initialization(self):
        """Test PipelineResult initializes with correct defaults."""
        result = PipelineResult("test-report-123")
        
        assert result.report_id == "test-report-123"
        assert result.status == ProcessingStatus.QUEUED
        assert result.structured_data is None
        assert result.textual_notes == []
        assert result.health_conditions == []
        assert result.alerts == []
        assert result.diet_rules == []
        assert result.diet_plan is None
        assert result.error_message is None
        assert result.processing_time == 0.0
    
    def test_pipeline_result_complete(self):
        """Test marking result as complete."""
        import time
        result = PipelineResult("test-report")
        time.sleep(0.01)  # Small delay to ensure processing_time > 0
        result.complete()
        
        assert result.status == ProcessingStatus.COMPLETED
        assert result.processing_time > 0.0
    
    def test_pipeline_result_fail(self):
        """Test marking result as failed."""
        import time
        result = PipelineResult("test-report")
        time.sleep(0.01)  # Small delay to ensure processing_time > 0
        result.fail("Test error message")
        
        assert result.status == ProcessingStatus.FAILED
        assert result.error_message == "Test error message"
        assert result.processing_time > 0.0


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_orchestrator_initializes_all_components(self):
        """Test that orchestrator initializes all required components."""
        orchestrator = AINutriCareOrchestrator(encryption_key=TEST_ENCRYPTION_KEY)
        
        # Verify all components are initialized
        assert orchestrator.report_processor is not None
        assert orchestrator.ocr_engine is not None
        assert orchestrator.data_extractor is not None
        assert orchestrator.ml_analyzer is not None
        assert orchestrator.nlp_interpreter is not None
        assert orchestrator.diet_generator is not None
        assert orchestrator.report_exporter is not None
        assert orchestrator.data_store is not None
    
    def test_orchestrator_custom_configuration(self):
        """Test orchestrator with custom configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            orchestrator = AINutriCareOrchestrator(
                ocr_backend="tesseract",
                nlp_model="bert",
                db_path=db_path,
                encryption_key=TEST_ENCRYPTION_KEY
            )
            
            assert orchestrator.ocr_engine.backend == "tesseract"
            assert orchestrator.nlp_interpreter.model == "bert"


class TestTextExtractionPipeline:
    """Test text extraction from different file types."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return AINutriCareOrchestrator(encryption_key=TEST_ENCRYPTION_KEY)
    
    def test_extract_text_from_direct_text(self, orchestrator):
        """Test extracting text from direct text input."""
        text_content = "Patient glucose level: 150 mg/dL"
        uploaded_file = UploadedFile(
            filename="report.txt",
            content=text_content.encode('utf-8')
        )
        
        report_id = orchestrator.report_processor.accept_report(uploaded_file)
        extracted_text = orchestrator._extract_text(report_id, uploaded_file)
        
        assert extracted_text == text_content
    
    def test_extract_text_handles_errors_gracefully(self, orchestrator):
        """Test that text extraction handles errors gracefully."""
        # Create invalid file
        uploaded_file = UploadedFile(
            filename="invalid.pdf",
            content=b"not a real pdf"
        )
        
        report_id = "test-report"
        extracted_text = orchestrator._extract_text(report_id, uploaded_file)
        
        # Should return None on error, not crash
        assert extracted_text is None


class TestMetricsConversion:
    """Test conversion of metrics to ML analyzer format."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return AINutriCareOrchestrator(encryption_key=TEST_ENCRYPTION_KEY)
    
    def test_convert_metrics_to_dict(self, orchestrator):
        """Test converting StructuredHealthData to dictionary."""
        from ai_diet_planner.models import StructuredHealthData, HealthMetric, MetricType
        
        structured_data = StructuredHealthData(
            metrics=[
                HealthMetric(
                    metric_type=MetricType.GLUCOSE,
                    value=150.0,
                    unit="mg/dL",
                    confidence=0.95,
                    extracted_at=datetime.now()
                ),
                HealthMetric(
                    metric_type=MetricType.BMI,
                    value=28.5,
                    unit="kg/m²",
                    confidence=0.98,
                    extracted_at=datetime.now()
                ),
            ],
            report_id="test-report",
            extraction_timestamp=datetime.now()
        )
        
        metrics_dict = orchestrator._convert_metrics_to_dict(structured_data)
        
        assert "Glucose" in metrics_dict
        assert metrics_dict["Glucose"] == 150.0
        assert "BMI" in metrics_dict
        assert metrics_dict["BMI"] == 28.5
    
    def test_convert_metrics_handles_all_types(self, orchestrator):
        """Test that all metric types are properly converted."""
        from ai_diet_planner.models import StructuredHealthData, HealthMetric, MetricType
        
        # Create metrics for all types
        metrics = []
        metric_types = [
            (MetricType.GLUCOSE, 120.0),
            (MetricType.CHOLESTEROL_TOTAL, 200.0),
            (MetricType.BMI, 25.0),
            (MetricType.BP_SYSTOLIC, 120.0),
            (MetricType.HEMOGLOBIN, 14.0),
        ]
        
        for metric_type, value in metric_types:
            metrics.append(HealthMetric(
                metric_type=metric_type,
                value=value,
                unit="unit",
                confidence=0.9,
                extracted_at=datetime.now()
            ))
        
        structured_data = StructuredHealthData(
            metrics=metrics,
            report_id="test",
            extraction_timestamp=datetime.now()
        )
        
        metrics_dict = orchestrator._convert_metrics_to_dict(structured_data)
        
        # Verify all metrics converted
        assert len(metrics_dict) == len(metrics)


class TestEndToEndPipeline:
    """Test complete end-to-end pipeline."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with temporary database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield AINutriCareOrchestrator(db_path=db_path, encryption_key=TEST_ENCRYPTION_KEY)
    
    @pytest.fixture
    def sample_patient(self):
        """Create sample patient profile."""
        return PatientProfile(
            patient_id="test-patient-123",
            age=45,
            gender="M",
            height_cm=175.0,
            weight_kg=80.0,
            activity_level="moderate",
            preferences=UserPreferences(
                dietary_style="balanced",
                allergies=["peanuts"],
                dislikes=["liver"],
                cultural_preferences=[]
            ),
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_preferences(self):
        """Create sample user preferences."""
        return UserPreferences(
            dietary_style="vegetarian",
            allergies=["shellfish"],
            dislikes=["mushrooms"],
            cultural_preferences=[]
        )
    
    def test_process_text_report_end_to_end(self, orchestrator, sample_patient, sample_preferences):
        """
        Test complete pipeline with text input.
        
        Validates:
        - Text extraction
        - Data extraction
        - ML analysis
        - NLP interpretation
        - Diet plan generation
        - Export functionality
        """
        # Create sample medical report text
        report_text = """
        MEDICAL REPORT
        
        Patient: John Doe
        Date: 2024-01-15
        
        LAB RESULTS:
        - Fasting Blood Glucose: 155 mg/dL (High)
        - HbA1c: 7.2% (Elevated)
        - Total Cholesterol: 240 mg/dL (High)
        - BMI: 29.5 (Overweight)
        - Blood Pressure: 135/85 mmHg (Elevated)
        
        DOCTOR'S NOTES:
        Patient shows signs of prediabetes with elevated glucose and HbA1c levels.
        Recommend dietary modifications to reduce sugar intake and increase fiber.
        Monitor blood glucose levels regularly.
        
        RECOMMENDATIONS:
        - Low glycemic index diet
        - Reduce processed foods
        - Increase physical activity
        - Follow up in 3 months
        """
        
        uploaded_file = UploadedFile(
            filename="medical_report.txt",
            content=report_text.encode('utf-8')
        )
        
        # Process through complete pipeline
        result = orchestrator.process_report(
            uploaded_file=uploaded_file,
            patient_profile=sample_patient,
            user_preferences=sample_preferences,
            export_pdf=True,
            export_json=True
        )
        
        # Verify processing completed
        assert result.status == ProcessingStatus.COMPLETED
        assert result.processing_time > 0.0
        assert result.error_message is None
        
        # Verify data extraction
        assert result.structured_data is not None
        assert len(result.structured_data.metrics) > 0
        
        # Verify ML analysis
        assert len(result.health_conditions) > 0
        assert len(result.alerts) > 0
        
        # Verify NLP interpretation
        assert len(result.textual_notes) > 0
        # Diet rules may be empty with basic BERT extraction
        assert isinstance(result.diet_rules, list)
        
        # Verify diet plan generation
        assert result.diet_plan is not None
        assert result.diet_plan.daily_calories > 0
        assert len(result.diet_plan.meals) == 4  # breakfast, lunch, snack, dinner
        
        # Verify exports
        assert result.pdf_export is not None
        assert len(result.pdf_export) > 0
        assert result.json_export is not None
        assert len(result.json_export) > 0
        
        # Verify database storage
        assert result.diet_plan_id is not None
    
    def test_process_report_without_patient_profile(self, orchestrator):
        """Test processing without patient profile (no database storage)."""
        report_text = "Glucose: 120 mg/dL, BMI: 24"
        
        uploaded_file = UploadedFile(
            filename="report.txt",
            content=report_text.encode('utf-8')
        )
        
        result = orchestrator.process_report(
            uploaded_file=uploaded_file,
            export_pdf=False,
            export_json=False
        )
        
        # Should complete but not store in database
        assert result.status == ProcessingStatus.COMPLETED
        assert result.diet_plan_id is None
    
    def test_process_report_handles_insufficient_data(self, orchestrator):
        """Test pipeline handles reports with insufficient data."""
        report_text = "This is just random text with no health data."
        
        uploaded_file = UploadedFile(
            filename="invalid_report.txt",
            content=report_text.encode('utf-8')
        )
        
        result = orchestrator.process_report(uploaded_file)
        
        # Should fail gracefully
        assert result.status == ProcessingStatus.FAILED
        assert result.error_message is not None
        assert "extract health metrics" in result.error_message.lower()
    
    def test_process_report_with_minimal_data(self, orchestrator):
        """Test pipeline with minimal but valid data."""
        report_text = "Blood Glucose: 130 mg/dL"
        
        uploaded_file = UploadedFile(
            filename="minimal_report.txt",
            content=report_text.encode('utf-8')
        )
        
        result = orchestrator.process_report(uploaded_file)
        
        # Should complete with minimal data
        assert result.status == ProcessingStatus.COMPLETED
        assert result.structured_data is not None
        assert len(result.structured_data.metrics) >= 1
    
    def test_process_report_with_multiple_conditions(self, orchestrator):
        """Test pipeline detects multiple health conditions."""
        report_text = """
        LAB RESULTS:
        - Glucose: 160 mg/dL
        - Blood Pressure: 150/95 mmHg
        - Total Cholesterol: 280 mg/dL
        - BMI: 33
        - Hemoglobin: 10.5 g/dL
        """
        
        uploaded_file = UploadedFile(
            filename="multi_condition_report.txt",
            content=report_text.encode('utf-8')
        )
        
        result = orchestrator.process_report(uploaded_file)
        
        assert result.status == ProcessingStatus.COMPLETED
        
        # Should detect multiple conditions
        assert len(result.health_conditions) >= 2
        
        # Should generate multiple alerts
        assert len(result.alerts) >= 3
    
    def test_pipeline_performance(self, orchestrator):
        """Test that pipeline meets performance requirements."""
        report_text = """
        Glucose: 140 mg/dL
        Cholesterol: 220 mg/dL
        BMI: 27
        Blood Pressure: 130/85 mmHg
        
        Doctor's notes: Monitor glucose levels.
        """
        
        uploaded_file = UploadedFile(
            filename="performance_test.txt",
            content=report_text.encode('utf-8')
        )
        
        result = orchestrator.process_report(uploaded_file)
        
        # Single-page report should complete within 30 seconds (Requirement 20.1)
        assert result.processing_time < 30.0
        assert result.status == ProcessingStatus.COMPLETED


class TestDatabaseIntegration:
    """Test database storage and retrieval."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with temporary database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield AINutriCareOrchestrator(db_path=db_path, encryption_key=TEST_ENCRYPTION_KEY)
    
    @pytest.fixture
    def sample_patient(self):
        """Create sample patient profile."""
        return PatientProfile(
            patient_id="test-patient-456",
            age=35,
            gender="F",
            height_cm=165.0,
            weight_kg=65.0,
            activity_level="active",
            preferences=UserPreferences(
                dietary_style="vegan",
                allergies=[],
                dislikes=[],
                cultural_preferences=[]
            ),
            created_at=datetime.now()
        )
    
    def test_patient_data_persistence(self, orchestrator, sample_patient):
        """Test that patient data is stored and retrievable."""
        report_text = "Glucose: 110 mg/dL, BMI: 22"
        
        uploaded_file = UploadedFile(
            filename="test_report.txt",
            content=report_text.encode('utf-8')
        )
        
        # Process report
        result = orchestrator.process_report(
            uploaded_file=uploaded_file,
            patient_profile=sample_patient
        )
        
        assert result.status == ProcessingStatus.COMPLETED
        assert result.diet_plan_id is not None
        
        # Retrieve patient history
        history = orchestrator.get_patient_history(sample_patient.patient_id)
        
        assert history is not None
        # History should contain the saved diet plan
        assert "diet_plans" in history or len(history) > 0
    
    def test_delete_patient_data(self, orchestrator, sample_patient):
        """Test complete patient data deletion."""
        report_text = "Glucose: 115 mg/dL"
        
        uploaded_file = UploadedFile(
            filename="test_report.txt",
            content=report_text.encode('utf-8')
        )
        
        # Process and store
        result = orchestrator.process_report(
            uploaded_file=uploaded_file,
            patient_profile=sample_patient
        )
        
        assert result.status == ProcessingStatus.COMPLETED
        
        # Delete patient data
        deleted = orchestrator.delete_patient_data(sample_patient.patient_id)
        
        assert deleted is True


class TestConvenienceFunction:
    """Test convenience function for simple usage."""
    
    def test_process_medical_report_function(self):
        """Test convenience function with text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Glucose: 125 mg/dL\nBMI: 26")
            temp_path = Path(f.name)
        
        try:
            result = process_medical_report(temp_path, encryption_key=TEST_ENCRYPTION_KEY)
            
            assert result.status == ProcessingStatus.COMPLETED
            assert result.structured_data is not None
        finally:
            temp_path.unlink()


class TestErrorHandling:
    """Test error handling throughout the pipeline."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return AINutriCareOrchestrator(encryption_key=TEST_ENCRYPTION_KEY)
    
    def test_pipeline_handles_invalid_file(self, orchestrator):
        """Test pipeline handles invalid files gracefully."""
        from ai_diet_planner.processor.report_processor import UnsupportedFormatError
        
        invalid_file = UploadedFile(
            filename="invalid.xyz",
            content=b"invalid content"
        )
        
        with pytest.raises(UnsupportedFormatError):
            orchestrator.process_report(invalid_file)
    
    def test_pipeline_handles_oversized_file(self, orchestrator):
        """Test pipeline rejects oversized files."""
        from ai_diet_planner.processor.report_processor import FileSizeError
        
        large_file = UploadedFile(
            filename="large.txt",
            content=b"x" * (11 * 1024 * 1024)  # 11 MB
        )
        
        with pytest.raises(FileSizeError):
            orchestrator.process_report(large_file)
    
    def test_pipeline_handles_exceptions_gracefully(self, orchestrator):
        """Test that unexpected exceptions are caught and reported."""
        # This should trigger an error but not crash
        uploaded_file = UploadedFile(
            filename="test.txt",
            content=b""  # Empty file
        )
        
        result = orchestrator.process_report(uploaded_file)
        
        # Should fail gracefully with error message
        assert result.status == ProcessingStatus.FAILED
        assert result.error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
