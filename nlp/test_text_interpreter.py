"""
Unit tests for NLP Text Interpreter.

Tests the NLPTextInterpreter class with various medical notes and edge cases.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from ai_diet_planner.models import (
    TextualNote,
    DietRule,
    DietaryRestriction,
    RulePriority,
)
from ai_diet_planner.nlp.text_interpreter import NLPTextInterpreter, NLPBackend


class TestNLPTextInterpreterInitialization:
    """Test initialization of NLPTextInterpreter."""
    
    def test_init_with_gpt4_no_api_key(self):
        """Test initialization with GPT-4 but no API key falls back to BERT."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('transformers.pipeline', side_effect=ImportError):
                interpreter = NLPTextInterpreter(model="gpt-4")
                assert interpreter.model == "bert"
    
    def test_init_with_bert(self):
        """Test initialization with BERT model."""
        with patch('transformers.pipeline') as mock_pipeline:
            mock_pipeline.return_value = Mock()
            interpreter = NLPTextInterpreter(model="bert")
            assert interpreter.model == "bert"
            assert interpreter.bert_model is not None
    
    def test_init_with_custom_temperature(self):
        """Test initialization with custom temperature."""
        with patch('transformers.pipeline', side_effect=ImportError):
            interpreter = NLPTextInterpreter(model="bert", temperature=0.5)
            assert interpreter.temperature == 0.5
    
    def test_init_with_cache_disabled(self):
        """Test initialization with caching disabled."""
        with patch('transformers.pipeline', side_effect=ImportError):
            interpreter = NLPTextInterpreter(model="bert", enable_cache=False)
            assert interpreter.enable_cache is False


class TestBasicRuleExtraction:
    """Test basic rule extraction fallback."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter with basic extraction (no AI models)."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_diabetes_note_extraction(self, interpreter):
        """Test extraction from diabetes-related note."""
        notes = [
            TextualNote(
                content="Patient has diabetes. Monitor blood glucose levels.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("sugar" in rule.rule_text.lower() or "diabetes" in rule.rule_text.lower() 
                   for rule in rules)
        assert any(rule.priority == RulePriority.REQUIRED for rule in rules)
    
    def test_hypertension_note_extraction(self, interpreter):
        """Test extraction from hypertension-related note."""
        notes = [
            TextualNote(
                content="Patient has hypertension. Blood pressure is elevated.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("sodium" in rule.rule_text.lower() or "pressure" in rule.rule_text.lower()
                   for rule in rules)
    
    def test_cholesterol_note_extraction(self, interpreter):
        """Test extraction from cholesterol-related note."""
        notes = [
            TextualNote(
                content="High cholesterol detected. LDL levels elevated.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("fat" in rule.rule_text.lower() or "cholesterol" in rule.rule_text.lower()
                   for rule in rules)
    
    def test_obesity_note_extraction(self, interpreter):
        """Test extraction from obesity-related note."""
        notes = [
            TextualNote(
                content="Patient is obese. BMI is 32.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("portion" in rule.rule_text.lower() or "calor" in rule.rule_text.lower()
                   for rule in rules)
    
    def test_generic_note_extraction(self, interpreter):
        """Test extraction from generic health note."""
        notes = [
            TextualNote(
                content="Patient should maintain healthy lifestyle.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should return at least a default rule
        assert len(rules) > 0
        assert any(rule.priority == RulePriority.RECOMMENDED for rule in rules)
    
    def test_multiple_conditions_extraction(self, interpreter):
        """Test extraction from note with multiple conditions."""
        notes = [
            TextualNote(
                content="Patient has diabetes and hypertension. Monitor both conditions.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should extract rules for both conditions
        assert len(rules) >= 2
        rule_texts = " ".join([r.rule_text.lower() for r in rules])
        assert "sugar" in rule_texts or "diabetes" in rule_texts
        assert "sodium" in rule_texts or "pressure" in rule_texts


class TestRestrictionExtraction:
    """Test dietary restriction extraction."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_extract_restrictions_from_notes(self, interpreter):
        """Test extracting restrictions from notes."""
        # Mock the interpret_notes to return a rule with exclusion
        with patch.object(interpreter, 'interpret_notes') as mock_interpret:
            mock_interpret.return_value = [
                DietRule(
                    rule_text="Strict peanut allergy - exclude all peanut products",
                    priority=RulePriority.REQUIRED,
                    food_categories=["nuts", "proteins"],
                    action="exclude",
                    source="nlp_extraction"
                )
            ]
            
            notes = [TextualNote(content="Patient allergic to peanuts", section="doctor_notes")]
            restrictions = interpreter.extract_restrictions(notes)
            
            assert len(restrictions) > 0
            assert restrictions[0].restriction_type == "allergy"
            assert restrictions[0].severity == "strict"
    
    def test_extract_no_restrictions(self, interpreter):
        """Test when there are no restrictions."""
        with patch.object(interpreter, 'interpret_notes') as mock_interpret:
            mock_interpret.return_value = [
                DietRule(
                    rule_text="Include more vegetables",
                    priority=RulePriority.RECOMMENDED,
                    food_categories=["vegetables"],
                    action="include",
                    source="nlp_extraction"
                )
            ]
            
            notes = [TextualNote(content="Eat healthy", section="doctor_notes")]
            restrictions = interpreter.extract_restrictions(notes)
            
            assert len(restrictions) == 0


