"""
Rules Mapping Module for the AI NutriCare System.

This module provides enhanced mapping of dietary instructions to structured diet rules
with food category mapping, priority assignment, and conflict resolution.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import json
import logging
from typing import List, Dict, Optional, Set
from dataclasses import asdict

from ai_diet_planner.models import DietRule, RulePriority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Food category definitions
FOOD_CATEGORIES = {
    "proteins": ["meat", "chicken", "fish", "eggs", "beans", "lentils", "tofu", "nuts"],
    "carbs": ["rice", "bread", "pasta", "potato", "wheat", "grains", "cereals"],
    "fats": ["oil", "butter", "ghee", "cream", "fried", "fatty"],
    "dairy": ["milk", "cheese", "yogurt", "paneer", "curd"],
    "vegetables": ["vegetables", "greens", "salad", "leafy"],
    "fruits": ["fruits", "berries", "citrus"],
    "sweets": ["sugar", "candy", "dessert", "sweet", "honey", "jaggery"],
    "whole_grains": ["whole grain", "oats", "quinoa", "brown rice", "barley"],
    "fiber": ["fiber", "bran", "roughage"],
    "sodium": ["salt", "sodium", "salty"],
}


# Medical condition to diet rule mappings with priorities
CONDITION_RULES = {
    "diabetes": [
        {
            "rule_text": "Limit sugar and refined carbohydrates",
            "priority": RulePriority.REQUIRED,
            "food_categories": ["carbs", "sweets"],
            "action": "limit",
        },
        {
            "rule_text": "Include high-fiber foods",
            "priority": RulePriority.RECOMMENDED,
            "food_categories": ["fiber", "vegetables", "whole_grains"],
            "action": "include",
        },
        {
            "rule_text": "Choose complex carbohydrates over simple sugars",
            "priority": RulePriority.RECOMMENDED,
            "food_categories": ["whole_grains", "carbs"],
            "action": "include",
        },
    ],
    "hypertension": [
        {
            "rule_text": "Reduce sodium intake",
            "priority": RulePriority.REQUIRED,
            "food_categories": ["sodium"],
            "action": "limit",
        },
        {
            "rule_text": "Increase potassium-rich foods",
            "priority": RulePriority.RECOMMENDED,
            "food_categories": ["vegetables", "fruits"],
            "action": "include",
        },
    ],
    "hyperlipidemia": [
        {
            "rule_text": "Limit saturated fats and cholesterol",
            "priority": RulePriority.REQUIRED,
            "food_categories": ["fats", "dairy"],
            "action": "limit",
        },
        {
            "rule_text": "Include omega-3 fatty acids",
            "priority": RulePriority.RECOMMENDED,
            "food_categories": ["proteins"],
            "action": "include",
        },
    ],
    "obesity": [
        {
            "rule_text": "Control portion sizes and reduce caloric intake",
            "priority": RulePriority.REQUIRED,
            "food_categories": ["all"],
            "action": "limit",
        },
        {
            "rule_text": "Increase vegetable and fiber intake",
            "priority": RulePriority.RECOMMENDED,
            "food_categories": ["vegetables", "fiber"],
            "action": "include",
        },
    ],
}


# Instruction keyword to rule mappings
INSTRUCTION_RULES = {
    "reduce sugar": {
        "rule_text": "Reduce sugar intake",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["sweets", "carbs"],
        "action": "limit",
    },
    "avoid sugar": {
        "rule_text": "Avoid sugar completely",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["sweets"],
        "action": "exclude",
    },
    "low sugar": {
        "rule_text": "Follow low sugar diet",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["sweets", "carbs"],
        "action": "limit",
    },
    "avoid oily": {
        "rule_text": "Avoid oily foods",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["fats"],
        "action": "exclude",
    },
    "avoid oil": {
        "rule_text": "Avoid oil",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["fats"],
        "action": "exclude",
    },
    "reduce oil": {
        "rule_text": "Reduce oil consumption",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["fats"],
        "action": "limit",
    },
    "reduce fat": {
        "rule_text": "Reduce fat intake",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["fats"],
        "action": "limit",
    },
    "avoid fried": {
        "rule_text": "Avoid fried foods",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["fats"],
        "action": "exclude",
    },
    "low salt": {
        "rule_text": "Follow low salt diet",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["sodium"],
        "action": "limit",
    },
    "avoid salt": {
        "rule_text": "Avoid salt",
        "priority": RulePriority.REQUIRED,
        "food_categories": ["sodium"],
        "action": "exclude",
    },
    "increase fiber": {
        "rule_text": "Increase fiber intake",
        "priority": RulePriority.RECOMMENDED,
        "food_categories": ["fiber", "vegetables", "whole_grains"],
        "action": "include",
    },
    "eat vegetables": {
        "rule_text": "Increase vegetable consumption",
        "priority": RulePriority.RECOMMENDED,
        "food_categories": ["vegetables"],
        "action": "include",
    },
    "exercise": {
        "rule_text": "Regular physical activity",
        "priority": RulePriority.RECOMMENDED,
        "food_categories": [],
        "action": "include",
    },
}


class RulesMapper:
    """
    Maps dietary instructions to structured diet rules with food categories,
    priorities, and conflict resolution.
    """
    
    def __init__(self):
        """Initialize the rules mapper."""
        self.condition_rules = CONDITION_RULES
        self.instruction_rules = INSTRUCTION_RULES
        self.food_categories = FOOD_CATEGORIES
    
    def map_instruction_to_rule(
        self,
        instruction: str,
        source: str = "rules_mapping"
    ) -> Optional[DietRule]:
        """
        Map a dietary instruction to a structured DietRule.
        
        Args:
            instruction: The dietary instruction text
            source: Source of the instruction (default: "rules_mapping")
            
        Returns:
            DietRule object or None if no mapping found
        """
        instruction_lower = instruction.lower().strip()
        
        # Check for exact match in instruction rules
        if instruction_lower in self.instruction_rules:
            rule_data = self.instruction_rules[instruction_lower]
            return DietRule(
                rule_text=rule_data["rule_text"],
                priority=rule_data["priority"],
                food_categories=rule_data["food_categories"],
                action=rule_data["action"],
                source=source
            )
        
        # Check for partial matches
        for key, rule_data in self.instruction_rules.items():
            if key in instruction_lower or instruction_lower in key:
                return DietRule(
                    rule_text=rule_data["rule_text"],
                    priority=rule_data["priority"],
                    food_categories=rule_data["food_categories"],
                    action=rule_data["action"],
                    source=source
                )
        
        logger.warning(f"No mapping found for instruction: {instruction}")
        return None
    
    def map_condition_to_rules(
        self,
        condition: str,
        source: str = "rules_mapping"
    ) -> List[DietRule]:
        """
        Map a health condition to a list of diet rules.
        
        Args:
            condition: The health condition name
            source: Source of the rules (default: "rules_mapping")
            
        Returns:
            List of DietRule objects
        """
        condition_lower = condition.lower().strip()
        
        # Check for exact or partial match
        for key, rules_data in self.condition_rules.items():
            if key in condition_lower or condition_lower in key:
                diet_rules = []
                for rule_data in rules_data:
                    diet_rule = DietRule(
                        rule_text=rule_data["rule_text"],
                        priority=rule_data["priority"],
                        food_categories=rule_data["food_categories"],
                        action=rule_data["action"],
                        source=source
                    )
                    diet_rules.append(diet_rule)
                return diet_rules
        
        logger.warning(f"No mapping found for condition: {condition}")
        return []
    
    def identify_food_categories(self, text: str) -> List[str]:
        """
        Identify food categories mentioned in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified food category names
        """
        text_lower = text.lower()
        identified = []
        
        for category, keywords in self.food_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    identified.append(category)
                    break
        
        return list(set(identified))  # Remove duplicates
    
    def assign_priority(
        self,
        rule_text: str,
        action: str,
        is_allergy: bool = False
    ) -> RulePriority:
        """
        Assign priority level to a diet rule based on context.
        
        Args:
            rule_text: The rule text
            action: The action (include, exclude, limit)
            is_allergy: Whether this is an allergy-related rule
            
        Returns:
            RulePriority enum value
        """
        rule_lower = rule_text.lower()
        
        # Allergies are always REQUIRED
        if is_allergy or "allerg" in rule_lower:
            return RulePriority.REQUIRED
        
        # Medical contraindications are REQUIRED
        if action == "exclude" or "avoid" in rule_lower or "must not" in rule_lower:
            return RulePriority.REQUIRED
        
        # Strict limitations are REQUIRED
        if "critical" in rule_lower or "essential" in rule_lower or "must" in rule_lower:
            return RulePriority.REQUIRED
        
        # Recommendations are RECOMMENDED
        if action == "include" or "recommend" in rule_lower or "should" in rule_lower:
            return RulePriority.RECOMMENDED
        
        # Preferences are OPTIONAL
        if "prefer" in rule_lower or "optional" in rule_lower or "consider" in rule_lower:
            return RulePriority.OPTIONAL
        
        # Default to RECOMMENDED for limit actions
        return RulePriority.RECOMMENDED
    
    def resolve_conflicts(self, rules: List[DietRule]) -> List[DietRule]:
        """
        Resolve conflicting diet rules using medical priority hierarchies.
        
        Priority hierarchy:
        1. REQUIRED > RECOMMENDED > OPTIONAL
        2. Exclude > Limit > Include (for same category)
        3. More specific categories override general "all" category
        
        Args:
            rules: List of potentially conflicting diet rules
            
        Returns:
            List of resolved diet rules
        """
        if not rules:
            return []
        
        # Priority order for sorting
        priority_order = {
            RulePriority.REQUIRED: 0,
            RulePriority.RECOMMENDED: 1,
            RulePriority.OPTIONAL: 2
        }
        
        # Action order (exclude is strongest)
        action_order = {
            "exclude": 0,
            "limit": 1,
            "include": 2
        }
        
        # Sort rules by priority and action
        sorted_rules = sorted(
            rules,
            key=lambda r: (priority_order[r.priority], action_order.get(r.action, 3))
        )
        
        # Track conflicts by food category
        resolved = {}
        conflicts_detected = []
        
        for rule in sorted_rules:
            for category in rule.food_categories:
                conflict_key = category
                
                if conflict_key not in resolved:
                    # First rule for this category
                    resolved[conflict_key] = rule
                else:
                    # Conflict detected
                    existing_rule = resolved[conflict_key]
                    
                    # Check if new rule has higher priority
                    if priority_order[rule.priority] < priority_order[existing_rule.priority]:
                        # New rule has higher priority - replace
                        conflicts_detected.append({
                            "replaced": existing_rule.rule_text,
                            "with": rule.rule_text,
                            "reason": "higher_priority"
                        })
                        resolved[conflict_key] = rule
                    elif priority_order[rule.priority] == priority_order[existing_rule.priority]:
                        # Same priority - check action strength
                        if action_order.get(rule.action, 3) < action_order.get(existing_rule.action, 3):
                            conflicts_detected.append({
                                "replaced": existing_rule.rule_text,
                                "with": rule.rule_text,
                                "reason": "stronger_action"
                            })
                            resolved[conflict_key] = rule
        
        # Log conflicts
        if conflicts_detected:
            logger.info(f"Resolved {len(conflicts_detected)} conflicts:")
            for conflict in conflicts_detected:
                logger.info(
                    f"  - '{conflict['with']}' overrides '{conflict['replaced']}' "
                    f"({conflict['reason']})"
                )
        
        # Handle "all" category rules
        # If there's a specific category rule, it overrides "all" category
        final_rules = []
        all_category_rules = []
        specific_categories = set()
        
        for rule in resolved.values():
            if "all" in rule.food_categories:
                all_category_rules.append(rule)
            else:
                specific_categories.update(rule.food_categories)
                final_rules.append(rule)
        
        # Add "all" category rules only if they don't conflict with specific ones
        for all_rule in all_category_rules:
            # Check if this rule's action conflicts with any specific category
            has_conflict = False
            for category in specific_categories:
                if category in resolved and resolved[category] != all_rule:
                    # There's a specific rule for this category
                    has_conflict = True
                    break
            
            if not has_conflict:
                final_rules.append(all_rule)
        
        # Remove duplicates based on rule_text
        unique_rules = []
        seen_texts = set()
        for rule in final_rules:
            if rule.rule_text not in seen_texts:
                seen_texts.add(rule.rule_text)
                unique_rules.append(rule)
        
        return unique_rules
    
    def rules_to_json(self, rules: List[DietRule]) -> str:
        """
        Convert list of DietRule objects to JSON format.
        
        Args:
            rules: List of DietRule objects
            
        Returns:
            JSON string representation
        """
        rules_data = []
        for rule in rules:
            rule_dict = asdict(rule)
            # Convert enum to string
            rule_dict["priority"] = rule.priority.value
            rules_data.append(rule_dict)
        
        return json.dumps(rules_data, indent=2)
    
    def json_to_rules(self, json_str: str) -> List[DietRule]:
        """
        Convert JSON string to list of DietRule objects.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            List of DietRule objects
        """
        rules_data = json.loads(json_str)
        rules = []
        
        for rule_data in rules_data:
            # Convert string priority back to enum
            priority_str = rule_data["priority"].upper()
            priority = RulePriority[priority_str]
            
            rule = DietRule(
                rule_text=rule_data["rule_text"],
                priority=priority,
                food_categories=rule_data["food_categories"],
                action=rule_data["action"],
                source=rule_data["source"]
            )
            rules.append(rule)
        
        return rules


# Convenience functions for backward compatibility
def get_instruction_rule(instruction: str) -> Optional[str]:
    """
    Get simple rule text for an instruction (backward compatibility).
    
    Args:
        instruction: Dietary instruction
        
    Returns:
        Rule text or None
    """
    mapper = RulesMapper()
    rule = mapper.map_instruction_to_rule(instruction)
    return rule.rule_text if rule else None
