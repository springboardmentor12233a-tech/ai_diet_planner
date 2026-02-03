from diet_rules import DIET_RULES

def extract_diet_instructions(prescription_text):
    text = prescription_text.lower()
    
    result = {
        "avoid": set(),
        "add": set()
    }

    for action, categories in DIET_RULES.items():
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    result[action].add(category)

    return {
        "avoid": list(result["avoid"]),
        "add": list(result["add"])
    }
