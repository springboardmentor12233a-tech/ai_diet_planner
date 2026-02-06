import re

DIET_RULES = {
    "avoid sugar": ["avoid sugar", "no sugar", "reduce sugar", "diabetes"],
    "low carb diet": ["low carb", "reduce carbohydrate", "avoid carbs", "carb"],
    "increase fiber": ["increase fiber", "high fiber", "fiber"],
    "avoid fried food": ["avoid fried", "no fried", "oily food"],
    "increase vegetables": ["vegetables", "greens", "leafy"],
    "soft diet": ["sepsis", "aspiration", "pneumonia", "infection", "hospital stay", "icu", "difficult swallow"],
    "high protein diet": ["severe", "sepsis", "recovery", "strength", "muscle"],
    "easy to digest": ["aspiration", "pneumonia", "recovery", "care"],
    "hydration": ["stay hydrated", "drink water", "fluids", "maintain fluids"]
}

DIET_GUIDELINES = {
    "avoid sugar": "Avoid sweets, sugary drinks, and desserts",
    "low carb diet": "Reduce rice, bread, and refined carbohydrates",
    "increase fiber": "Eat vegetables, fruits, and whole grains",
    "avoid fried food": "Avoid deep-fried and oily foods",
    "increase vegetables": "Include vegetables in every meal",
    "soft diet": "Consume soft, easy-to-eat foods like soups, porridges, and steamed vegetables",
    "high protein diet": "Include high-protein foods (eggs, fish, chicken, legumes) for recovery and strength",
    "easy to digest": "Eat easily digestible foods - avoid spicy, fatty, and hard foods",
    "hydration": "Maintain proper hydration - drink water, herbal teas, and nutritious broths regularly"
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

    # If no rules found, provide default recommendations
    if not rules_found:
        rules_found = ["increase vegetables", "hydration"]

    return list(set(rules_found))


def generate_diet_plan(rules):
    if not rules:
        return ["Maintain a balanced diet", "Consult with a healthcare provider for personalized recommendations"]
    return [DIET_GUIDELINES[r] for r in rules if r in DIET_GUIDELINES]
