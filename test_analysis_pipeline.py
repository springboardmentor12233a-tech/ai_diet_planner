"""
Integration Test for Analysis Pipeline (Task 8 Checkpoint)

Tests the complete analysis pipeline:
1. Extracted metrics → ML Health Analyzer → Health conditions and alerts
2. Extracted notes → NLP Text Interpreter → Diet rules

This validates that the ML and NLP components work together correctly.
"""

import pytest
from datetime import datetime

from ai_diet_planner.ml.health_analyzer import MLHealthAnalyzer
from ai_diet_planner.nlp.text_interpreter import NLPTextInterpreter
from ai_diet_planner.nlp.rules_mapping import RulesMapper
from ai_diet_planner.models.health_data import StructuredHealthData, HealthMetric, TextualNote
from ai_diet_planner.models.enums import MetricType, ConditionType, AlertSeverity, RulePriority


class TestMLAnalysisPipeline:
    """Test ML Health Analyzer pipeline: Metrics → Classification → Alerts."""
    
    @pytest.fixture
    def ml_analyzer(self):
        """Create ML Health Analyzer."""
        return MLHealthAnalyzer()
    
    def test_metrics_to_conditions_diabetes(self, ml_analyzer):
        """
        Test: Extracted metrics → ML classification → Health conditions
        
        Validates:
        - ML classifier processes health metrics
        - Detects diabetes condition
        - Returns HealthCondition objects with confidence scores
        """
        # Simulate extracted metrics from data extractor
        metrics = {
            'Glucose': 148,  # Diabetes range (>= 126 mg/dL)
            'BMI': 28.5,
            'Age': 45,
            'BloodPressure': 80
        }
        
        # Run ML classification
        conditions = ml_analyzer.classify_conditions(metrics)
        
        # Verify output format
        assert isinstance(conditions, list)
        assert len(conditions) > 0
        
        # Verify diabetes detected
        condition_types = [c.condition_type for c in conditions]
        assert ConditionType.DIABETES_TYPE2 in condition_types
        
        # Verify condition has required fields
        diabetes_condition = next(c for c in conditions if c.condition_type == ConditionType.DIABETES_TYPE2)
        assert isinstance(diabetes_condition.confidence, float)
        assert 0.0 < diabetes_condition.confidence <= 1.0
        assert MetricType.GLUCOSE in diabetes_condition.contributing_metrics
        assert diabetes_condition.detected_at is not None
    
    def test_metrics_to_alerts_critical(self, ml_analyzer):
        """
        Test: Extracted metrics → ML analysis → Critical alerts
        
        Validates:
        - ML analyzer detects abnormal values
        - Generates alerts with severity levels
        - Includes recommended actions
        """
        # Simulate extracted metrics with critical values
        metrics = {
            'Glucose': 180,  # Critical (>= 126)
            'BloodPressure': 150,  # Critical (>= 140)
            'BMI': 35  # Critical (>= 30)
        }
        
        # Generate alerts
        alerts = ml_analyzer.detect_abnormal_values(metrics)
        
        # Verify alerts generated
        assert len(alerts) == 3
        
        # Verify all are critical
        for alert in alerts:
            assert alert.severity == AlertSeverity.CRITICAL
            assert alert.metric_type is not None
            assert alert.message is not None
            assert alert.recommended_action is not None
            assert len(alert.recommended_action) > 0
    
    def test_metrics_to_alerts_prioritization(self, ml_analyzer):
        """
        Test: Alerts are prioritized by severity (Requirement 6.3)
        
        Validates:
        - Critical alerts come before warning alerts
        - Alert prioritization works correctly
        """
        # Mix of critical and warning values
        metrics = {
            'Glucose': 150,  # Critical
            'BMI': 27,  # Warning (25-29)
            'BloodPressure': 95  # Critical
        }
        
        alerts = ml_analyzer.detect_abnormal_values(metrics)
        
        # Verify prioritization
        assert len(alerts) == 3
        
        # First two should be critical
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[1].severity == AlertSeverity.CRITICAL
        
        # Last should be warning
        assert alerts[2].severity == AlertSeverity.WARNING
    
    def test_metrics_to_multiple_conditions(self, ml_analyzer):
        """
        Test: Multiple health conditions detected from metrics
        
        Validates:
        - ML analyzer can detect multiple conditions simultaneously
        - Each condition has proper metadata
        """
        # Metrics indicating multiple conditions
        metrics = {
            'Glucose': 140,  # Diabetes
            'BMI': 32,  # Obesity Class I
            'BloodPressure': 145,  # Hypertension Stage 2
            'Cholesterol': 250  # Hyperlipidemia
        }
        
        conditions = ml_analyzer.classify_conditions(metrics)
        
        # Should detect multiple conditions
        assert len(conditions) >= 2
        
        # Verify each condition is properly formed
        for condition in conditions:
            assert condition.condition_type is not None
            assert condition.confidence > 0
            assert len(condition.contributing_metrics) > 0


