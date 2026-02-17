"""
Comprehensive Test Suite for NLP Interpretation
Tests dietary restriction extraction, medication parsing, and allergy detection
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.nlp_interpretation import nlp_interpretation_service

class TestNLPInterpretation:
    """Test NLP interpretation service"""
    
    def test_dietary_restriction_extraction(self):
        """Test extraction of dietary restrictions from doctor notes"""
        textual_data = {
            "doctor_notes": "Patient has diabetes. Recommend low sugar diet and reduce carbohydrate intake. Avoid fried foods.",
            "prescriptions": "Metformin 500mg twice daily"
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        
        # Check structure
        assert 'dietary_restrictions' in result
        assert 'medications' in result
        assert 'insights' in result
        
        # Should detect dietary restrictions
        restrictions = result['dietary_restrictions']
        assert 'no_sugar' in restrictions or 'low_carb' in restrictions
        print(f"✅ Detected restrictions: {restrictions}")
    
    def test_medication_extraction(self):
        """Test medication extraction from prescriptions"""
        textual_data = {
            "doctor_notes": "",
            "prescriptions": "1. Metformin 500mg BD\n2. Atorvastatin 10mg OD\n3. Aspirin 75mg OD"
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        medications = result['medications']
        
        # Should detect medications
        assert 'metformin' in medications
        assert 'atorvastatin' in medications or 'statin' in medications
        print(f"✅ Detected medications: {medications}")
    
    def test_allergy_detection(self):
        """Test food allergy detection"""
        textual_data = {
            "doctor_notes": "Patient is allergic to peanuts and shellfish. Lactose intolerant.",
            "prescriptions": ""
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        allergies = result['allergies']
        
        # Should detect allergies
        assert 'peanuts' in allergies or 'dairy' in allergies or 'shellfish' in allergies
        print(f"✅ Detected allergies: {allergies}")
    
    def test_dietary_advice_extraction(self):
        """Test extraction of dietary advice"""
        textual_data = {
            "doctor_notes": "Increase fiber intake. Add more vegetables to diet. Reduce salt consumption. Drink more water.",
            "prescriptions": ""
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        advice = result['dietary_advice']
        
        # Should extract advice
        assert len(advice) > 0
        print(f"✅ Extracted advice: {advice}")
    
    def test_medication_food_interactions(self):
        """Test detection of medication-food interactions"""
        textual_data = {
            "doctor_notes": "",
            "prescriptions": "Warfarin 5mg daily, Metformin 500mg BD"
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        interactions = result['medication_interactions']
        
        # Warfarin has interactions with vitamin K foods
        assert len(interactions) > 0
        print(f"✅ Detected interactions: {interactions}")
    
    def test_complex_medical_text(self):
        """Test with complex medical text"""
        textual_data = {
            "doctor_notes": """
            Patient presents with Type 2 Diabetes Mellitus and Hypertension.
            HbA1c: 8.5% (elevated)
            Blood Pressure: 145/92 mmHg
            
            Recommendations:
            - Strict diabetic diet with low glycemic index foods
            - Reduce sodium intake to <2000mg/day
            - Increase physical activity
            - Monitor blood sugar levels regularly
            
            Patient reports lactose intolerance.
            """,
            "prescriptions": """
            1. Metformin 850mg BD
            2. Lisinopril 10mg OD
            3. Aspirin 75mg OD
            """
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        
        # Should detect multiple aspects
        assert len(result['dietary_restrictions']) > 0
        assert len(result['medications']) >= 2
        assert 'dairy' in result['allergies'] or 'lactose' in str(result).lower()
        
        print(f"✅ Complex text analysis:")
        print(f"   Restrictions: {result['dietary_restrictions']}")
        print(f"   Medications: {result['medications']}")
        print(f"   Allergies: {result['allergies']}")
        print(f"   Advice: {result['dietary_advice']}")
    
    def test_empty_input(self):
        """Test with empty input"""
        textual_data = {
            "doctor_notes": "",
            "prescriptions": ""
        }
        
        result = nlp_interpretation_service.interpret_doctor_notes(textual_data)
        
        # Should handle gracefully
        assert isinstance(result['dietary_restrictions'], list)
        assert isinstance(result['medications'], list)
        print("✅ Empty input handled correctly")
    
    def test_health_goals_extraction(self):
        """Test health goals extraction"""
        textual_data = {
            "doctor_notes": "Patient needs to lose weight and control blood sugar levels. Focus on cholesterol reduction.",
            "prescriptions": ""
        }
        
        goals = nlp_interpretation_service.extract_health_goals(textual_data)
        
        assert len(goals) > 0
        print(f"✅ Extracted health goals: {goals}")
    
    def test_accuracy_with_ground_truth(self):
        """Test accuracy against known ground truth"""
        test_cases = [
            {
                "input": {
                    "doctor_notes": "Diabetic patient. Avoid sugar and sweets.",
                    "prescriptions": ""
                },
                "expected_restrictions": ["no_sugar", "low_carb"]
            },
            {
                "input": {
                    "doctor_notes": "High blood pressure. Reduce salt intake.",
                    "prescriptions": ""
                },
                "expected_restrictions": ["low_sodium"]
            },
            {
                "input": {
                    "doctor_notes": "High cholesterol. Limit fatty foods.",
                    "prescriptions": ""
                },
                "expected_restrictions": ["low_fat"]
            }
        ]
        
        correct = 0
        total = len(test_cases)
        
        for case in test_cases:
            result = nlp_interpretation_service.interpret_doctor_notes(case['input'])
            detected = result['dietary_restrictions']
            expected = case['expected_restrictions']
            
            # Check if at least one expected restriction is detected
            if any(exp in detected for exp in expected):
                correct += 1
        
        accuracy = (correct / total) * 100
        print(f"✅ NLP Accuracy: {accuracy:.1f}% ({correct}/{total} correct)")
        
        # Should achieve at least 85% accuracy
        assert accuracy >= 85, f"NLP accuracy {accuracy:.1f}% is below 85% threshold"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
