"""
AI-powered text interpretation for medical reports and prescriptions.
Uses OpenAI GPT for intelligent interpretation of doctor notes.
"""

import os
import json
from typing import Dict, List, Optional
import re


class AIInterpreter:
    """Interprets medical text using AI/LLM to extract actionable diet rules."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.use_openai = bool(self.api_key)
        
        if self.use_openai:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Using fallback method.")
                self.use_openai = False
    
    def interpret_medical_text(self, text: str) -> Dict:
        """
        Interpret medical text and extract health conditions and diet recommendations.
        
        Returns:
            Dict with 'conditions', 'dietary_restrictions', and 'recommendations'
        """
        if self.use_openai:
            return self._interpret_with_gpt(text)
        else:
            return self._interpret_with_rules(text)
    
    def _interpret_with_gpt(self, text: str) -> Dict:
        """Use GPT to interpret medical text intelligently."""
        try:
            prompt = f"""Analyze the following medical report/prescription and extract:
1. Health conditions or diagnoses mentioned
2. Dietary restrictions or recommendations
3. Specific nutrients or food groups to focus on
4. Any warnings or foods to avoid

Medical Text:
{text}

Respond in JSON format with these exact keys:
{{
    "conditions": ["list of health conditions"],
    "dietary_restrictions": ["list of specific dietary restrictions"],
    "recommendations": ["list of diet recommendations"],
    "nutrients_focus": ["nutrients to focus on"],
    "foods_to_avoid": ["foods to avoid"]
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical nutrition expert analyzing doctor's notes and prescriptions to provide dietary guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return self._interpret_with_rules(text)
                
        except Exception as e:
            print(f"GPT interpretation failed: {e}. Using fallback method.")
            return self._interpret_with_rules(text)
    
    def _interpret_with_rules(self, text: str) -> Dict:
        """Fallback rule-based interpretation for when GPT is unavailable."""
        text_lower = text.lower()
        
        # Enhanced keyword detection
        conditions = []
        dietary_restrictions = []
        recommendations = []
        nutrients_focus = []
        foods_to_avoid = []
        
        # Detect conditions
        condition_keywords = {
            "diabetes": ["diabetes", "diabetic", "high glucose", "blood sugar"],
            "hypertension": ["hypertension", "high blood pressure", "bp"],
            "heart disease": ["heart disease", "cardiac", "cardiovascular"],
            "obesity": ["obesity", "overweight", "weight management"],
            "sepsis": ["sepsis", "severe infection"],
            "pneumonia": ["pneumonia", "lung infection", "respiratory"],
            "kidney disease": ["kidney", "renal", "ckd"],
            "liver disease": ["liver", "hepatic"],
            "gastric issues": ["gastric", "stomach", "digestion", "aspiration"]
        }
        
        for condition, keywords in condition_keywords.items():
            if any(kw in text_lower for kw in keywords):
                conditions.append(condition)
        
        # Detect dietary restrictions and recommendations
        if any(k in text_lower for k in ["diabetes", "diabetic", "glucose", "sugar"]):
            dietary_restrictions.append("Low sugar / Low glycemic index foods")
            recommendations.append("Complex carbohydrates over simple sugars")
            foods_to_avoid.extend(["Sugary drinks", "White bread", "Pastries", "Candy"])
            nutrients_focus.append("Fiber")
        
        if any(k in text_lower for k in ["sepsis", "severe", "infection", "recovery", "icu"]):
            dietary_restrictions.append("Soft, easy-to-digest foods")
            recommendations.append("High protein for recovery and healing")
            recommendations.append("Nutrient-dense foods to boost immunity")
            nutrients_focus.extend(["Protein", "Vitamins A, C, D", "Zinc"])
        
        if any(k in text_lower for k in ["pneumonia", "aspiration", "swallow"]):
            dietary_restrictions.append("Pureed or soft foods")
            recommendations.append("Foods that are easy to swallow")
            recommendations.append("Avoid dry or hard foods")
            foods_to_avoid.extend(["Hard nuts", "Dry crackers", "Raw vegetables"])
        
        if any(k in text_lower for k in ["hypertension", "blood pressure", "bp"]):
            dietary_restrictions.append("Low sodium diet")
            recommendations.append("DASH diet principles")
            foods_to_avoid.extend(["Processed foods", "Canned soups", "Salty snacks"])
            nutrients_focus.append("Potassium")
        
        if any(k in text_lower for k in ["heart", "cardiac", "cholesterol"]):
            dietary_restrictions.append("Low saturated fat")
            recommendations.append("Heart-healthy fats (omega-3)")
            foods_to_avoid.extend(["Trans fats", "Fried foods", "Fatty meats"])
            nutrients_focus.append("Omega-3 fatty acids")
        
        # General health recommendations if nothing specific found
        if not recommendations:
            recommendations.append("Balanced, nutritious diet")
            recommendations.append("Adequate hydration")
            recommendations.append("Regular meal timing")
        
        return {
            "conditions": list(set(conditions)) if conditions else ["General health maintenance"],
            "dietary_restrictions": list(set(dietary_restrictions)) if dietary_restrictions else ["None specified"],
            "recommendations": list(set(recommendations)),
            "nutrients_focus": list(set(nutrients_focus)) if nutrients_focus else ["Balanced nutrition"],
            "foods_to_avoid": list(set(foods_to_avoid)) if foods_to_avoid else ["Processed junk food"]
        }
    
    def generate_diet_rules(self, interpreted_data: Dict) -> List[str]:
        """Convert interpreted data into actionable diet rules."""
        rules = []
        
        # Add dietary restrictions as rules
        for restriction in interpreted_data.get("dietary_restrictions", []):
            rules.append(restriction)
        
        # Add recommendations as rules
        for recommendation in interpreted_data.get("recommendations", []):
            rules.append(recommendation)
        
        # Add nutrient focus
        nutrients = interpreted_data.get("nutrients_focus", [])
        if nutrients:
            rules.append(f"Focus on: {', '.join(nutrients)}")
        
        # Add foods to avoid
        avoid = interpreted_data.get("foods_to_avoid", [])
        if avoid:
            rules.append(f"Avoid: {', '.join(avoid[:5])}")  # Limit to 5 items
        
        return rules


# Singleton instance
_interpreter_instance = None


def get_ai_interpreter() -> AIInterpreter:
    """Get or create AI interpreter singleton."""
    global _interpreter_instance
    if _interpreter_instance is None:
        _interpreter_instance = AIInterpreter()
    return _interpreter_instance
