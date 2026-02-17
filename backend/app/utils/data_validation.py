from typing import Dict, Any, List

class DataValidator:
    """Validate extracted medical data"""
    
    # Normal ranges for common health metrics
    NORMAL_RANGES = {
        "blood_sugar": (70, 100),  # Fasting glucose mg/dl
        "cholesterol": (0, 200),  # Total cholesterol mg/dl
        "hdl": (40, 60),  # HDL cholesterol mg/dl
        "ldl": (0, 100),  # LDL cholesterol mg/dl
        "triglycerides": (0, 150),  # mg/dl
        "bmi": (18.5, 24.9),
        "systolic_bp": (90, 120),  # mmHg
        "diastolic_bp": (60, 80),  # mmHg
        "hemoglobin": (12, 16),  # g/dl (women: 12-15, men: 13-17)
        "vitamin_d": (20, 50),  # ng/ml
        "iron": (60, 170),  # mcg/dl
    }
    
    def validate_numeric_data(self, numeric_data: Dict[str, float]) -> Dict[str, Any]:
        """Validate and flag abnormal values"""
        validation_results = {
            "valid": True,
            "abnormal_values": [],
            "warnings": []
        }
        
        for metric, value in numeric_data.items():
            if metric in self.NORMAL_RANGES:
                min_val, max_val = self.NORMAL_RANGES[metric]
                if value < min_val or value > max_val:
                    validation_results["valid"] = False
                    validation_results["abnormal_values"].append({
                        "metric": metric,
                        "value": value,
                        "normal_range": (min_val, max_val),
                        "status": "low" if value < min_val else "high"
                    })
        
        return validation_results
    
    def clean_numeric_data(self, numeric_data: Dict[str, float]) -> Dict[str, float]:
        """Clean and normalize numeric data"""
        cleaned = {}
        for key, value in numeric_data.items():
            if isinstance(value, (int, float)):
                # Round to 2 decimal places
                cleaned[key] = round(float(value), 2)
        return cleaned

validator = DataValidator()
