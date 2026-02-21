def map_text_to_diet_rules(text):

    text = text.lower()

    rules = {
        "avoid": [],
        "recommended": [],
        "calorie_target": 2000
    }

    if "diabetes" in text:
        rules["avoid"].append("Sugar")
        rules["avoid"].append("White rice")
        rules["calorie_target"] = 1500

    if "bp" in text or "hypertension" in text:
        rules["avoid"].append("Salt")
        rules["recommended"].append("Fruits")

    if "cholesterol" in text:
        rules["avoid"].append("Fried food")
        rules["recommended"].append("Vegetables")

    if "weight loss" in text:
        rules["calorie_target"] = 1400

    return rules
