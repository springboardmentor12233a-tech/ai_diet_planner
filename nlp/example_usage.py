"""
Example usage of NLP Text Interpreter.

This script demonstrates how to use the NLPTextInterpreter to extract
diet rules from doctor notes and prescriptions.
"""

import os
from datetime import datetime

from ai_diet_planner.models import TextualNote
from ai_diet_planner.nlp import NLPTextInterpreter


def example_basic_usage():
    """Basic usage example with simple doctor notes."""
    print("=" * 60)
    print("Example 1: Basic Usage with Diabetes Note")
    print("=" * 60)
    
    # Create sample doctor notes
    notes = [
        TextualNote(
            content="Patient diagnosed with Type 2 diabetes. Blood glucose levels elevated at 180 mg/dL. "
                   "Recommend limiting sugar intake and refined carbohydrates. "
                   "Increase fiber intake through vegetables and whole grains.",
            section="doctor_notes"
        )
    ]
    
    # Initialize interpreter (will use BERT fallback if no OpenAI key)
    interpreter = NLPTextInterpreter(model="gpt-4")
    
    # Extract diet rules
    diet_rules = interpreter.interpret_notes(notes)
    
    print(f"\nExtracted {len(diet_rules)} diet rules:\n")
    for i, rule in enumerate(diet_rules, 1):
        print(f"{i}. {rule.rule_text}")
        print(f"   Priority: {rule.priority.value}")
        print(f"   Action: {rule.action}")
        print(f"   Categories: {', '.join(rule.food_categories)}")
        print()


def example_multiple_conditions():
    """Example with multiple health conditions."""
    print("=" * 60)
    print("Example 2: Multiple Health Conditions")
    print("=" * 60)
    
    notes = [
        TextualNote(
            content="Patient has hypertension (BP 150/95) and hyperlipidemia (LDL 160 mg/dL). "
                   "Reduce sodium intake to less than 2000mg per day. "
                   "Avoid saturated fats and fried foods. "
                   "Include omega-3 rich foods like fish.",
            section="doctor_notes"
        )
    ]
    
    interpreter = NLPTextInterpreter(model="gpt-4")
    diet_rules = interpreter.interpret_notes(notes)
    
    print(f"\nExtracted {len(diet_rules)} diet rules:\n")
    for i, rule in enumerate(diet_rules, 1):
        print(f"{i}. {rule.rule_text}")
        print(f"   Priority: {rule.priority.value}")
        print()


def example_with_allergies():
    """Example with food allergies."""
    print("=" * 60)
    print("Example 3: Food Allergies and Restrictions")
    print("=" * 60)
    
    notes = [
        TextualNote(
            content="Patient reports severe peanut allergy. History of anaphylaxis. "
                   "Strictly avoid all peanut products and foods processed in facilities with peanuts.",
            section="doctor_notes"
        ),
        TextualNote(
            content="EpiPen prescribed for emergency use.",
            section="prescription"
        )
    ]
    
    interpreter = NLPTextInterpreter(model="gpt-4")
    
    # Extract restrictions
    restrictions = interpreter.extract_restrictions(notes)
    
    print(f"\nExtracted {len(restrictions)} dietary restrictions:\n")
    for i, restriction in enumerate(restrictions, 1):
        print(f"{i}. Type: {restriction.restriction_type}")
        print(f"   Severity: {restriction.severity}")
        print(f"   Restricted items: {', '.join(restriction.restricted_items)}")
        print()


def example_with_recommendations():
    """Example extracting recommendations."""
    print("=" * 60)
    print("Example 4: Dietary Recommendations")
    print("=" * 60)
    
    notes = [
        TextualNote(
            content="Patient is prediabetic. Recommend increasing physical activity. "
                   "Include more vegetables and lean proteins in diet. "
                   "Limit processed foods and sugary beverages. "
                   "Consider Mediterranean diet pattern.",
            section="recommendation"
        )
    ]
    
    interpreter = NLPTextInterpreter(model="gpt-4")
    
    # Extract recommendations
    recommendations = interpreter.extract_recommendations(notes)
    
    print(f"\nExtracted {len(recommendations)} recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")


