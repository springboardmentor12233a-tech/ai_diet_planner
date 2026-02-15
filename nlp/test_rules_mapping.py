"""
Unit tests for the rules mapping module.

Tests the enhanced rules mapping functionality including food category mapping,
priority assignment, conflict resolution, and JSON serialization.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import json
import pytest
from ai_diet_planner.nlp.rules_mapping import (
    RulesMapper,
    FOOD_CATEGORIES,
    CONDITION_RULES,
    INSTRUCTION_RULES,
    get_instruction_rule,
)
from ai_diet_planner.models import DietRule, RulePriority


class TestRulesMapper:
    """Test suite for RulesMapper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mapper = RulesMapper()
    
    def test_initialization(self):
        """Test RulesMapper initialization."""
        assert self.mapper.condition_rules == CONDITION_RULES
        assert self.mapper.instruction_rules == INSTRUCTION_RULES
        assert self.mapper.food_categories == FOOD_CATEGORIES
    
    def test_map_instruction_exact_match(self):
        """Test mapping instruction with exact match."""
        rule = self.mapper.map_instruction_to_rule("reduce sugar")
        
        assert rule is not None
        assert rule.rule_text == "Reduce sugar intake"
        assert rule.priority == RulePriority.REQUIRED
        assert "sweets" in rule.food_categories
        assert rule.action == "limit"
        assert rule.source == "rules_mapping"
    
    def test_map_instruction_case_insensitive(self):
        """Test instruction mapping is case insensitive."""
        rule1 = self.mapper.map_instruction_to_rule("REDUCE SUGAR")
        rule2 = self.mapper.map_instruction_to_rule("Reduce Sugar")
        rule3 = self.mapper.map_instruction_to_rule("reduce sugar")
        
        assert rule1 is not None
        assert rule2 is not None
        assert rule3 is not None
        assert rule1.rule_text == rule2.rule_text == rule3.rule_text
    
    def test_map_instruction_partial_match(self):
        """Test instruction mapping with partial match."""
        rule = self.mapper.map_instruction_to_rule("avoid oily foods")
        
        assert rule is not None
        assert "fats" in rule.food_categories
        assert rule.action == "exclude"
    
    def test_map_instruction_no_match(self):
        """Test instruction mapping with no match returns None."""
        rule = self.mapper.map_instruction_to_rule("eat more chocolate")
        assert rule is None
    
    def test_map_instruction_custom_source(self):
        """Test instruction mapping with custom source."""
        rule = self.mapper.map_instruction_to_rule(
            "low salt",
            source="doctor_notes"
        )
        
        assert rule is not None
        assert rule.source == "doctor_notes"
    
    def test_map_condition_diabetes(self):
        """Test mapping diabetes condition to rules."""
        rules = self.mapper.map_condition_to_rules("diabetes")
        
        assert len(rules) > 0
        assert any("sugar" in r.rule_text.lower() for r in rules)
        assert any("fiber" in r.rule_text.lower() for r in rules)
        assert any(r.priority == RulePriority.REQUIRED for r in rules)
    
    def test_map_condition_hypertension(self):
        """Test mapping hypertension condition to rules."""
        rules = self.mapper.map_condition_to_rules("hypertension")
        
        assert len(rules) > 0
        assert any("sodium" in r.rule_text.lower() for r in rules)
        assert any(r.action == "limit" for r in rules)
    
    def test_map_condition_case_insensitive(self):
        """Test condition mapping is case insensitive."""
        rules1 = self.mapper.map_condition_to_rules("DIABETES")
        rules2 = self.mapper.map_condition_to_rules("Diabetes")
        
        assert len(rules1) == len(rules2)
    
    def test_map_condition_partial_match(self):
        """Test condition mapping with partial match."""
        rules = self.mapper.map_condition_to_rules("type 2 diabetes")
        
        assert len(rules) > 0
        assert any("sugar" in r.rule_text.lower() for r in rules)
    
    def test_map_condition_no_match(self):
        """Test condition mapping with no match returns empty list."""
        rules = self.mapper.map_condition_to_rules("unknown condition")
        assert rules == []
    
    def test_identify_food_categories_single(self):
        """Test identifying single food category."""
        categories = self.mapper.identify_food_categories("avoid sugar")
        
        assert "sweets" in categories
    
    def test_identify_food_categories_multiple(self):
        """Test identifying multiple food categories."""
        categories = self.mapper.identify_food_categories(
            "reduce oil and avoid fried foods"
        )
        
        assert "fats" in categories
    
    def test_identify_food_categories_none(self):
        """Test identifying food categories with no matches."""
        categories = self.mapper.identify_food_categories("exercise daily")
        
        assert categories == []
    
    def test_identify_food_categories_duplicates(self):
        """Test that duplicate categories are removed."""
        categories = self.mapper.identify_food_categories(
            "avoid oil, butter, and fried foods"
        )
        
        # All three keywords map to "fats" category
        assert categories.count("fats") == 1
    
    def test_assign_priority_allergy(self):
        """Test priority assignment for allergies."""
        priority = self.mapper.assign_priority(
            "Patient allergic to peanuts",
            "exclude",
            is_allergy=True
        )
        
        assert priority == RulePriority.REQUIRED
    
    def test_assign_priority_exclude_action(self):
        """Test priority assignment for exclude actions."""
        priority = self.mapper.assign_priority(
            "Avoid sugar",
            "exclude",
            is_allergy=False
        )
        
        assert priority == RulePriority.REQUIRED
    
    def test_assign_priority_include_action(self):
        """Test priority assignment for include actions."""
        priority = self.mapper.assign_priority(
            "Include more vegetables",
            "include",
            is_allergy=False
        )
        
        assert priority == RulePriority.RECOMMENDED
    
    def test_assign_priority_preference(self):
        """Test priority assignment for preferences."""
        priority = self.mapper.assign_priority(
            "Prefer whole grains",
            "limit",  # Action doesn't matter when "prefer" is in text
            is_allergy=False
        )
        
        assert priority == RulePriority.OPTIONAL
    
    def test_assign_priority_critical(self):
        """Test priority assignment for critical rules."""
        priority = self.mapper.assign_priority(
            "Critical: must avoid salt",
            "exclude",
            is_allergy=False
        )
        
        assert priority == RulePriority.REQUIRED
    
    def test_resolve_conflicts_empty_list(self):
        """Test conflict resolution with empty list."""
        resolved = self.mapper.resolve_conflicts([])
        assert resolved == []
    
    def test_resolve_conflicts_no_conflicts(self):
        """Test conflict resolution with no conflicts."""
        rules = [
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="test"
            ),
            DietRule(
                rule_text="Include vegetables",
                priority=RulePriority.RECOMMENDED,
                food_categories=["vegetables"],
                action="include",
                source="test"
            ),
        ]
        
        resolved = self.mapper.resolve_conflicts(rules)
        assert len(resolved) == 2
    
    def test_resolve_conflicts_priority_hierarchy(self):
        """Test conflict resolution respects priority hierarchy."""
        rules = [
            DietRule(
                rule_text="Optional: consider reducing sugar",
                priority=RulePriority.OPTIONAL,
                food_categories=["sweets"],
                action="limit",
                source="test"
            ),
            DietRule(
                rule_text="Required: avoid all sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="exclude",
                source="test"
            ),
        ]
        
        resolved = self.mapper.resolve_conflicts(rules)
        
        # Should keep only the REQUIRED rule
        assert len(resolved) == 1
        assert resolved[0].priority == RulePriority.REQUIRED
        assert "Required" in resolved[0].rule_text
    
    def test_resolve_conflicts_action_hierarchy(self):
        """Test conflict resolution respects action hierarchy."""
        rules = [
            DietRule(
                rule_text="Include some fats",
                priority=RulePriority.RECOMMENDED,
                food_categories=["fats"],
                action="include",
                source="test"
            ),
            DietRule(
                rule_text="Exclude all fats",
                priority=RulePriority.RECOMMENDED,
                food_categories=["fats"],
                action="exclude",
                source="test"
            ),
        ]
        
        resolved = self.mapper.resolve_conflicts(rules)
        
        # Should keep the exclude rule (stronger action)
        assert len(resolved) == 1
        assert resolved[0].action == "exclude"
    
    def test_resolve_conflicts_specific_over_general(self):
        """Test specific category rules override general 'all' category."""
        rules = [
            DietRule(
                rule_text="Limit all foods",
                priority=RulePriority.RECOMMENDED,
                food_categories=["all"],
                action="limit",
                source="test"
            ),
            DietRule(
                rule_text="Include vegetables",
                priority=RulePriority.RECOMMENDED,
                food_categories=["vegetables"],
                action="include",
                source="test"
            ),
        ]
        
        resolved = self.mapper.resolve_conflicts(rules)
        
        # Should keep the specific vegetable rule
        assert any("vegetables" in r.food_categories for r in resolved)
    
    def test_resolve_conflicts_removes_duplicates(self):
        """Test conflict resolution removes duplicate rules."""
        rules = [
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="test"
            ),
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="test"
            ),
        ]
        
        resolved = self.mapper.resolve_conflicts(rules)
        assert len(resolved) == 1
    
    def test_rules_to_json(self):
        """Test converting rules to JSON format."""
        rules = [
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="test"
            ),
        ]
        
        json_str = self.mapper.rules_to_json(rules)
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert len(data) == 1
        assert data[0]["rule_text"] == "Limit sugar"
        assert data[0]["priority"] == "required"
        assert data[0]["food_categories"] == ["sweets"]
        assert data[0]["action"] == "limit"
    
    def test_json_to_rules(self):
        """Test converting JSON to rules."""
        json_str = '''[
            {
                "rule_text": "Limit sugar",
                "priority": "required",
                "food_categories": ["sweets"],
                "action": "limit",
                "source": "test"
            }
        ]'''
        
        rules = self.mapper.json_to_rules(json_str)
        
        assert len(rules) == 1
        assert rules[0].rule_text == "Limit sugar"
        assert rules[0].priority == RulePriority.REQUIRED
        assert rules[0].food_categories == ["sweets"]
        assert rules[0].action == "limit"
    
    def test_rules_json_roundtrip(self):
        """Test converting rules to JSON and back."""
        original_rules = [
            DietRule(
                rule_text="Limit sugar",
                priority=RulePriority.REQUIRED,
                food_categories=["sweets"],
                action="limit",
                source="test"
            ),
            DietRule(
                rule_text="Include vegetables",
                priority=RulePriority.RECOMMENDED,
                food_categories=["vegetables"],
                action="include",
                source="test"
            ),
        ]
        
        json_str = self.mapper.rules_to_json(original_rules)
        restored_rules = self.mapper.json_to_rules(json_str)
        
        assert len(restored_rules) == len(original_rules)
        for orig, restored in zip(original_rules, restored_rules):
            assert orig.rule_text == restored.rule_text
            assert orig.priority == restored.priority
            assert orig.food_categories == restored.food_categories
            assert orig.action == restored.action


