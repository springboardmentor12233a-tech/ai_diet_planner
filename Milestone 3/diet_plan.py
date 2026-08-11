import pandas as pd

def apply_diet_rules(rules):
    # Expanded food dataset
    food_data = pd.DataFrame({
        "Food": ["Rice", "Chicken", "Cake", "Chips", "Vegetables", "Fruits", "Egg", "Oats", "Paneer", "Salad"],
        "Calories": [130, 250, 400, 300, 50, 60, 70, 120, 200, 30],
        "Protein": [2.5, 25, 4, 5, 2, 1, 6, 4, 14, 1],
        "Carbs": [28, 0, 50, 40, 10, 15, 1, 20, 5, 5],
        "Fat": [0.3, 10, 20, 15, 0.2, 0.1, 5, 2, 10, 0],
        "Sugar": [0, 0, 30, 2, 0, 10, 0, 1, 0, 2],
        "Salt": [1, 2, 2, 5, 0, 0, 1, 0, 1, 0],
        "Meal": ["Lunch", "Lunch", "Snack", "Snack", "Dinner", "Breakfast", "Breakfast", "Breakfast", "Dinner", "Lunch"]
    })

    # Apply avoid rules
    if "sugar" in rules["avoid"]:
        food_data = food_data[food_data["Sugar"] < 10]
    if "fried food" in rules["avoid"]:
        food_data = food_data[~food_data["Food"].isin(["Cake", "Chips"])]
    if "snacks" in rules["avoid"]:
        food_data = food_data[~food_data["Food"].isin(["Cake", "Chips"])]

    # Apply reduce rules
    if "salt" in rules["reduce"]:
        food_data = food_data[food_data["Salt"] < 3]
    if "oil" in rules["reduce"]:
        food_data = food_data[food_data["Fat"] < 15]

    # Apply increase rules (optional: prioritize or highlight)
    if "vegetables" in rules["increase"]:
        food_data = food_data.sort_values(by="Food", key=lambda x: x.str.contains("Vegetables"), ascending=False)

    return food_data

