# 1. IMPORT LIBRARIES
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# 2. LOAD DATASET
df = pd.read_csv("E:\InfosysSpringboard-Project\Datasets\diabetes.csv")

# 3. BASIC EDA
print(df.head())
print(df.info())
print(df.describe())

# 4. HANDLE INVALID ZERO VALUES (before split, as it's domain cleaning)
cols_with_zero = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI']
df[cols_with_zero] = df[cols_with_zero].replace(0, np.nan)

# 5. SPLIT FEATURES & TARGET
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# 6. TRAIN-TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 7. CREATE TEMPORARY DATAFRAMES FOR IMPUTATION AND ENGINEERING
train_df = pd.DataFrame(X_train, columns=X.columns)
train_df['Outcome'] = y_train.values

test_df = pd.DataFrame(X_test, columns=X.columns)
test_df['Outcome'] = y_test.values

# 8. TARGET-BASED MEDIAN IMPUTATION (now after split, using train medians only)
def median_target(col, df):
    return df.groupby('Outcome')[col].median()

for col in cols_with_zero:
    medians = median_target(col, train_df)
    # Impute train
    train_df.loc[(train_df[col].isnull()) & (train_df['Outcome']==0), col] = medians[0]
    train_df.loc[(train_df[col].isnull()) & (train_df['Outcome']==1), col] = medians[1]
    # Impute test using train's medians (using test Outcome for choice, as it's evaluation-only)
    test_df.loc[(test_df[col].isnull()) & (test_df['Outcome']==0), col] = medians[0]
    test_df.loc[(test_df[col].isnull()) & (test_df['Outcome']==1), col] = medians[1]

# 9. FEATURE ENGINEERING (applied separately to train and test)
# BMI Categories
def bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif bmi <= 24.9:
        return 'Normal'
    elif bmi <= 29.9:
        return 'Overweight'
    elif bmi <= 34.9:
        return 'Obesity_1'
    elif bmi <= 39.9:
        return 'Obesity_2'
    else:
        return 'Obesity_3'

train_df['NewBMI'] = train_df['BMI'].apply(bmi_category)
test_df['NewBMI'] = test_df['BMI'].apply(bmi_category)

# Insulin Score
def insulin_score(insulin):
    return 'Normal' if 16 <= insulin <= 166 else 'Abnormal'

train_df['NewInsulinScore'] = train_df['Insulin'].apply(insulin_score)
test_df['NewInsulinScore'] = test_df['Insulin'].apply(insulin_score)

# Glucose Category
def glucose_category(glucose):
    if glucose <= 70:
        return 'Low'
    elif glucose <= 99:
        return 'Normal'
    elif glucose <= 126:
        return 'Prediabetic'
    else:
        return 'Diabetic'

train_df['NewGlucose'] = train_df['Glucose'].apply(glucose_category)
test_df['NewGlucose'] = test_df['Glucose'].apply(glucose_category)

# 10. ONE-HOT ENCODING (fit on train, apply to test)
train_df = pd.get_dummies(train_df, columns=['NewBMI','NewInsulinScore','NewGlucose'], drop_first=True)
# Align test columns to train (in case of missing categories)
test_df = pd.get_dummies(test_df, columns=['NewBMI','NewInsulinScore','NewGlucose'], drop_first=True)
missing_cols = set(train_df.columns) - set(test_df.columns)
for col in missing_cols:
    if col != 'Outcome':  
        test_df[col] = 0
test_df = test_df[train_df.columns]  # Reorder to match

# 11. SEPARATE FEATURES & TARGET AGAIN
X_train = train_df.drop('Outcome', axis=1)
y_train = train_df['Outcome']
X_test = test_df.drop('Outcome', axis=1)
y_test = test_df['Outcome']

# 12. STANDARD SCALING FOR ML MODELS
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 13. MODEL TRAINING & EVALUATION
def evaluate_model(model, name):
    model.fit(X_train, y_train)
    # Training predictions
    y_train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, y_train_pred)
    # Testing predictions
    y_test_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    print(f"\n{name}")
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Testing Accuracy : {test_acc:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_test_pred))
    print(classification_report(y_test, y_test_pred))
    return train_acc, test_acc

# MODEL TRAINING & COMPARISON
results = []
# Logistic Regression
train_acc, test_acc = evaluate_model(
    LogisticRegression(), "Logistic Regression"
)
results.append(["Logistic Regression", train_acc, test_acc])
# KNN
train_acc, test_acc = evaluate_model(
    KNeighborsClassifier(), "KNN"
)
results.append(["KNN", train_acc, test_acc])
# SVM (Tuned)
svc = SVC(C=10, gamma=0.01, probability=True)
train_acc, test_acc = evaluate_model(
    svc, "Support Vector Machine"
)
results.append(["SVM", train_acc, test_acc])
# Decision Tree (Tuned)
dt = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=7,
    min_samples_leaf=3,
    min_samples_split=3
)
train_acc, test_acc = evaluate_model(
    dt, "Decision Tree"
)
results.append(["Decision Tree", train_acc, test_acc])
# Random Forest
rf = RandomForestClassifier(
    n_estimators=130,
    max_depth=15,
    min_samples_leaf=2,
    min_samples_split=3,
    criterion='entropy'
)
train_acc, test_acc = evaluate_model(
    rf, "Random Forest"
)
results.append(["Random Forest", train_acc, test_acc])
# XGBoost
xgb = XGBClassifier(
    objective='binary:logistic',
    learning_rate=0.01,
    max_depth=10,
    n_estimators=180,
    eval_metric='logloss'
)
train_acc, test_acc = evaluate_model(
    xgb, "XGBoost"
)
results.append(["XGBoost", train_acc, test_acc])

# FINAL MODEL PERFORMANCE SUMMARY
summary_df = pd.DataFrame(
    results,
    columns=["Model", "Training Accuracy", "Testing Accuracy"]
)
print("\nMODEL PERFORMANCE SUMMARY")
print(summary_df.sort_values(by="Testing Accuracy", ascending=False))
print("\nPipeline execution completed successfully.")

import pickle
# Dictionary to store all trained models
models_dir = r"E:\InfosysSpringboard-Project\models"
os.makedirs(models_dir, exist_ok=True)

trained_models = {
    "logistic_regression": LogisticRegression().fit(X_train, y_train),
    "knn": KNeighborsClassifier().fit(X_train, y_train),
    "svm": svc,
    "decision_tree": dt,
    "random_forest": rf,
    "xgboost": xgb
}
# Save each model
for name, model in trained_models.items():
    with open(os.path.join(models_dir, f"{name}_model.pkl"), "wb") as f:
        pickle.dump(model, f)
with open(os.path.join(models_dir, "standard_scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)
    
    
# # Save model performance summary
# model_accuracy = {
# "logistic_regression": log_reg_acc,
# "knn": knn_acc,
# "svm": svc_acc,
# "decision_tree": dt_acc,
# "random_forest": rand_acc,
# "xgboost": xgb_acc
# }
# with open("model_accuracy.pkl", "wb") as f:
# pickle.dump(model_accuracy, f)
# print("All models and scalers saved successfully.")