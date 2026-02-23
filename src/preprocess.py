import re
import numpy as np
import pandas as pd


# ==========================
# OCR TEXT PREPROCESSING
# ==========================

def preprocess_text(text):
    print("\n--- RAW OCR TEXT ---")
    print(text)

    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9./\s()-]', ' ', text)

    print("\n--- PREPROCESSED TEXT ---")
    print(text)

    return text


def is_valid_value(value):
    try:
        val = float(value)
        return val > 0
    except ValueError:
        return False


def extract_parameters(text):
    patterns = {
        "Hemoglobin": r'hemoglobin\s*[:\-]?\s*(\d+\.?\d*)\s*(g/dl)?',
        "Total WBC Count": r'total wbc count\s*[:\-]?\s*(\d+\.?\d*)\s*(/cumm)?',
        "Platelet Count": r'platelet count\s*[:\-]?\s*(\d+\.?\d*)\s*(lakhs/cmm)?',
        "AST (SGOT)": r'(?:ast|sgot)\s*[:\-]?\s*(\d+\.?\d*)\s*(iu/l)?',
        "ALT (SGPT)": r'(?:alt|sgpt)\s*[:\-]?\s*(\d+\.?\d*)\s*(iu/l)?',
        "Glucose": r'glucose\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?',
        "LDL": r'ldl\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?'
    }

    records = []

    print("\n--- PARAMETER EXTRACTION ---")

    for test_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1)
            unit = match.group(2) if match.lastindex and match.lastindex >= 2 else ""

            if is_valid_value(value):
                print(f"[FOUND] {test_name}")
                print(f"        Value: {value}")
                print(f"        Unit : {unit}")

                records.append({
                    "Test Name": test_name,
                    "Observed Value": float(value),
                    "Unit": unit
                })
            else:
                print(f"[REJECTED] {test_name} (low confidence: {value})")
        else:
            print(f"[NOT FOUND] {test_name}")

    return records


# ==========================
# ML DATA PREPROCESSING
# ==========================
from sklearn.preprocessing import StandardScaler


def preprocess_data(df):
    """
    Prepares features (X) and target (y) for model training
    """
    target_col = "Outcome"  # <-- changed from 'diet_label'

    print("Columns in df:", df.columns)
    print("Target column expected:", target_col)

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset. Available columns: {df.columns.tolist()}")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Convert all features to numeric
    X = X.apply(pd.to_numeric, errors="coerce")

    # Fill missing values
    for col in X.columns:
        X[col] = X[col].fillna(X[col].median())

    # Scale features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y
