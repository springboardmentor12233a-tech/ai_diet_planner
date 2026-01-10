import pandas as pd

def load_and_clean_csv(csv_path):
    df = pd.read_csv(csv_path)

    print("CSV Columns:")
    print(df.columns)

    # Basic cleaning
    df = df.drop_duplicates()

    # Handle missing values
    df.fillna({
        "Gender": "Unknown",
        "Medical_Condition": "Unknown",
        "Smoking_Status": "Unknown",
        "Insurance_Type": "Unknown",
        "Region": "Unknown",
        "Admission_Type": "Unknown"
    }, inplace=True)

    # Convert Age & Length_of_Stay to numeric (safe)
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Length_of_Stay"] = pd.to_numeric(df["Length_of_Stay"], errors="coerce")

    # Replace missing numeric values with mean
    df["Age"].fillna(df["Age"].mean(), inplace=True)
    df["Length_of_Stay"].fillna(df["Length_of_Stay"].mean(), inplace=True)

    print("\nCleaned Data Preview:")
    print(df.head())

    return df
