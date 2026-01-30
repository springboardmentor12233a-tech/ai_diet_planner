from rules_mapping import INSTRUCTION_RULES

def map_advice_to_rules(text):
    text = text.lower()
    detected_rules = set()

    for keyword, rule in INSTRUCTION_RULES.items():
        if keyword in text:
            detected_rules.add(rule)

    return list(detected_rules)


# -------- MANUAL INPUT --------
print("Enter doctor's advice (type END to finish):")

lines = []
while True:
    line = input()
    if line.strip().upper() == "END":
        break
    lines.append(line)

manual_text = "\n".join(lines)

# -------- PROCESS --------
rules = map_advice_to_rules(manual_text)

# -------- OUTPUT --------
print("\n===== DIET RULES IDENTIFIED =====\n")

if rules:
    for r in rules:
        print("-", r)
else:
    print("No diet-related instructions detected.")
