"""
Comprehensive meal plan generator for personalized diet planning.
Creates breakfast, lunch, and dinner plans based on health conditions.
"""

from typing import Dict, List
import random


class MealPlanner:
    """Generates personalized meal plans based on health conditions and dietary needs."""
    
    def __init__(self):
        # Meal database organized by dietary categories
        self.meal_database = {
            "low_sugar": {
                "breakfast": [
                    {"name": "Oatmeal with berries and nuts", "calories": 350, "protein": "12g", "carbs": "45g", "description": "Steel-cut oats with fresh berries, almonds, and cinnamon"},
                    {"name": "Vegetable omelet with whole wheat toast", "calories": 320, "protein": "20g", "carbs": "25g", "description": "3-egg omelet with spinach, tomatoes, and mushrooms"},
                    {"name": "Greek yogurt with chia seeds", "calories": 280, "protein": "18g", "carbs": "30g", "description": "Plain Greek yogurt with chia seeds, flaxseeds, and sliced almonds"},
                ],
                "lunch": [
                    {"name": "Grilled chicken salad", "calories": 420, "protein": "35g", "carbs": "20g", "description": "Grilled chicken breast with mixed greens, olive oil dressing"},
                    {"name": "Quinoa bowl with roasted vegetables", "calories": 380, "protein": "15g", "carbs": "55g", "description": "Quinoa with roasted broccoli, bell peppers, and chickpeas"},
                    {"name": "Lentil soup with vegetables", "calories": 350, "protein": "18g", "carbs": "50g", "description": "Hearty lentil soup with carrots, celery, and spinach"},
                ],
                "dinner": [
                    {"name": "Baked salmon with steamed vegetables", "calories": 450, "protein": "40g", "carbs": "25g", "description": "Herb-crusted salmon with broccoli and cauliflower"},
                    {"name": "Grilled chicken with brown rice", "calories": 480, "protein": "38g", "carbs": "45g", "description": "Grilled chicken breast with brown rice and green beans"},
                    {"name": "Turkey meatballs with zucchini noodles", "calories": 420, "protein": "35g", "carbs": "30g", "description": "Lean turkey meatballs with spiralized zucchini and marinara"},
                ]
            },
            "high_protein": {
                "breakfast": [
                    {"name": "Protein smoothie bowl", "calories": 400, "protein": "30g", "carbs": "40g", "description": "Protein powder, banana, spinach, topped with granola"},
                    {"name": "Scrambled eggs with turkey sausage", "calories": 420, "protein": "32g", "carbs": "15g", "description": "4 egg whites with lean turkey sausage and avocado"},
                    {"name": "Cottage cheese with fruit and nuts", "calories": 360, "protein": "28g", "carbs": "35g", "description": "Low-fat cottage cheese with berries and walnuts"},
                ],
                "lunch": [
                    {"name": "Grilled fish with sweet potato", "calories": 480, "protein": "38g", "carbs": "45g", "description": "Grilled tilapia with roasted sweet potato and asparagus"},
                    {"name": "Chicken breast with quinoa salad", "calories": 500, "protein": "42g", "carbs": "48g", "description": "Grilled chicken with quinoa, cucumber, and feta"},
                    {"name": "Tuna salad wrap", "calories": 450, "protein": "35g", "carbs": "40g", "description": "Whole wheat wrap with tuna, avocado, and mixed greens"},
                ],
                "dinner": [
                    {"name": "Lean beef stir-fry", "calories": 520, "protein": "45g", "carbs": "35g", "description": "Lean beef with mixed vegetables and brown rice"},
                    {"name": "Grilled shrimp with whole grain pasta", "calories": 480, "protein": "40g", "carbs": "50g", "description": "Garlic shrimp with whole wheat pasta and vegetables"},
                    {"name": "Baked chicken with roasted vegetables", "calories": 460, "protein": "42g", "carbs": "30g", "description": "Herb-baked chicken with Brussels sprouts and carrots"},
                ]
            },
            "soft_diet": {
                "breakfast": [
                    {"name": "Banana oatmeal porridge", "calories": 320, "protein": "10g", "carbs": "55g", "description": "Smooth oatmeal with mashed banana and honey"},
                    {"name": "Scrambled eggs with mashed avocado", "calories": 280, "protein": "16g", "carbs": "12g", "description": "Soft scrambled eggs with creamy avocado"},
                    {"name": "Smoothie with yogurt and berries", "calories": 300, "protein": "15g", "carbs": "45g", "description": "Blended smoothie with Greek yogurt and soft fruits"},
                ],
                "lunch": [
                    {"name": "Pureed vegetable soup", "calories": 280, "protein": "12g", "carbs": "40g", "description": "Creamy blended soup with carrots, potatoes, and peas"},
                    {"name": "Mashed potato with tender chicken", "calories": 380, "protein": "28g", "carbs": "45g", "description": "Smooth mashed potatoes with finely shredded chicken"},
                    {"name": "Soft tofu with steamed vegetables", "calories": 320, "protein": "20g", "carbs": "35g", "description": "Silken tofu with well-cooked vegetables"},
                ],
                "dinner": [
                    {"name": "Baked fish with pureed vegetables", "calories": 350, "protein": "30g", "carbs": "30g", "description": "Flaky white fish with smooth vegetable puree"},
                    {"name": "Chicken and rice porridge", "calories": 380, "protein": "25g", "carbs": "50g", "description": "Congee-style porridge with tender chicken"},
                    {"name": "Lentil dal with soft rice", "calories": 360, "protein": "18g", "carbs": "60g", "description": "Smooth lentil curry with well-cooked rice"},
                ]
            },
            "low_sodium": {
                "breakfast": [
                    {"name": "Fresh fruit with unsalted nuts", "calories": 300, "protein": "8g", "carbs": "45g", "description": "Mixed berries with unsalted almonds and walnuts"},
                    {"name": "Oatmeal with fresh berries", "calories": 320, "protein": "10g", "carbs": "55g", "description": "Steel-cut oats with blueberries (no added salt)"},
                    {"name": "Whole grain toast with avocado", "calories": 280, "protein": "8g", "carbs": "35g", "description": "Unsalted whole wheat toast with fresh avocado"},
                ],
                "lunch": [
                    {"name": "Fresh herb-grilled chicken salad", "calories": 380, "protein": "32g", "carbs": "25g", "description": "Herb-seasoned chicken with fresh vegetables"},
                    {"name": "Brown rice with steamed vegetables", "calories": 350, "protein": "12g", "carbs": "65g", "description": "Unsalted brown rice with fresh steamed veggies"},
                    {"name": "Homemade vegetable soup", "calories": 280, "protein": "10g", "carbs": "45g", "description": "Low-sodium vegetable soup with fresh herbs"},
                ],
                "dinner": [
                    {"name": "Herb-baked fish with vegetables", "calories": 420, "protein": "36g", "carbs": "30g", "description": "Fresh fish with lemon and herbs (no salt)"},
                    {"name": "Roasted chicken with sweet potato", "calories": 460, "protein": "38g", "carbs": "40g", "description": "Unsalted roasted chicken with baked sweet potato"},
                    {"name": "Pasta with fresh tomato sauce", "calories": 400, "protein": "15g", "carbs": "70g", "description": "Whole wheat pasta with homemade tomato sauce"},
                ]
            },
            "general_healthy": {
                "breakfast": [
                    {"name": "Whole grain cereal with milk", "calories": 300, "protein": "12g", "carbs": "50g", "description": "High-fiber cereal with low-fat milk and banana"},
                    {"name": "Whole wheat toast with peanut butter", "calories": 320, "protein": "14g", "carbs": "40g", "description": "Toast with natural peanut butter and sliced apple"},
                    {"name": "Fruit and nut granola with yogurt", "calories": 350, "protein": "15g", "carbs": "45g", "description": "Homemade granola with Greek yogurt and berries"},
                ],
                "lunch": [
                    {"name": "Turkey sandwich with vegetables", "calories": 420, "protein": "28g", "carbs": "45g", "description": "Whole grain bread with turkey, lettuce, tomato"},
                    {"name": "Mediterranean chickpea salad", "calories": 380, "protein": "15g", "carbs": "50g", "description": "Chickpeas with cucumbers, tomatoes, and olive oil"},
                    {"name": "Vegetable stir-fry with tofu", "calories": 400, "protein": "20g", "carbs": "55g", "description": "Mixed vegetables with tofu and brown rice"},
                ],
                "dinner": [
                    {"name": "Grilled chicken with roasted vegetables", "calories": 480, "protein": "40g", "carbs": "35g", "description": "Herb chicken with mixed roasted vegetables"},
                    {"name": "Baked fish with quinoa", "calories": 450, "protein": "35g", "carbs": "45g", "description": "Lemon-herb fish with quinoa and steamed broccoli"},
                    {"name": "Vegetable curry with brown rice", "calories": 420, "protein": "12g", "carbs": "70g", "description": "Mixed vegetable curry with aromatic brown rice"},
                ]
            }
        }
        
        # Snack options
        self.snacks = [
            {"name": "Fresh fruit", "calories": 80, "description": "Apple, banana, or orange"},
            {"name": "Handful of nuts", "calories": 160, "description": "Almonds, walnuts, or mixed nuts"},
            {"name": "Greek yogurt", "calories": 120, "description": "Plain Greek yogurt with berries"},
            {"name": "Vegetable sticks with hummus", "calories": 100, "description": "Carrots, celery, cucumber with hummus"},
            {"name": "Whole grain crackers with cheese", "calories": 140, "description": "Low-fat cheese with whole wheat crackers"},
        ]
    
    def generate_meal_plan(self, conditions: List[str], dietary_restrictions: List[str], 
                          diabetes_risk: str = None) -> Dict:
        """
        Generate a comprehensive meal plan based on health conditions.
        
        Args:
            conditions: List of health conditions
            dietary_restrictions: List of dietary restrictions
            diabetes_risk: Optional diabetes risk level (Low, Moderate, High)
        
        Returns:
            Dictionary with meal plan for breakfast, lunch, dinner, and snacks
        """
        # Determine dietary category
        category = self._determine_category(conditions, dietary_restrictions, diabetes_risk)
        
        # Get meals from appropriate category
        meals = self.meal_database.get(category, self.meal_database["general_healthy"])
        
        # Select random meals (or we could use AI to select based on variety/nutrition)
        meal_plan = {
            "category": category,
            "breakfast": random.choice(meals["breakfast"]),
            "lunch": random.choice(meals["lunch"]),
            "dinner": random.choice(meals["dinner"]),
            "snacks": random.sample(self.snacks, 2),  # Provide 2 snack options
            "daily_summary": self._calculate_daily_summary(meals, category),
            "hydration": "Drink 8-10 glasses of water throughout the day",
            "notes": self._generate_notes(conditions, dietary_restrictions)
        }
        
        return meal_plan
    
    def _determine_category(self, conditions: List[str], restrictions: List[str], 
                           diabetes_risk: str = None) -> str:
        """Determine the most appropriate meal category based on conditions."""
        conditions_lower = [c.lower() for c in conditions]
        restrictions_lower = [r.lower() for r in restrictions]
        
        # Priority-based selection
        if any("sepsis" in c or "pneumonia" in c or "aspiration" in c for c in conditions_lower):
            return "soft_diet"
        
        if any("soft" in r or "pureed" in r for r in restrictions_lower):
            return "soft_diet"
        
        if (diabetes_risk and diabetes_risk != "Low Risk") or any("diabetes" in c for c in conditions_lower):
            return "low_sugar"
        
        if any("low sugar" in r or "low glycemic" in r for r in restrictions_lower):
            return "low_sugar"
        
        if any("hypertension" in c or "blood pressure" in c for c in conditions_lower):
            return "low_sodium"
        
        if any("low sodium" in r for r in restrictions_lower):
            return "low_sodium"
        
        if any("protein" in r or "recovery" in r for r in restrictions_lower):
            return "high_protein"
        
        if any("severe" in c or "recovery" in c for c in conditions_lower):
            return "high_protein"
        
        return "general_healthy"
    
    def _calculate_daily_summary(self, meals: Dict, category: str) -> Dict:
        """Calculate approximate daily nutritional summary."""
        # This is a simplified version - could be enhanced with actual calculations
        summaries = {
            "low_sugar": {"total_calories": "1400-1600", "protein": "85-100g", "carbs": "150-180g", "focus": "Low glycemic index foods"},
            "high_protein": {"total_calories": "1700-1900", "protein": "120-140g", "carbs": "140-170g", "focus": "Muscle recovery and strength"},
            "soft_diet": {"total_calories": "1300-1500", "protein": "65-80g", "carbs": "180-210g", "focus": "Easy digestion and nutrient absorption"},
            "low_sodium": {"total_calories": "1500-1700", "protein": "80-95g", "carbs": "170-200g", "focus": "Heart health and blood pressure management"},
            "general_healthy": {"total_calories": "1600-1800", "protein": "75-90g", "carbs": "180-220g", "focus": "Balanced nutrition"},
        }
        
        return summaries.get(category, summaries["general_healthy"])
    
    def _generate_notes(self, conditions: List[str], restrictions: List[str]) -> List[str]:
        """Generate personalized notes and tips."""
        notes = []
        
        if any("diabetes" in c.lower() for c in conditions):
            notes.append("Monitor blood sugar levels regularly, especially before and after meals")
            notes.append("Eat smaller, frequent meals to maintain stable blood sugar")
        
        if any("hypertension" in c.lower() or "blood pressure" in c.lower() for c in conditions):
            notes.append("Limit sodium intake to less than 2000mg per day")
            notes.append("Include potassium-rich foods like bananas and spinach")
        
        if any("soft" in r.lower() or "sepsis" in c.lower() for r in restrictions for c in conditions):
            notes.append("Eat slowly and chew thoroughly")
            notes.append("Avoid foods that are difficult to swallow")
        
        if not notes:
            notes.append("Maintain regular meal times")
            notes.append("Practice portion control")
        
        notes.append("Consult with a healthcare provider for personalized guidance")
        
        return notes


# Singleton instance
_meal_planner_instance = None


def get_meal_planner() -> MealPlanner:
    """Get or create meal planner singleton."""
    global _meal_planner_instance
    if _meal_planner_instance is None:
        _meal_planner_instance = MealPlanner()
    return _meal_planner_instance
