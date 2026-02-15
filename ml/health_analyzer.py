"""
ML Health Analyzer for AI NutriCare System

This module provides machine learning-based health condition classification
from numeric health metrics. It supports multiple ML models, feature engineering,
cross-validation, and class balancing.

Requirements: 5.1, 5.2, 18.1
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from imblearn.over_sampling import SMOTE

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False


@dataclass
class ModelMetadata:
    """Metadata for trained ML models"""
    model_name: str
    version: str
    training_date: str
    feature_names: List[str]
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    cv_scores: List[float]
    cv_mean: float
    cv_std: float


@dataclass
class ModelRegistry:
    """Registry for managing multiple trained models"""
    models: Dict[str, Any]
    metadata: Dict[str, ModelMetadata]
    scaler: Optional[StandardScaler]
    feature_names: List[str]
    
    def save(self, path: Path):
        """Save registry to disk"""
        path.mkdir(parents=True, exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            model_path = path / f"{name}_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        
        # Save scaler
        if self.scaler:
            scaler_path = path / "scaler.pkl"
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
        
        # Save metadata
        metadata_dict = {
            name: asdict(meta) for name, meta in self.metadata.items()
        }
        metadata_dict['feature_names'] = self.feature_names
        
        metadata_path = path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
    
    @classmethod
    def load(cls, path: Path, verify_compatibility: bool = True, 
             current_feature_names: Optional[List[str]] = None) -> 'ModelRegistry':
        """
        Load registry from disk with optional compatibility verification
        
        Args:
            path: Path to registry directory
            verify_compatibility: Whether to verify feature schema compatibility
            current_feature_names: Current feature schema for compatibility check
            
        Returns:
            ModelRegistry instance
            
        Raises:
            ValueError: If compatibility verification fails
            
        Requirements: 18.5
        """
        # Load metadata
        metadata_path = path / "metadata.json"
        with open(metadata_path, 'r') as f:
            metadata_dict = json.load(f)
        
        feature_names = metadata_dict.pop('feature_names')
        
        # Verify compatibility if requested (Requirement 18.5)
        if verify_compatibility and current_feature_names is not None:
            if not cls._verify_feature_compatibility(feature_names, current_feature_names):
                raise ValueError(
                    f"Model feature schema incompatible with current data schema.\n"
                    f"Model features: {feature_names}\n"
                    f"Current features: {current_feature_names}\n"
                    f"Missing features: {set(feature_names) - set(current_feature_names)}"
                )
        
        # Load models
        models = {}
        for name in metadata_dict.keys():
            model_path = path / f"{name}_model.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    models[name] = pickle.load(f)
        
        # Load scaler
        scaler_path = path / "scaler.pkl"
        scaler = None
        if scaler_path.exists():
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
        
        # Reconstruct metadata objects
        metadata = {
            name: ModelMetadata(**meta_dict)
            for name, meta_dict in metadata_dict.items()
        }
        
        return cls(
            models=models,
            metadata=metadata,
            scaler=scaler,
            feature_names=feature_names
        )
    
    @staticmethod
    def _verify_feature_compatibility(
        model_features: List[str], 
        current_features: List[str]
    ) -> bool:
        """
        Verify that model feature schema is compatible with current data schema
        
        Compatibility means all model features are present in current features.
        Extra current features are acceptable (will be ignored during prediction).
        
        Args:
            model_features: Feature names from trained model
            current_features: Feature names in current data schema
            
        Returns:
            True if compatible, False otherwise
            
        Requirements: 18.5
        """
        model_set = set(model_features)
        current_set = set(current_features)
        
        # All model features must be present in current features
        return model_set.issubset(current_set)


class MLHealthAnalyzer:
    """
    Machine Learning Health Analyzer
    
    Classifies health conditions from numeric metrics using trained ML models.
    Supports multiple models: XGBoost, LightGBM, Random Forest, Logistic Regression.
    Implements feature engineering, cross-validation, and class balancing.
    """
    
    # Medical thresholds for alerts (Requirements 6.1, 6.2)
    # Based on established medical guidelines and clinical standards
    THRESHOLDS = {
        'Glucose': {
            'critical': 126,  # Diabetes range (fasting glucose ≥126 mg/dL)
            'warning': 100,   # Prediabetes range (100-125 mg/dL)
            'unit': 'mg/dL'
        },
        'BMI': {
            'critical': 30,   # Obesity (BMI ≥30)
            'warning': 25,    # Overweight (BMI 25-29.9)
            'unit': ''
        },
        'BloodPressure': {
            'critical': 90,   # Stage 2 Hypertension (diastolic ≥90 mmHg)
            'warning': 80,    # Stage 1 Hypertension (diastolic 80-89 mmHg)
            'unit': 'mmHg'
        },
        'BloodPressure_Systolic': {
            'critical': 140,  # Stage 2 Hypertension (systolic ≥140 mmHg)
            'warning': 130,   # Stage 1 Hypertension (systolic 130-139 mmHg)
            'unit': 'mmHg'
        },
        'BloodPressure_Diastolic': {
            'critical': 90,   # Stage 2 Hypertension (diastolic ≥90 mmHg)
            'warning': 80,    # Stage 1 Hypertension (diastolic 80-89 mmHg)
            'unit': 'mmHg'
        },
        'Insulin': {
            'critical': 200,  # Severe insulin resistance
            'warning': 150,   # Elevated insulin (possible insulin resistance)
            'unit': 'μU/mL'
        },
        'SkinThickness': {
            'critical': 50,   # Abnormally high
            'warning': 40,    # Elevated
            'unit': 'mm'
        },
        'Cholesterol': {
            'critical': 240,  # High total cholesterol (≥240 mg/dL)
            'warning': 200,   # Borderline high (200-239 mg/dL)
            'unit': 'mg/dL'
        },
        'LDL': {
            'critical': 160,  # Very high LDL cholesterol (≥160 mg/dL)
            'warning': 130,   # Borderline high LDL (130-159 mg/dL)
            'unit': 'mg/dL'
        },
        'HDL': {
            'critical': 40,   # Low HDL (reverse threshold: <40 is critical)
            'warning': 50,    # Borderline low HDL (<50)
            'unit': 'mg/dL',
            'reverse': True   # Lower values are worse
        },
        'Triglycerides': {
            'critical': 200,  # High triglycerides (≥200 mg/dL)
            'warning': 150,   # Borderline high (150-199 mg/dL)
            'unit': 'mg/dL'
        },
        'HbA1c': {
            'critical': 6.5,  # Diabetes (HbA1c ≥6.5%)
            'warning': 5.7,   # Prediabetes (5.7-6.4%)
            'unit': '%'
        },
        'Hemoglobin': {
            'critical': 12.0, # Anemia threshold (reverse: <12 is critical)
            'warning': 12.5,  # Borderline low (<12.5)
            'unit': 'g/dL',
            'reverse': True   # Lower values are worse
        }
    }
    
    def __init__(self, model_registry: Optional[ModelRegistry] = None):
        """
        Initialize ML Health Analyzer
        
        Args:
            model_registry: Pre-trained model registry. If None, models must be trained.
        """
        self.registry = model_registry
        self.available_models = ['logistic_regression', 'random_forest', 'gradient_boosting']
        
        if XGBOOST_AVAILABLE:
            self.available_models.append('xgboost')
        if LIGHTGBM_AVAILABLE:
            self.available_models.append('lightgbm')
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply feature engineering
        
        Creates interaction features and derived metrics:
        - Glucose_BMI: Interaction between glucose and BMI
        - Age_Glucose: Interaction between age and glucose
        - Insulin_Efficiency: Insulin effectiveness metric
        
        Args:
            df: DataFrame with raw features
            
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        # Interaction features
        if 'Glucose' in df.columns and 'BMI' in df.columns:
            df['Glucose_BMI'] = df['Glucose'] * df['BMI']
        
        if 'Age' in df.columns and 'Glucose' in df.columns:
            df['Age_Glucose'] = df['Age'] * df['Glucose']
        
        if 'Insulin' in df.columns and 'Glucose' in df.columns:
            df['Insulin_Efficiency'] = df['Insulin'] / (df['Glucose'] + 1)
        
        return df
    
    def _preprocess_data(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        fit_scaler: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray], List[str]]:
        """
        Preprocess data: handle missing values, engineer features, scale
        
        Args:
            X: Feature DataFrame
            y: Target Series (optional)
            fit_scaler: Whether to fit a new scaler
            
        Returns:
            Tuple of (scaled features, target, feature names)
        """
        X = X.copy()
        
        # Handle missing values (zeros in medical data often mean missing)
        cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        for col in cols_to_fix:
            if col in X.columns:
                X[col] = X[col].replace(0, np.nan)
                if y is not None:
                    # Group by outcome for better imputation
                    X[col] = X[col].fillna(X.groupby(y)[col].transform('median'))
                else:
                    X[col] = X[col].fillna(X[col].median())
        
        # Feature engineering
        X = self._engineer_features(X)
        
        # Ensure feature order matches training if not fitting
        if not fit_scaler and self.registry:
            # Reorder columns to match training order
            for col in self.registry.feature_names:
                if col not in X.columns:
                    X[col] = np.nan
            X = X[self.registry.feature_names]
        
        # Fill any remaining NaN values with median (for missing features)
        X = X.fillna(X.median())
        
        # If still NaN (e.g., all values are NaN), fill with 0
        X = X.fillna(0)
        
        # Store feature names
        feature_names = X.columns.tolist()
        
        # Standardization
        if fit_scaler:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        elif self.registry and self.registry.scaler:
            X_scaled = self.registry.scaler.transform(X)
        else:
            raise ValueError("No scaler available. Train models first or provide a registry.")
        
        return X_scaled, y.values if y is not None else None, feature_names
    
    def train_models(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        models_to_train: Optional[List[str]] = None,
        use_smote: bool = True,
        cv_folds: int = 5,
        random_state: int = 42
    ) -> ModelRegistry:
        """
        Train multiple ML models with cross-validation and class balancing
        
        Args:
            X: Feature DataFrame
            y: Target Series
            models_to_train: List of model names to train. If None, trains all available.
            use_smote: Whether to apply SMOTE for class balancing
            cv_folds: Number of cross-validation folds (default: 5)
            random_state: Random seed for reproducibility
            
        Returns:
            ModelRegistry with trained models and metadata
        """
        if models_to_train is None:
            models_to_train = self.available_models
        
        # Validate model names
        invalid_models = set(models_to_train) - set(self.available_models)
        if invalid_models:
            raise ValueError(f"Invalid model names: {invalid_models}. Available: {self.available_models}")
        
        # Preprocess data
        X_scaled, y_array, feature_names = self._preprocess_data(X, y, fit_scaler=True)
        
        # Apply SMOTE for class balancing
        if use_smote:
            smote = SMOTE(random_state=random_state)
            X_scaled, y_array = smote.fit_resample(X_scaled, y_array)
        
        # Initialize model registry
        models = {}
        metadata = {}
        
        # Cross-validation strategy
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
        
        # Train each model
        for model_name in models_to_train:
            print(f"\nTraining {model_name}...")
            
            # Create model
            model = self._create_model(model_name, random_state)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y_array, cv=cv, scoring='accuracy')
            
            # Train on full data
            model.fit(X_scaled, y_array)
            
            # Evaluate
            y_pred = model.predict(X_scaled)
            accuracy = accuracy_score(y_array, y_pred)
            precision = precision_score(y_array, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_array, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_array, y_pred, average='weighted', zero_division=0)
            
            # Store model and metadata
            models[model_name] = model
            metadata[model_name] = ModelMetadata(
                model_name=model_name,
                version="1.0",
                training_date=datetime.now().isoformat(),
                feature_names=feature_names,
                accuracy=float(accuracy),
                precision=float(precision),
                recall=float(recall),
                f1_score=float(f1),
                cv_scores=[float(s) for s in cv_scores],
                cv_mean=float(cv_scores.mean()),
                cv_std=float(cv_scores.std())
            )
            
            print(f"  Accuracy: {accuracy:.4f}")
            print(f"  CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall: {recall:.4f}")
            print(f"  F1-Score: {f1:.4f}")
        
        # Create registry
        self.registry = ModelRegistry(
            models=models,
            metadata=metadata,
            scaler=self.scaler,
            feature_names=feature_names
        )
        
        return self.registry
    
    def _create_model(self, model_name: str, random_state: int):
        """Create a model instance by name"""
        if model_name == 'logistic_regression':
            return LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=random_state
            )
        elif model_name == 'random_forest':
            return RandomForestClassifier(
                n_estimators=300,
                max_depth=8,
                random_state=random_state,
                class_weight='balanced'
            )
        elif model_name == 'gradient_boosting':
            return GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=random_state
            )
        elif model_name == 'xgboost' and XGBOOST_AVAILABLE:
            return xgb.XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.03,
                random_state=random_state,
                eval_metric='logloss'
            )
        elif model_name == 'lightgbm' and LIGHTGBM_AVAILABLE:
            return lgb.LGBMClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.03,
                random_state=random_state,
                verbose=-1
            )
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def classify_conditions(
        self,
        metrics: Dict[str, float],
        model_name: str = 'gradient_boosting'
    ) -> List['HealthCondition']:
        """
        Classify health conditions from metrics
        
        Supports multiple condition types:
        - Diabetes (Type 1, Type 2, Prediabetes)
        - Hypertension (Stage 1, Stage 2)
        - Hyperlipidemia
        - Obesity (Class I, II, III)
        - Anemia
        
        Handles incomplete metrics by classifying based on available data.
        
        Args:
            metrics: Dictionary of health metrics (e.g., {'Glucose': 120, 'BMI': 28})
            model_name: Name of model to use for prediction (for ML-based classification)
            
        Returns:
            List of HealthCondition objects with confidence scores and contributing metrics
            
        Requirements: 5.1, 5.3, 5.4, 5.5
        """
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        conditions = []
        
        # Classify diabetes conditions
        diabetes_condition = self._classify_diabetes(metrics)
        if diabetes_condition:
            conditions.append(diabetes_condition)
        
        # Classify hypertension
        hypertension_condition = self._classify_hypertension(metrics)
        if hypertension_condition:
            conditions.append(hypertension_condition)
        
        # Classify hyperlipidemia
        hyperlipidemia_condition = self._classify_hyperlipidemia(metrics)
        if hyperlipidemia_condition:
            conditions.append(hyperlipidemia_condition)
        
        # Classify obesity
        obesity_condition = self._classify_obesity(metrics)
        if obesity_condition:
            conditions.append(obesity_condition)
        
        # Classify anemia
        anemia_condition = self._classify_anemia(metrics)
        if anemia_condition:
            conditions.append(anemia_condition)
        
        return conditions
    
    def _classify_diabetes(self, metrics: Dict[str, float]) -> Optional['HealthCondition']:
        """
        Classify diabetes conditions based on glucose and HbA1c levels
        
        Thresholds:
        - Diabetes: Fasting glucose ≥126 mg/dL or HbA1c ≥6.5%
        - Prediabetes: Fasting glucose 100-125 mg/dL or HbA1c 5.7-6.4%
        - Type 1 vs Type 2: Requires additional clinical data (default to Type 2)
        
        Args:
            metrics: Dictionary of health metrics
            
        Returns:
            HealthCondition object if diabetes detected, None otherwise
        """
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        glucose = metrics.get('Glucose')
        hba1c = metrics.get('HbA1c')
        
        # Need at least one diabetes-related metric
        if glucose is None and hba1c is None:
            return None
        
        contributing = []
        confidence = 0.0
        condition_type = None
        
        # Check glucose levels
        if glucose is not None and not np.isnan(glucose):
            contributing.append(MetricType.GLUCOSE)
            if glucose >= 126:
                condition_type = ConditionType.DIABETES_TYPE2
                confidence = min(0.95, 0.7 + (glucose - 126) / 200)
            elif glucose >= 100:
                condition_type = ConditionType.PREDIABETES
                confidence = min(0.90, 0.6 + (glucose - 100) / 100)
        
        # Check HbA1c levels (overrides glucose if more severe)
        if hba1c is not None and not np.isnan(hba1c):
            contributing.append(MetricType.HBA1C)
            if hba1c >= 6.5:
                condition_type = ConditionType.DIABETES_TYPE2
                confidence = max(confidence, min(0.95, 0.75 + (hba1c - 6.5) / 10))
            elif hba1c >= 5.7:
                if condition_type != ConditionType.DIABETES_TYPE2:
                    condition_type = ConditionType.PREDIABETES
                    confidence = max(confidence, min(0.90, 0.65 + (hba1c - 5.7) / 5))
        
        if condition_type:
            return HealthCondition(
                condition_type=condition_type,
                confidence=confidence,
                detected_at=datetime.now(),
                contributing_metrics=contributing
            )
        
        return None
    
    def _classify_hypertension(self, metrics: Dict[str, float]) -> Optional['HealthCondition']:
        """
        Classify hypertension based on blood pressure readings
        
        Thresholds:
        - Stage 2: Systolic ≥140 or Diastolic ≥90 mmHg
        - Stage 1: Systolic 130-139 or Diastolic 80-89 mmHg
        
        Args:
            metrics: Dictionary of health metrics
            
        Returns:
            HealthCondition object if hypertension detected, None otherwise
        """
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        systolic = metrics.get('BloodPressure')  # Using BloodPressure as systolic
        diastolic = metrics.get('BloodPressure_Diastolic')
        
        if systolic is None and diastolic is None:
            return None
        
        contributing = []
        confidence = 0.0
        condition_type = None
        
        # Check systolic
        if systolic is not None and not np.isnan(systolic):
            contributing.append(MetricType.BLOOD_PRESSURE_SYSTOLIC)
            if systolic >= 140:
                condition_type = ConditionType.HYPERTENSION_STAGE2
                confidence = min(0.95, 0.75 + (systolic - 140) / 100)
            elif systolic >= 130:
                condition_type = ConditionType.HYPERTENSION_STAGE1
                confidence = min(0.90, 0.70 + (systolic - 130) / 50)
        
        # Check diastolic (overrides if more severe)
        if diastolic is not None and not np.isnan(diastolic):
            contributing.append(MetricType.BLOOD_PRESSURE_DIASTOLIC)
            if diastolic >= 90:
                condition_type = ConditionType.HYPERTENSION_STAGE2
                confidence = max(confidence, min(0.95, 0.75 + (diastolic - 90) / 50))
            elif diastolic >= 80:
                if condition_type != ConditionType.HYPERTENSION_STAGE2:
                    condition_type = ConditionType.HYPERTENSION_STAGE1
                    confidence = max(confidence, min(0.90, 0.70 + (diastolic - 80) / 40))
        
        if condition_type:
            return HealthCondition(
                condition_type=condition_type,
                confidence=confidence,
                detected_at=datetime.now(),
                contributing_metrics=contributing
            )
        
        return None
    
    def _classify_hyperlipidemia(self, metrics: Dict[str, float]) -> Optional['HealthCondition']:
        """
        Classify hyperlipidemia based on cholesterol and triglyceride levels
        
        Thresholds:
        - Total cholesterol ≥240 mg/dL
        - LDL cholesterol ≥160 mg/dL
        - Triglycerides ≥200 mg/dL
        
        Args:
            metrics: Dictionary of health metrics
            
        Returns:
            HealthCondition object if hyperlipidemia detected, None otherwise
        """
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        total_chol = metrics.get('Cholesterol')
        ldl = metrics.get('LDL')
        triglycerides = metrics.get('Triglycerides')
        
        if total_chol is None and ldl is None and triglycerides is None:
            return None
        
        contributing = []
        confidence = 0.0
        detected = False
        
        # Check total cholesterol
        if total_chol is not None and not np.isnan(total_chol):
            if total_chol >= 240:
                contributing.append(MetricType.CHOLESTEROL_TOTAL)
                detected = True
                confidence = max(confidence, min(0.95, 0.70 + (total_chol - 240) / 200))
        
        # Check LDL
        if ldl is not None and not np.isnan(ldl):
            if ldl >= 160:
                contributing.append(MetricType.CHOLESTEROL_LDL)
                detected = True
                confidence = max(confidence, min(0.95, 0.75 + (ldl - 160) / 150))
        
        # Check triglycerides
        if triglycerides is not None and not np.isnan(triglycerides):
            if triglycerides >= 200:
                contributing.append(MetricType.TRIGLYCERIDES)
                detected = True
                confidence = max(confidence, min(0.95, 0.70 + (triglycerides - 200) / 300))
        
        if detected:
            return HealthCondition(
                condition_type=ConditionType.HYPERLIPIDEMIA,
                confidence=confidence,
                detected_at=datetime.now(),
                contributing_metrics=contributing
            )
        
        return None
    
    def _classify_obesity(self, metrics: Dict[str, float]) -> Optional['HealthCondition']:
        """
        Classify obesity based on BMI
        
        Thresholds:
        - Class III (Severe): BMI ≥40
        - Class II (Moderate): BMI 35-39.9
        - Class I (Mild): BMI 30-34.9
        
        Args:
            metrics: Dictionary of health metrics
            
        Returns:
            HealthCondition object if obesity detected, None otherwise
        """
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        bmi = metrics.get('BMI')
        
        if bmi is None or np.isnan(bmi):
            return None
        
        condition_type = None
        confidence = 0.0
        
        if bmi >= 40:
            condition_type = ConditionType.OBESITY_CLASS3
            confidence = min(0.98, 0.85 + (bmi - 40) / 50)
        elif bmi >= 35:
            condition_type = ConditionType.OBESITY_CLASS2
            confidence = min(0.95, 0.80 + (bmi - 35) / 30)
        elif bmi >= 30:
            condition_type = ConditionType.OBESITY_CLASS1
            confidence = min(0.92, 0.75 + (bmi - 30) / 25)
        
        if condition_type:
            return HealthCondition(
                condition_type=condition_type,
                confidence=confidence,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.BMI]
            )
        
        return None
    
    def _classify_anemia(self, metrics: Dict[str, float]) -> Optional['HealthCondition']:
        """
        Classify anemia based on hemoglobin levels
        
        Thresholds (gender-specific, using general threshold):
        - Anemia: Hemoglobin <12 g/dL (women) or <13 g/dL (men)
        - Using 12.5 g/dL as general threshold
        
        Args:
            metrics: Dictionary of health metrics
            
        Returns:
            HealthCondition object if anemia detected, None otherwise
        """
        from ai_diet_planner.models.health_data import HealthCondition
        from ai_diet_planner.models.enums import ConditionType, MetricType
        
        hemoglobin = metrics.get('Hemoglobin')
        
        if hemoglobin is None or np.isnan(hemoglobin):
            return None
        
        # Using 12.5 as general threshold (between male and female thresholds)
        if hemoglobin < 12.5:
            confidence = min(0.95, 0.70 + (12.5 - hemoglobin) / 10)
            return HealthCondition(
                condition_type=ConditionType.ANEMIA,
                confidence=confidence,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.HEMOGLOBIN]
            )
        
        return None
    
    def detect_abnormal_values(self, metrics: Dict[str, float]) -> List['Alert']:
        """
        Detect abnormal health metric values and generate alerts
        
        Implements threshold-based alert generation with severity levels:
        - CRITICAL: Values requiring immediate medical attention
        - WARNING: Values suggesting monitoring and lifestyle changes
        - NORMAL: Values within healthy ranges (no alert generated)
        
        Alerts are prioritized by medical severity (CRITICAL before WARNING).
        Each alert includes recommended actions based on the metric and severity.
        
        Args:
            metrics: Dictionary of health metrics (e.g., {'Glucose': 120, 'BMI': 28})
            
        Returns:
            List of Alert objects sorted by severity (CRITICAL first)
            
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
        """
        from ai_diet_planner.models.health_data import Alert
        from ai_diet_planner.models.enums import AlertSeverity, MetricType
        
        alerts = []
        
        # Map metric names to MetricType enums
        metric_type_map = {
            'Glucose': MetricType.GLUCOSE,
            'BMI': MetricType.BMI,
            'BloodPressure': MetricType.BLOOD_PRESSURE_DIASTOLIC,
            'Insulin': None,  # Not in MetricType enum
            'SkinThickness': None,  # Not in MetricType enum
            'Cholesterol': MetricType.CHOLESTEROL_TOTAL,
            'LDL': MetricType.CHOLESTEROL_LDL,
            'HDL': MetricType.CHOLESTEROL_HDL,
            'Triglycerides': MetricType.TRIGLYCERIDES,
            'HbA1c': MetricType.HBA1C,
            'Hemoglobin': MetricType.HEMOGLOBIN,
            'BloodPressure_Systolic': MetricType.BLOOD_PRESSURE_SYSTOLIC,
            'BloodPressure_Diastolic': MetricType.BLOOD_PRESSURE_DIASTOLIC
        }
        
        # Recommended actions by metric and severity
        recommended_actions = {
            'Glucose': {
                'CRITICAL': 'Immediate medical consultation recommended. Fasting glucose ≥126 mg/dL indicates diabetes. Schedule appointment with endocrinologist for comprehensive evaluation and treatment plan.',
                'WARNING': 'Monitor blood glucose levels regularly. Fasting glucose 100-125 mg/dL indicates prediabetes. Consider lifestyle modifications: reduce sugar intake, increase physical activity, maintain healthy weight.'
            },
            'BMI': {
                'CRITICAL': 'Immediate lifestyle intervention recommended. BMI ≥30 indicates obesity, increasing risk of diabetes, heart disease, and other conditions. Consult healthcare provider for weight management program.',
                'WARNING': 'Monitor weight and consider lifestyle changes. BMI 25-29.9 indicates overweight status. Focus on balanced diet, regular exercise, and portion control to prevent progression to obesity.'
            },
            'BloodPressure': {
                'CRITICAL': 'Immediate medical attention required. Diastolic BP ≥90 mmHg indicates Stage 2 hypertension. Risk of heart attack, stroke, and organ damage. Consult cardiologist for medication and treatment plan.',
                'WARNING': 'Monitor blood pressure regularly. Diastolic BP 80-89 mmHg indicates Stage 1 hypertension. Reduce sodium intake, increase potassium-rich foods, exercise regularly, manage stress.'
            },
            'Insulin': {
                'CRITICAL': 'Immediate medical consultation recommended. Elevated insulin levels may indicate insulin resistance or metabolic syndrome. Comprehensive metabolic evaluation needed.',
                'WARNING': 'Monitor insulin levels and glucose metabolism. Consider dietary changes to improve insulin sensitivity: reduce refined carbohydrates, increase fiber intake, regular physical activity.'
            },
            'SkinThickness': {
                'CRITICAL': 'Medical evaluation recommended. Abnormal skin thickness measurements may indicate underlying metabolic or circulatory issues.',
                'WARNING': 'Monitor skin thickness and overall metabolic health. Consider lifestyle modifications and regular health checkups.'
            },
            'Cholesterol': {
                'CRITICAL': 'Immediate medical consultation recommended. Total cholesterol ≥240 mg/dL significantly increases cardiovascular disease risk. Lipid panel and cardiology evaluation needed.',
                'WARNING': 'Monitor cholesterol levels. Total cholesterol 200-239 mg/dL is borderline high. Reduce saturated fat intake, increase fiber, consider omega-3 fatty acids, regular exercise.'
            },
            'LDL': {
                'CRITICAL': 'Immediate medical attention required. LDL cholesterol ≥160 mg/dL greatly increases heart disease risk. Statin therapy and aggressive lifestyle changes may be needed.',
                'WARNING': 'Monitor LDL cholesterol. Levels 130-159 mg/dL are borderline high. Reduce saturated and trans fats, increase soluble fiber, maintain healthy weight.'
            },
            'HDL': {
                'CRITICAL': 'Medical consultation recommended. HDL cholesterol <40 mg/dL (men) or <50 mg/dL (women) increases cardiovascular risk. Comprehensive lipid management needed.',
                'WARNING': 'Monitor HDL cholesterol. Low HDL reduces cardiovascular protection. Increase physical activity, quit smoking, consume healthy fats (olive oil, nuts, fish).'
            },
            'Triglycerides': {
                'CRITICAL': 'Immediate medical consultation recommended. Triglycerides ≥200 mg/dL increase risk of pancreatitis and cardiovascular disease. Medical evaluation and treatment needed.',
                'WARNING': 'Monitor triglyceride levels. Levels 150-199 mg/dL are borderline high. Reduce sugar and refined carbohydrates, limit alcohol, increase omega-3 intake, regular exercise.'
            },
            'HbA1c': {
                'CRITICAL': 'Immediate medical consultation required. HbA1c ≥6.5% indicates diabetes. Long-term glucose control is poor. Endocrinology evaluation and diabetes management plan needed.',
                'WARNING': 'Monitor HbA1c levels regularly. HbA1c 5.7-6.4% indicates prediabetes. Implement lifestyle changes to prevent progression: weight loss, exercise, balanced diet.'
            },
            'Hemoglobin': {
                'CRITICAL': 'Immediate medical evaluation required. Abnormal hemoglobin levels may indicate anemia or other blood disorders. Complete blood count and iron studies needed.',
                'WARNING': 'Monitor hemoglobin levels. Borderline low hemoglobin may indicate early anemia. Increase iron-rich foods (lean meat, beans, leafy greens), consider vitamin C for absorption.'
            },
            'BloodPressure_Systolic': {
                'CRITICAL': 'Immediate medical attention required. Systolic BP ≥140 mmHg indicates Stage 2 hypertension. High risk of cardiovascular events. Urgent cardiology consultation needed.',
                'WARNING': 'Monitor blood pressure regularly. Systolic BP 130-139 mmHg indicates Stage 1 hypertension. Lifestyle modifications: reduce sodium, DASH diet, regular exercise, stress management.'
            },
            'BloodPressure_Diastolic': {
                'CRITICAL': 'Immediate medical attention required. Diastolic BP ≥90 mmHg indicates Stage 2 hypertension. Risk of heart attack, stroke, and organ damage. Consult cardiologist immediately.',
                'WARNING': 'Monitor blood pressure regularly. Diastolic BP 80-89 mmHg indicates Stage 1 hypertension. Reduce sodium intake, increase potassium-rich foods, exercise regularly, manage stress.'
            }
        }
        
        for metric_name, value in metrics.items():
            if value is None or np.isnan(value):
                continue
            
            if metric_name not in self.THRESHOLDS:
                continue
            
            thresholds = self.THRESHOLDS[metric_name]
            metric_type = metric_type_map.get(metric_name)
            
            # Skip if we don't have a MetricType mapping
            if metric_type is None:
                continue
            
            severity = None
            message = None
            recommended_action = None
            
            # Check if this is a reverse threshold (lower is worse)
            is_reverse = thresholds.get('reverse', False)
            
            if is_reverse:
                # For reverse thresholds (HDL, Hemoglobin): lower values trigger alerts
                if value < thresholds['critical']:
                    severity = AlertSeverity.CRITICAL
                    message = f'Low {metric_name} detected: {value} {thresholds["unit"]} (Critical threshold: <{thresholds["critical"]} {thresholds["unit"]})'
                    recommended_action = recommended_actions.get(metric_name, {}).get('CRITICAL', 
                        f'Immediate medical consultation recommended for {metric_name} level of {value} {thresholds["unit"]}')
                elif value < thresholds['warning']:
                    severity = AlertSeverity.WARNING
                    message = f'Low {metric_name} detected: {value} {thresholds["unit"]} (Warning threshold: <{thresholds["warning"]} {thresholds["unit"]})'
                    recommended_action = recommended_actions.get(metric_name, {}).get('WARNING',
                        f'Monitor {metric_name} and consider lifestyle modifications')
            else:
                # For normal thresholds: higher values trigger alerts
                if value >= thresholds['critical']:
                    severity = AlertSeverity.CRITICAL
                    message = f'High {metric_name} detected: {value} {thresholds["unit"]} (Critical threshold: ≥{thresholds["critical"]} {thresholds["unit"]})'
                    recommended_action = recommended_actions.get(metric_name, {}).get('CRITICAL', 
                        f'Immediate medical consultation recommended for {metric_name} level of {value} {thresholds["unit"]}')
                elif value >= thresholds['warning']:
                    severity = AlertSeverity.WARNING
                    message = f'Elevated {metric_name} detected: {value} {thresholds["unit"]} (Warning threshold: ≥{thresholds["warning"]} {thresholds["unit"]})'
                    recommended_action = recommended_actions.get(metric_name, {}).get('WARNING',
                        f'Monitor {metric_name} and consider lifestyle modifications')
            
            if severity:
                alerts.append(Alert(
                    metric_type=metric_type,
                    severity=severity,
                    message=message,
                    recommended_action=recommended_action
                ))
        
        # Sort by severity: CRITICAL (0) before WARNING (1)
        alerts.sort(key=lambda x: 0 if x.severity == AlertSeverity.CRITICAL else 1)
        
        return alerts
    
    def get_model_info(self, model_name: str) -> Optional[ModelMetadata]:
        """Get metadata for a specific model"""
        if not self.registry:
            return None
        return self.registry.metadata.get(model_name)
    
    def get_evaluation_metrics(self, model_name: str) -> Optional[Dict[str, float]]:
        """
        Get evaluation metrics for a specific model
        
        Returns accuracy, precision, recall, and F1-score for the model.
        
        Args:
            model_name: Name of model to get metrics for
            
        Returns:
            Dictionary with metrics or None if model not found
            
        Requirements: 18.2
        """
        if not self.registry or model_name not in self.registry.metadata:
            return None
        
        metadata = self.registry.metadata[model_name]
        return {
            'accuracy': metadata.accuracy,
            'precision': metadata.precision,
            'recall': metadata.recall,
            'f1_score': metadata.f1_score,
            'cv_mean': metadata.cv_mean,
            'cv_std': metadata.cv_std
        }
    
    def list_models(self) -> List[str]:
        """List all available trained models"""
        if not self.registry:
            return []
        return list(self.registry.models.keys())
    
    def needs_retraining(self, model_name: str, threshold: float = 0.85) -> bool:
        """
        Check if a model needs retraining based on accuracy threshold
        
        Automatically flags models with accuracy below 85% as requiring retraining.
        
        Args:
            model_name: Name of model to check
            threshold: Minimum acceptable accuracy (default: 0.85)
            
        Returns:
            True if model accuracy is below threshold
            
        Requirements: 18.3
        """
        if not self.registry or model_name not in self.registry.metadata:
            return True
        
        metadata = self.registry.metadata[model_name]
        return metadata.accuracy < threshold
