"""
Enhanced medical data extraction from OCR text.
Extracts numeric health parameters (glucose, BMI, blood pressure, etc.)
"""

import re
from typing import Dict, Optional


class HealthParameterExtractor:
    """Extracts specific health metrics from medical text."""
    
    # Regex patterns for different health parameters
    PATTERNS = {
        'glucose': {
            'patterns': [
                r'glucose[:\s]+(\d+(?:\.\d+)?)',
                r'fasting\s+glucose[:\s]+(\d+(?:\.\d+)?)',
                r'blood\s+glucose[:\s]+(\d+(?:\.\d+)?)',
                r'glucose\s+level[:\s]+(\d+(?:\.\d+)?)',
                r'(?:fbs|random\s+glucose)[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (70, 400)
        },
        'bmi': {
            'patterns': [
                r'bmi[:\s]+(\d+(?:\.\d+)?)',
                r'body\s+mass\s+index[:\s]+(\d+(?:\.\d+)?)',
                r'bmi:\s*(\d+(?:\.\d+)?)',
            ],
            'range': (10, 100)
        },
        'blood_pressure': {
            'patterns': [
                r'bp[:\s]+(\d+)\s*[/\\]\s*(\d+)',
                r'blood\s+pressure[:\s]+(\d+)\s*[/\\]\s*(\d+)',
                r'systolic[:\s]+(\d+)[^\d]*diastolic[:\s]+(\d+)',
                r'(\d{2,3})\s*[/\\]\s*(\d{2,3})',
            ],
            'range': (40, 200),  # systolic
            'is_pair': True
        },
        'cholesterol': {
            'patterns': [
                r'cholesterol[:\s]+(\d+(?:\.\d+)?)',
                r'total\s+cholesterol[:\s]+(\d+(?:\.\d+)?)',
                r'serum\s+cholesterol[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (100, 400)
        },
        'ldl': {
            'patterns': [
                r'ldl[:\s]+(\d+(?:\.\d+)?)',
                r'ldl\s+cholesterol[:\s]+(\d+(?:\.\d+)?)',
                r'(?:bad|low\s+density)\s+cholesterol[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (0, 300)
        },
        'hdl': {
            'patterns': [
                r'hdl[:\s]+(\d+(?:\.\d+)?)',
                r'hdl\s+cholesterol[:\s]+(\d+(?:\.\d+)?)',
                r'(?:good|high\s+density)\s+cholesterol[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (0, 150)
        },
        'triglycerides': {
            'patterns': [
                r'triglycerides[:\s]+(\d+(?:\.\d+)?)',
                r'serum\s+triglycerides[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (0, 500)
        },
        'hemoglobin_a1c': {
            'patterns': [
                r'a1c[:\s]+(\d+(?:\.\d+)?)',
                r'hba1c[:\s]+(\d+(?:\.\d+)?)',
                r'hemoglobin\s+a1c[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (3, 15)
        },
        'insulin': {
            'patterns': [
                r'insulin[:\s]+(\d+(?:\.\d+)?)',
                r'fasting\s+insulin[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (0, 300)
        },
        'age': {
            'patterns': [
                r'age[:\s]+(\d+)',
                r'dob.*?(\d{1,2})\s+years?',
                r'patient\s+age[:\s]+(\d+)',
            ],
            'range': (0, 150)
        },
        'weight': {
            'patterns': [
                r'weight[:\s]+(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilograms)',
                r'wt[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (20, 300)
        },
        'height': {
            'patterns': [
                r'height[:\s]+(\d+(?:\.\d+)?)\s*(?:cm|cms|centimeters)',
                r'ht[:\s]+(\d+(?:\.\d+)?)',
            ],
            'range': (100, 250)
        }
    }
    
    @staticmethod
    def extract_parameters(text: str) -> Dict[str, Optional[float]]:
        """
        Extract health parameters from OCR text.
        
        Args:
            text: OCR extracted text from medical report
            
        Returns:
            Dictionary with extracted health parameters
        """
        text_lower = text.lower()
        extracted = {}
        
        for param_name, param_config in HealthParameterExtractor.PATTERNS.items():
            value = None
            
            for pattern in param_config['patterns']:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                
                if match:
                    if param_config.get('is_pair'):
                        # For blood pressure (systolic/diastolic)
                        systolic = float(match.group(1))
                        diastolic = float(match.group(2))
                        
                        if param_config['range'][0] <= systolic <= param_config['range'][1]:
                            value = systolic  # Return systolic for now
                            extracted['blood_pressure_systolic'] = systolic
                            extracted['blood_pressure_diastolic'] = diastolic
                            break
                    else:
                        # Standard numeric extraction
                        value = float(match.group(1))
                        
                        # Validate value is in reasonable range
                        if param_config['range'][0] <= value <= param_config['range'][1]:
                            extracted[param_name] = value
                            break
        
        return extracted
    
    @staticmethod
    def extract_to_diabetes_form(text: str) -> Dict:
        """
        Extract and format for DiabetesInput form.
        
        Maps extracted parameters to the form fields.
        """
        extracted = HealthParameterExtractor.extract_parameters(text)
        
        form_data = {
            'pregnancies': extracted.get('pregnancies', None),
            'glucose': extracted.get('glucose', None),
            'blood_pressure': extracted.get('blood_pressure_systolic', None),
            'skin_thickness': None,  # Usually not in reports
            'insulin': extracted.get('insulin', None),
            'bmi': extracted.get('bmi', None),
            'dpf': None,  # Requires family history data
            'age': extracted.get('age', None),
        }
        
        # If we have weight and height, calculate BMI
        if 'weight' in extracted and 'height' in extracted:
            weight_kg = extracted['weight']
            height_m = extracted['height'] / 100  # Convert cm to m
            if height_m > 0:
                calculated_bmi = weight_kg / (height_m ** 2)
                form_data['bmi'] = round(calculated_bmi, 1)
        
        # Filter out None values
        return {k: v for k, v in form_data.items() if v is not None}


# Example usage
if __name__ == "__main__":
    sample_text = """
    MEDICAL REPORT
    Patient Name: John Doe
    Age: 50
    Date: 2026-02-17
    
    LAB RESULTS:
    Glucose Level: 148 mg/dL
    Blood Pressure: 140/90 mmHg
    BMI: 33.6
    Fasting Insulin: 25
    Weight: 85 kg
    Height: 160 cm
    Cholesterol: 240 mg/dL
    """
    
    extracted = HealthParameterExtractor.extract_to_diabetes_form(sample_text)
    print("Extracted Parameters:")
    for key, value in extracted.items():
        print(f"  {key}: {value}")