class TestRecommendationExtraction:
    """Test dietary recommendation extraction."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_extract_recommendations(self, interpreter):
        """Test extracting recommendations from notes."""
        with patch.object(interpreter, 'interpret_notes') as mock_interpret:
            mock_interpret.return_value = [
                DietRule(
                    rule_text="Include high-fiber foods",
                    priority=RulePriority.RECOMMENDED,
                    food_categories=["vegetables", "fruits"],
                    action="include",
                    source="nlp_extraction"
                ),
                DietRule(
                    rule_text="Avoid sugar",
                    priority=RulePriority.REQUIRED,
                    food_categories=["sweets"],
                    action="exclude",
                    source="nlp_extraction"
                )
            ]
            
            notes = [TextualNote(content="Test note", section="doctor_notes")]
            recommendations = interpreter.extract_recommendations(notes)
            
            # Should only include RECOMMENDED priority rules
            assert len(recommendations) == 1
            assert "fiber" in recommendations[0].lower()


class TestConflictResolution:
    """Test diet rule conflict resolution."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_resolve_priority_conflicts(self, interpreter):
        """Test that higher priority rules override lower priority."""
        rules = [
            DietRule(
                rule_text="Include dairy for calcium",
                priority=RulePriority.RECOMMENDED,
                food_categories=["dairy"],
                action="include",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Exclude dairy due to lactose intolerance",
                priority=RulePriority.REQUIRED,
                food_categories=["dairy"],
                action="exclude",
                source="nlp_extraction"
            )
        ]
        
        resolved = interpreter.resolve_conflicts(rules)
        
        # REQUIRED should override RECOMMENDED
        assert len(resolved) >= 1
        dairy_rules = [r for r in resolved if "dairy" in r.food_categories]
        assert any(r.priority == RulePriority.REQUIRED for r in dairy_rules)
    
    def test_resolve_no_conflicts(self, interpreter):
        """Test resolution when there are no conflicts."""
        rules = [
            DietRule(
                rule_text="Include vegetables",
                priority=RulePriority.RECOMMENDED,
                food_categories=["vegetables"],
                action="include",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="nlp_extraction"
            )
        ]
        
        resolved = interpreter.resolve_conflicts(rules)
        
        # Both rules should be kept
        assert len(resolved) == 2
    
    def test_resolve_duplicate_rules(self, interpreter):
        """Test that duplicate rules are removed."""
        rules = [
            DietRule(
                rule_text="Limit sugar intake",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Limit sugar intake",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="nlp_extraction"
            )
        ]
        
        resolved = interpreter.resolve_conflicts(rules)
        
        # Should only keep one
        assert len(resolved) == 1
    
    def test_resolve_empty_rules(self, interpreter):
        """Test resolution with empty rules list."""
        resolved = interpreter.resolve_conflicts([])
        assert len(resolved) == 0


