import pandas as pd
import os

DATA_DIR = "Datasets"

def load_pima():
    df = pd.read_csv(os.path.join(DATA_DIR, "diabetes.csv"))
    print("Pima Dataset Loaded:", df.shape)
    print(df.head())

def load_diet_recommendations():
    df = pd.read_csv(os.path.join(DATA_DIR, "diet_recommendations_dataset.csv"))
    print("Diet Recommendation Dataset Loaded:", df.shape)
    print(df.head())

def load_food_nutrition():
    food_dir = os.path.join(DATA_DIR, "food_nutrition")
    dfs = []

    for file in os.listdir(food_dir):
        if file.endswith(".csv"):
            dfs.append(pd.read_csv(os.path.join(food_dir, file)))

    food_df = pd.concat(dfs, ignore_index=True)
    print("Food Nutrition Dataset Loaded:", food_df.shape)
    print(food_df.head())

if __name__ == "__main__":
    load_pima()
    load_diet_recommendations()
    load_food_nutrition()
