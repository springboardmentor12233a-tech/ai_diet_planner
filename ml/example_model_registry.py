"""
Example: Model Registry and Versioning

Demonstrates the model registry functionality including:
- Model training with version metadata
- Saving and loading models
- Model compatibility verification
- Evaluation metrics reporting
- Automatic retraining flag

Requirements: 18.2, 18.3, 18.4, 18.5
"""

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_diet_planner.ml.health_analyzer import MLHealthAnalyzer


def main():
    print("=" * 70)
    print("Model Registry and Versioning Example")
    print("=" * 70)
    
    # Create synthetic diabetes dataset
    print("\n1. Creating synthetic training data...")
    np.random.seed(42)
    n_samples = 300
    
    data = pd.DataFrame({
        'Pregnancies': np.random.randint(0, 10, n_samples),
        'Glucose': np.random.randint(70, 200, n_samples),
        'BloodPressure': np.random.randint(60, 120, n_samples),
        'SkinThickness': np.random.randint(10, 60, n_samples),
        'Insulin': np.random.randint(0, 300, n_samples),
        'BMI': np.random.uniform(18, 45, n_samples),
        'DiabetesPedigreeFunction': np.random.uniform(0.1, 2.5, n_samples),
        'Age': np.random.randint(21, 80, n_samples)
    })
    
    # Create target based on simple rules
    target = ((data['Glucose'] > 140) | (data['BMI'] > 35)).astype(int)
    print(f"   Created {n_samples} samples with {target.sum()} positive cases")
    
    # Train models
    print("\n2. Training ML models with cross-validation...")
    analyzer = MLHealthAnalyzer()
    
    registry = analyzer.train_models(
        data,
        target,
        models_to_train=['logistic_regression', 'random_forest', 'gradient_boosting'],
        use_smote=True,
        cv_folds=5
    )
    
    print("\n3. Model Evaluation Metrics (Requirement 18.2):")
    print("-" * 70)
    for model_name in analyzer.list_models():
        metrics = analyzer.get_evaluation_metrics(model_name)
        print(f"\n{model_name.upper()}:")
        print(f"   Accuracy:  {metrics['accuracy']:.4f}")
        print(f"   Precision: {metrics['precision']:.4f}")
        print(f"   Recall:    {metrics['recall']:.4f}")
        print(f"   F1-Score:  {metrics['f1_score']:.4f}")
        print(f"   CV Mean:   {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")
    
    # Check retraining flags
    print("\n4. Automatic Retraining Flags (Requirement 18.3):")
    print("-" * 70)
    threshold = 0.85
    print(f"   Accuracy threshold: {threshold}")
    for model_name in analyzer.list_models():
        needs_retrain = analyzer.needs_retraining(model_name, threshold)
        metadata = analyzer.get_model_info(model_name)
        status = "NEEDS RETRAINING" if needs_retrain else "OK"
        print(f"   {model_name}: {metadata.accuracy:.4f} - {status}")
    
    # Model versioning
    print("\n5. Model Versioning (Requirement 18.4):")
    print("-" * 70)
    for model_name in analyzer.list_models():
        metadata = analyzer.get_model_info(model_name)
        print(f"\n{model_name.upper()}:")
        print(f"   Version:       {metadata.version}")
        print(f"   Training Date: {metadata.training_date}")
        print(f"   Features:      {len(metadata.feature_names)} features")
        print(f"   Feature Names: {', '.join(metadata.feature_names[:5])}...")
    
    # Save and load with compatibility verification
    print("\n6. Model Compatibility Verification (Requirement 18.5):")
    print("-" * 70)
    
    temp_dir = tempfile.mkdtemp()
    try:
        save_path = Path(temp_dir) / 'models'
        
        # Save models
        print(f"   Saving models to: {save_path}")
        registry.save(save_path)
        print("   ✓ Models saved successfully")
        
        # Load with compatible features
        print("\n   Loading with compatible features...")
        current_features = registry.feature_names.copy()
        loaded_registry = analyzer.registry.__class__.load(
            save_path,
            verify_compatibility=True,
            current_feature_names=current_features
        )
        print("   ✓ Compatibility verified - models loaded successfully")
        
        # Try loading with extra features (should succeed)
        print("\n   Loading with extra features (should succeed)...")
        extra_features = current_features + ['NewFeature1', 'NewFeature2']
        loaded_registry = analyzer.registry.__class__.load(
            save_path,
            verify_compatibility=True,
            current_feature_names=extra_features
        )
        print("   ✓ Extra features OK - models loaded successfully")
        
        # Try loading with incompatible features (should fail)
        print("\n   Loading with incompatible features (should fail)...")
        incompatible_features = ['OnlyOneFeature']
        try:
            loaded_registry = analyzer.registry.__class__.load(
                save_path,
                verify_compatibility=True,
                current_feature_names=incompatible_features
            )
            print("   ✗ ERROR: Should have failed compatibility check!")
        except ValueError as e:
            print(f"   ✓ Compatibility check failed as expected")
            print(f"   Error: {str(e)[:100]}...")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
    
    # Demonstrate classification with loaded model
    print("\n7. Classification with Loaded Model:")
    print("-" * 70)
    
    test_metrics = {
        'Glucose': 148,
        'BMI': 33.6,
        'BloodPressure': 72,
        'Age': 50,
        'Pregnancies': 6,
        'SkinThickness': 35,
        'Insulin': 0,
        'DiabetesPedigreeFunction': 0.627
    }
    
    print("   Test metrics:")
    for key, value in test_metrics.items():
        print(f"      {key}: {value}")
    
    conditions = analyzer.classify_conditions(test_metrics)
    
    print(f"\n   Detected {len(conditions)} condition(s):")
    for condition in conditions:
        print(f"      - {condition.condition_type.value}")
        print(f"        Confidence: {condition.confidence:.2%}")
        print(f"        Contributing metrics: {[m.value for m in condition.contributing_metrics]}")
    
    print("\n" + "=" * 70)
    print("Model Registry Example Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
