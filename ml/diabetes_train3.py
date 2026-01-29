import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# 1. Load and Clean (Grouped Median Imputation)
df = pd.read_csv('../datasets/diabetes.csv')
cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols_to_fix:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df.groupby('Outcome')[col].transform('median'))

# Use all relevant features for maximum accuracy
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# 2. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3. Scaling (fit only on training data to avoid data leakage)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# --- MODEL 1: LOGISTIC REGRESSION TUNING ---
lr_params = {'C': [0.01, 0.1, 1, 10, 100], 'solver': ['liblinear']}
lr_grid = GridSearchCV(LogisticRegression(), lr_params, cv=5).fit(X_train, y_train)
lr_acc = accuracy_score(y_test, lr_grid.predict(X_test))

# --- MODEL 2: SVM TUNING ---
svm_params = {'C': [0.1, 1, 10], 'gamma': ['scale', 'auto'], 'kernel': ['rbf']}
svm_grid = GridSearchCV(SVC(), svm_params, cv=5).fit(X_train, y_train)
svm_acc = accuracy_score(y_test, svm_grid.predict(X_test))

# --- MODEL 3: RANDOM FOREST TUNING ---
rf_params = {
    'n_estimators': [100, 200],
    'max_depth': [5, 7, 10],
    'min_samples_leaf': [2, 4]
}
rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=5).fit(X_train, y_train)
rf_acc = accuracy_score(y_test, rf_grid.predict(X_test))

# 4. Final Comparison Output
print("--- Mentor Review: Model Accuracies ---")
print(f"Logistic Regression (Tuned): {lr_acc:.3f}")
print(f"SVM (Tuned):                 {svm_acc:.3f}")
print(f"Random Forest (Tuned):       {rf_acc:.3f}")
print(f"Best RF Params: {rf_grid.best_params_}")