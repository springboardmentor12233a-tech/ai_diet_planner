# 1. IMPORT LIBRARIES
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

# 4. HANDLE INVALID ZERO VALUES
cols_with_zero = ['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI']
df[cols_with_zero] = df[cols_with_zero].replace(0, np.nan)

# 5. TARGET-BASED MEDIAN IMPUTATION
def median_target(col):
    return df.groupby('Outcome')[col].median()

for col in cols_with_zero:
    df.loc[(df[col].isnull()) & (df['Outcome']==0), col] = median_target(col)[0]
    df.loc[(df[col].isnull()) & (df['Outcome']==1), col] = median_target(col)[1]

# 6. FEATURE ENGINEERING
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

df['NewBMI'] = df['BMI'].apply(bmi_category)

# Insulin Score
def insulin_score(insulin):
    return 'Normal' if 16 <= insulin <= 166 else 'Abnormal'

df['NewInsulinScore'] = df['Insulin'].apply(insulin_score)

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

df['NewGlucose'] = df['Glucose'].apply(glucose_category)

# 7. ONE-HOT ENCODING
df = pd.get_dummies(df, columns=['NewBMI','NewInsulinScore','NewGlucose'], drop_first=True)

# 8. SPLIT FEATURES & TARGET
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# 9. ROBUST SCALING 
robust_scaler = RobustScaler()
X[X.columns] = robust_scaler.fit_transform(X)

# 10. TRAIN-TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 
# 11. STANDARD SCALING FOR ML MODELS
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 12. MODEL TRAINING & EVALUATION

def evaluate_model(model, name):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"\n{name}")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))

# Logistic Regression
evaluate_model(LogisticRegression(), "Logistic Regression")

# KNN
evaluate_model(KNeighborsClassifier(), "KNN")

# SVM (Tuned)
svc = SVC(C=10, gamma=0.01, probability=True)
evaluate_model(svc, "Support Vector Machine")

# Decision Tree (Tuned)
dt = DecisionTreeClassifier(
    criterion='entropy', max_depth=7,
    min_samples_leaf=3, min_samples_split=3
)
evaluate_model(dt, "Decision Tree")

# Random Forest
rf = RandomForestClassifier(
    n_estimators=130, max_depth=15,
    min_samples_leaf=2, min_samples_split=3,
    criterion='entropy'
)
evaluate_model(rf, "Random Forest")

# XGBoost
xgb = XGBClassifier(
    objective='binary:logistic',
    learning_rate=0.01,
    max_depth=10,
    n_estimators=180,
    eval_metric='logloss'
)
evaluate_model(xgb, "XGBoost")

print("\nPipeline execution completed successfully.")


import pickle

# Dictionary to store all trained models
trained_models = {
    "logistic_regression": LogisticRegression().fit(X_train, y_train),
    "knn": KNeighborsClassifier().fit(X_train, y_train),
    "svm": svc,   # already trained
    "decision_tree": dt,
    "random_forest": rf,
    "xgboost": xgb
}

# Save each model
for name, model in trained_models.items():
    with open(f"{name}_model.pkl", "wb") as f:
        pickle.dump(model, f)

# Save scalers
with open("robust_scaler.pkl", "wb") as f:
    pickle.dump(robust_scaler, f)

with open("standard_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# # Save model performance summary 
# model_accuracy = {
#     "logistic_regression": log_reg_acc,
#     "knn": knn_acc,
#     "svm": svc_acc,
#     "decision_tree": dt_acc,
#     "random_forest": rand_acc,
#     "xgboost": xgb_acc
# }

# with open("model_accuracy.pkl", "wb") as f:
#     pickle.dump(model_accuracy, f)

# print("All models and scalers saved successfully.")
