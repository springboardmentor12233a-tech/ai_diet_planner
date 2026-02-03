def generate_diet_plan(diet_rules):
    plan = []

    if diet_rules["avoid"]:
        plan.append(f"Avoid foods related to: {', '.join(diet_rules['avoid'])}")

    if diet_rules["add"]:
        plan.append(f"Include more: {', '.join(diet_rules['add'])}")

    return plan
