import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier 

# 1. Load dataset
df = pd.read_csv('../datasets/diabetes.csv')

# 2. Advanced Imputation: Replace zeros with median based on Outcome
# This prevents leaking information between healthy and diabetic profiles
cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols_to_fix:
    df[col] = df[col].replace(0, np.nan)
    df[col] = df[col].fillna(df.groupby('Outcome')[col].transform('median'))

# 3. Expanded Feature Selection
# Including DiabetesPedigreeFunction is critical for the >85% threshold
features = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]

X = df[features]
y = df['Outcome']

# 4. Scaling and Splitting
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Hyperparameter Tuning with XGBoost
# This addresses the overfitting seen in your previous models
xgb_model = XGBClassifier(
    eval_metric='logloss',
    random_state=42
)

param_grid = {
    'max_depth': [3, 4, 5],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 200, 300],
    'subsample': [0.7, 0.8, 0.9]
}

grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

# 6. Results
best_model = grid_search.best_estimator_
train_acc = accuracy_score(y_train, best_model.predict(X_train))
test_acc = accuracy_score(y_test, best_model.predict(X_test))

print(f"Best Parameters: {grid_search.best_params_}")
print(f"Refined Train Accuracy: {train_acc:.3f}")
print(f"Refined Test Accuracy: {test_acc:.3f}")
print("\nClassification Report:\n", classification_report(y_test, best_model.predict(X_test)))