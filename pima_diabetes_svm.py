# pima_diabetes_svm.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

# ---------------------------
# 1. Load Dataset
# ---------------------------
df = pd.read_csv('data/diabetes.csv')  # adjust path if needed

# ---------------------------
# 2. Advanced Imputation
# ---------------------------
cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols_to_fix:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df.groupby('Outcome')[col].transform('median'))

# ---------------------------
# 3. Features and Target
# ---------------------------
features = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin',
            'BMI','DiabetesPedigreeFunction','Age']
X = df[features]
y = df['Outcome']

# ---------------------------
# 4. Scaling
# ---------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------------------------
# 5. Train-Test Split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.25, stratify=y, random_state=42
)

# ---------------------------
# 6. Hyperparameter Tuning for SVM
# ---------------------------
param_grid = {
    'C': [0.1, 1, 10, 50],
    'gamma': ['scale', 0.01, 0.05, 0.1],
    'kernel': ['rbf']
}

svm = SVC(class_weight='balanced', probability=True, random_state=42)

grid = GridSearchCV(svm, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid.fit(X_train, y_train)

best_svm = grid.best_estimator_

# ---------------------------
# 7. Predictions & Evaluation
# ---------------------------
y_train_pred = best_svm.predict(X_train)
y_test_pred = best_svm.predict(X_test)
y_test_prob = best_svm.predict_proba(X_test)[:,1]

train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_test_pred)
roc_auc = roc_auc_score(y_test, y_test_prob)

print("----- SVM Tuned Results -----")
print(f"Best Parameters: {grid.best_params_}")
print(f"Training Accuracy: {train_acc:.3f}")
print(f"Testing Accuracy: {test_acc:.3f}")
print(f"ROC-AUC Score: {roc_auc:.3f}")
print("\nClassification Report:\n", classification_report(y_test, y_test_pred))
