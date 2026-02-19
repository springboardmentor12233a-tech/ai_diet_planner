# m4_rule_mapper.py
# Converts health alerts into diet rules

def alerts_to_diet_rules(alerts):
    diet_rules = {
        "limit": [],
        "increase": []
    }

    for metric, status, message in alerts:

        # Glucose related rules
        if metric == "Glucose" and status in ["Warning", "Critical"]:
            diet_rules["limit"].append("sugar")
            diet_rules["increase"].append("vegetables and fiber")

        # BMI related rules
        if metric == "BMI" and status in ["Warning", "Critical"]:
            diet_rules["limit"].append("fried foods")
            diet_rules["increase"].append("vegetables and fiber")

        # Blood Pressure related rules
        if metric == "Blood Pressure" and status in ["Warning", "Critical"]:
            diet_rules["limit"].append("salt")

    return diet_rules