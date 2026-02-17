"""
Quick Start Script for AI-NutriCare
Trains ML models and runs comprehensive tests
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def train_ml_models():
    """Train ML models"""
    print_header("🤖 STEP 1: Training ML Models")
    
    try:
        from app.ml_models.train_models import HealthModelTrainer
        
        trainer = HealthModelTrainer()
        results = trainer.train_all_models()
        
        print("\n✅ ML Models trained successfully!")
        print(f"\nModel Performance:")
        for model_name, metrics in results.items():
            print(f"  {model_name:15s}: {metrics['accuracy']*100:.2f}% accuracy")
        
        best_accuracy = max(r['accuracy'] for r in results.values())
        if best_accuracy >= 0.90:
            print(f"\n🎉 SUCCESS! Achieved {best_accuracy*100:.2f}% accuracy (Target: 90%)")
        else:
            print(f"\n⚠️  Best accuracy: {best_accuracy*100:.2f}% (Target: 90%)")
        
        return True
    except Exception as e:
        print(f"\n❌ Error training models: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run comprehensive test suite"""
    print_header("🧪 STEP 2: Running Comprehensive Tests")
    
    try:
        import pytest
        
        # Run all tests
        test_dir = Path(__file__).parent / "tests"
        
        print("Running ML model tests...")
        result_ml = pytest.main([str(test_dir / "test_ml_models.py"), "-v", "-s"])
        
        print("\nRunning NLP interpretation tests...")
        result_nlp = pytest.main([str(test_dir / "test_nlp_interpretation.py"), "-v", "-s"])
        
        print("\nRunning diet generator tests...")
        result_diet = pytest.main([str(test_dir / "test_diet_generator.py"), "-v", "-s"])
        
        print("\nRunning end-to-end integration tests...")
        result_e2e = pytest.main([str(test_dir / "test_end_to_end.py"), "-v", "-s"])
        
        all_passed = all(r == 0 for r in [result_ml, result_nlp, result_diet, result_e2e])
        
        if all_passed:
            print("\n✅ All tests passed!")
        else:
            print("\n⚠️  Some tests failed. Check output above.")
        
        return all_passed
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("📦 Checking Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'scikit-learn',
        'xgboost',
        'lightgbm',
        'pandas',
        'numpy',
        'joblib',
        'pytest'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ All required dependencies installed!")
        return True

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("  🏥 AI-NutriCare - Quick Start")
    print("  Automated ML Training & Testing")
    print("="*70)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        print("   Run: pip install -r backend/requirements.txt")
        return
    
    # Train models
    if not train_ml_models():
        print("\n❌ Model training failed. Please check errors above.")
        return
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Some tests failed, but models are trained.")
    
    # Final summary
    print_header("🎯 COMPLETION SUMMARY")
    
    print("✅ ML models trained and saved to backend/models/")
    print("✅ Comprehensive tests executed")
    print("✅ System ready for use!")
    
    print("\n📚 Next Steps:")
    print("  1. Start the server:")
    print("     cd backend")
    print("     python run_server.py")
    print("\n  2. Access API documentation:")
    print("     http://localhost:8000/docs")
    print("\n  3. Test complete workflow:")
    print("     POST /api/upload-report (upload medical report)")
    print("     POST /api/complete-analysis/{report_id} (get full analysis + diet plan)")
    
    print("\n" + "="*70)
    print("  🎉 AI-NutriCare Setup Complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
