"""
Unit tests for MLHealthAnalyzer

Tests the core functionality of the ML Health Analyzer including:
- Model training with cross-validation
- Feature engineering
- Health condition classification
- Abnormal value detection
- Model registry management
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np

from health_analyzer import MLHealthAnalyzer, ModelRegistry, ModelMetadata


class TestMLHealthAnalyzer(unittest.TestCase):
    """Test cases for MLHealthAnalyzer"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests"""
        # Create synthetic diabetes dataset
        np.random.seed(42)
        n_samples = 200
        
        cls.test_data = pd.DataFrame({
            'Pregnancies': np.random.randint(0, 10, n_samples),
            'Glucose': np.random.randint(70, 200, n_samples),
            'BloodPressure': np.random.randint(60, 120, n_samples),
            'SkinThickness': np.random.randint(10, 60, n_samples),
            'Insulin': np.random.randint(0, 300, n_samples),
            'BMI': np.random.uniform(18, 45, n_samples),
            'DiabetesPedigreeFunction': np.random.uniform(0.1, 2.5, n_samples),
            'Age': np.random.randint(21, 80, n_samples)
        })
        
        # Create target based on simple rules (for testing)
        cls.test_target = (
            (cls.test_data['Glucose'] > 140) | 
            (cls.test_data['BMI'] > 35)
        ).astype(int)
    
    def setUp(self):
        """Set up for each test"""
        self.analyzer = MLHealthAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test MLHealthAnalyzer initialization"""
        self.assertIsNone(self.analyzer.registry)
        self.assertIsInstance(self.analyzer.available_models, list)
        self.assertIn('logistic_regression', self.analyzer.available_models)
        self.assertIn('random_forest', self.analyzer.available_models)
        self.assertIn('gradient_boosting', self.analyzer.available_models)
    
    def test_feature_engineering(self):
        """Test feature engineering creates interaction features"""
        df = pd.DataFrame({
            'Glucose': [100, 120],
            'BMI': [25, 30],
            'Age': [40, 50],
            'Insulin': [80, 100]
        })
        
        engineered = self.analyzer._engineer_features(df)
        
        # Check interaction features are created
        self.assertIn('Glucose_BMI', engineered.columns)
        self.assertIn('Age_Glucose', engineered.columns)
        self.assertIn('Insulin_Efficiency', engineered.columns)
        
        # Verify calculations
        self.assertEqual(engineered['Glucose_BMI'].iloc[0], 100 * 25)
        self.assertEqual(engineered['Age_Glucose'].iloc[0], 40 * 100)
        self.assertAlmostEqual(engineered['Insulin_Efficiency'].iloc[0], 80 / 101, places=5)
    
    def test_train_single_model(self):
        """Test training a single model"""
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            use_smote=False,
            cv_folds=3  # Fewer folds for faster testing
        )
        
        # Check registry is created
        self.assertIsInstance(registry, ModelRegistry)
        self.assertIn('logistic_regression', registry.models)
        self.assertIn('logistic_regression', registry.metadata)
        
        # Check metadata
        metadata = registry.metadata['logistic_regression']
        self.assertIsInstance(metadata, ModelMetadata)
        self.assertEqual(metadata.model_name, 'logistic_regression')
        self.assertGreater(metadata.accuracy, 0)
        self.assertLessEqual(metadata.accuracy, 1)
        self.assertEqual(len(metadata.cv_scores), 3)
    
    def test_train_multiple_models(self):
        """Test training multiple models"""
        models_to_train = ['logistic_regression', 'random_forest']
        
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=models_to_train,
            use_smote=True,
            cv_folds=3
        )
        
        # Check all models are trained
        for model_name in models_to_train:
            self.assertIn(model_name, registry.models)
            self.assertIn(model_name, registry.metadata)
    
    def test_train_with_smote(self):
        """Test training with SMOTE class balancing"""
        # Create imbalanced dataset
        imbalanced_target = pd.Series([0] * 150 + [1] * 50)
        
        registry = self.analyzer.train_models(
            self.test_data,
            imbalanced_target,
            models_to_train=['logistic_regression'],
            use_smote=True,
            cv_folds=3
        )
        
        self.assertIsNotNone(registry)
        self.assertIn('logistic_regression', registry.models)
    
    def test_cross_validation_folds(self):
        """Test that cross-validation uses correct number of folds"""
        cv_folds = 5
        
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=cv_folds
        )
        
        metadata = registry.metadata['logistic_regression']
        self.assertEqual(len(metadata.cv_scores), cv_folds)
    
    def test_classify_conditions(self):
        """Test health condition classification with multiple conditions"""
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType
        
        # Test classification with diabetes and obesity
        metrics = {
            'Glucose': 148,  # Diabetes range
            'BMI': 33.6,     # Obesity Class I
            'BloodPressure': 72,
            'Age': 50
        }
        
        conditions = self.analyzer.classify_conditions(metrics)
        
        # Check result is a list of HealthCondition objects
        self.assertIsInstance(conditions, list)
        self.assertGreater(len(conditions), 0)
        
        for condition in conditions:
            self.assertIsInstance(condition, HealthCondition)
            self.assertIsInstance(condition.confidence, float)
            self.assertGreater(condition.confidence, 0)
            self.assertLessEqual(condition.confidence, 1)
            self.assertIsInstance(condition.contributing_metrics, list)
            self.assertGreater(len(condition.contributing_metrics), 0)
        
        # Should detect diabetes and obesity
        condition_types = [c.condition_type for c in conditions]
        self.assertIn(ConditionType.DIABETES_TYPE2, condition_types)
        self.assertIn(ConditionType.OBESITY_CLASS1, condition_types)
    
    def test_detect_abnormal_values_critical(self):
        """Test detection of critical abnormal values"""
        from ai_diet_planner.models.health_data import Alert
        from ai_diet_planner.models.enums import AlertSeverity
        
        metrics = {
            'Glucose': 150,  # Critical (>= 126)
            'BMI': 32,       # Critical (>= 30)
            'BloodPressure': 95  # Critical (>= 90)
        }
        
        alerts = self.analyzer.detect_abnormal_values(metrics)
        
        # Should have 3 critical alerts
        self.assertEqual(len(alerts), 3)
        
        # All should be Alert objects with CRITICAL severity
        for alert in alerts:
            self.assertIsInstance(alert, Alert)
            self.assertEqual(alert.severity, AlertSeverity.CRITICAL)
            self.assertIsNotNone(alert.metric_type)
            self.assertIsNotNone(alert.message)
            self.assertIsNotNone(alert.recommended_action)
    
    def test_detect_abnormal_values_warning(self):
        """Test detection of warning-level abnormal values"""
        from ai_diet_planner.models.health_data import Alert
        from ai_diet_planner.models.enums import AlertSeverity
        
        metrics = {
            'Glucose': 110,  # Warning (100-125)
            'BMI': 27,       # Warning (25-29)
        }
        
        alerts = self.analyzer.detect_abnormal_values(metrics)
        
        # Should have 2 warning alerts
        self.assertEqual(len(alerts), 2)
        
        # All should be Alert objects with WARNING severity
        for alert in alerts:
            self.assertIsInstance(alert, Alert)
            self.assertEqual(alert.severity, AlertSeverity.WARNING)
    
    def test_detect_abnormal_values_normal(self):
        """Test that normal values don't generate alerts"""
        metrics = {
            'Glucose': 90,   # Normal
            'BMI': 22,       # Normal
            'BloodPressure': 75  # Normal
        }
        
        alerts = self.analyzer.detect_abnormal_values(metrics)
        
        # Should have no alerts
        self.assertEqual(len(alerts), 0)
    
    def test_alert_prioritization(self):
        """Test that alerts are prioritized by severity (Requirement 6.3)"""
        from ai_diet_planner.models.enums import AlertSeverity
        
        metrics = {
            'Glucose': 150,  # Critical
            'BMI': 27,       # Warning
            'BloodPressure': 95  # Critical
        }
        
        alerts = self.analyzer.detect_abnormal_values(metrics)
        
        # Critical alerts should come first
        critical_count = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
        warning_count = sum(1 for a in alerts if a.severity == AlertSeverity.WARNING)
        
        self.assertEqual(critical_count, 2)
        self.assertEqual(warning_count, 1)
        
        # First alerts should be critical
        self.assertEqual(alerts[0].severity, AlertSeverity.CRITICAL)
        self.assertEqual(alerts[1].severity, AlertSeverity.CRITICAL)
        self.assertEqual(alerts[2].severity, AlertSeverity.WARNING)
    
    def test_alert_recommended_actions(self):
        """Test that alerts include recommended actions (Requirement 6.4)"""
        from ai_diet_planner.models.enums import AlertSeverity
        
        metrics = {
            'Glucose': 150,  # Critical
            'BMI': 27,       # Warning
        }
        
        alerts = self.analyzer.detect_abnormal_values(metrics)
        
        # All alerts should have recommended actions
        for alert in alerts:
            self.assertIsNotNone(alert.recommended_action)
            self.assertIsInstance(alert.recommended_action, str)
            self.assertGreater(len(alert.recommended_action), 0)
            
            # Critical alerts should have more urgent language
            if alert.severity == AlertSeverity.CRITICAL:
                self.assertTrue(
                    'immediate' in alert.recommended_action.lower() or
                    'urgent' in alert.recommended_action.lower() or
                    'consult' in alert.recommended_action.lower()
                )
    
    def test_alert_severity_levels(self):
        """Test all three severity levels: CRITICAL, WARNING, NORMAL (Requirement 6.2)"""
        from ai_diet_planner.models.enums import AlertSeverity
        
        # Test CRITICAL
        critical_metrics = {'Glucose': 150}
        critical_alerts = self.analyzer.detect_abnormal_values(critical_metrics)
        self.assertEqual(len(critical_alerts), 1)
        self.assertEqual(critical_alerts[0].severity, AlertSeverity.CRITICAL)
        
        # Test WARNING
        warning_metrics = {'Glucose': 110}
        warning_alerts = self.analyzer.detect_abnormal_values(warning_metrics)
        self.assertEqual(len(warning_alerts), 1)
        self.assertEqual(warning_alerts[0].severity, AlertSeverity.WARNING)
        
        # Test NORMAL (no alerts)
        normal_metrics = {'Glucose': 90}
        normal_alerts = self.analyzer.detect_abnormal_values(normal_metrics)
        self.assertEqual(len(normal_alerts), 0)
    
    def test_threshold_based_alert_generation(self):
        """Test threshold-based alert generation (Requirement 6.1)"""
        from ai_diet_planner.models.enums import AlertSeverity, MetricType
        
        # Test exact threshold boundaries
        metrics_at_critical = {'Glucose': 126}  # Exactly at critical threshold
        alerts_critical = self.analyzer.detect_abnormal_values(metrics_at_critical)
        self.assertEqual(len(alerts_critical), 1)
        self.assertEqual(alerts_critical[0].severity, AlertSeverity.CRITICAL)
        self.assertEqual(alerts_critical[0].metric_type, MetricType.GLUCOSE)
        
        metrics_at_warning = {'Glucose': 100}  # Exactly at warning threshold
        alerts_warning = self.analyzer.detect_abnormal_values(metrics_at_warning)
        self.assertEqual(len(alerts_warning), 1)
        self.assertEqual(alerts_warning[0].severity, AlertSeverity.WARNING)
        
        metrics_below_warning = {'Glucose': 99}  # Just below warning threshold
        alerts_normal = self.analyzer.detect_abnormal_values(metrics_below_warning)
        self.assertEqual(len(alerts_normal), 0)
    
    def test_comprehensive_thresholds(self):
        """Test comprehensive threshold coverage for all metrics"""
        from ai_diet_planner.models.enums import AlertSeverity
        
        # Test all metrics with critical values
        all_critical_metrics = {
            'Glucose': 130,
            'BMI': 32,
            'BloodPressure': 95,
            'Cholesterol': 250,
            'LDL': 170,
            'Triglycerides': 210,
            'HbA1c': 7.0,
            'BloodPressure_Systolic': 145
        }
        
        alerts = self.analyzer.detect_abnormal_values(all_critical_metrics)
        
        # Should generate alerts for all metrics
        self.assertGreater(len(alerts), 0)
        
        # All should be critical
        for alert in alerts:
            self.assertEqual(alert.severity, AlertSeverity.CRITICAL)
    
    def test_reverse_threshold_hdl(self):
        """Test reverse threshold for HDL (lower is worse)"""
        from ai_diet_planner.models.enums import AlertSeverity, MetricType
        
        # Low HDL should trigger alert
        metrics_low_hdl = {'HDL': 35}  # Below critical threshold of 40
        alerts = self.analyzer.detect_abnormal_values(metrics_low_hdl)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.CRITICAL)
        self.assertEqual(alerts[0].metric_type, MetricType.CHOLESTEROL_HDL)
        self.assertIn('Low', alerts[0].message)
    
    def test_reverse_threshold_hemoglobin(self):
        """Test reverse threshold for Hemoglobin (lower is worse)"""
        from ai_diet_planner.models.enums import AlertSeverity, MetricType
        
        # Low hemoglobin should trigger alert
        metrics_low_hb = {'Hemoglobin': 11.0}  # Below critical threshold of 12.0
        alerts = self.analyzer.detect_abnormal_values(metrics_low_hb)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, AlertSeverity.CRITICAL)
        self.assertEqual(alerts[0].metric_type, MetricType.HEMOGLOBIN)
        self.assertIn('Low', alerts[0].message)
    
    def test_model_registry_save_load(self):
        """Test saving and loading model registry"""
        # Train models
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression', 'random_forest'],
            cv_folds=3
        )
        
        # Save registry
        save_path = Path(self.temp_dir) / 'models'
        registry.save(save_path)
        
        # Check files are created
        self.assertTrue((save_path / 'metadata.json').exists())
        self.assertTrue((save_path / 'scaler.pkl').exists())
        self.assertTrue((save_path / 'logistic_regression_model.pkl').exists())
        self.assertTrue((save_path / 'random_forest_model.pkl').exists())
        
        # Load registry without compatibility check
        loaded_registry = ModelRegistry.load(save_path, verify_compatibility=False)
        
        # Verify loaded registry
        self.assertEqual(set(loaded_registry.models.keys()), set(registry.models.keys()))
        self.assertEqual(set(loaded_registry.metadata.keys()), set(registry.metadata.keys()))
        self.assertIsNotNone(loaded_registry.scaler)
    
    def test_model_versioning(self):
        """Test model versioning with metadata (Requirement 18.4)"""
        # Train a model
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        # Check version metadata is present
        metadata = registry.metadata['logistic_regression']
        self.assertIsNotNone(metadata.version)
        self.assertIsNotNone(metadata.training_date)
        self.assertIsNotNone(metadata.feature_names)
        self.assertIsInstance(metadata.feature_names, list)
        self.assertGreater(len(metadata.feature_names), 0)
        
        # Verify version format
        self.assertIsInstance(metadata.version, str)
        self.assertIsInstance(metadata.training_date, str)
    
    def test_model_compatibility_verification_success(self):
        """Test successful model compatibility verification (Requirement 18.5)"""
        # Train and save models
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        save_path = Path(self.temp_dir) / 'models'
        registry.save(save_path)
        
        # Load with compatible features (same features)
        current_features = registry.feature_names.copy()
        loaded_registry = ModelRegistry.load(
            save_path, 
            verify_compatibility=True,
            current_feature_names=current_features
        )
        
        self.assertIsNotNone(loaded_registry)
        self.assertEqual(loaded_registry.feature_names, registry.feature_names)
    
    def test_model_compatibility_verification_with_extra_features(self):
        """Test compatibility verification with extra current features (Requirement 18.5)"""
        # Train and save models
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        save_path = Path(self.temp_dir) / 'models'
        registry.save(save_path)
        
        # Load with extra features (should succeed - extra features are OK)
        current_features = registry.feature_names.copy() + ['NewFeature1', 'NewFeature2']
        loaded_registry = ModelRegistry.load(
            save_path,
            verify_compatibility=True,
            current_feature_names=current_features
        )
        
        self.assertIsNotNone(loaded_registry)
    
    def test_model_compatibility_verification_failure(self):
        """Test failed model compatibility verification (Requirement 18.5)"""
        # Train and save models
        registry = self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        save_path = Path(self.temp_dir) / 'models'
        registry.save(save_path)
        
        # Load with incompatible features (missing required features)
        current_features = ['OnlyOneFeature']
        
        with self.assertRaises(ValueError) as context:
            ModelRegistry.load(
                save_path,
                verify_compatibility=True,
                current_feature_names=current_features
            )
        
        # Check error message mentions incompatibility
        self.assertIn('incompatible', str(context.exception).lower())
    
    def test_get_evaluation_metrics(self):
        """Test getting evaluation metrics report (Requirement 18.2)"""
        # Train a model
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['gradient_boosting'],
            cv_folds=3
        )
        
        # Get evaluation metrics
        metrics = self.analyzer.get_evaluation_metrics('gradient_boosting')
        
        # Check all required metrics are present
        self.assertIsNotNone(metrics)
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        self.assertIn('cv_mean', metrics)
        self.assertIn('cv_std', metrics)
        
        # Check metrics are valid floats
        for metric_name, value in metrics.items():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
            if metric_name != 'cv_std':  # std can be > 1
                self.assertLessEqual(value, 1.0)
    
    def test_get_evaluation_metrics_nonexistent_model(self):
        """Test getting metrics for non-existent model"""
        metrics = self.analyzer.get_evaluation_metrics('nonexistent_model')
        self.assertIsNone(metrics)
    
    def test_needs_retraining_below_threshold(self):
        """Test retraining flag for accuracy below 85% (Requirement 18.3)"""
        # Train a model
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        # Manually set accuracy below threshold for testing
        self.analyzer.registry.metadata['logistic_regression'].accuracy = 0.80
        
        # Should flag for retraining
        needs_retrain = self.analyzer.needs_retraining('logistic_regression', threshold=0.85)
        self.assertTrue(needs_retrain)
    
    def test_needs_retraining_above_threshold(self):
        """Test retraining flag for accuracy above 85% (Requirement 18.3)"""
        # Train a model
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        # Manually set accuracy above threshold for testing
        self.analyzer.registry.metadata['logistic_regression'].accuracy = 0.90
        
        # Should not flag for retraining
        needs_retrain = self.analyzer.needs_retraining('logistic_regression', threshold=0.85)
        self.assertFalse(needs_retrain)
    
    def test_needs_retraining_exact_threshold(self):
        """Test retraining flag at exact threshold boundary"""
        # Train a model
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        # Set accuracy exactly at threshold
        self.analyzer.registry.metadata['logistic_regression'].accuracy = 0.85
        
        # Should not flag for retraining (>= threshold is acceptable)
        needs_retrain = self.analyzer.needs_retraining('logistic_regression', threshold=0.85)
        self.assertFalse(needs_retrain)
    
    def test_needs_retraining(self):
        """Test retraining flag logic"""
        # Train a model
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression'],
            cv_folds=3
        )
        
        # Check retraining logic
        # With synthetic data, accuracy might be below 85%
        needs_retrain = self.analyzer.needs_retraining('logistic_regression', threshold=0.85)
        self.assertIsInstance(needs_retrain, bool)
        
        # With very low threshold, should not need retraining
        needs_retrain_low = self.analyzer.needs_retraining('logistic_regression', threshold=0.1)
        self.assertFalse(needs_retrain_low)
    
    def test_list_models(self):
        """Test listing trained models"""
        # Initially no models
        self.assertEqual(self.analyzer.list_models(), [])
        
        # Train models
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['logistic_regression', 'random_forest'],
            cv_folds=3
        )
        
        # Should list trained models
        models = self.analyzer.list_models()
        self.assertEqual(set(models), {'logistic_regression', 'random_forest'})
    
    def test_get_model_info(self):
        """Test getting model metadata"""
        # Train a model
        self.analyzer.train_models(
            self.test_data,
            self.test_target,
            models_to_train=['gradient_boosting'],
            cv_folds=3
        )
        
        # Get model info
        info = self.analyzer.get_model_info('gradient_boosting')
        
        self.assertIsInstance(info, ModelMetadata)
        self.assertEqual(info.model_name, 'gradient_boosting')
        self.assertGreater(info.accuracy, 0)
        self.assertGreater(info.cv_mean, 0)
    
    def test_invalid_model_name(self):
        """Test error handling for invalid model names"""
        with self.assertRaises(ValueError):
            self.analyzer.train_models(
                self.test_data,
                self.test_target,
                models_to_train=['invalid_model']
            )
    
    def test_classify_without_training(self):
        """Test that classification works without trained models (uses rule-based)"""
        from ai_diet_planner.models.health_data import HealthCondition
        
        metrics = {'Glucose': 130, 'BMI': 32}
        
        # Should work with rule-based classification
        conditions = self.analyzer.classify_conditions(metrics)
        self.assertIsInstance(conditions, list)
    
    def test_missing_features_handling(self):
        """Test handling of missing features in classification"""
        from ai_diet_planner.models.health_data import HealthCondition
        
        # Classify with partial features
        partial_metrics = {
            'Glucose': 120,
            'BMI': 28,
            'Age': 45
            # Missing other features
        }
        
        # Should handle missing features gracefully
        conditions = self.analyzer.classify_conditions(partial_metrics)
        self.assertIsInstance(conditions, list)
        # May or may not detect conditions depending on thresholds
    
    def test_classify_diabetes_type2(self):
        """Test diabetes type 2 classification"""
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        metrics = {'Glucose': 130}  # Diabetes range
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.DIABETES_TYPE2)
        self.assertIn(MetricType.GLUCOSE, conditions[0].contributing_metrics)
        self.assertGreater(conditions[0].confidence, 0.7)
    
    def test_classify_prediabetes(self):
        """Test prediabetes classification"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {'Glucose': 110}  # Prediabetes range
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.PREDIABETES)
    
    def test_classify_diabetes_with_hba1c(self):
        """Test diabetes classification using HbA1c"""
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        metrics = {'HbA1c': 7.0}  # Diabetes range
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.DIABETES_TYPE2)
        self.assertIn(MetricType.HBA1C, conditions[0].contributing_metrics)
    
    def test_classify_hypertension_stage1(self):
        """Test hypertension stage 1 classification"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {'BloodPressure': 135}  # Stage 1 range
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.HYPERTENSION_STAGE1)
    
    def test_classify_hypertension_stage2(self):
        """Test hypertension stage 2 classification"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {'BloodPressure': 145}  # Stage 2 range
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.HYPERTENSION_STAGE2)
    
    def test_classify_hyperlipidemia(self):
        """Test hyperlipidemia classification"""
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        metrics = {'Cholesterol': 250, 'LDL': 170}
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.HYPERLIPIDEMIA)
        self.assertIn(MetricType.CHOLESTEROL_TOTAL, conditions[0].contributing_metrics)
        self.assertIn(MetricType.CHOLESTEROL_LDL, conditions[0].contributing_metrics)
    
    def test_classify_obesity_class1(self):
        """Test obesity class I classification"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {'BMI': 32}
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.OBESITY_CLASS1)
    
    def test_classify_obesity_class2(self):
        """Test obesity class II classification"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {'BMI': 37}
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.OBESITY_CLASS2)
    
    def test_classify_obesity_class3(self):
        """Test obesity class III classification"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {'BMI': 42}
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.OBESITY_CLASS3)
    
    def test_classify_anemia(self):
        """Test anemia classification"""
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        metrics = {'Hemoglobin': 11.0}
        conditions = self.analyzer.classify_conditions(metrics)
        
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.ANEMIA)
        self.assertIn(MetricType.HEMOGLOBIN, conditions[0].contributing_metrics)
    
    def test_classify_multiple_conditions(self):
        """Test classification with multiple conditions present"""
        from ai_diet_planner.models.enums import ConditionType
        
        metrics = {
            'Glucose': 130,      # Diabetes
            'BMI': 35,           # Obesity Class II
            'BloodPressure': 145,  # Hypertension Stage 2
            'Hemoglobin': 11.5   # Anemia
        }
        conditions = self.analyzer.classify_conditions(metrics)
        
        # Should detect all 4 conditions
        self.assertEqual(len(conditions), 4)
        condition_types = [c.condition_type for c in conditions]
        self.assertIn(ConditionType.DIABETES_TYPE2, condition_types)
        self.assertIn(ConditionType.OBESITY_CLASS2, condition_types)
        self.assertIn(ConditionType.HYPERTENSION_STAGE2, condition_types)
        self.assertIn(ConditionType.ANEMIA, condition_types)
    
    def test_classify_no_conditions(self):
        """Test classification with normal values"""
        metrics = {
            'Glucose': 90,
            'BMI': 23,
            'BloodPressure': 115,
            'Hemoglobin': 14.0
        }
        conditions = self.analyzer.classify_conditions(metrics)
        
        # Should detect no conditions
        self.assertEqual(len(conditions), 0)
    
    def test_incomplete_metrics_handling(self):
        """Test handling of incomplete metrics (Requirement 5.5)"""
        from ai_diet_planner.models.enums import ConditionType
        
        # Only provide glucose, missing other metrics
        metrics = {'Glucose': 130}
        conditions = self.analyzer.classify_conditions(metrics)
        
        # Should still classify diabetes based on available data
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].condition_type, ConditionType.DIABETES_TYPE2)
        
        # Contributing metrics should only include what was provided
        from ai_diet_planner.models.enums import MetricType
        self.assertEqual(conditions[0].contributing_metrics, [MetricType.GLUCOSE])


if __name__ == '__main__':
    unittest.main()