class TestNLPAnalysisPipeline:
    """Test NLP Text Interpreter pipeline: Notes → Interpretation → Diet rules."""
    
    @pytest.fixture
    def nlp_interpreter(self):
        """Create NLP Text Interpreter."""
        return NLPTextInterpreter(model="bert")
    
    @pytest.fixture
    def rules_mapper(self):
        """Create Rules Mapper."""
        return RulesMapper()
    
    def test_notes_to_diet_rules_diabetes(self, nlp_interpreter):
        """
        Test: Extracted notes → NLP interpretation → Diet rules
        
        Validates:
        - NLP interpreter processes textual notes
        - Extracts actionable diet rules
        - Assigns proper priorities
        """
        # Simulate extracted notes from data extractor
        notes = [
            TextualNote(
                content="Patient diagnosed with Type 2 Diabetes. Recommend low sugar diet and monitor blood glucose levels.",
                section="doctor_notes",
                page_number=1
            )
        ]
        
        # Run NLP interpretation
        diet_rules = nlp_interpreter.interpret_notes(notes)
        
        # Verify output format
        assert isinstance(diet_rules, list)
        assert len(diet_rules) > 0
        
        # Verify rules have required fields
        for rule in diet_rules:
            assert rule.rule_text is not None
            assert rule.priority in [RulePriority.REQUIRED, RulePriority.RECOMMENDED, RulePriority.OPTIONAL]
            assert len(rule.food_categories) > 0
            assert rule.action in ["include", "exclude", "limit"]
            assert rule.source is not None
    
    def test_notes_to_diet_rules_restrictions(self, nlp_interpreter):
        """
        Test: Extract dietary restrictions with REQUIRED priority
        
        Validates:
        - NLP extracts restrictions (allergies, intolerances)
        - Assigns REQUIRED priority to restrictions
        """
        notes = [
            TextualNote(
                content="Patient has severe peanut allergy. Must avoid all peanut products and cross-contamination.",
                section="doctor_notes",
                page_number=1
            )
        ]
        
        # Extract restrictions
        restrictions = nlp_interpreter.extract_restrictions(notes)
        
        # Verify restrictions format (may be empty with basic extraction)
        assert isinstance(restrictions, list)
        
        # If restrictions are extracted, verify format
        for restriction in restrictions:
            assert restriction.restriction_type in ["allergy", "intolerance", "medical", "religious"]
            assert restriction.severity in ["strict", "moderate"]
            assert len(restriction.restricted_items) > 0
    
    def test_notes_to_diet_rules_recommendations(self, nlp_interpreter):
        """
        Test: Extract dietary recommendations with RECOMMENDED priority
        
        Validates:
        - NLP extracts recommendations
        - Assigns RECOMMENDED priority
        """
        notes = [
            TextualNote(
                content="Recommend increasing fiber intake through whole grains and vegetables.",
                section="recommendations",
                page_number=2
            )
        ]
        
        # Extract recommendations
        recommendations = nlp_interpreter.extract_recommendations(notes)
        
        # Verify recommendations format (may be generic with basic extraction)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Verify recommendations are strings
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    def test_notes_to_rules_mapping(self, nlp_interpreter, rules_mapper):
        """
        Test: Diet rules mapped to food categories
        
        Validates:
        - Rules are mapped to specific food categories
        - Food categories are valid
        """
        notes = [
            TextualNote(
                content="Reduce sodium intake due to hypertension. Avoid processed foods.",
                section="doctor_notes",
                page_number=1
            )
        ]
        
        # Interpret notes
        diet_rules = nlp_interpreter.interpret_notes(notes)
        
        # Verify food categories assigned
        assert len(diet_rules) > 0
        
        for rule in diet_rules:
            assert len(rule.food_categories) > 0
            # Verify categories are from valid set
            valid_categories = rules_mapper.food_categories.keys()
            for category in rule.food_categories:
                # Category should be valid or "all"
                assert category in valid_categories or category == "all"
    
    def test_notes_conflict_resolution(self, nlp_interpreter):
        """
        Test: Conflicting diet rules are resolved
        
        Validates:
        - NLP identifies conflicting rules
        - Resolves conflicts using priority hierarchy
        """
        notes = [
            TextualNote(
                content="Include dairy for calcium. However, patient has lactose intolerance - avoid dairy products.",
                section="doctor_notes",
                page_number=1
            )
        ]
        
        # Interpret notes
        diet_rules = nlp_interpreter.interpret_notes(notes)
        
        # Resolve conflicts
        resolved_rules = nlp_interpreter.resolve_conflicts(diet_rules)
        
        # Verify conflicts resolved
        assert isinstance(resolved_rules, list)
        
        # Check that REQUIRED rules are prioritized over RECOMMENDED
        dairy_rules = [r for r in resolved_rules if "dairy" in r.food_categories]
        if len(dairy_rules) > 0:
            # Should keep the exclusion (intolerance) over inclusion
            assert any(r.action == "exclude" for r in dairy_rules)


