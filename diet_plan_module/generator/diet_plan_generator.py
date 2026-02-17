# from rules.diet_rules import DIET_RULES

# def generate_diet_plan(intents):
#     avoid_set = set()
#     include_set = set()
#     notes_set = set()

#     # Collect diet components
#     for intent in intents:
#         rule = DIET_RULES.get(intent)
#         if rule:
#             avoid_set.update(rule.get("avoid", []))
#             include_set.update(rule.get("include", []))
#             note = rule.get("note")
#             if note:
#                 notes_set.add(note)

#     # Convert sets → ordered lists (important!)
#     include = list(include_set)
#     avoid = list(avoid_set)
#     notes = list(notes_set)

#     # Build meal-wise plan safely
#     diet_plan = {
#     "Breakfast": include[:3],
#     "Lunch": include[3:6],
#     "Dinner": include[3:5] if len(include) >= 4 else include[:2],
#     "Avoid": avoid,
#     "Notes": notes
# }

#     return diet_plan

from rules.diet_rules import DIET_RULES

def generate_diet_plan(intents):
    avoid_set = set()
    include_set = set()
    notes_set = set()

    for intent in intents:
        rule = DIET_RULES.get(intent)
        if rule:
            avoid_set.update(rule.get("avoid", []))
            include_set.update(rule.get("include", []))
            if rule.get("note"):
                notes_set.add(rule["note"])

    include = list(include_set)
    avoid = list(avoid_set)
    notes = list(notes_set)

    breakfast = include[:3]
    lunch = include[3:5]
    dinner = []
    for item in include:
        if item not in breakfast and item not in lunch:
            dinner.append(item)
        if len(dinner) == 2:
            break

    if not dinner:
        dinner = lunch[:1]  

    return {
        "Breakfast": breakfast,
        "Lunch": lunch,
        "Dinner": dinner,
        "Avoid": avoid,
        "Notes": notes
    }
