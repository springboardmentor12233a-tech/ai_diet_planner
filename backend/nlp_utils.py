import re

DIET_RULES = {
    "avoid sugar": ["avoid sugar", "no sugar", "reduce sugar"],
    "low carb diet": ["low carb", "reduce carbohydrate", "avoid carbs"],
    "increase fiber": ["increase fiber", "high fiber"],
    "avoid fried food": ["avoid fried", "no fried", "oily food"],
    "increase vegetables": ["vegetables", "greens", "leafy"]
}

DIET_GUIDELINES = {
    "avoid sugar": "Avoid sweets, sugary drinks, and desserts",
    "low carb diet": "Reduce rice, bread, and refined carbohydrates",
    "increase fiber": "Eat vegetables, fruits, and whole grains",
    "avoid fried food": "Avoid deep-fried and oily foods",
    "increase vegetables": "Include vegetables in every meal"
}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    return text


def interpret_doctor_notes(text: str):
    text = clean_text(text)
    rules_found = []

    for rule, keywords in DIET_RULES.items():
        for kw in keywords:
            if kw in text:
                rules_found.append(rule)
                break

    return list(set(rules_found))


def generate_diet_plan(rules):
    return [DIET_GUIDELINES[r] for r in rules]