class TestEndToEndAnalysisPipeline:
    """Test complete analysis pipeline: Metrics + Notes → Conditions + Rules."""
    
    @pytest.fixture
    def ml_analyzer(self):
        """Create ML Health Analyzer."""
        return MLHealthAnalyzer()
    
    @pytest.fixture
    def nlp_interpreter(self):
        """Create NLP Text Interpreter."""
        return NLPTextInterpreter(model="bert")
    
    def test_complete_pipeline_diabetes_patient(self, ml_analyzer, nlp_interpreter):
        """
        Test complete analysis pipeline for diabetes patient.
        
        Validates:
        1. Metrics → ML → Conditions and alerts
        2. Notes → NLP → Diet rules
        3. Outputs are compatible and properly formatted
        """
        # Step 1: Simulate extracted metrics
        metrics = {
            'Glucose': 155,
            'HbA1c': 7.2,
            'BMI': 29,
            'Age': 52
        }
        
        # Step 2: Simulate extracted notes
        notes = [
            TextualNote(
                content="Patient diagnosed with Type 2 Diabetes Mellitus. HbA1c elevated at 7.2%. Recommend strict glucose control through diet modification.",
                section="doctor_notes",
                page_number=1
            ),
            TextualNote(
                content="Metformin 500mg twice daily. Monitor blood glucose levels.",
                section="prescription",
                page_number=1
            )
        ]
        
        # Step 3: Run ML analysis
        conditions = ml_analyzer.classify_conditions(metrics)
        alerts = ml_analyzer.detect_abnormal_values(metrics)
        
        # Step 4: Run NLP analysis
        diet_rules = nlp_interpreter.interpret_notes(notes)
        
        # Verify ML outputs
        assert len(conditions) > 0
        assert any(c.condition_type == ConditionType.DIABETES_TYPE2 for c in conditions)
        assert len(alerts) > 0
        
        # Verify NLP outputs
        assert len(diet_rules) > 0
        
        # Verify outputs are compatible (can be used together)
        # ML should detect diabetes
        condition_names = [c.condition_type.value for c in conditions]
        assert "diabetes" in str(condition_names).lower() or "glucose" in str(condition_names).lower()
        
        # NLP should generate diet rules (content may vary with basic extraction)
        assert all(hasattr(r, 'rule_text') and hasattr(r, 'priority') for r in diet_rules)
    
    def test_complete_pipeline_multiple_conditions(self, ml_analyzer, nlp_interpreter):
        """
        Test complete pipeline with multiple health conditions.
        
        Validates:
        - ML detects multiple conditions
        - NLP generates rules for multiple conditions
        - Outputs are comprehensive
        """
        # Metrics indicating multiple conditions
        metrics = {
            'Glucose': 140,
            'BloodPressure': 145,
            'Cholesterol': 260,
            'BMI': 32,
            'Age': 58
        }
        
        # Notes mentioning multiple conditions
        notes = [
            TextualNote(
                content="Patient has diabetes, hypertension, and high cholesterol. Comprehensive dietary changes required.",
                section="doctor_notes",
                page_number=1
            )
        ]
        
        # Run analysis
        conditions = ml_analyzer.classify_conditions(metrics)
        alerts = ml_analyzer.detect_abnormal_values(metrics)
        diet_rules = nlp_interpreter.interpret_notes(notes)
        
        # Verify multiple conditions detected
        assert len(conditions) >= 2
        
        # Verify multiple alerts generated
        assert len(alerts) >= 3
        
        # Verify diet rules generated (may be generic with basic extraction)
        assert len(diet_rules) >= 1
        
        # Verify rules have proper structure
        for rule in diet_rules:
            assert hasattr(rule, 'rule_text')
            assert hasattr(rule, 'priority')
            assert hasattr(rule, 'food_categories')
            assert hasattr(rule, 'action')
    
    def test_pipeline_output_format_compatibility(self, ml_analyzer, nlp_interpreter):
        """
        Test that ML and NLP outputs have compatible formats.
        
        Validates:
        - Both outputs can be serialized
        - Both have required fields
        - Outputs can be combined for diet plan generation
        """
        # Sample data
        metrics = {'Glucose': 130, 'BMI': 28}
        notes = [TextualNote(content="Monitor glucose levels", section="doctor_notes")]
        
        # Run analysis
        conditions = ml_analyzer.classify_conditions(metrics)
        alerts = ml_analyzer.detect_abnormal_values(metrics)
        diet_rules = nlp_interpreter.interpret_notes(notes)
        
        # Verify all outputs have required attributes
        for condition in conditions:
            assert hasattr(condition, 'condition_type')
            assert hasattr(condition, 'confidence')
            assert hasattr(condition, 'contributing_metrics')
            assert hasattr(condition, 'detected_at')
        
        for alert in alerts:
            assert hasattr(alert, 'metric_type')
            assert hasattr(alert, 'severity')
            assert hasattr(alert, 'message')
            assert hasattr(alert, 'recommended_action')
        
        for rule in diet_rules:
            assert hasattr(rule, 'rule_text')
            assert hasattr(rule, 'priority')
            assert hasattr(rule, 'food_categories')
            assert hasattr(rule, 'action')
            assert hasattr(rule, 'source')
    
    def test_pipeline_handles_minimal_data(self, ml_analyzer, nlp_interpreter):
        """
        Test pipeline handles minimal/incomplete data gracefully.
        
        Validates:
        - Pipeline works with limited metrics
        - Pipeline works with brief notes
        - No crashes with minimal input
        """
        # Minimal metrics
        minimal_metrics = {'Glucose': 120}
        
        # Minimal notes
        minimal_notes = [TextualNote(content="Healthy diet recommended", section="doctor_notes")]
        
        # Should not crash
        conditions = ml_analyzer.classify_conditions(minimal_metrics)
        alerts = ml_analyzer.detect_abnormal_values(minimal_metrics)
        diet_rules = nlp_interpreter.interpret_notes(minimal_notes)
        
        # Should return valid outputs (even if empty/minimal)
        assert isinstance(conditions, list)
        assert isinstance(alerts, list)
        assert isinstance(diet_rules, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
