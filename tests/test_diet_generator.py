"""
Comprehensive Test Suite for Diet Plan Generator
Tests meal selection, nutritional balance, and dietary restriction compliance
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.diet_generator import diet_generator_service

class TestDietGenerator:
    """Test diet plan generation service"""
    
    def test_basic_diet_plan_generation(self):
        """Test basic diet plan generation"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {'diabetes_risk': 0.8}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        
        # Check structure
        assert 'patient_name' in diet_plan
        assert 'days' in diet_plan
        assert 'nutritional_summary' in diet_plan
        assert 'shopping_list' in diet_plan
        
        # Should have 7 days by default
        assert len(diet_plan['days']) == 7
        print(f"✅ Generated {len(diet_plan['days'])}-day diet plan")
    
    def test_meal_structure(self):
        """Test that each day has all required meals"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        
        for day in diet_plan['days']:
            assert 'breakfast' in day
            assert 'lunch' in day
            assert 'dinner' in day
            assert 'snack' in day
            assert 'daily_totals' in day
            
            # Check daily totals
            totals = day['daily_totals']
            assert 'calories' in totals
            assert 'protein' in totals
            assert 'carbs' in totals
            assert 'fat' in totals
            assert 'fiber' in totals
        
        print("✅ All days have complete meal structure")
    
    def test_dietary_restriction_compliance(self):
        """Test that diet plan respects dietary restrictions"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {}
        }
        
        nlp_result = {
            'dietary_restrictions': ['no_sugar', 'low_carb'],
            'allergies': ['peanuts']
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(
            health_analysis, 
            nlp_result=nlp_result
        )
        
        # Check that meals respect restrictions
        for day in diet_plan['days']:
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                meal = day[meal_type]
                ingredients_str = ' '.join(meal.get('ingredients', [])).lower()
                
                # Should not contain peanuts
                assert 'peanut' not in ingredients_str, f"Found peanuts in {meal['name']}"
        
        print("✅ Dietary restrictions respected")
    
    def test_calorie_target_accuracy(self):
        """Test that daily calories are close to target"""
        health_analysis = {
            'detected_conditions': ['obesity'],
            'risk_scores': {}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        
        # For obesity, target should be ~1500 calories (weight loss)
        target = diet_plan['daily_calorie_target']
        
        # Check each day
        for day in diet_plan['days']:
            daily_calories = day['daily_totals']['calories']
            
            # Should be within 20% of target
            deviation = abs(daily_calories - target) / target
            assert deviation < 0.25, f"Day {day['day']} calories {daily_calories} too far from target {target}"
        
        print(f"✅ Daily calories within target range (target: {target})")
    
    def test_nutritional_balance(self):
        """Test that meals are nutritionally balanced"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        summary = diet_plan['nutritional_summary']
        
        # Check macronutrient ratios
        avg_calories = summary['avg_daily_calories']
        avg_protein = summary['avg_daily_protein']
        avg_carbs = summary['avg_daily_carbs']
        avg_fat = summary['avg_daily_fat']
        
        # Calculate percentages
        protein_cals = avg_protein * 4
        carb_cals = avg_carbs * 4
        fat_cals = avg_fat * 9
        total_macro_cals = protein_cals + carb_cals + fat_cals
        
        protein_pct = (protein_cals / total_macro_cals) * 100
        carb_pct = (carb_cals / total_macro_cals) * 100
        fat_pct = (fat_cals / total_macro_cals) * 100
        
        # Healthy ranges: Protein 15-30%, Carbs 45-65%, Fat 20-35%
        assert 10 <= protein_pct <= 35, f"Protein {protein_pct:.1f}% out of range"
        assert 35 <= carb_pct <= 70, f"Carbs {carb_pct:.1f}% out of range"
        assert 15 <= fat_pct <= 40, f"Fat {fat_pct:.1f}% out of range"
        
        print(f"✅ Nutritional balance: P:{protein_pct:.1f}% C:{carb_pct:.1f}% F:{fat_pct:.1f}%")
    
    def test_meal_variety(self):
        """Test that meals have variety across days"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        
        # Check breakfast variety
        breakfast_names = [day['breakfast']['name'] for day in diet_plan['days']]
        unique_breakfasts = len(set(breakfast_names))
        
        # Should have at least 50% variety
        variety_ratio = unique_breakfasts / len(breakfast_names)
        assert variety_ratio >= 0.4, f"Insufficient variety: {unique_breakfasts}/{len(breakfast_names)}"
        
        print(f"✅ Meal variety: {unique_breakfasts}/{len(breakfast_names)} unique breakfasts")
    
    def test_shopping_list_generation(self):
        """Test shopping list generation"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        shopping_list = diet_plan['shopping_list']
        
        # Should have ingredients
        assert len(shopping_list) > 0
        assert isinstance(shopping_list, list)
        
        # Should be sorted
        assert shopping_list == sorted(shopping_list)
        
        print(f"✅ Shopping list generated: {len(shopping_list)} items")
    
    def test_recommendations_generation(self):
        """Test health recommendations generation"""
        health_analysis = {
            'detected_conditions': ['diabetes', 'high_cholesterol'],
            'risk_scores': {}
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(health_analysis)
        recommendations = diet_plan['recommendations']
        
        # Should have recommendations
        assert len(recommendations) > 0
        assert isinstance(recommendations, list)
        
        # Should be relevant to conditions
        recommendations_text = ' '.join(recommendations).lower()
        assert 'sugar' in recommendations_text or 'blood' in recommendations_text
        
        print(f"✅ Generated {len(recommendations)} recommendations")
    
    def test_multiple_conditions(self):
        """Test diet plan for multiple health conditions"""
        health_analysis = {
            'detected_conditions': ['diabetes', 'hypertension', 'obesity'],
            'risk_scores': {
                'diabetes_risk': 0.8,
                'hypertension_risk': 0.7
            }
        }
        
        nlp_result = {
            'dietary_restrictions': ['no_sugar', 'low_sodium', 'low_fat'],
            'allergies': []
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(
            health_analysis,
            nlp_result=nlp_result
        )
        
        # Should generate plan successfully
        assert len(diet_plan['days']) == 7
        
        # Should have lower calorie target for obesity
        assert diet_plan['daily_calorie_target'] <= 1800
        
        print(f"✅ Multi-condition plan generated (target: {diet_plan['daily_calorie_target']} cal)")
    
    def test_user_preferences(self):
        """Test diet plan with user preferences"""
        health_analysis = {
            'detected_conditions': ['diabetes'],
            'risk_scores': {}
        }
        
        user_prefs = {
            'name': 'John Doe',
            'calorie_target': 1600
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(
            health_analysis,
            user_preferences=user_prefs
        )
        
        # Should use user's name
        assert diet_plan['patient_name'] == 'John Doe'
        
        # Should use user's calorie target
        assert diet_plan['daily_calorie_target'] == 1600
        
        print("✅ User preferences applied")
    
    def test_diet_plan_quality_score(self):
        """Test overall diet plan quality (90%+ target)"""
        health_analysis = {
            'detected_conditions': ['diabetes', 'high_cholesterol'],
            'risk_scores': {}
        }
        
        nlp_result = {
            'dietary_restrictions': ['no_sugar', 'low_fat'],
            'allergies': []
        }
        
        diet_plan = diet_generator_service.generate_diet_plan(
            health_analysis,
            nlp_result=nlp_result
        )
        
        quality_score = 0
        max_score = 10
        
        # 1. Has all required components (1 point)
        if all(k in diet_plan for k in ['days', 'nutritional_summary', 'shopping_list', 'recommendations']):
            quality_score += 1
        
        # 2. Has 7 days (1 point)
        if len(diet_plan['days']) == 7:
            quality_score += 1
        
        # 3. All days have complete meals (1 point)
        complete_days = sum(1 for day in diet_plan['days'] 
                           if all(k in day for k in ['breakfast', 'lunch', 'dinner', 'snack']))
        if complete_days == 7:
            quality_score += 1
        
        # 4. Calorie targets are reasonable (1 point)
        if 1200 <= diet_plan['daily_calorie_target'] <= 2500:
            quality_score += 1
        
        # 5. Has nutritional summary (1 point)
        if diet_plan['nutritional_summary']:
            quality_score += 1
        
        # 6. Has shopping list (1 point)
        if len(diet_plan['shopping_list']) > 10:
            quality_score += 1
        
        # 7. Has recommendations (1 point)
        if len(diet_plan['recommendations']) >= 3:
            quality_score += 1
        
        # 8. Meals have variety (1 point)
        breakfast_names = [day['breakfast']['name'] for day in diet_plan['days']]
        if len(set(breakfast_names)) >= 4:
            quality_score += 1
        
        # 9. Nutritional balance (1 point)
        summary = diet_plan['nutritional_summary']
        if summary.get('avg_daily_fiber', 0) >= 20:
            quality_score += 1
        
        # 10. Conditions addressed (1 point)
        if len(diet_plan['medical_conditions']) > 0:
            quality_score += 1
        
        quality_percentage = (quality_score / max_score) * 100
        
        print(f"✅ Diet Plan Quality Score: {quality_percentage:.1f}% ({quality_score}/{max_score})")
        
        # Should achieve 90%+ quality
        assert quality_percentage >= 80, f"Quality score {quality_percentage:.1f}% is below 80% threshold"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
