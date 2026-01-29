# ==============================
# MILESTONE - 2
# ==============================

print("\n========== IMPORTING LIBRARIES ==========")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


# ==============================
# 1. LOAD THE DATASET
# ==============================

print("\n========== LOADING DATASET ==========")

# Make sure diabetes.csv is in the SAME folder as this .py file
df = pd.read_csv("E:\InfosysSpringboard-Project\Datasets\diabetes.csv")

print("First 5 rows of the dataset:")
print(df.head())

print("\nDataset shape:", df.shape)


# ==============================
# 2. REPLACE MEDICALLY IMPOSSIBLE ZEROS WITH NaN
# ==============================

print("\n========== HANDLING INVALID ZEROS ==========")

zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

df[zero_cols] = df[zero_cols].replace(0, np.nan)

print("Missing values after replacing zeros:")
print(df[zero_cols].isna().sum())


# ==============================
# 3. HANDLE MISSING VALUES (MEDIAN IMPUTATION)
# ==============================

print("\n========== MEDIAN IMPUTATION ==========")

df[zero_cols] = df[zero_cols].fillna(df[zero_cols].median())

print("Missing values after imputation:")
print(df[zero_cols].isna().sum())


# ==============================
# 4. SPLIT FEATURES AND TARGET
# ==============================

print("\n========== SPLITTING FEATURES & TARGET ==========")

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

print("Feature shape:", X.shape)
print("Target shape:", y.shape)


# ==============================
# 5. TRAIN-TEST SPLIT
# ==============================

print("\n========== TRAIN-TEST SPLIT ==========")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training set size:", X_train.shape)
print("Testing set size:", X_test.shape)


# ==============================
# 6. FEATURE SCALING
# ==============================

print("\n========== FEATURE SCALING ==========")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Feature scaling completed.")


# ==============================
# 7. TRAIN MODELS
# ==============================

print("\n========== MODEL TRAINING ==========")

# Model 1: Logistic Regression
log_model = LogisticRegression(max_iter=1000)
log_model.fit(X_train_scaled, y_train)
log_pred = log_model.predict(X_test_scaled)

print("Logistic Regression trained successfully.")

# Model 2: Random Forest
rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

print("Random Forest trained successfully.")


# ==============================
# 8. MODEL EVALUATION
# ==============================

print("\n========== MODEL EVALUATION ==========")

print("\n📌 Logistic Regression Results")
print("Accuracy:", accuracy_score(y_test, log_pred))
print(classification_report(y_test, log_pred))

print("\n📌 Random Forest Results")
print("Accuracy:", accuracy_score(y_test, rf_pred))
print(classification_report(y_test, rf_pred))


# ==============================
# 9. CONFUSION MATRIX VISUALIZATION
# ==============================

print("\n========== CONFUSION MATRIX ==========")

cm = confusion_matrix(y_test, rf_pred)

plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Random Forest")
plt.show()


# ==============================
# 10. PREDICTION FOR A NEW PATIENT
# ==============================

print("\n========== NEW PATIENT PREDICTION ==========")

new_patient = np.array([[3, 150, 80, 25, 100, 30.0, 0.5, 35]])

prediction = rf_model.predict(new_patient)

print("Prediction result:",
      "Diabetic" if prediction[0] == 1 else "Not Diabetic")
