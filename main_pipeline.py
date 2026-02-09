from ocr_extractor import extract_text
from advice_filter import extract_diet_advice
from rule_mapper import rule_based_mapping
from bert_semantic import bert_mapping
from diet_plan import apply_diet_rules

print("1. Upload prescription OR")
print("2. Type doctor advice manually")
choice = input("Choose (1/2): ")

if choice == "1":
    path = input("Enter prescription path: ")
    text = extract_text(path)
else:
    print("Type doctor advice (END to stop):")
    lines = []
    while True:
        line = input()
        if line.upper() == "END":
            break
        lines.append(line)
    text = "\n".join(lines)

print("\n--- Extracted Text ---")
print(text)

advice = extract_diet_advice(text)
if not advice:
    print("\nNo actionable advice found in prescription.")
else:
    print("\n--- Doctor Advice Lines ---")
    for a in advice:
        print("-", a)

    # Combine rule-based and BERT-based mapping
    rules_rb = rule_based_mapping(" ".join(advice))
    rules_bert = bert_mapping(" ".join(advice))

    # Merge rules
    rules = {
        "avoid": list(set(rules_rb["avoid"] + rules_bert["avoid"])),
        "reduce": list(set(rules_rb["reduce"] + rules_bert["reduce"])),
        "increase": list(set(rules_rb["increase"] + rules_bert["increase"]))
    }

    print("\n--- FINAL DIET RULES ---")
    print(rules)

    updated_diet = apply_diet_rules(rules)
    print("\n--- UPDATED DIET PLAN ---")
    print(updated_diet)