class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_get_instruction_rule(self):
        """Test backward compatibility function."""
        rule_text = get_instruction_rule("reduce sugar")
        
        assert rule_text is not None
        assert "sugar" in rule_text.lower()
    
    def test_get_instruction_rule_no_match(self):
        """Test backward compatibility function with no match."""
        rule_text = get_instruction_rule("unknown instruction")
        assert rule_text is None


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mapper = RulesMapper()
    
    def test_diabetes_patient_scenario(self):
        """Test complete scenario for diabetes patient."""
        # Map condition to rules
        rules = self.mapper.map_condition_to_rules("type 2 diabetes")
        
        # Add instruction-based rules
        instruction_rule = self.mapper.map_instruction_to_rule("avoid sugar")
        if instruction_rule:
            rules.append(instruction_rule)
        
        # Resolve conflicts
        resolved = self.mapper.resolve_conflicts(rules)
        
        # Convert to JSON
        json_output = self.mapper.rules_to_json(resolved)
        
        assert len(resolved) > 0
        assert json_output is not None
        assert "sugar" in json_output.lower()
    
    def test_multiple_conditions_scenario(self):
        """Test scenario with multiple health conditions."""
        # Patient has both diabetes and hypertension
        diabetes_rules = self.mapper.map_condition_to_rules("diabetes")
        hypertension_rules = self.mapper.map_condition_to_rules("hypertension")
        
        all_rules = diabetes_rules + hypertension_rules
        
        # Resolve conflicts
        resolved = self.mapper.resolve_conflicts(all_rules)
        
        # Should have rules for both conditions
        assert any("sugar" in r.rule_text.lower() for r in resolved)
        assert any("sodium" in r.rule_text.lower() for r in resolved)
    
    def test_conflicting_instructions_scenario(self):
        """Test scenario with conflicting dietary instructions."""
        rules = [
            DietRule(
                rule_text="Include dairy for calcium",
                priority=RulePriority.RECOMMENDED,
                food_categories=["dairy"],
                action="include",
                source="nutritionist"
            ),
            DietRule(
                rule_text="Avoid dairy due to lactose intolerance",
                priority=RulePriority.REQUIRED,
                food_categories=["dairy"],
                action="exclude",
                source="doctor"
            ),
        ]
        
        resolved = self.mapper.resolve_conflicts(rules)
        
        # Should keep the REQUIRED exclude rule
        assert len(resolved) == 1
        assert resolved[0].action == "exclude"
        assert resolved[0].priority == RulePriority.REQUIRED
