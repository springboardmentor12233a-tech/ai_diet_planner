"""
Example demonstrating ambiguous instruction flagging in NLP Text Interpreter.

This example shows how the NLPTextInterpreter detects and flags ambiguous or
contradictory dietary instructions for manual review.
"""

from ai_diet_planner.models import TextualNote
from ai_diet_planner.nlp.text_interpreter import NLPTextInterpreter


def main():
    """Demonstrate ambiguous instruction flagging."""
    
    # Initialize interpreter (will use BERT fallback without API key)
    interpreter = NLPTextInterpreter(model="bert")
    
    print("=" * 80)
    print("Ambiguous Instruction Flagging Examples")
    print("=" * 80)
    
    # Example 1: Contradictory instructions
    print("\n1. Contradictory Instructions:")
    print("-" * 80)
    notes1 = [
        TextualNote(
            content="Include dairy products for calcium. Avoid all dairy due to lactose intolerance.",
            section="doctor_notes"
        )
    ]
    rules1 = interpreter.interpret_notes(notes1)
    print(f"Input: {notes1[0].content}")
    print(f"\nExtracted {len(rules1)} rules:")
    for i, rule in enumerate(rules1, 1):
        flagged = "⚠️ FLAGGED" if interpreter.is_flagged_for_review(rule) else "✓ Clear"
        print(f"  {i}. [{flagged}] {rule.rule_text}")
        print(f"     Priority: {rule.priority.value}, Action: {rule.action}")
    
    # Example 2: Vague instructions
    print("\n\n2. Vague Instructions:")
    print("-" * 80)
    notes2 = [
        TextualNote(
            content="Patient might want to consider reducing some sugar occasionally.",
            section="doctor_notes"
        )
    ]
    rules2 = interpreter.interpret_notes(notes2)
    print(f"Input: {notes2[0].content}")
    print(f"\nExtracted {len(rules2)} rules:")
    for i, rule in enumerate(rules2, 1):
        flagged = "⚠️ FLAGGED" if interpreter.is_flagged_for_review(rule) else "✓ Clear"
        print(f"  {i}. [{flagged}] {rule.rule_text}")
        print(f"     Priority: {rule.priority.value}, Action: {rule.action}")
    
    # Example 3: Conflicting carbohydrate recommendations
    print("\n\n3. Conflicting Carbohydrate Recommendations:")
    print("-" * 80)
    notes3 = [
        TextualNote(
            content="Follow low carb diet for diabetes management. Increase carb intake for athletic training.",
            section="doctor_notes"
        )
    ]
    rules3 = interpreter.interpret_notes(notes3)
    print(f"Input: {notes3[0].content}")
    print(f"\nExtracted {len(rules3)} rules:")
    for i, rule in enumerate(rules3, 1):
        flagged = "⚠️ FLAGGED" if interpreter.is_flagged_for_review(rule) else "✓ Clear"
        print(f"  {i}. [{flagged}] {rule.rule_text}")
        print(f"     Priority: {rule.priority.value}, Action: {rule.action}")
    
    # Example 4: Unclear allergy information
    print("\n\n4. Unclear Allergy Information:")
    print("-" * 80)
    notes4 = [
        TextualNote(
            content="Patient has possible allergy to shellfish. Needs confirmation testing.",
            section="doctor_notes"
        )
    ]
    rules4 = interpreter.interpret_notes(notes4)
    print(f"Input: {notes4[0].content}")
    print(f"\nExtracted {len(rules4)} rules:")
    for i, rule in enumerate(rules4, 1):
        flagged = "⚠️ FLAGGED" if interpreter.is_flagged_for_review(rule) else "✓ Clear"
        print(f"  {i}. [{flagged}] {rule.rule_text}")
        print(f"     Priority: {rule.priority.value}, Action: {rule.action}")
    
    # Example 5: Clear instructions (no flagging)
    print("\n\n5. Clear Instructions (No Flagging):")
    print("-" * 80)
    notes5 = [
        TextualNote(
            content="Patient has diabetes. Strictly avoid sugar and refined carbohydrates. Include high-fiber vegetables.",
            section="doctor_notes"
        )
    ]
    rules5 = interpreter.interpret_notes(notes5)
    print(f"Input: {notes5[0].content}")
    print(f"\nExtracted {len(rules5)} rules:")
    for i, rule in enumerate(rules5, 1):
        flagged = "⚠️ FLAGGED" if interpreter.is_flagged_for_review(rule) else "✓ Clear"
        print(f"  {i}. [{flagged}] {rule.rule_text}")
        print(f"     Priority: {rule.priority.value}, Action: {rule.action}")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    all_rules = rules1 + rules2 + rules3 + rules4 + rules5
    flagged_count = sum(1 for r in all_rules if interpreter.is_flagged_for_review(r))
    clear_count = len(all_rules) - flagged_count
    
    print(f"Total rules extracted: {len(all_rules)}")
    print(f"  - Flagged for manual review: {flagged_count}")
    print(f"  - Clear rules: {clear_count}")
    print("\nFlagged rules have OPTIONAL priority and should be reviewed by a healthcare")
    print("professional before being applied to diet plan generation.")


if __name__ == "__main__":
    main()