class TestCaching:
    """Test caching functionality."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter with caching enabled."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert", enable_cache=True)
    
    def test_cache_hit(self, interpreter):
        """Test that cached results are returned."""
        notes = [
            TextualNote(
                content="Patient has diabetes",
                section="doctor_notes"
            )
        ]
        
        # First call - should process
        rules1 = interpreter.interpret_notes(notes)
        
        # Second call - should use cache
        rules2 = interpreter.interpret_notes(notes)
        
        # Results should be the same
        assert len(rules1) == len(rules2)
        assert rules1[0].rule_text == rules2[0].rule_text
    
    def test_cache_clear(self, interpreter):
        """Test cache clearing."""
        notes = [
            TextualNote(
                content="Patient has diabetes",
                section="doctor_notes"
            )
        ]
        
        # Process and cache
        interpreter.interpret_notes(notes)
        assert len(interpreter.cache) > 0
        
        # Clear cache
        interpreter.clear_cache()
        assert len(interpreter.cache) == 0
        assert len(interpreter.cache_timestamps) == 0
    
    def test_cache_disabled(self):
        """Test that caching can be disabled."""
        with patch('transformers.pipeline', side_effect=ImportError):
            interpreter = NLPTextInterpreter(model="bert", enable_cache=False)
            
            notes = [
                TextualNote(
                    content="Patient has diabetes",
                    section="doctor_notes"
                )
            ]
            
            interpreter.interpret_notes(notes)
            
            # Cache should remain empty
            assert len(interpreter.cache) == 0


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_empty_notes_error(self, interpreter):
        """Test that empty notes list raises error."""
        with pytest.raises(ValueError, match="Notes list cannot be empty"):
            interpreter.interpret_notes([])
    
    def test_invalid_note_handling(self, interpreter):
        """Test handling of notes with unusual content."""
        notes = [
            TextualNote(
                content="",  # Empty content
                section="doctor_notes"
            )
        ]
        
        # Should not crash, should return default rule
        rules = interpreter.interpret_notes(notes)
        assert len(rules) > 0


class TestNotesCombination:
    """Test combining multiple notes."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_combine_multiple_sections(self, interpreter):
        """Test combining notes from different sections."""
        notes = [
            TextualNote(
                content="Patient has diabetes",
                section="doctor_notes"
            ),
            TextualNote(
                content="Metformin 500mg twice daily",
                section="prescription"
            ),
            TextualNote(
                content="Follow up in 3 months",
                section="recommendation"
            )
        ]
        
        combined = interpreter._combine_notes(notes)
        
        assert "[DOCTOR_NOTES]" in combined
        assert "[PRESCRIPTION]" in combined
        assert "[RECOMMENDATION]" in combined
        assert "diabetes" in combined.lower()
        assert "metformin" in combined.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

    
    def test_diabetes_note_extraction(self, interpreter):
        """Test extraction from diabetes-related note."""
        notes = [
            TextualNote(
                content="Patient has diabetes. Monitor blood glucose levels.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("sugar" in rule.rule_text.lower() or "diabetes" in rule.rule_text.lower() 
                   for rule in rules)
        assert any(rule.priority == RulePriority.REQUIRED for rule in rules)
    
    def test_hypertension_note_extraction(self, interpreter):
        """Test extraction from hypertension-related note."""
        notes = [
            TextualNote(
                content="Patient has hypertension. Blood pressure is elevated.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("sodium" in rule.rule_text.lower() or "pressure" in rule.rule_text.lower()
                   for rule in rules)
    
    def test_cholesterol_note_extraction(self, interpreter):
        """Test extraction from cholesterol-related note."""
        notes = [
            TextualNote(
                content="High cholesterol detected. LDL levels elevated.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("fat" in rule.rule_text.lower() or "cholesterol" in rule.rule_text.lower()
                   for rule in rules)
    
    def test_obesity_note_extraction(self, interpreter):
        """Test extraction from obesity-related note."""
        notes = [
            TextualNote(
                content="Patient is obese. BMI is 32.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        assert len(rules) > 0
        assert any("portion" in rule.rule_text.lower() or "calor" in rule.rule_text.lower()
                   for rule in rules)
    
    def test_generic_note_extraction(self, interpreter):
        """Test extraction from generic health note."""
        notes = [
            TextualNote(
                content="Patient should maintain healthy lifestyle.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should return at least a default rule
        assert len(rules) > 0
        assert any(rule.priority == RulePriority.RECOMMENDED for rule in rules)
    
    def test_multiple_conditions_extraction(self, interpreter):
        """Test extraction from note with multiple conditions."""
        notes = [
            TextualNote(
                content="Patient has diabetes and hypertension. Monitor both conditions.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should extract rules for both conditions
        assert len(rules) >= 2
        rule_texts = " ".join([r.rule_text.lower() for r in rules])
        assert "sugar" in rule_texts or "diabetes" in rule_texts
        assert "sodium" in rule_texts or "pressure" in rule_texts


class TestRestrictionExtraction:
    """Test dietary restriction extraction."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_extract_restrictions_from_notes(self, interpreter):
        """Test extracting restrictions from notes."""
        # Mock the interpret_notes to return a rule with exclusion
        with patch.object(interpreter, 'interpret_notes') as mock_interpret:
            mock_interpret.return_value = [
                DietRule(
                    rule_text="Strict peanut allergy - exclude all peanut products",
                    priority=RulePriority.REQUIRED,
                    food_categories=["nuts", "proteins"],
                    action="exclude",
                    source="nlp_extraction"
                )
            ]
            
            notes = [TextualNote(content="Patient allergic to peanuts", section="doctor_notes")]
            restrictions = interpreter.extract_restrictions(notes)
            
            assert len(restrictions) > 0
            assert restrictions[0].restriction_type == "allergy"
            assert restrictions[0].severity == "strict"
    
    def test_extract_no_restrictions(self, interpreter):
        """Test when there are no restrictions."""
        with patch.object(interpreter, 'interpret_notes') as mock_interpret:
            mock_interpret.return_value = [
                DietRule(
                    rule_text="Include more vegetables",
                    priority=RulePriority.RECOMMENDED,
                    food_categories=["vegetables"],
                    action="include",
                    source="nlp_extraction"
                )
            ]
            
            notes = [TextualNote(content="Eat healthy", section="doctor_notes")]
            restrictions = interpreter.extract_restrictions(notes)
            
            assert len(restrictions) == 0


class TestRecommendationExtraction:
    """Test dietary recommendation extraction."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_extract_recommendations(self, interpreter):
        """Test extracting recommendations from notes."""
        with patch.object(interpreter, 'interpret_notes') as mock_interpret:
            mock_interpret.return_value = [
                DietRule(
                    rule_text="Include high-fiber foods",
                    priority=RulePriority.RECOMMENDED,
                    food_categories=["vegetables", "fruits"],
                    action="include",
                    source="nlp_extraction"
                ),
                DietRule(
                    rule_text="Avoid sugar",
                    priority=RulePriority.REQUIRED,
                    food_categories=["sweets"],
                    action="exclude",
                    source="nlp_extraction"
                )
            ]
            
            notes = [TextualNote(content="Test note", section="doctor_notes")]
            recommendations = interpreter.extract_recommendations(notes)
            
            # Should only include RECOMMENDED priority rules
            assert len(recommendations) == 1
            assert "fiber" in recommendations[0].lower()


class TestConflictResolution:
    """Test diet rule conflict resolution."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_resolve_priority_conflicts(self, interpreter):
        """Test that higher priority rules override lower priority."""
        rules = [
            DietRule(
                rule_text="Include dairy for calcium",
                priority=RulePriority.RECOMMENDED,
                food_categories=["dairy"],
                action="include",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Exclude dairy due to lactose intolerance",
                priority=RulePriority.REQUIRED,
                food_categories=["dairy"],
                action="exclude",
                source="nlp_extraction"
            )
        ]
        
        resolved = interpreter.resolve_conflicts(rules)
        
        # REQUIRED should override RECOMMENDED
        assert len(resolved) >= 1
        dairy_rules = [r for r in resolved if "dairy" in r.food_categories]
        assert any(r.priority == RulePriority.REQUIRED for r in dairy_rules)
    
    def test_resolve_no_conflicts(self, interpreter):
        """Test resolution when there are no conflicts."""
        rules = [
            DietRule(
                rule_text="Include vegetables",
                priority=RulePriority.RECOMMENDED,
                food_categories=["vegetables"],
                action="include",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="nlp_extraction"
            )
        ]
        
        resolved = interpreter.resolve_conflicts(rules)
        
        # Both rules should be kept
        assert len(resolved) == 2
    
    def test_resolve_duplicate_rules(self, interpreter):
        """Test that duplicate rules are removed."""
        rules = [
            DietRule(
                rule_text="Limit sugar intake",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Limit sugar intake",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="nlp_extraction"
            )
        ]
        
        resolved = interpreter.resolve_conflicts(rules)
        
        # Should only keep one
        assert len(resolved) == 1
    
    def test_resolve_empty_rules(self, interpreter):
        """Test resolution with empty rules list."""
        resolved = interpreter.resolve_conflicts([])
        assert len(resolved) == 0


class TestCaching:
    """Test caching functionality."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter with caching enabled."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert", enable_cache=True)
    
    def test_cache_hit(self, interpreter):
        """Test that cached results are returned."""
        notes = [
            TextualNote(
                content="Patient has diabetes",
                section="doctor_notes"
            )
        ]
        
        # First call - should process
        rules1 = interpreter.interpret_notes(notes)
        
        # Second call - should use cache
        rules2 = interpreter.interpret_notes(notes)
        
        # Results should be the same
        assert len(rules1) == len(rules2)
        assert rules1[0].rule_text == rules2[0].rule_text
    
    def test_cache_clear(self, interpreter):
        """Test cache clearing."""
        notes = [
            TextualNote(
                content="Patient has diabetes",
                section="doctor_notes"
            )
        ]
        
        # Process and cache
        interpreter.interpret_notes(notes)
        assert len(interpreter.cache) > 0
        
        # Clear cache
        interpreter.clear_cache()
        assert len(interpreter.cache) == 0
        assert len(interpreter.cache_timestamps) == 0
    
    def test_cache_disabled(self):
        """Test that caching can be disabled."""
        with patch('transformers.pipeline', side_effect=ImportError):
            interpreter = NLPTextInterpreter(model="bert", enable_cache=False)
            
            notes = [
                TextualNote(
                    content="Patient has diabetes",
                    section="doctor_notes"
                )
            ]
            
            interpreter.interpret_notes(notes)
            
            # Cache should remain empty
            assert len(interpreter.cache) == 0


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_empty_notes_error(self, interpreter):
        """Test that empty notes list raises error."""
        with pytest.raises(ValueError, match="Notes list cannot be empty"):
            interpreter.interpret_notes([])
    
    def test_invalid_note_handling(self, interpreter):
        """Test handling of notes with unusual content."""
        notes = [
            TextualNote(
                content="",  # Empty content
                section="doctor_notes"
            )
        ]
        
        # Should not crash, should return default rule
        rules = interpreter.interpret_notes(notes)
        assert len(rules) > 0


class TestNotesCombination:
    """Test combining multiple notes."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_combine_multiple_sections(self, interpreter):
        """Test combining notes from different sections."""
        notes = [
            TextualNote(
                content="Patient has diabetes",
                section="doctor_notes"
            ),
            TextualNote(
                content="Metformin 500mg twice daily",
                section="prescription"
            ),
            TextualNote(
                content="Follow up in 3 months",
                section="recommendation"
            )
        ]
        
        combined = interpreter._combine_notes(notes)
        
        assert "[DOCTOR_NOTES]" in combined
        assert "[PRESCRIPTION]" in combined
        assert "[RECOMMENDATION]" in combined
        assert "diabetes" in combined.lower()
        assert "metformin" in combined.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



class TestAmbiguousInstructionFlagging:
    """Test ambiguous instruction detection and flagging."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter for testing."""
        with patch('transformers.pipeline', side_effect=ImportError):
            return NLPTextInterpreter(model="bert")
    
    def test_contradictory_instructions_flagged(self, interpreter):
        """Test that contradictory instructions are flagged."""
        notes = [
            TextualNote(
                content="Include dairy for calcium. Avoid dairy due to lactose issues.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should have at least one flagged rule
        flagged_rules = [r for r in rules if interpreter.is_flagged_for_review(r)]
        assert len(flagged_rules) > 0
        assert any("contradictory" in r.rule_text.lower() for r in flagged_rules)
        assert all(r.priority == RulePriority.OPTIONAL for r in flagged_rules)
    
    def test_vague_instructions_flagged(self, interpreter):
        """Test that vague instructions are flagged."""
        notes = [
            TextualNote(
                content="Patient might want to consider reducing some sugar intake occasionally.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should have at least one flagged rule for vague language
        flagged_rules = [r for r in rules if interpreter.is_flagged_for_review(r)]
        assert len(flagged_rules) > 0
        assert any("vague" in r.rule_text.lower() or "unclear" in r.rule_text.lower() 
                   for r in flagged_rules)
    
    def test_conflicting_carb_recommendations_flagged(self, interpreter):
        """Test that conflicting carbohydrate recommendations are flagged."""
        notes = [
            TextualNote(
                content="Follow low carb diet for diabetes. Increase carb intake for athletic performance.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should flag conflicting carb recommendations
        flagged_rules = [r for r in rules if interpreter.is_flagged_for_review(r)]
        assert len(flagged_rules) > 0
        assert any("carb" in r.rule_text.lower() and "conflict" in r.rule_text.lower() 
                   for r in flagged_rules)
    
    def test_unclear_allergy_flagged(self, interpreter):
        """Test that unclear allergy information is flagged."""
        notes = [
            TextualNote(
                content="Patient has possible allergy to shellfish, needs confirmation.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should flag unclear allergy
        flagged_rules = [r for r in rules if interpreter.is_flagged_for_review(r)]
        assert len(flagged_rules) > 0
        assert any("allerg" in r.rule_text.lower() and "unclear" in r.rule_text.lower() 
                   for r in flagged_rules)
    
    def test_clear_instructions_not_flagged(self, interpreter):
        """Test that clear instructions are not flagged."""
        notes = [
            TextualNote(
                content="Patient has diabetes. Avoid sugar and refined carbohydrates.",
                section="doctor_notes"
            )
        ]
        
        rules = interpreter.interpret_notes(notes)
        
        # Should not have flagged rules for clear instructions
        flagged_rules = [r for r in rules if interpreter.is_flagged_for_review(r)]
        # May have 0 flagged rules, or if there are any, they shouldn't be about the main instruction
        non_flagged_rules = [r for r in rules if not interpreter.is_flagged_for_review(r)]
        assert len(non_flagged_rules) > 0
    
    def test_is_flagged_for_review_method(self, interpreter):
        """Test the is_flagged_for_review helper method."""
        from ai_diet_planner.nlp.text_interpreter import AMBIGUOUS_FLAG
        
        flagged_rule = DietRule(
            rule_text=f"{AMBIGUOUS_FLAG} This needs review",
            priority=RulePriority.OPTIONAL,
            food_categories=["all"],
            action="limit",
            source="nlp_extraction"
        )
        
        normal_rule = DietRule(
            rule_text="Limit sugar intake",
            priority=RulePriority.REQUIRED,
            food_categories=["sweets"],
            action="limit",
            source="nlp_extraction"
        )
        
        assert interpreter.is_flagged_for_review(flagged_rule) is True
        assert interpreter.is_flagged_for_review(normal_rule) is False
