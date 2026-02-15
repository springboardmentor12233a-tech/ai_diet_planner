"""
Example usage of the enhanced rules mapping module.

This script demonstrates how to use the RulesMapper class to:
1. Map dietary instructions to structured rules
2. Map health conditions to diet rules
3. Identify food categories
4. Assign priorities
5. Resolve conflicts
6. Convert to/from JSON format
"""

from ai_diet_planner.nlp.rules_mapping import RulesMapper
from ai_diet_planner.models import DietRule, RulePriority


def example_basic_instruction_mapping():
    """Example: Map basic dietary instructions to rules."""
    print("=" * 60)
    print("Example 1: Basic Instruction Mapping")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    instructions = [
        "reduce sugar",
        "avoid oily",
        "low salt",
        "increase fiber",
    ]
    
    for instruction in instructions:
        rule = mapper.map_instruction_to_rule(instruction)
        if rule:
            print(f"\nInstruction: '{instruction}'")
            print(f"  Rule: {rule.rule_text}")
            print(f"  Priority: {rule.priority.value}")
            print(f"  Categories: {', '.join(rule.food_categories)}")
            print(f"  Action: {rule.action}")


def example_condition_mapping():
    """Example: Map health conditions to diet rules."""
    print("\n" + "=" * 60)
    print("Example 2: Health Condition Mapping")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    conditions = ["diabetes", "hypertension", "obesity"]
    
    for condition in conditions:
        rules = mapper.map_condition_to_rules(condition)
        print(f"\nCondition: {condition}")
        print(f"Generated {len(rules)} rules:")
        for i, rule in enumerate(rules, 1):
            print(f"  {i}. {rule.rule_text} [{rule.priority.value}]")


def example_food_category_identification():
    """Example: Identify food categories in text."""
    print("\n" + "=" * 60)
    print("Example 3: Food Category Identification")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    texts = [
        "Avoid sugar and fried foods",
        "Include more vegetables and fruits",
        "Reduce salt and oil intake",
        "Eat whole grains and fiber-rich foods",
    ]
    
    for text in texts:
        categories = mapper.identify_food_categories(text)
        print(f"\nText: '{text}'")
        print(f"  Categories: {', '.join(categories) if categories else 'None'}")


def example_priority_assignment():
    """Example: Assign priorities to rules."""
    print("\n" + "=" * 60)
    print("Example 4: Priority Assignment")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    scenarios = [
        ("Patient allergic to peanuts", "exclude", True),
        ("Avoid sugar completely", "exclude", False),
        ("Include more vegetables", "include", False),
        ("Prefer whole grains", "include", False),
        ("Critical: must avoid salt", "exclude", False),
    ]
    
    for rule_text, action, is_allergy in scenarios:
        priority = mapper.assign_priority(rule_text, action, is_allergy)
        print(f"\nRule: '{rule_text}'")
        print(f"  Action: {action}")
        print(f"  Is Allergy: {is_allergy}")
        print(f"  Assigned Priority: {priority.value}")


def example_conflict_resolution():
    """Example: Resolve conflicting diet rules."""
    print("\n" + "=" * 60)
    print("Example 5: Conflict Resolution")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    # Create conflicting rules
    rules = [
        DietRule(
            rule_text="Optional: consider reducing sugar",
            priority=RulePriority.OPTIONAL,
            food_categories=["sweets"],
            action="limit",
            source="preference"
        ),
        DietRule(
            rule_text="Required: avoid all sugar due to diabetes",
            priority=RulePriority.REQUIRED,
            food_categories=["sweets"],
            action="exclude",
            source="medical"
        ),
        DietRule(
            rule_text="Include some healthy fats",
            priority=RulePriority.RECOMMENDED,
            food_categories=["fats"],
            action="include",
            source="nutritionist"
        ),
        DietRule(
            rule_text="Exclude all fats due to hyperlipidemia",
            priority=RulePriority.REQUIRED,
            food_categories=["fats"],
            action="exclude",
            source="doctor"
        ),
    ]
    
    print("\nOriginal rules:")
    for i, rule in enumerate(rules, 1):
        print(f"  {i}. {rule.rule_text} [{rule.priority.value}]")
    
    resolved = mapper.resolve_conflicts(rules)
    
    print(f"\nResolved rules ({len(resolved)} rules):")
    for i, rule in enumerate(resolved, 1):
        print(f"  {i}. {rule.rule_text} [{rule.priority.value}]")


def example_json_conversion():
    """Example: Convert rules to/from JSON."""
    print("\n" + "=" * 60)
    print("Example 6: JSON Conversion")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    # Create some rules
    rules = [
        DietRule(
            rule_text="Limit sugar intake for diabetes management",
            priority=RulePriority.REQUIRED,
            food_categories=["sweets", "carbs"],
            action="limit",
            source="medical"
        ),
        DietRule(
            rule_text="Include high-fiber foods",
            priority=RulePriority.RECOMMENDED,
            food_categories=["fiber", "vegetables", "whole_grains"],
            action="include",
            source="nutritionist"
        ),
    ]
    
    # Convert to JSON
    json_output = mapper.rules_to_json(rules)
    print("\nRules as JSON:")
    print(json_output)
    
    # Convert back to rules
    restored_rules = mapper.json_to_rules(json_output)
    print(f"\nRestored {len(restored_rules)} rules from JSON:")
    for i, rule in enumerate(restored_rules, 1):
        print(f"  {i}. {rule.rule_text} [{rule.priority.value}]")


def example_complete_workflow():
    """Example: Complete workflow for a patient."""
    print("\n" + "=" * 60)
    print("Example 7: Complete Workflow")
    print("=" * 60)
    
    mapper = RulesMapper()
    
    # Patient has diabetes and hypertension
    print("\nPatient Profile:")
    print("  Conditions: Type 2 Diabetes, Hypertension")
    print("  Doctor's Instructions: 'avoid sugar', 'low salt'")
    
    # Get rules from conditions
    diabetes_rules = mapper.map_condition_to_rules("type 2 diabetes")
    hypertension_rules = mapper.map_condition_to_rules("hypertension")
    
    # Get rules from instructions
    sugar_rule = mapper.map_instruction_to_rule("avoid sugar")
    salt_rule = mapper.map_instruction_to_rule("low salt")
    
    # Combine all rules
    all_rules = diabetes_rules + hypertension_rules
    if sugar_rule:
        all_rules.append(sugar_rule)
    if salt_rule:
        all_rules.append(salt_rule)
    
    print(f"\nTotal rules before conflict resolution: {len(all_rules)}")
    
    # Resolve conflicts
    resolved_rules = mapper.resolve_conflicts(all_rules)
    
    print(f"Total rules after conflict resolution: {len(resolved_rules)}")
    print("\nFinal Diet Rules:")
    for i, rule in enumerate(resolved_rules, 1):
        print(f"  {i}. [{rule.priority.value.upper()}] {rule.rule_text}")
        print(f"     Categories: {', '.join(rule.food_categories)}")
        print(f"     Action: {rule.action}")
    
    # Export to JSON
    json_output = mapper.rules_to_json(resolved_rules)
    print("\nExported to JSON format (ready for diet plan generator)")
    print(f"JSON length: {len(json_output)} characters")


if __name__ == "__main__":
    # Run all examples
    example_basic_instruction_mapping()
    example_condition_mapping()
    example_food_category_identification()
    example_priority_assignment()
    example_conflict_resolution()
    example_json_conversion()
    example_complete_workflow()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
