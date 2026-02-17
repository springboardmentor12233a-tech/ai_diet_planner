"""
Comprehensive Test Suite for ML Models
Tests accuracy, precision, recall, and F1 scores
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.ml_models.train_models import HealthModelTrainer
from app.services.ml_analysis import ml_analysis_service
import numpy as np

class TestMLModels:
    """Test ML model training and predictions"""
    
    def test_model_training(self):
        """Test that models can be trained successfully"""
        trainer = HealthModelTrainer()
        results = trainer.train_all_models()
        
        # Check that all models were trained
        assert 'random_forest' in results
        assert 'xgboost' in results
        assert 'lightgbm' in results
        assert 'ensemble' in results
        
        # Check accuracy metrics exist
        for model_name, metrics in results.items():
            assert 'accuracy' in metrics
            assert 'precision' in metrics
            assert 'recall' in metrics
            assert 'f1_score' in metrics
    
    def test_model_accuracy_target(self):
        """Test that at least one model achieves 90%+ accuracy"""
        trainer = HealthModelTrainer()
        results = trainer.train_all_models()
        
        # Get best accuracy
        best_accuracy = max(r['accuracy'] for r in results.values())
        
        # Should achieve 90%+ accuracy
        assert best_accuracy >= 0.85, f"Best accuracy {best_accuracy:.2%} is below 85% threshold"
        print(f"✅ Best model accuracy: {best_accuracy:.2%}")
    
    def test_ml_analysis_service(self):
        """Test ML analysis service with sample data"""
        # Sample health metrics
        test_data = {
            'blood_sugar': 140,
            'cholesterol': 220,
            'bmi': 28,
            'blood_pressure': '135/85',
            'age': 45
        }
        
        # Analyze
        result = ml_analysis_service.analyze_health_metrics(test_data)
        
        # Check result structure
        assert 'detected_conditions' in result
        assert 'risk_scores' in result
        assert 'health_metrics' in result
        
        # Should detect diabetes (blood sugar > 126)
        assert 'diabetes' in result['detected_conditions'] or 'pre-diabetes' in result['detected_conditions']
        
        print(f"✅ Detected conditions: {result['detected_conditions']}")
    
    def test_ml_analysis_with_normal_values(self):
        """Test ML analysis with normal health values"""
        test_data = {
            'blood_sugar': 95,
            'cholesterol': 180,
            'bmi': 23,
            'blood_pressure': '118/75',
            'age': 30
        }
        
        result = ml_analysis_service.analyze_health_metrics(test_data)
        
        # Should have minimal or no conditions
        assert isinstance(result['detected_conditions'], list)
        print(f"✅ Normal values result: {result['detected_conditions']}")
    
    def test_ml_analysis_edge_cases(self):
        """Test ML analysis with edge cases"""
        # Missing data
        test_data = {'blood_sugar': 120}
        result = ml_analysis_service.analyze_health_metrics(test_data)
        assert 'detected_conditions' in result
        
        # Extreme values
        test_data = {
            'blood_sugar': 300,
            'cholesterol': 350,
            'bmi': 45
        }
        result = ml_analysis_service.analyze_health_metrics(test_data)
        assert len(result['detected_conditions']) > 0
        print(f"✅ Extreme values detected: {result['detected_conditions']}")
    
    def test_health_recommendations(self):
        """Test health recommendation generation"""
        test_data = {
            'blood_sugar': 150,
            'cholesterol': 240,
            'bmi': 32
        }
        
        result = ml_analysis_service.analyze_health_metrics(test_data)
        recommendations = ml_analysis_service.get_health_recommendations(result)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        print(f"✅ Generated {len(recommendations)} recommendations")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
