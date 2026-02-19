# m4_diet_generator.py

import pandas as pd
import random


def generate_weekly_plan(diet_rules, strictness="Moderate"):

    df = pd.read_csv("data/foods.csv")

    limit = diet_rules.get("limit", [])

    # -------------------------------------------------
    # HEALTH-BASED FILTERING
    # -------------------------------------------------
    if "sugar" in limit:
        df = df[df["Sugar"] == "Low"]

    if "salt" in limit:
        df = df[df["Sodium"] == "Low"]

    # -------------------------------------------------
    # STRICTNESS FILTERING
    # -------------------------------------------------
    if strictness == "High":
        df = df[df["Calories"] <= 250]

    elif strictness == "Moderate":
        df = df[df["Calories"] <= 350]

    # Low strictness → allow most balanced meals

    # -------------------------------------------------
    # SPLIT BY CATEGORY
    # -------------------------------------------------
    breakfast_options = df[df["Category"] == "Breakfast"]["Food"].tolist()
    lunch_options = df[df["Category"] == "Lunch"]["Food"].tolist()
    dinner_options = df[df["Category"] == "Dinner"]["Food"].tolist()

    # -------------------------------------------------
    # SAFETY FALLBACKS
    # -------------------------------------------------
    if not breakfast_options:
        breakfast_options = ["Oatmeal with Fruits"]

    if not lunch_options:
        lunch_options = ["Chapati with Sabzi"]

    if not dinner_options:
        dinner_options = ["Vegetable Soup"]

    # -------------------------------------------------
    # RANDOMIZED WEEKLY PLAN
    # -------------------------------------------------
    weekly_plan = {}

    for i in range(7):
        weekly_plan[f"Day {i+1}"] = {
            "Breakfast": random.choice(breakfast_options),
            "Lunch": random.choice(lunch_options),
            "Dinner": random.choice(dinner_options)
        }

    return weekly_plan