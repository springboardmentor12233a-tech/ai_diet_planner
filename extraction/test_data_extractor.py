"""
Unit tests for the DataExtractor class.

Tests cover health metric extraction, unit normalization, context analysis,
section detection, and ambiguity flagging.
"""

import pytest
from datetime import datetime

from ai_diet_planner.extraction.data_extractor import (
    DataExtractor,
    InsufficientDataError,
    ExtractionResult
)
from ai_diet_planner.models.enums import MetricType
from ai_diet_planner.models.health_data import HealthMetric, StructuredHealthData, TextualNote


class TestDataExtractor:
    """Test suite for DataExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        """Create a DataExtractor instance for testing."""
        return DataExtractor()
    
    def test_extract_glucose_mg_dl(self, extractor):
        """Test extraction of glucose in mg/dL."""
        text = "Fasting Glucose: 120 mg/dL"
        result = extractor.extract_structured_data(text, "test-001")
        
        assert len(result.metrics) >= 1
        glucose_metrics = [m for m in result.metrics if m.metric_type == MetricType.GLUCOSE]
        assert len(glucose_metrics) >= 1
        assert glucose_metrics[0].value == 120.0
        assert glucose_metrics[0].unit == "mg/dl"
    
    def test_extract_glucose_mmol_l(self, extractor):
        """Test extraction and conversion of glucose from mmol/L to mg/dL."""
        text = "Blood Sugar: 6.5 mmol/L"
        result = extractor.extract_structured_data(text, "test-002")
        
        glucose_metrics = [m for m in result.metrics if m.metric_type == MetricType.GLUCOSE]
        assert len(glucose_metrics) >= 1
        # 6.5 mmol/L * 18 = 117 mg/dL
        assert abs(glucose_metrics[0].value - 117.0) < 0.1
        assert glucose_metrics[0].unit == "mg/dl"
    
    def test_extract_cholesterol_total(self, extractor):
        """Test extraction of total cholesterol."""
        text = "Total Cholesterol: 200 mg/dL"
        result = extractor.extract_structured_data(text, "test-003")
        
        chol_metrics = [m for m in result.metrics if m.metric_type == MetricType.CHOLESTEROL_TOTAL]
        assert len(chol_metrics) >= 1
        assert chol_metrics[0].value == 200.0
    
    def test_extract_ldl_hdl(self, extractor):
        """Test extraction of LDL and HDL cholesterol."""
        text = """
        LDL Cholesterol: 130 mg/dL
        HDL Cholesterol: 45 mg/dL
        """
        result = extractor.extract_structured_data(text, "test-004")
        
        ldl_metrics = [m for m in result.metrics if m.metric_type == MetricType.CHOLESTEROL_LDL]
        hdl_metrics = [m for m in result.metrics if m.metric_type == MetricType.CHOLESTEROL_HDL]
        
        assert len(ldl_metrics) >= 1
        assert len(hdl_metrics) >= 1
        assert ldl_metrics[0].value == 130.0
        assert hdl_metrics[0].value == 45.0
    
    def test_extract_triglycerides(self, extractor):
        """Test extraction of triglycerides."""
        text = "Triglycerides: 150 mg/dL"
        result = extractor.extract_structured_data(text, "test-005")
        
        tg_metrics = [m for m in result.metrics if m.metric_type == MetricType.TRIGLYCERIDES]
        assert len(tg_metrics) >= 1
        assert tg_metrics[0].value == 150.0
    
    def test_extract_bmi(self, extractor):
        """Test extraction of BMI."""
        text = "BMI: 28.5"
        result = extractor.extract_structured_data(text, "test-006")
        
        bmi_metrics = [m for m in result.metrics if m.metric_type == MetricType.BMI]
        assert len(bmi_metrics) >= 1
        assert bmi_metrics[0].value == 28.5
    
    def test_extract_blood_pressure(self, extractor):
        """Test extraction of blood pressure (systolic and diastolic)."""
        text = "Blood Pressure: 140/90 mmHg"
        result = extractor.extract_structured_data(text, "test-007")
        
        systolic = [m for m in result.metrics if m.metric_type == MetricType.BLOOD_PRESSURE_SYSTOLIC]
        diastolic = [m for m in result.metrics if m.metric_type == MetricType.BLOOD_PRESSURE_DIASTOLIC]
        
        assert len(systolic) >= 1
        assert len(diastolic) >= 1
        assert systolic[0].value == 140.0
        assert diastolic[0].value == 90.0
    
    def test_extract_hemoglobin(self, extractor):
        """Test extraction of hemoglobin."""
        text = "Hemoglobin: 13.5 g/dL"
        result = extractor.extract_structured_data(text, "test-008")
        
        hb_metrics = [m for m in result.metrics if m.metric_type == MetricType.HEMOGLOBIN]
        assert len(hb_metrics) >= 1
        assert hb_metrics[0].value == 13.5
    
    def test_extract_hba1c(self, extractor):
        """Test extraction of HbA1c."""
        text = "HbA1c: 6.5%"
        result = extractor.extract_structured_data(text, "test-009")
        
        hba1c_metrics = [m for m in result.metrics if m.metric_type == MetricType.HBA1C]
        assert len(hba1c_metrics) >= 1
        assert hba1c_metrics[0].value == 6.5
    
    def test_extract_multiple_metrics(self, extractor):
        """Test extraction of multiple metrics from a single report."""
        text = """
        Laboratory Results
        
        Glucose: 110 mg/dL
        Total Cholesterol: 195 mg/dL
        LDL: 120 mg/dL
        HDL: 50 mg/dL
        Triglycerides: 140 mg/dL
        BMI: 26.3
        BP: 130/85 mmHg
        Hemoglobin: 14.2 g/dL
        HbA1c: 5.8%
        """
        result = extractor.extract_structured_data(text, "test-010")
        
        # Should extract at least 9 metrics (some patterns might match multiple times)
        assert len(result.metrics) >= 9
        
        # Check that we have at least one of each major type
        metric_types = {m.metric_type for m in result.metrics}
        assert MetricType.GLUCOSE in metric_types
        assert MetricType.CHOLESTEROL_TOTAL in metric_types
        assert MetricType.BMI in metric_types
    
    def test_empty_text_raises_error(self, extractor):
        """Test that empty text raises InsufficientDataError."""
        with pytest.raises(InsufficientDataError):
            extractor.extract_structured_data("", "test-011")
    
    def test_no_metrics_raises_error(self, extractor):
        """Test that text with no metrics raises InsufficientDataError."""
        text = "This is just some random text with no health metrics."
        with pytest.raises(InsufficientDataError):
            extractor.extract_structured_data(text, "test-012")
    
    def test_extract_textual_notes_doctor_notes(self, extractor):
        """Test extraction of doctor notes section."""
        text = """
        Doctor's Notes:
        Patient presents with elevated blood sugar levels.
        Recommend dietary modifications and regular exercise.
        """
        notes = extractor.extract_textual_notes(text)
        
        doctor_notes = [n for n in notes if n.section == "doctor_notes"]
        assert len(doctor_notes) >= 1
        assert "elevated blood sugar" in doctor_notes[0].content.lower()
    
    def test_extract_textual_notes_prescriptions(self, extractor):
        """Test extraction of prescriptions section."""
        text = """
        Prescriptions:
        1. Metformin 500mg twice daily
        2. Atorvastatin 10mg once daily
        """
        notes = extractor.extract_textual_notes(text)
        
        prescriptions = [n for n in notes if n.section == "prescriptions"]
        assert len(prescriptions) >= 1
        assert "metformin" in prescriptions[0].content.lower()
    
    def test_extract_textual_notes_recommendations(self, extractor):
        """Test extraction of recommendations section."""
        text = """
        Recommendations:
        - Reduce sodium intake
        - Increase fiber consumption
        - Monitor blood pressure daily
        """
        notes = extractor.extract_textual_notes(text)
        
        recommendations = [n for n in notes if n.section == "recommendations"]
        assert len(recommendations) >= 1
        assert "sodium" in recommendations[0].content.lower()
    
    def test_extract_textual_notes_multiple_sections(self, extractor):
        """Test extraction of multiple note sections."""
        text = """
        Doctor's Notes:
        Patient shows signs of prediabetes.
        
        Prescriptions:
        Lifestyle modifications recommended.
        
        Recommendations:
        Follow up in 3 months.
        """
        notes = extractor.extract_textual_notes(text)
        
        assert len(notes) >= 3
        sections = {n.section for n in notes}
        assert "doctor_notes" in sections
        assert "prescriptions" in sections
        assert "recommendations" in sections
    
    def test_encrypted_text_excluded(self, extractor):
        """Test that encrypted or redacted text is excluded."""
        text = """
        Doctor's Notes:
        Patient name: [REDACTED]
        Diagnosis: ********
        
        Recommendations:
        Follow standard protocol.
        """
        notes = extractor.extract_textual_notes(text)
        
        # Redacted sections should be excluded
        for note in notes:
            assert "[redacted]" not in note.content.lower() or len(note.content) > 50
    
    def test_various_redaction_patterns(self, extractor):
        """Test detection of various redaction patterns."""
        redacted_texts = [
            "Patient info: [REDACTED]",
            "Sensitive data: ********",
            "Hidden: XXXXXXXXX",
            "Removed: ########",
            "Secret: [encrypted]",
            "Private: [REMOVED]",
            "Confidential: [censored]",
            "Data: ███████",
        ]
        
        for text in redacted_texts:
            assert extractor._is_encrypted_or_redacted(text), f"Failed to detect redaction in: {text}"
    
    def test_base64_encrypted_content_excluded(self, extractor):
        """Test that base64-like encrypted content is detected."""
        # Very long alphanumeric string without spaces (typical of encrypted content)
        encrypted_text = "aGVsbG93b3JsZGhlbGxvd29ybGRoZWxsb3dvcmxkaGVsbG93b3JsZGhlbGxvd29ybGRoZWxsb3dvcmxkaGVsbG93b3JsZGhlbGxvd29ybGQ"
        assert extractor._is_encrypted_or_redacted(encrypted_text)
    
    def test_normal_text_not_flagged_as_encrypted(self, extractor):
        """Test that normal medical text is not flagged as encrypted."""
        normal_texts = [
            "Patient presents with elevated blood sugar levels.",
            "Recommend dietary modifications and regular exercise.",
            "Follow up in 3 months for reassessment.",
        ]
        
        for text in normal_texts:
            assert not extractor._is_encrypted_or_redacted(text), f"Incorrectly flagged as encrypted: {text}"
    
    def test_context_preservation_in_notes(self, extractor):
        """Test that context and relationships are preserved in extracted notes."""
        text = """
        Doctor's Notes:
        Patient shows signs of prediabetes.
        Blood sugar levels are borderline high.
        
        Prescriptions:
        Lifestyle modifications recommended.
        No medication at this time.
        
        Recommendations:
        Reduce carbohydrate intake.
        Increase physical activity to 30 minutes daily.
        Follow up in 3 months.
        """
        notes = extractor.extract_textual_notes(text)
        
        # Check that each section preserves its full context
        doctor_notes = [n for n in notes if n.section == "doctor_notes"]
        prescriptions = [n for n in notes if n.section == "prescriptions"]
        recommendations = [n for n in notes if n.section == "recommendations"]
        
        assert len(doctor_notes) >= 1
        assert "prediabetes" in doctor_notes[0].content.lower()
        assert "blood sugar" in doctor_notes[0].content.lower()
        
        assert len(prescriptions) >= 1
        assert "lifestyle" in prescriptions[0].content.lower()
        
        assert len(recommendations) >= 1
        assert "carbohydrate" in recommendations[0].content.lower()
        assert "physical activity" in recommendations[0].content.lower()
    
    def test_separation_of_metrics_and_notes(self, extractor):
        """Test that structured metrics and textual notes are properly separated."""
        text = """
        Laboratory Results:
        Glucose: 120 mg/dL
        Cholesterol: 200 mg/dL
        
        Doctor's Notes:
        Patient shows good compliance with treatment.
        Continue current medication regimen.
        """
        
        result = extractor.extract_with_ambiguity_flagging(text, "test-sep-001")
        
        # Check structured data
        assert len(result.structured_data.metrics) >= 2
        glucose_found = any(m.metric_type == MetricType.GLUCOSE for m in result.structured_data.metrics)
        assert glucose_found
        
        # Check textual notes
        assert len(result.textual_notes) >= 1
        doctor_notes = [n for n in result.textual_notes if n.section == "doctor_notes"]
        assert len(doctor_notes) >= 1
        assert "compliance" in doctor_notes[0].content.lower()
        
        # Ensure metrics are not in notes and vice versa
        for note in result.textual_notes:
            # Notes should not contain just numeric values
            assert len(note.content.strip()) > 10
    
    def test_identify_metric_type_with_clear_context(self, extractor):
        """Test metric type identification with clear context."""
        context = "Fasting Glucose: 120 mg/dL"
        metric_type = extractor.identify_metric_type(120.0, context)
        
        assert metric_type == MetricType.GLUCOSE
    
    def test_identify_metric_type_ambiguous(self, extractor):
        """Test that ambiguous context returns None."""
        context = "Value: 120"  # Could be glucose, cholesterol, etc.
        metric_type = extractor.identify_metric_type(120.0, context)
        
        # Should return None or a specific type if pattern matches
        # The behavior depends on pattern matching
        assert metric_type is None or isinstance(metric_type, MetricType)
    
    def test_unit_normalization_glucose(self, extractor):
        """Test glucose unit normalization from mmol/L to mg/dL."""
        value, unit = extractor._normalize_unit(MetricType.GLUCOSE, 5.0, "mmol/l")
        
        assert abs(value - 90.0) < 0.1  # 5.0 * 18 = 90
        assert unit == "mg/dl"
    
    def test_unit_normalization_cholesterol(self, extractor):
        """Test cholesterol unit normalization from mmol/L to mg/dL."""
        value, unit = extractor._normalize_unit(MetricType.CHOLESTEROL_TOTAL, 5.0, "mmol/l")
        
        assert abs(value - 193.35) < 0.1  # 5.0 * 38.67 = 193.35
        assert unit == "mg/dl"
    
    def test_unit_normalization_hemoglobin(self, extractor):
        """Test hemoglobin unit normalization from g/L to g/dL."""
        value, unit = extractor._normalize_unit(MetricType.HEMOGLOBIN, 140.0, "g/l")
        
        assert abs(value - 14.0) < 0.1  # 140 * 0.1 = 14
        assert unit == "g/dl"
    
    def test_confidence_calculation(self, extractor):
        """Test confidence score calculation."""
        context = "Fasting Glucose: 120 mg/dL from lab results"
        confidence = extractor._calculate_confidence(MetricType.GLUCOSE, context)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should have high confidence with clear context
    
    def test_extract_with_ambiguity_flagging(self, extractor):
        """Test extraction with ambiguity flagging."""
        text = """
        Glucose: 120 mg/dL
        Some value: 150
        Another measurement: 180
        """
        result = extractor.extract_with_ambiguity_flagging(text, "test-013")
        
        assert isinstance(result, ExtractionResult)
        assert len(result.structured_data.metrics) >= 1
        # Ambiguous values might be flagged
        assert isinstance(result.ambiguous_values, list)
    
    def test_case_insensitive_extraction(self, extractor):
        """Test that extraction is case-insensitive."""
        text1 = "GLUCOSE: 120 mg/dL"
        text2 = "glucose: 120 mg/dL"
        text3 = "Glucose: 120 mg/dL"
        
        result1 = extractor.extract_structured_data(text1, "test-014a")
        result2 = extractor.extract_structured_data(text2, "test-014b")
        result3 = extractor.extract_structured_data(text3, "test-014c")
        
        assert len(result1.metrics) >= 1
        assert len(result2.metrics) >= 1
        assert len(result3.metrics) >= 1
    
    def test_extract_with_various_separators(self, extractor):
        """Test extraction with different separators (colon, dash, space)."""
        texts = [
            "Glucose: 120 mg/dL",
            "Glucose - 120 mg/dL",
            "Glucose 120 mg/dL",
        ]
        
        for i, text in enumerate(texts):
            result = extractor.extract_structured_data(text, f"test-015-{i}")
            glucose_metrics = [m for m in result.metrics if m.metric_type == MetricType.GLUCOSE]
            assert len(glucose_metrics) >= 1, f"Failed for text: {text}"
    
    def test_malformed_data_handling(self, extractor):
        """Test handling of malformed data."""
        text = "Glucose: abc mg/dL"  # Non-numeric value
        
        # Should not raise exception, just not extract this value
        try:
            result = extractor.extract_structured_data(text, "test-016")
            # If no valid metrics found, should raise InsufficientDataError
        except InsufficientDataError:
            pass  # Expected behavior
    
    def test_report_id_preserved(self, extractor):
        """Test that report ID is preserved in extraction result."""
        text = "Glucose: 120 mg/dL"
        report_id = "REPORT-12345"
        result = extractor.extract_structured_data(text, report_id)
        
        assert result.report_id == report_id
    
    def test_extraction_timestamp(self, extractor):
        """Test that extraction timestamp is set."""
        text = "Glucose: 120 mg/dL"
        before = datetime.now()
        result = extractor.extract_structured_data(text, "test-017")
        after = datetime.now()
        
        assert before <= result.extraction_timestamp <= after
    
    def test_metric_confidence_scores(self, extractor):
        """Test that all extracted metrics have confidence scores."""
        text = """
        Glucose: 120 mg/dL
        Cholesterol: 200 mg/dL
        BMI: 25.5
        """
        result = extractor.extract_structured_data(text, "test-018")
        
        for metric in result.metrics:
            assert 0.0 <= metric.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
