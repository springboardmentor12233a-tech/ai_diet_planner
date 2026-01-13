import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ---------------------------
# 1. Load dataset
# ---------------------------
df = pd.read_csv("data/medical_data.csv")

print("\nDataset loaded successfully")
print(df.head())
print("\nColumns:", df.columns.tolist())


# ---------------------------
# 2. Drop ID column
# ---------------------------
df.drop(columns=["Patient_ID"], inplace=True)


# ---------------------------
# 3. Handle missing values
# ---------------------------
categorical_cols = [
    "Gender", "Medical_Condition", "Treatment",
    "Insurance_Type", "Region",
    "Smoking_Status", "Admission_Type"
]

for col in categorical_cols:
    df[col] = df[col].fillna("Unknown")

numeric_cols = ["Age", "Income", "Length_of_Stay"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col].fillna(df[col].mean(), inplace=True)


# ---------------------------
# 4. Encode categorical columns
# ---------------------------
encoder = LabelEncoder()

for col in categorical_cols + ["Outcome"]:
    df[col] = encoder.fit_transform(df[col])

print("\nEncoded Outcome classes:", df["Outcome"].unique())


# ---------------------------
# 5. Split features & target
# ---------------------------
X = df.drop("Outcome", axis=1)
y = df["Outcome"]


# ---------------------------
# 6. Train-test split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# ---------------------------
# 7. Feature scaling
# ---------------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# ---------------------------
# 8. Train Logistic Regression
# ---------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)


# ---------------------------
# 9. Predict & evaluate
# ---------------------------
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n✅ Model trained successfully")
print("🎯 Accuracy:", accuracy)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))
