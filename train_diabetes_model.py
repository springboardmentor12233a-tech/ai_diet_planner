"""
ML Model Training Script - AI-NutriCare
Trains models using Pima Indians Diabetes Dataset for 90%+ accuracy
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import xgboost as xgb
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

class DiabetesModelTrainer:
    """Train ML models for diabetes prediction with 90%+ accuracy"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_path = self.project_root / "diabetes.csv"
        self.model_dir = self.project_root / "backend" / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.models = {}
        self.scaler = None
        self.feature_names = []
        
    def load_data(self):
        """Load Pima Indians Diabetes dataset"""
        print("\n📊 Loading Pima Indians Diabetes Dataset...")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        print(f"✅ Loaded {len(df)} samples with {len(df.columns)} features")
        print(f"   Features: {list(df.columns)}")
        print(f"   Positive cases: {df['Outcome'].sum()} ({df['Outcome'].mean()*100:.1f}%)")
        
        return df
    
    def prepare_data(self, df):
        """Prepare data for training"""
        print("\n🔧 Preparing data...")
        
        # Separate features and target
        X = df.drop('Outcome', axis=1)
        y = df['Outcome']
        
        self.feature_names = list(X.columns)
        
        # Handle zero values (replace with median for specific columns)
        zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        for col in zero_cols:
            if col in X.columns:
                median_val = X[X[col] != 0][col].median()
                X[col] = X[col].replace(0, median_val)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"✅ Training set: {len(X_train)} samples")
        print(f"✅ Test set: {len(X_test)} samples")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_random_forest(self, X_train, y_train):
        """Train Random Forest with hyperparameter tuning"""
        print("\n🌲 Training Random Forest...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(
            rf, param_grid, cv=5, scoring='accuracy', n_jobs=1, verbose=0
        )
        grid_search.fit(X_train, y_train)
        
        best_model = grid_search.best_estimator_
        cv_score = grid_search.best_score_
        
        print(f"✅ Best params: {grid_search.best_params_}")
        print(f"✅ Best CV score: {cv_score:.4f}")
        
        return best_model
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost with hyperparameter tuning"""
        print("\n🚀 Training XGBoost...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.3],
            'subsample': [0.8, 0.9, 1.0]
        }
        
        xgb_model = xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
        grid_search = GridSearchCV(
            xgb_model, param_grid, cv=5, scoring='accuracy', n_jobs=1, verbose=0
        )
        grid_search.fit(X_train, y_train)
        
        best_model = grid_search.best_estimator_
        cv_score = grid_search.best_score_
        
        print(f"✅ Best params: {grid_search.best_params_}")
        print(f"✅ Best CV score: {cv_score:.4f}")
        
        return best_model
    
    def train_lightgbm(self, X_train, y_train):
        """Train LightGBM with hyperparameter tuning"""
        print("\n💡 Training LightGBM...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [5, 10, 15],
            'learning_rate': [0.01, 0.1, 0.3],
            'num_leaves': [31, 50, 70]
        }
        
        lgb_model = lgb.LGBMClassifier(random_state=42, verbose=-1)
        grid_search = GridSearchCV(
            lgb_model, param_grid, cv=5, scoring='accuracy', n_jobs=1, verbose=0
        )
        grid_search.fit(X_train, y_train)
        
        best_model = grid_search.best_estimator_
        cv_score = grid_search.best_score_
        
        print(f"✅ Best params: {grid_search.best_params_}")
        print(f"✅ Best CV score: {cv_score:.4f}")
        
        return best_model
    
    def create_ensemble(self, rf_model, xgb_model, lgb_model):
        """Create ensemble model"""
        print("\n🎯 Creating Ensemble Model...")
        
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf_model),
                ('xgb', xgb_model),
                ('lgb', lgb_model)
            ],
            voting='soft'
        )
        
        return ensemble
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"\n📊 {model_name} Performance:")
        print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1 Score:  {f1:.4f}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def save_models(self, models):
        """Save trained models"""
        print("\n💾 Saving models...")
        
        for name, model in models.items():
            model_path = self.model_dir / f"{name}_model.pkl"
            joblib.dump(model, model_path)
            print(f"✅ Saved {name} to {model_path}")
        
        # Save scaler
        scaler_path = self.model_dir / "scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        print(f"✅ Saved scaler to {scaler_path}")
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'model_names': list(models.keys()),
            'dataset': 'Pima Indians Diabetes Database',
            'target': 'Diabetes (0=No, 1=Yes)'
        }
        metadata_path = self.model_dir / "model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved metadata to {metadata_path}")
    
    def train_all_models(self):
        """Complete training pipeline"""
        print("="*70)
        print("  🏥 AI-NutriCare ML Model Training")
        print("  📊 Dataset: Pima Indians Diabetes Database")
        print("  🎯 Target: 90%+ Accuracy")
        print("="*70)
        
        # Load data
        df = self.load_data()
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(df)
        
        # Train individual models
        rf_model = self.train_random_forest(X_train, y_train)
        xgb_model = self.train_xgboost(X_train, y_train)
        lgb_model = self.train_lightgbm(X_train, y_train)
        
        # Create and train ensemble
        ensemble_model = self.create_ensemble(rf_model, xgb_model, lgb_model)
        print("\n🎯 Training Ensemble Model...")
        ensemble_model.fit(X_train, y_train)
        print("✅ Ensemble model trained")
        
        # Evaluate all models
        print("\n" + "="*70)
        print("  📈 MODEL EVALUATION RESULTS")
        print("="*70)
        
        results = {}
        results['random_forest'] = self.evaluate_model(rf_model, X_test, y_test, "Random Forest")
        results['xgboost'] = self.evaluate_model(xgb_model, X_test, y_test, "XGBoost")
        results['lightgbm'] = self.evaluate_model(lgb_model, X_test, y_test, "LightGBM")
        results['ensemble'] = self.evaluate_model(ensemble_model, X_test, y_test, "Ensemble")
        
        # Save models
        models = {
            'random_forest': rf_model,
            'xgboost': xgb_model,
            'lightgbm': lgb_model,
            'ensemble': ensemble_model
        }
        self.save_models(models)
        
        # Save results
        results_path = self.model_dir / "training_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to {results_path}")
        
        # Final summary
        print("\n" + "="*70)
        print("  🎉 TRAINING COMPLETE!")
        print("="*70)
        
        best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
        best_accuracy = best_model[1]['accuracy']
        
        print(f"\n🏆 Best Model: {best_model[0].upper()}")
        print(f"   Accuracy: {best_accuracy*100:.2f}%")
        
        if best_accuracy >= 0.90:
            print(f"\n✅ SUCCESS! Achieved {best_accuracy*100:.2f}% accuracy (Target: 90%)")
        elif best_accuracy >= 0.85:
            print(f"\n⚠️  Close! Achieved {best_accuracy*100:.2f}% accuracy (Target: 90%)")
            print("   Consider: More feature engineering or ensemble tuning")
        else:
            print(f"\n⚠️  Achieved {best_accuracy*100:.2f}% accuracy (Target: 90%)")
            print("   Recommendation: Review data preprocessing and model parameters")
        
        print("\n📁 Models saved to:", self.model_dir)
        print("="*70 + "\n")
        
        return results

if __name__ == "__main__":
    trainer = DiabetesModelTrainer()
    results = trainer.train_all_models()
