def rule_based_mapping(text):
    text = text.lower()

    # Empty rule structure
    rules = {
        "avoid": [],
        "reduce": [],
        "increase": []
    }

    RULES = {
        "sugar": ("avoid", "sugar"),
        "sweets": ("avoid", "sweets"),
        "fried": ("avoid", "fried food"),
        "chips": ("avoid", "fried food"),
        "cake": ("avoid", "fried food"),
        "oil": ("avoid", "oil"),
        "oily": ("avoid", "oil"),
        "salt": ("reduce", "salt"),
        "sodium": ("reduce", "salt"),
        "vegetables": ("increase", "vegetables"),
        "greens": ("increase", "vegetables"),
        "fruits": ("increase", "fruits"),
        "fruit": ("increase", "fruits"),
        "protein": ("increase", "protein"),
        "dairy": ("increase", "dairy"),
        "whole grains": ("increase", "whole grains"),
        "snacks": ("avoid", "snacks"),
        "processed": ("avoid", "processed food")
    }

    for keyword, (category, item) in RULES.items():
        if keyword in text:
            if item not in rules[category]:
                rules[category].append(item)

    return rules
