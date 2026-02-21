def get_food_recommendations(glucose, bmi):

    avoid_foods = []
    recommended_foods = []

    # High glucose condition
    if glucose >= 180:
        avoid_foods = [
            "Sugar",
            "Sweets",
            "Soft drinks",
            "White rice",
            "Bakery items",
            "Ice cream",
            "Chocolates"
        ]

        recommended_foods = [
            "Brown rice",
            "Oats",
            "Green vegetables",
            "Millets",
            "Fruits (low sugar)",
            "Boiled vegetables"
        ]

    # High BMI condition
    elif bmi >= 25:
        avoid_foods = [
            "Fried food",
            "Junk food",
            "Fast food",
            "High calorie snacks",
            "Oil rich food"
        ]

        recommended_foods = [
            "Salads",
            "Vegetable soup",
            "Boiled food",
            "Low fat diet"
        ]

    else:
        recommended_foods = [
            "Balanced diet",
            "Fruits",
            "Vegetables",
            "Protein rich food"
        ]

    return avoid_foods, recommended_foods