def example_conflict_resolution():
    """Example demonstrating conflict resolution."""
    print("=" * 60)
    print("Example 5: Conflict Resolution")
    print("=" * 60)
    
    from ai_diet_planner.models import DietRule, RulePriority
    
    # Create conflicting rules
    rules = [
        DietRule(
            rule_text="Include dairy for calcium and bone health",
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
        ),
        DietRule(
            rule_text="Include vegetables for fiber",
            priority=RulePriority.RECOMMENDED,
            food_categories=["vegetables"],
            action="include",
            source="nlp_extraction"
        )
    ]
    
    interpreter = NLPTextInterpreter(model="gpt-4")
    
    print("\nOriginal rules:")
    for i, rule in enumerate(rules, 1):
        print(f"{i}. {rule.rule_text} (Priority: {rule.priority.value})")
    
    # Resolve conflicts
    resolved = interpreter.resolve_conflicts(rules)
    
    print(f"\nResolved to {len(resolved)} rules:")
    for i, rule in enumerate(resolved, 1):
        print(f"{i}. {rule.rule_text} (Priority: {rule.priority.value})")


def example_with_caching():
    """Example demonstrating caching."""
    print("=" * 60)
    print("Example 6: Caching Demonstration")
    print("=" * 60)
    
    notes = [
        TextualNote(
            content="Patient has diabetes. Limit sugar intake.",
            section="doctor_notes"
        )
    ]
    
    interpreter = NLPTextInterpreter(model="gpt-4", enable_cache=True)
    
    print("\nFirst call (processing)...")
    import time
    start = time.time()
    rules1 = interpreter.interpret_notes(notes)
    time1 = time.time() - start
    
    print(f"Extracted {len(rules1)} rules in {time1:.3f} seconds")
    
    print("\nSecond call (from cache)...")
    start = time.time()
    rules2 = interpreter.interpret_notes(notes)
    time2 = time.time() - start
    
    print(f"Retrieved {len(rules2)} rules in {time2:.3f} seconds")
    print(f"Speedup: {time1/time2:.1f}x faster")
    
    # Clear cache
    interpreter.clear_cache()
    print("\nCache cleared")


def example_with_gpt4():
    """Example using GPT-4 (requires API key)."""
    print("=" * 60)
    print("Example 7: Using GPT-4 (requires API key)")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nOpenAI API key not found in environment variables.")
        print("Set OPENAI_API_KEY to use GPT-4.")
        print("Falling back to BERT model for this example.\n")
    
    notes = [
        TextualNote(
            content="Patient presents with metabolic syndrome. "
                   "Elevated fasting glucose (110 mg/dL), high triglycerides (200 mg/dL), "
                   "and central obesity (waist circumference 42 inches). "
                   "Recommend DASH diet with emphasis on whole grains, lean proteins, "
                   "and reduced sodium. Limit alcohol consumption to no more than one drink per day.",
            section="doctor_notes"
        )
    ]
    
    # Initialize with GPT-4
    interpreter = NLPTextInterpreter(
        model="gpt-4",
        api_key=api_key,
        temperature=0.3
    )
    
    print(f"\nUsing model: {interpreter.model}")
    
    try:
        diet_rules = interpreter.interpret_notes(notes)
        
        print(f"\nExtracted {len(diet_rules)} diet rules:\n")
        for i, rule in enumerate(diet_rules, 1):
            print(f"{i}. {rule.rule_text}")
            print(f"   Priority: {rule.priority.value}")
            print(f"   Action: {rule.action}")
            print(f"   Categories: {', '.join(rule.food_categories)}")
            print()
    except Exception as e:
        print(f"\nError: {e}")
        print("This is expected if OpenAI API key is not configured.")


def main():
    """Run all examples."""
    examples = [
        example_basic_usage,
        example_multiple_conditions,
        example_with_allergies,
        example_with_recommendations,
        example_conflict_resolution,
        example_with_caching,
        example_with_gpt4,
    ]
    
    for example in examples:
        try:
            example()
            print("\n")
        except Exception as e:
            print(f"Error in example: {e}")
            print("\n")


if __name__ == "__main__":
    main()
