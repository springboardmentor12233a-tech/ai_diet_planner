import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# --- UPDATED: Expanded Threshold and Alert Function ---
def check_for_alerts(glucose=None, bp=None, bmi=None, hb=None, crp=None, rbc=None):
    """
    Checks for abnormal numeric lab values and returns clinical alerts.
    Now includes CBC (Hb, RBC) and CRP (Inflammation) parameters.
    """
    alerts = []
    
    # Blood Sugar / RBS
    if glucose and glucose > 140: 
        alerts.append(f"HIGH SUGAR (RBS): {glucose} mg/dL")
    
    # Blood Pressure
    if bp and bp > 90:      
        alerts.append(f"HIGH BLOOD PRESSURE: {bp} mmHg")
    
    # BMI
    if bmi and bmi > 30:     
        alerts.append(f"ABNORMAL BMI: {bmi}")
    
    # NEW: Hemoglobin (Normal range roughly 13.0-17.0 for males)
    if hb and hb < 13.0:
        alerts.append(f"LOW HEMOGLOBIN: {hb} g/dL (Anemic Risk)")
        
    # NEW: CRP (Normal is usually < 10 mg/L)
    if crp and crp > 10.0:
        alerts.append(f"HIGH CRP: {crp} mg/L (Active Inflammation)")
        
    # NEW: RBC Count (Normal 4.5 - 5.5)
    if rbc and rbc < 4.5:
        alerts.append(f"LOW RBC COUNT: {rbc} million/mcL")
        
    return alerts

def train_ultra_accuracy_model():
    # Load data
    df = pd.read_csv('diabetes.csv')

    # Advanced Cleaning
    cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in cols_to_fix:
        df[col] = df[col].replace(0, np.nan)
        df[col] = df[col].fillna(df[col].median())

    # Feature Engineering
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.1, random_state=230)

    # Ensemble Learning
    model1 = LogisticRegression(C=0.1)
    model2 = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    model3 = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, random_state=42)

    ensemble_model = VotingClassifier(
        estimators=[('lr', model1), ('rf', model2), ('gb', model3)], 
        voting='soft'
    )

    ensemble_model.fit(X_train, y_train)
    y_pred = ensemble_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("-" * 35)
    print(f"MODEL ACCURACY: {accuracy * 100:.2f}%")
    print("-" * 35)

if __name__ == "__main__":
    train_ultra_accuracy_model()