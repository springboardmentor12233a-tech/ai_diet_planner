def generate_7_day_diet(glucose, bp, bmi):

    import random

    high_glucose = glucose > 180
    high_bp = bp > 140
    obese = bmi > 30

    # food pool

    low_carb_breakfast = [
    "Boiled Eggs + Green Tea",
    "Vegetable Omelette + Cucumber Salad",
    "Sprouts Salad + Lemon Water",
    "Paneer Bhurji (no oil)"
   ]

    low_sodium_lunch = [
    "Brown Rice (low salt) + Dal + Steamed Vegetables",
    "Grilled Chicken + Mixed Salad (no added salt)",
    "Chapati + Lauki Sabzi + Curd",
    "Vegetable Khichdi (low sodium)"
   ]

    weight_loss_dinner = [
    "Vegetable Soup + 1 Multigrain Roti",
    "Grilled Paneer + Stir Fry Veggies",
    "Clear Chicken Soup + Salad",
    "Tofu + Steamed Broccoli"
   ]

    balanced_meals = [
    "Oats + Apple",
    "Rice + Dal + Salad",
    "Chapati + Mixed Veg Sabzi",
    "Poha + Peanuts"
   ]
    
    diet_plan = ""

    for day in range(1, 8):

        diet_plan += f"\nDay {day}:\n"

        if high_glucose:
            breakfast = random.choice(low_carb_breakfast)
        else:
            breakfast = random.choice(balanced_meals)

        if high_bp:
            lunch = random.choice(low_sodium_lunch)
        else:
            lunch = random.choice(balanced_meals)

        if obese:
            dinner = random.choice(weight_loss_dinner)
        else:
            dinner = random.choice(balanced_meals)

        diet_plan += f"Breakfast: {breakfast}\n"
        diet_plan += f"Lunch: {lunch}\n"
        diet_plan += f"Dinner: {dinner}\n"

    return diet_plan
