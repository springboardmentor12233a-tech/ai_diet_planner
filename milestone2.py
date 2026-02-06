

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

#load dataset
print("===== MODEL TRAINING STARTED =====\n")

csv_path = "data/diabetes.csv"
df = pd.read_csv(csv_path)


# 2. Data Cleaning

zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
for col in zero_cols:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df[col].median())


# 3. Features & Target

X = df.drop("Outcome", axis=1)
y = df["Outcome"]


# 4. Train-Test Split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# 5. Scaling 

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# 6. Train Gradient Boosting Model

model = GradientBoostingClassifier(random_state=42)
model.fit(X_train, y_train)


# 7. Evaluation

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]


roc_auc = roc_auc_score(y_test, y_prob)


print(f"ROC-AUC   : {roc_auc:.4f}")
print("\n===== MODEL TRAINING COMPLETED =====")
