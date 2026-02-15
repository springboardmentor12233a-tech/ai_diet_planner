import re
from rules_mapping import INSTRUCTION_RULES

def _normalize_line(line):
    line = line.lower()
    line = re.sub(r"[^a-z\s]", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line

def generate_advice_from_text(text):
    normalized = _normalize_line(text)
    advice = []

    if "diabetes" in normalized or "glucose" in normalized or "sugar" in normalized:
        advice.append("Limit sugar intake and choose low-glycemic foods.")
    if "bp" in normalized or "hypertension" in normalized or "pressure" in normalized:
        advice.append("Reduce salt intake and avoid processed foods.")
    if "cholesterol" in normalized or "lipid" in normalized:
        advice.append("Avoid oily/fried foods and choose healthy fats.")
    if "obese" in normalized or "overweight" in normalized:
        advice.append("Control portion sizes and increase daily activity.")

    if not advice:
        advice.extend([
            "Avoid oily and fried foods.",
            "Limit sugar and sweetened drinks.",
            "Reduce salt intake.",
            "Drink adequate water daily.",
            "Follow prescribed medicines and maintain regular meals."
        ])

    return advice

def generate_diet_rules_from_advice(advice_lines):
    rules = []
    for line in advice_lines:
        normalized = _normalize_line(line)
        for key, rule in INSTRUCTION_RULES.items():
            if key in normalized:
                rules.append(rule)

    if not rules:
        rules.append("General healthy diet")

    seen = set()
    deduped = []
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            deduped.append(rule)
    return deduped


# -------- MANUAL PRESCRIPTION ADVICE (BYPASS OCR) --------
manual_advice = "avoid sugar"
full_text = manual_advice

# -------- ADVICE + DIET RULES --------
generated_advice = generate_advice_from_text(full_text)
diet_rules = generate_diet_rules_from_advice(generated_advice)

# -------- OUTPUT --------
print("\n===== GENERATED ADVICE =====\n")
for line in generated_advice:
    print("-", line)

print("\n===== DIET RULES (FROM ADVICE) =====\n")
for rule in diet_rules:
    print("-", rule)