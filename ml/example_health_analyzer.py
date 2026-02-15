"""
Example usage of MLHealthAnalyzer

Demonstrates training models and making predictions with the unified ML Health Analyzer.
"""

import pandas as pd
from pathlib import Path
from health_analyzer import MLHealthAnalyzer


def main():
    # Load diabetes dataset
    dataset_path = Path(__file__).parent.parent / 'datasets' / 'diabetes.csv'
    
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}")
        print("Please ensure the diabetes.csv dataset is available.")
        return
    
    df = pd.read_csv(dataset_path)
    
    # Separate features and target
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']
    
    print("=" * 60)
    print("ML Health Analyzer - Training Example")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = MLHealthAnalyzer()
    
    # Train models (all available models)
    print("\nTraining models with 5-fold cross-validation and SMOTE...")
    registry = analyzer.train_models(
        X, y,
        models_to_train=None,  # Train all available models
        use_smote=True,
        cv_folds=5,
        random_state=42
    )
    
    # Save trained models
    model_dir = Path(__file__).parent / 'trained_models'
    registry.save(model_dir)
    print(f"\nModels saved to {model_dir}")
    
    # List trained models
    print("\n" + "=" * 60)
    print("Trained Models:")
    print("=" * 60)
    for model_name in analyzer.list_models():
        info = analyzer.get_model_info(model_name)
        print(f"\n{model_name}:")
        print(f"  Accuracy: {info.accuracy:.4f}")
        print(f"  CV Mean: {info.cv_mean:.4f} (+/- {info.cv_std:.4f})")
        print(f"  Precision: {info.precision:.4f}")
        print(f"  Recall: {info.recall:.4f}")
        print(f"  F1-Score: {info.f1_score:.4f}")
        
        # Check if retraining needed
        if analyzer.needs_retraining(model_name):
            print(f"  ⚠️  Model needs retraining (accuracy < 85%)")
        else:
            print(f"  ✓ Model meets accuracy threshold")
    
    # Example prediction
    print("\n" + "=" * 60)
    print("Example Health Condition Classification:")
    print("=" * 60)
    
    sample_metrics = {
        'Glucose': 148,
        'BloodPressure': 145,
        'BMI': 35.6,
        'Hemoglobin': 11.5,
        'Cholesterol': 250,
        'HbA1c': 7.2,
        'Age': 50
    }
    
    print("\nPatient Metrics:")
    for metric, value in sample_metrics.items():
        print(f"  {metric}: {value}")
    
    # Classify conditions (now returns list of HealthCondition objects)
    conditions = analyzer.classify_conditions(sample_metrics)
    
    print(f"\n✓ Detected {len(conditions)} health condition(s):")
    for i, condition in enumerate(conditions, 1):
        print(f"\n{i}. {condition.condition_type.value.replace('_', ' ').title()}")
        print(f"   Confidence: {condition.confidence:.2%}")
        print(f"   Contributing Metrics: {', '.join([m.value for m in condition.contributing_metrics])}")
        print(f"   Detected At: {condition.detected_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detect abnormal values
    print("\n" + "=" * 60)
    print("Health Alerts:")
    print("=" * 60)
    
    alerts = analyzer.detect_abnormal_values(sample_metrics)
    
    if not alerts:
        print("\n✓ No abnormal values detected. All metrics within normal ranges.")
    else:
        for alert in alerts:
            severity_icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
            print(f"\n{severity_icon} [{alert['severity']}] {alert['metric']}")
            print(f"   Value: {alert['value']} {alert['unit']}")
            print(f"   Message: {alert['message']}")
            print(f"   Action: {alert['recommended_action']}")
    
    # Example with incomplete metrics
    print("\n" + "=" * 60)
    print("Example with Incomplete Metrics:")
    print("=" * 60)
    
    incomplete_metrics = {
        'Glucose': 130,
        'BMI': 32
        # Missing other metrics
    }
    
    print("\nPatient Metrics (Incomplete):")
    for metric, value in incomplete_metrics.items():
        print(f"  {metric}: {value}")
    
    conditions = analyzer.classify_conditions(incomplete_metrics)
    
    print(f"\n✓ Detected {len(conditions)} health condition(s) from available data:")
    for i, condition in enumerate(conditions, 1):
        print(f"\n{i}. {condition.condition_type.value.replace('_', ' ').title()}")
        print(f"   Confidence: {condition.confidence:.2%}")
        print(f"   Based on: {', '.join([m.value for m in condition.contributing_metrics])}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
