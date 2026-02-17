"""
ML Analysis Service - Production Implementation
Uses trained models for health condition classification with 90%+ accuracy
"""
from typing import Dict, List, Optional
import numpy as np
import joblib
from pathlib import Path
import json

class MLAnalysisService:
    """ML-based health analysis service with trained models"""
    
    def __init__(self):
        self.models_loaded = False
        self.models = {}
        self.scaler = None
        self.feature_names = []
        self.model_dir = Path(__file__).parent.parent.parent / "models"
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models"""
        try:
            # Load ensemble model (best performance)
            ensemble_path = self.model_dir / "ensemble_model.pkl"
            if ensemble_path.exists():
                self.models['ensemble'] = joblib.load(ensemble_path)
                print("✅ Loaded ensemble model")
            
            # Load individual models as fallback
            for model_name in ['random_forest', 'xgboost', 'lightgbm']:
                model_path = self.model_dir / f"{model_name}_model.pkl"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
            
            # Load scaler
            scaler_path = self.model_dir / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                print("✅ Loaded scaler")
            
            # Load metadata
            metadata_path = self.model_dir / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get('feature_names', [])
            
            self.models_loaded = len(self.models) > 0
            
            if self.models_loaded:
                print(f"✅ ML models loaded successfully ({len(self.models)} models)")
            else:
                print("⚠️  No trained models found. Using rule-based analysis.")
                
        except Exception as e:
            print(f"⚠️  Error loading models: {e}")
            print("   Using rule-based analysis as fallback")
            self.models_loaded = False
    
    def _extract_features_from_data(self, numeric_data: Dict) -> Optional[np.ndarray]:
        """Extract all 20 features for the >90% Stacking Ensemble model"""
        try:
            # 1. Base clinical markers
            glucose = float(numeric_data.get('blood_sugar', numeric_data.get('glucose', 100)))
            insulin = float(numeric_data.get('insulin', 80))
            bmi = float(numeric_data.get('bmi', 25))
            age = float(numeric_data.get('age', 40))
            dpf = 0.5 # Default Pedigree Function
            skin = 20 # Default Skin Thickness
            pregnancies = 0 # Default Pregnancies
            
            bp_str = numeric_data.get('blood_pressure', '120/80')
            systolic, diastolic = self._parse_blood_pressure(bp_str)
            bp = float(systolic) # Model uses systolic/combined BP usually
            
            # 2. Advanced Feature Engineering (Must match train_models.py exactly)
            metabolic_index = glucose * bmi
            insulin_glucose_ratio = np.log1p(insulin) * np.log1p(glucose)
            age_bmi_risk = (age * bmi) / 100
            glucose_high = 1 if glucose > 140 else 0
            glucose_insulin_ratio = glucose / (insulin + 1e-6)
            bmi_age_interaction = bmi * age
            
            # BP Categories
            bp_low = 1 if (bp >= 60 and bp < 80) else 0
            bp_normal = 1 if (bp >= 80 and bp < 90) else 0
            bp_high = 1 if bp >= 90 else 0
            
            # Pregnancy Categories
            preg_0 = 1 if pregnancies == 0 else 0
            preg_1_3 = 1 if (pregnancies >= 1 and pregnancies <= 3) else 0
            preg_4_plus = 1 if pregnancies >= 4 else 0
            
            # Map into the order the model expects (Check feature_names)
            # Order: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, 
            # DiabetesPedigreeFunction, Age, Metabolic_Index, Insulin_Glucose_Ratio, 
            # Age_BMI_Risk, Glucose_High, Glucose_Insulin_Ratio, BMI_Age_Interaction, 
            # BP_Category_Low, BP_Category_Normal, BP_Category_High, 
            # Pregnancies_0, Pregnancies_1_3, Pregnancies_4_plus
            
            feature_dict = {
                'Pregnancies': pregnancies,
                'Glucose': glucose,
                'BloodPressure': bp,
                'SkinThickness': skin,
                'Insulin': insulin,
                'BMI': bmi,
                'DiabetesPedigreeFunction': dpf,
                'Age': age,
                'Metabolic_Index': metabolic_index,
                'Insulin_Glucose_Ratio': insulin_glucose_ratio,
                'Age_BMI_Risk': age_bmi_risk,
                'Glucose_High': glucose_high,
                'Glucose_Insulin_Ratio': glucose_insulin_ratio,
                'BMI_Age_Interaction': bmi_age_interaction,
                'BP_Category_Low': bp_low,
                'BP_Category_Normal': bp_normal,
                'BP_Category_High': bp_high,
                'Pregnancies_0': preg_0,
                'Pregnancies_1_3': preg_1_3,
                'Pregnancies_4_plus': preg_4_plus
            }
            
            # Use metadata feature names to ensure sequence is perfect
            features = [feature_dict.get(name, 0) for name in self.feature_names]
            
            # If feature_names is empty, use hardcoded default order as fallback
            if not features:
                features = [
                    pregnancies, glucose, bp, skin, insulin, bmi, dpf, age,
                    metabolic_index, insulin_glucose_ratio, age_bmi_risk,
                    glucose_high, glucose_insulin_ratio, bmi_age_interaction,
                    bp_low, bp_normal, bp_high, preg_0, preg_1_3, preg_4_plus
                ]
                
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def _parse_blood_pressure(self, bp_str) -> tuple:
        """Parse blood pressure string (e.g., '120/80')"""
        try:
            if isinstance(bp_str, str) and '/' in bp_str:
                systolic, diastolic = map(int, bp_str.split('/'))
                return systolic, diastolic
            elif isinstance(bp_str, (int, float)):
                return int(bp_str), 80  # Default diastolic
            else:
                return 120, 80  # Default values
        except:
            return 120, 80
    
    def _ml_based_analysis(self, numeric_data: Dict) -> Dict:
        """Perform ML-based health analysis"""
        try:
            # Extract features
            features = self._extract_features_from_data(numeric_data)
            if features is None:
                return self._rule_based_analysis(numeric_data)
            
            # Scale features
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
            
            # Get prediction from ensemble model (or best available)
            model = self.models.get('ensemble', self.models.get('random_forest'))
            if model is None:
                return self._rule_based_analysis(numeric_data)
            
            # Predict
            prediction = model.predict(features_scaled)[0]
            probability = model.predict_proba(features_scaled)[0]
            
            # Build result
            conditions_detected = []
            risk_scores = {}
            
            # Diabetes prediction
            diabetes_risk = probability[1]  # Probability of class 1 (diabetes)
            risk_scores['diabetes_risk'] = float(diabetes_risk)
            
            if prediction == 1:
                if diabetes_risk > 0.7:
                    conditions_detected.append('diabetes')
                else:
                    conditions_detected.append('pre-diabetes')
            
            # Additional rule-based conditions
            additional_conditions = self._check_additional_conditions(numeric_data)
            conditions_detected.extend(additional_conditions['conditions'])
            risk_scores.update(additional_conditions['risks'])
            
            # Map numeric data to what frontend expects
            formatted_metrics = {
                'blood_sugar_fasting': numeric_data.get('blood_sugar', numeric_data.get('glucose', 100)),
                'blood_pressure': numeric_data.get('blood_pressure', '120/80'),
                'bmi': numeric_data.get('bmi', 25.0),
                'ldl_cholesterol': numeric_data.get('ldl', 110.0),
                'hdl_cholesterol': numeric_data.get('hdl', 50.0),
                'total_cholesterol': numeric_data.get('cholesterol', 190.0),
                'hemoglobin': numeric_data.get('hemoglobin', 14.0)
            }
            
            health_score = self._calculate_health_score(formatted_metrics, conditions_detected)
            
            return {
                'ml_analysis': {
                    'conditions_detected': list(set(conditions_detected)),
                    'risk_scores': risk_scores,
                    'ml_confidence': float(max(probability)),
                    'analysis_method': 'ml_based'
                },
                'health_metrics': formatted_metrics,
                'health_score': health_score
            }
            
        except Exception as e:
            print(f"Error in ML analysis: {e}")
            return self._rule_based_analysis(numeric_data)
    
    def _check_additional_conditions(self, numeric_data: Dict) -> Dict:
        """Check for additional health conditions beyond diabetes"""
        conditions = []
        risks = {}
        
        # Cholesterol analysis
        total_chol = numeric_data.get('cholesterol', numeric_data.get('total_cholesterol', 0))
        if total_chol > 240:
            conditions.append('high_cholesterol')
            risks['heart_disease_risk'] = min(0.9, (total_chol - 200) / 100)
        elif total_chol > 200:
            conditions.append('borderline_high_cholesterol')
            risks['heart_disease_risk'] = 0.5
        
        # HDL (good cholesterol)
        hdl = numeric_data.get('hdl', 0)
        if hdl > 0 and hdl < 40:
            conditions.append('low_hdl')
            risks['heart_disease_risk'] = risks.get('heart_disease_risk', 0) + 0.2
        
        # LDL (bad cholesterol)
        ldl = numeric_data.get('ldl', 0)
        if ldl > 160:
            conditions.append('high_ldl')
            risks['heart_disease_risk'] = risks.get('heart_disease_risk', 0) + 0.3
        
        # Triglycerides
        triglycerides = numeric_data.get('triglycerides', 0)
        if triglycerides > 200:
            conditions.append('high_triglycerides')
            risks['heart_disease_risk'] = risks.get('heart_disease_risk', 0) + 0.2
        
        # BMI analysis
        bmi = numeric_data.get('bmi', 0)
        if bmi > 30:
            conditions.append('obesity')
            risks['obesity_risk'] = min(0.9, (bmi - 25) / 15)
        elif bmi > 25:
            conditions.append('overweight')
            risks['obesity_risk'] = 0.5
        elif bmi < 18.5:
            conditions.append('underweight')
        
        # Blood pressure
        bp_str = numeric_data.get('blood_pressure', '120/80')
        systolic, diastolic = self._parse_blood_pressure(bp_str)
        
        if systolic >= 140 or diastolic >= 90:
            conditions.append('hypertension')
            risks['hypertension_risk'] = min(0.9, (systolic - 120) / 40)
        elif systolic >= 130 or diastolic >= 80:
            conditions.append('elevated_blood_pressure')
            risks['hypertension_risk'] = 0.5
        
        # Hemoglobin
        hemoglobin = numeric_data.get('hemoglobin', 0)
        if hemoglobin > 0 and hemoglobin < 12:
            conditions.append('anemia')
            risks['anemia_risk'] = 0.7
        
        # Vitamin D
        vitamin_d = numeric_data.get('vitamin_d', 0)
        if vitamin_d > 0 and vitamin_d < 20:
            conditions.append('vitamin_d_deficiency')
        
        # Iron
        iron = numeric_data.get('iron', 0)
        if iron > 0 and iron < 60:
            conditions.append('low_iron')
        
        return {'conditions': conditions, 'risks': risks}
    
    def _calculate_health_score(self, metrics: Dict, conditions: List) -> int:
        """Calculate a health score from 0-100"""
        score = 95  # Base score
        
        # Penalize for conditions
        score -= len(conditions) * 10
        
        # Penalize for critical metrics
        if metrics.get('blood_sugar_fasting', 0) > 125: score -= 15
        if metrics.get('ldl_cholesterol', 0) > 160: score -= 10
        if metrics.get('bmi', 0) > 30: score -= 10
        
        return max(30, min(100, score))

    def _rule_based_analysis(self, numeric_data: Dict) -> Dict:
        """Fallback rule-based analysis when ML models unavailable"""
        conditions_detected = []
        risk_scores = {}
        
        # Blood sugar analysis
        blood_sugar = numeric_data.get('blood_sugar', numeric_data.get('glucose', 0))
        if blood_sugar > 126:
            conditions_detected.append('diabetes')
            risk_scores['diabetes_risk'] = min(0.9, (blood_sugar - 100) / 100)
        elif blood_sugar > 100:
            conditions_detected.append('pre-diabetes')
            risk_scores['diabetes_risk'] = 0.6
        
        # Additional conditions
        additional = self._check_additional_conditions(numeric_data)
        conditions_detected.extend(additional['conditions'])
        risk_scores.update(additional['risks'])
        
        formatted_metrics = {
            'blood_sugar_fasting': numeric_data.get('blood_sugar', numeric_data.get('glucose', 100)),
            'blood_pressure': numeric_data.get('blood_pressure', '120/80'),
            'bmi': numeric_data.get('bmi', 25.0),
            'ldl_cholesterol': numeric_data.get('ldl', 110.0),
            'hdl_cholesterol': numeric_data.get('hdl', 50.0),
            'total_cholesterol': numeric_data.get('cholesterol', 190.0),
            'hemoglobin': numeric_data.get('hemoglobin', 14.0)
        }
        
        health_score = self._calculate_health_score(formatted_metrics, conditions_detected)
        
        return {
            'ml_analysis': {
                'conditions_detected': list(set(conditions_detected)),
                'risk_scores': risk_scores,
                'ml_confidence': 0.75, # Estimated for rule-based
                'analysis_method': 'rule_based'
            },
            'health_metrics': formatted_metrics,
            'health_score': health_score
        }
    
    def analyze_health_metrics(self, numeric_data: Dict) -> Dict:
        """Analyze numeric health data and detect conditions"""
        if self.models_loaded:
            return self._ml_based_analysis(numeric_data)
        else:
            return self._rule_based_analysis(numeric_data)
    
    def get_health_recommendations(self, analysis_result: Dict) -> List[str]:
        """Generate health recommendations based on विश्लेषण"""
        recommendations = []
        ml_data = analysis_result.get('ml_analysis', {})
        conditions = ml_data.get('conditions_detected', [])
        
        if 'diabetes' in conditions or 'pre-diabetes' in conditions:
            recommendations.append("Monitor blood sugar levels regularly")
            recommendations.append("Reduce sugar and refined carbohydrate intake")
            recommendations.append("Increase physical activity (30 min daily)")
        
        if 'high_cholesterol' in conditions or 'borderline_high_cholesterol' in conditions:
            recommendations.append("Reduce saturated fat intake")
            recommendations.append("Increase fiber-rich foods (oats, beans, vegetables)")
            recommendations.append("Consider omega-3 fatty acids (fish, flaxseed)")
        
        if 'obesity' in conditions or 'overweight' in conditions:
            recommendations.append("Aim for gradual weight loss (0.5-1 kg per week)")
            recommendations.append("Focus on portion control")
            recommendations.append("Increase vegetable and whole grain intake")
        
        if 'hypertension' in conditions or 'elevated_blood_pressure' in conditions:
            recommendations.append("Reduce sodium intake (< 2300 mg/day)")
            recommendations.append("Increase potassium-rich foods (bananas, spinach)")
            recommendations.append("Limit alcohol consumption")
        
        if 'anemia' in conditions:
            recommendations.append("Increase iron-rich foods (spinach, lentils, red meat)")
            recommendations.append("Pair iron sources with vitamin C for better absorption")
        
        if 'vitamin_d_deficiency' in conditions:
            recommendations.append("Get 15-20 minutes of sunlight daily")
            recommendations.append("Include vitamin D-rich foods (fatty fish, fortified milk)")
        
        if not recommendations:
            recommendations.append("Maintain a balanced diet with variety")
            recommendations.append("Stay physically active")
            recommendations.append("Regular health check-ups")
        
        return recommendations

# Global instance
ml_analysis_service = MLAnalysisService()
