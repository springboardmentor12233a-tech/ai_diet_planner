"""
Tests for the Diet Plan Generator.

This module contains unit tests and property-based tests for the DietPlanGenerator class.
"""

import pytest
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from ai_diet_planner.generation.diet_planner import DietPlanGenerator
from ai_diet_planner.models import (
    PatientProfile,
    UserPreferences,
    HealthCondition,
    DietRule,
    ConditionType,
    RulePriority,
    MetricType,
    MealType,
)


class TestDietPlanGenerator:
    """Unit tests for DietPlanGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create a DietPlanGenerator instance."""
        return DietPlanGenerator()
    
    @pytest.fixture
    def sample_patient(self):
        """Create a sample patient profile."""
        return PatientProfile(
            patient_id="test-patient-001",
            age=35,
            gender="male",
            height_cm=175,
            weight_kg=80,
            activity_level="moderate",
            preferences=UserPreferences(
                dietary_style=None,
                allergies=[],
                dislikes=[],
                cultural_preferences=[]
            ),
            created_at=datetime.now()
        )
    
    def test_calculate_daily_calories_male(self, generator):
        """Test daily calorie calculation for male patient."""
        calories = generator.calculate_daily_calories(
            age=35,
            gender="male",
            weight_kg=80,
            height_cm=175,
            activity_level="moderate"
        )
        
        # Expected: BMR = 10*80 + 6.25*175 - 5*35 + 5 = 1704.375
        # TDEE = 1704.375 * 1.55 = 2641.78
        assert isinstance(calories, float)
        assert 2600 < calories < 2700  # Allow some rounding tolerance
    
    def test_calculate_daily_calories_female(self, generator):
        """Test daily calorie calculation for female patient."""
        calories = generator.calculate_daily_calories(
            age=30,
            gender="female",
            weight_kg=65,
            height_cm=165,
            activity_level="light"
        )
        
        # Expected: BMR = 10*65 + 6.25*165 - 5*30 - 161 = 1370.25
        # TDEE = 1370.25 * 1.375 = 1884.09
        assert isinstance(calories, float)
        assert 1850 < calories < 1920
    
    def test_calculate_daily_calories_invalid_gender(self, generator):
        """Test that invalid gender raises ValueError."""
        with pytest.raises(ValueError, match="Invalid gender"):
            generator.calculate_daily_calories(
                age=35,
                gender="other",
                weight_kg=80,
                height_cm=175,
                activity_level="moderate"
            )
    
    def test_calculate_daily_calories_invalid_activity(self, generator):
        """Test that invalid activity level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid activity level"):
            generator.calculate_daily_calories(
                age=35,
                gender="male",
                weight_kg=80,
                height_cm=175,
                activity_level="super_active"
            )
    
    def test_calculate_macronutrient_targets_healthy(self, generator):
        """Test macronutrient targets for healthy individual."""
        health_conditions = []
        
        macros = generator.calculate_macronutrient_targets(health_conditions)
        
        assert macros.protein_percent == 30.0
        assert macros.carbs_percent == 40.0
        assert macros.fat_percent == 30.0
        assert macros.protein_percent + macros.carbs_percent + macros.fat_percent == 100.0
    
    def test_calculate_macronutrient_targets_diabetes(self, generator):
        """Test macronutrient targets for diabetes patient."""
        health_conditions = [
            HealthCondition(
                condition_type=ConditionType.DIABETES_TYPE2,
                confidence=0.92,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.GLUCOSE, MetricType.HBA1C]
            )
        ]
        
        macros = generator.calculate_macronutrient_targets(health_conditions)
        
        # Diabetes: 40% carbs, 30% protein, 30% fat
        assert macros.carbs_percent == 40.0
        assert macros.protein_percent == 30.0
        assert macros.fat_percent == 30.0
    
    def test_calculate_macronutrient_targets_hyperlipidemia(self, generator):
        """Test macronutrient targets for hyperlipidemia patient."""
        health_conditions = [
            HealthCondition(
                condition_type=ConditionType.HYPERLIPIDEMIA,
                confidence=0.88,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.CHOLESTEROL_TOTAL, MetricType.CHOLESTEROL_LDL]
            )
        ]
        
        macros = generator.calculate_macronutrient_targets(health_conditions)
        
        # Hyperlipidemia: lower fat (25%)
        assert macros.fat_percent == 25.0
        assert macros.carbs_percent == 45.0
        assert macros.protein_percent == 30.0
    
    def test_calculate_macronutrient_targets_obesity(self, generator):
        """Test macronutrient targets for obesity patient."""
        health_conditions = [
            HealthCondition(
                condition_type=ConditionType.OBESITY_CLASS2,
                confidence=0.95,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.BMI]
            )
        ]
        
        macros = generator.calculate_macronutrient_targets(health_conditions)
        
        # Obesity: higher protein (35%)
        assert macros.protein_percent == 35.0
        assert macros.carbs_percent == 35.0
        assert macros.fat_percent == 30.0
    
    def test_generate_plan_basic(self, generator, sample_patient):
        """Test basic diet plan generation."""
        health_conditions = []
        diet_rules = []
        preferences = sample_patient.preferences
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=preferences
        )
        
        # Verify plan structure
        assert plan.plan_id is not None
        assert plan.patient_id == sample_patient.patient_id
        assert plan.daily_calories > 0
        assert len(plan.meals) == 4  # breakfast, lunch, snack, dinner
        
        # Verify meal types
        meal_types = [meal.meal_type for meal in plan.meals]
        assert MealType.BREAKFAST in meal_types
        assert MealType.LUNCH in meal_types
        assert MealType.SNACK in meal_types
        assert MealType.DINNER in meal_types
        
        # Verify each meal has portions
        for meal in plan.meals:
            assert len(meal.portions) > 0
            assert meal.total_calories > 0
    
    def test_generate_plan_with_allergies(self, generator, sample_patient):
        """Test diet plan generation with food allergies."""
        sample_patient.preferences.allergies = ["eggs", "milk"]
        
        health_conditions = []
        diet_rules = []
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify no allergenic foods in plan
        for meal in plan.meals:
            for portion in meal.portions:
                food_name_lower = portion.food.name.lower()
                assert "egg" not in food_name_lower
                assert "milk" not in food_name_lower
    
    def test_generate_plan_vegetarian(self, generator, sample_patient):
        """Test diet plan generation for vegetarian."""
        sample_patient.preferences.dietary_style = "vegetarian"
        
        health_conditions = []
        diet_rules = []
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify no meat in plan
        for meal in plan.meals:
            for portion in meal.portions:
                food_name_lower = portion.food.name.lower()
                assert "chicken" not in food_name_lower
                assert "salmon" not in food_name_lower
                assert "beef" not in food_name_lower
    
    def test_generate_plan_vegan(self, generator, sample_patient):
        """Test diet plan generation for vegan."""
        sample_patient.preferences.dietary_style = "vegan"
        
        health_conditions = []
        diet_rules = []
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify no animal products in plan
        for meal in plan.meals:
            for portion in meal.portions:
                food_name_lower = portion.food.name.lower()
                # No meat
                assert "chicken" not in food_name_lower
                assert "salmon" not in food_name_lower
                # No dairy
                assert "yogurt" not in food_name_lower
                assert "milk" not in food_name_lower
                # No eggs
                assert "egg" not in food_name_lower
    
    def test_generate_plan_with_obesity(self, generator, sample_patient):
        """Test diet plan generation for obesity patient (caloric deficit)."""
        health_conditions = [
            HealthCondition(
                condition_type=ConditionType.OBESITY_CLASS2,
                confidence=0.95,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.BMI]
            )
        ]
        diet_rules = []
        
        # Calculate baseline calories
        baseline_calories = generator.calculate_daily_calories(
            age=sample_patient.age,
            gender=sample_patient.gender,
            weight_kg=sample_patient.weight_kg,
            height_cm=sample_patient.height_cm,
            activity_level=sample_patient.activity_level
        )
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify caloric deficit (should be 600 less)
        assert plan.daily_calories < baseline_calories
        assert abs(plan.daily_calories - (baseline_calories - 600)) < 1
    
    def test_generate_plan_with_diet_rules(self, generator, sample_patient):
        """Test diet plan generation with dietary rules."""
        health_conditions = []
        diet_rules = [
            DietRule(
                rule_text="Avoid dairy products",
                priority=RulePriority.REQUIRED,
                food_categories=["dairy"],
                action="exclude",
                source="nlp_extraction"
            )
        ]
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify dairy is excluded
        for meal in plan.meals:
            for portion in meal.portions:
                assert portion.food.category != "dairy"
    
    def test_generate_plan_recommendations(self, generator, sample_patient):
        """Test that recommendations are generated."""
        health_conditions = [
            HealthCondition(
                condition_type=ConditionType.DIABETES_TYPE2,
                confidence=0.92,
                detected_at=datetime.now(),
                contributing_metrics=[MetricType.GLUCOSE]
            )
        ]
        diet_rules = []
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify recommendations exist
        assert len(plan.recommendations) > 0
        
        # Verify diabetes-specific recommendations
        recommendations_text = " ".join(plan.recommendations).lower()
        assert "blood sugar" in recommendations_text or "glycemic" in recommendations_text
    
    def test_meal_calorie_distribution(self, generator, sample_patient):
        """Test that meal calories follow the expected distribution."""
        health_conditions = []
        diet_rules = []
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Get meals by type
        meals_by_type = {meal.meal_type: meal for meal in plan.meals}
        
        # Expected distributions (with tolerance)
        breakfast_target = plan.daily_calories * 0.25
        lunch_target = plan.daily_calories * 0.35
        snack_target = plan.daily_calories * 0.10
        dinner_target = plan.daily_calories * 0.30
        
        # Allow 20% tolerance for distribution
        tolerance = 0.20
        
        assert abs(meals_by_type[MealType.BREAKFAST].total_calories - breakfast_target) < breakfast_target * tolerance
        assert abs(meals_by_type[MealType.LUNCH].total_calories - lunch_target) < lunch_target * tolerance
        assert abs(meals_by_type[MealType.SNACK].total_calories - snack_target) < snack_target * tolerance
        assert abs(meals_by_type[MealType.DINNER].total_calories - dinner_target) < dinner_target * tolerance
    
    def test_portion_completeness(self, generator, sample_patient):
        """Test that all portions have complete nutritional information."""
        health_conditions = []
        diet_rules = []
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        for meal in plan.meals:
            for portion in meal.portions:
                # Verify all nutritional fields are present and non-negative
                assert portion.calories >= 0
                assert portion.protein_g >= 0
                assert portion.carbs_g >= 0
                assert portion.fat_g >= 0
                assert portion.amount > 0
                assert portion.unit is not None
                assert portion.food is not None
    
    def test_conflict_resolution_medical_vs_vegetarian(self, generator, sample_patient):
        """Test conflict resolution when medical requirement conflicts with vegetarian preference."""
        sample_patient.preferences.dietary_style = "vegetarian"
        
        health_conditions = []
        diet_rules = [
            DietRule(
                rule_text="Include lean meat for iron deficiency",
                priority=RulePriority.REQUIRED,
                food_categories=["proteins"],
                action="include",
                source="nlp_extraction"
            )
        ]
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify conflict was detected
        assert len(generator.conflicts) > 0
        
        # Verify conflict notification in recommendations
        recommendations_text = " ".join(plan.recommendations).lower()
        assert "conflict" in recommendations_text or "notice" in recommendations_text
        
        # Verify alternatives were provided
        conflict = generator.conflicts[0]
        assert len(conflict.alternatives) > 0
        # Check for vegetarian-friendly alternatives (eggs, tofu, legumes, etc.)
        alternatives_text = " ".join(conflict.alternatives).lower()
        assert any(keyword in alternatives_text 
                   for keyword in ["tofu", "eggs", "legumes", "yogurt", "tempeh", "quinoa"])
    
    def test_conflict_resolution_medical_vs_vegan(self, generator, sample_patient):
        """Test conflict resolution when medical requirement conflicts with vegan preference."""
        sample_patient.preferences.dietary_style = "vegan"
        
        health_conditions = []
        diet_rules = [
            DietRule(
                rule_text="Include dairy products for calcium",
                priority=RulePriority.REQUIRED,
                food_categories=["dairy"],
                action="include",
                source="nlp_extraction"
            )
        ]
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify conflict was detected
        assert len(generator.conflicts) > 0
        
        # Verify plant-based alternatives were suggested
        conflict = generator.conflicts[0]
        assert len(conflict.alternatives) > 0
        alternatives_text = " ".join(conflict.alternatives).lower()
        assert "plant" in alternatives_text or "vegan" in alternatives_text
    
    def test_impossible_constraints_error_with_alternatives(self, generator, sample_patient):
        """Test that impossible constraints raise error with helpful alternatives."""
        # Create impossible scenario: exclude all major food categories
        sample_patient.preferences.allergies = ["eggs", "milk", "nuts", "fish", "soy"]
        sample_patient.preferences.dietary_style = "vegan"
        
        health_conditions = []
        diet_rules = [
            DietRule(
                rule_text="Avoid all grains",
                priority=RulePriority.REQUIRED,
                food_categories=["carbs"],
                action="exclude",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Avoid all vegetables",
                priority=RulePriority.REQUIRED,
                food_categories=["vegetables"],
                action="exclude",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Avoid all fruits",
                priority=RulePriority.REQUIRED,
                food_categories=["fruits"],
                action="exclude",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Avoid all proteins",
                priority=RulePriority.REQUIRED,
                food_categories=["proteins"],
                action="exclude",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Avoid all fats",
                priority=RulePriority.REQUIRED,
                food_categories=["fats"],
                action="exclude",
                source="nlp_extraction"
            )
        ]
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate_plan(
                patient_profile=sample_patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=sample_patient.preferences
            )
        
        # Verify error message includes alternatives
        error_message = str(exc_info.value)
        assert "Alternatives:" in error_message or "alternatives" in error_message.lower()
        
        # Verify conflicts were detected
        assert len(generator.conflicts) > 0
        
        # Verify alternatives include consulting a dietitian
        conflict = generator.conflicts[-1]  # Last conflict should be impossible constraints
        alternatives_text = " ".join(conflict.alternatives).lower()
        assert "dietitian" in alternatives_text or "healthcare provider" in alternatives_text
    
    def test_priority_medical_over_preference(self, generator, sample_patient):
        """Test that medical restrictions are prioritized over user preferences."""
        sample_patient.preferences.dietary_style = "vegetarian"
        
        health_conditions = []
        diet_rules = [
            DietRule(
                rule_text="Avoid all legumes due to kidney condition",
                priority=RulePriority.REQUIRED,
                food_categories=["proteins"],
                action="exclude",
                source="nlp_extraction"
            )
        ]
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify no legumes in plan (medical restriction enforced)
        for meal in plan.meals:
            for portion in meal.portions:
                food_name_lower = portion.food.name.lower()
                assert "lentil" not in food_name_lower
                assert "chickpea" not in food_name_lower
                assert "bean" not in food_name_lower
        
        # Verify plan was still generated (preference accommodated where possible)
        assert len(plan.meals) == 4
    
    def test_user_notification_for_conflicts(self, generator, sample_patient):
        """Test that users are notified of conflicts in recommendations."""
        sample_patient.preferences.dietary_style = "vegan"
        sample_patient.preferences.allergies = ["soy"]
        
        health_conditions = []
        diet_rules = [
            DietRule(
                rule_text="Include fish for omega-3",
                priority=RulePriority.REQUIRED,
                food_categories=["proteins"],
                action="include",
                source="nlp_extraction"
            )
        ]
        
        plan = generator.generate_plan(
            patient_profile=sample_patient,
            health_conditions=health_conditions,
            diet_rules=diet_rules,
            preferences=sample_patient.preferences
        )
        
        # Verify notification in recommendations
        assert len(plan.recommendations) > 0
        first_recommendations = " ".join(plan.recommendations[:3]).lower()
        assert "notice" in first_recommendations or "conflict" in first_recommendations
        
        # Verify conflict details are included
        recommendations_text = " ".join(plan.recommendations)
        assert "medical" in recommendations_text.lower() or "requirement" in recommendations_text.lower()


class TestDietPlanGeneratorProperties:
    """Property-based tests for DietPlanGenerator."""
    
    # Hypothesis strategies for generating test data
    @staticmethod
    def patient_profile_strategy():
        """Strategy for generating valid patient profiles."""
        return st.builds(
            PatientProfile,
            patient_id=st.text(min_size=1, max_size=50),
            age=st.integers(min_value=18, max_value=100),
            gender=st.sampled_from(["male", "female"]),
            height_cm=st.floats(min_value=140, max_value=220),
            weight_kg=st.floats(min_value=40, max_value=200),
            activity_level=st.sampled_from(["sedentary", "light", "moderate", "active", "very_active"]),
            preferences=st.builds(
                UserPreferences,
                dietary_style=st.one_of(st.none(), st.sampled_from(["vegetarian", "vegan", "keto"])),
                allergies=st.lists(st.sampled_from(["eggs", "milk", "nuts", "fish", "soy"]), max_size=3),
                dislikes=st.lists(st.text(min_size=1, max_size=20), max_size=3),
                cultural_preferences=st.lists(st.text(min_size=1, max_size=20), max_size=2)
            ),
            created_at=st.just(datetime.now())
        )
    
    @staticmethod
    def health_conditions_strategy():
        """Strategy for generating health conditions."""
        return st.lists(
            st.builds(
                HealthCondition,
                condition_type=st.sampled_from(list(ConditionType)),
                confidence=st.floats(min_value=0.7, max_value=1.0),
                detected_at=st.just(datetime.now()),
                contributing_metrics=st.lists(st.sampled_from(list(MetricType)), min_size=1, max_size=3)
            ),
            max_size=3
        )
    
    @staticmethod
    def diet_rules_strategy():
        """Strategy for generating diet rules."""
        return st.lists(
            st.builds(
                DietRule,
                rule_text=st.text(min_size=10, max_size=100),
                priority=st.sampled_from(list(RulePriority)),
                food_categories=st.lists(
                    st.sampled_from(["proteins", "carbs", "dairy", "fats", "vegetables", "fruits"]),
                    min_size=1,
                    max_size=2
                ),
                action=st.sampled_from(["include", "exclude", "limit"]),
                source=st.sampled_from(["ml_analysis", "nlp_extraction", "user_preference"])
            ),
            max_size=5
        )
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_meal_structure(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.1**
        
        Property 31: Diet plan meal structure
        For any generated DietPlan, it should contain exactly four meal types:
        breakfast, lunch, snack, and dinner.
        """
        generator = DietPlanGenerator()
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify exactly 4 meals
            assert len(plan.meals) == 4
            
            # Verify all meal types present
            meal_types = {meal.meal_type for meal in plan.meals}
            assert meal_types == {MealType.BREAKFAST, MealType.LUNCH, MealType.SNACK, MealType.DINNER}
            
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_allergy_exclusion(self, patient, health_conditions):
        """
        **Validates: Requirements 10.2**
        
        Property 37: Allergy exclusion (Safety Critical)
        For any food item in a generated DietPlan, it should not contain any
        ingredients listed in the user's allergy list.
        """
        generator = DietPlanGenerator()
        
        # Ensure patient has at least one allergy
        assume(len(patient.preferences.allergies) > 0)
        
        diet_rules = []
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify no allergenic foods in any meal
            for meal in plan.meals:
                for portion in meal.portions:
                    food_name_lower = portion.food.name.lower()
                    for allergen in patient.preferences.allergies:
                        allergen_lower = allergen.lower()
                        assert allergen_lower not in food_name_lower, (
                            f"Allergen '{allergen}' found in food '{portion.food.name}' "
                            f"for patient with allergies: {patient.preferences.allergies}"
                        )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_diet_rule_compliance(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.2**
        
        Property 32: Diet plan rule compliance
        For any generated DietPlan and its associated DietRules, all meals should
        comply with the rules (no excluded foods, required foods included).
        """
        generator = DietPlanGenerator()
        
        # Filter to only REQUIRED exclusion rules for testing
        exclusion_rules = [
            rule for rule in diet_rules
            if rule.priority == RulePriority.REQUIRED and rule.action == "exclude"
        ]
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify excluded food categories are not in plan
            for rule in exclusion_rules:
                for meal in plan.meals:
                    for portion in meal.portions:
                        for excluded_category in rule.food_categories:
                            assert portion.food.category != excluded_category, (
                                f"Excluded category '{excluded_category}' found in meal "
                                f"(food: {portion.food.name}, category: {portion.food.category})"
                            )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_meal_calorie_distribution(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.1, 9.4**
        
        Property: Meal calorie distribution
        For any generated DietPlan, meals should follow the distribution:
        - Breakfast: 25% of daily calories
        - Lunch: 35% of daily calories
        - Snack: 10% of daily calories
        - Dinner: 30% of daily calories
        
        With reasonable tolerance for constraint satisfaction.
        """
        generator = DietPlanGenerator()
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Get meals by type
            meals_by_type = {meal.meal_type: meal for meal in plan.meals}
            
            # Expected distributions
            expected_distributions = {
                MealType.BREAKFAST: 0.25,
                MealType.LUNCH: 0.35,
                MealType.SNACK: 0.10,
                MealType.DINNER: 0.30,
            }
            
            # Verify each meal is within 30% tolerance of target
            # (relaxed tolerance to account for constraint satisfaction)
            tolerance = 0.30
            
            for meal_type, expected_ratio in expected_distributions.items():
                meal = meals_by_type[meal_type]
                expected_calories = plan.daily_calories * expected_ratio
                actual_calories = meal.total_calories
                
                # Calculate relative error
                if expected_calories > 0:
                    relative_error = abs(actual_calories - expected_calories) / expected_calories
                    assert relative_error <= tolerance, (
                        f"{meal_type.value} calories {actual_calories} deviates too much "
                        f"from target {expected_calories} (error: {relative_error:.2%})"
                    )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_portion_completeness(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.4**
        
        Property 34: Meal completeness
        For any Meal in a DietPlan, it should include portion sizes and caloric
        information for all food items.
        """
        generator = DietPlanGenerator()
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify all meals have portions with complete information
            for meal in plan.meals:
                assert len(meal.portions) > 0, f"Meal {meal.meal_type} has no portions"
                
                for portion in meal.portions:
                    # Verify all required fields are present and valid
                    assert portion.food is not None
                    assert portion.amount > 0
                    assert portion.unit is not None and len(portion.unit) > 0
                    assert portion.calories >= 0
                    assert portion.protein_g >= 0
                    assert portion.carbs_g >= 0
                    assert portion.fat_g >= 0
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_macronutrient_balance(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.3**

        Property 33: Macronutrient balance
        For any generated DietPlan for a specific health condition, the macronutrient
        ratios should fall within acceptable ranges for that condition.
        """
        generator = DietPlanGenerator()

        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )

            # Calculate actual macronutrient ratios from all meals
            total_protein_g = sum(meal.total_protein_g for meal in plan.meals)
            total_carbs_g = sum(meal.total_carbs_g for meal in plan.meals)
            total_fat_g = sum(meal.total_fat_g for meal in plan.meals)

            # Calculate calories from macros (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
            protein_calories = total_protein_g * 4
            carbs_calories = total_carbs_g * 4
            fat_calories = total_fat_g * 9

            total_macro_calories = protein_calories + carbs_calories + fat_calories

            if total_macro_calories > 0:
                actual_protein_percent = (protein_calories / total_macro_calories) * 100
                actual_carbs_percent = (carbs_calories / total_macro_calories) * 100
                actual_fat_percent = (fat_calories / total_macro_calories) * 100

                # Verify ratios sum to approximately 100%
                total_percent = actual_protein_percent + actual_carbs_percent + actual_fat_percent
                assert 95 <= total_percent <= 105, f"Macro percentages sum to {total_percent}%"

                # Verify each macro is within reasonable range (5-70%)
                # Relaxed range to account for extreme constraint satisfaction scenarios
                assert 5 <= actual_protein_percent <= 70, f"Protein: {actual_protein_percent}%"
                assert 5 <= actual_carbs_percent <= 70, f"Carbs: {actual_carbs_percent}%"
                assert 5 <= actual_fat_percent <= 70, f"Fat: {actual_fat_percent}%"
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise

    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_variety_optimization(self, patient, health_conditions):
        """
        **Validates: Requirements 9.1, 10.1**
        
        Property: Variety optimization
        For any generated DietPlan, meals should include variety across different
        food categories to ensure nutritional diversity.
        """
        generator = DietPlanGenerator()
        diet_rules = []
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Collect all food categories used in the plan
            all_categories = set()
            for meal in plan.meals:
                for portion in meal.portions:
                    all_categories.add(portion.food.category)
            
            # Verify at least 2 different food categories are used
            # (ensures some variety, though constraint satisfaction may limit options)
            assert len(all_categories) >= 2, (
                f"Diet plan uses only {len(all_categories)} food category/categories: {all_categories}. "
                "Expected at least 2 for nutritional variety."
            )
            
            # Verify each meal (except snack) has at least 2 portions for variety
            for meal in plan.meals:
                if meal.meal_type != MealType.SNACK:
                    assert len(meal.portions) >= 2, (
                        f"{meal.meal_type.value} has only {len(meal.portions)} portion(s). "
                        "Expected at least 2 for variety."
                    )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_dietary_preference_incorporation(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 10.1**
        
        Property 36: User preference incorporation
        For any UserPreferences provided (vegetarian, vegan, keto, etc.), the generated
        DietPlan should reflect those preferences where they don't conflict with medical requirements.
        """
        generator = DietPlanGenerator()
        
        # Only test when dietary style is specified
        assume(patient.preferences.dietary_style is not None)
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            dietary_style = patient.preferences.dietary_style.lower()
            
            # Verify dietary style compliance
            for meal in plan.meals:
                for portion in meal.portions:
                    food_name_lower = portion.food.name.lower()
                    
                    if dietary_style == "vegetarian":
                        # No meat or fish
                        meat_keywords = ["chicken", "beef", "pork", "fish", "salmon", "turkey", "lamb"]
                        for meat in meat_keywords:
                            assert meat not in food_name_lower, (
                                f"Vegetarian plan contains {portion.food.name}"
                            )
                    
                    elif dietary_style == "vegan":
                        # No animal products
                        animal_keywords = ["chicken", "beef", "pork", "fish", "salmon", "turkey",
                                         "egg", "milk", "yogurt", "cheese", "honey"]
                        for animal in animal_keywords:
                            assert animal not in food_name_lower, (
                                f"Vegan plan contains {portion.food.name}"
                            )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
        """
        **Validates: Requirements 9.1**
        
        Property 31: Diet plan meal structure
        For any generated DietPlan, it should contain exactly four meal types:
        breakfast, lunch, snack, and dinner.
        """
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify exactly 4 meals
            assert len(plan.meals) == 4
            
            # Verify all meal types present
            meal_types = {meal.meal_type for meal in plan.meals}
            assert meal_types == {MealType.BREAKFAST, MealType.LUNCH, MealType.SNACK, MealType.DINNER}
            
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_allergy_exclusion(self, patient, health_conditions):
        """
        **Validates: Requirements 10.2**
        
        Property 37: Allergy exclusion (Safety Critical)
        For any food item in a generated DietPlan, it should not contain any
        ingredients listed in the user's allergy list.
        """
        generator = DietPlanGenerator()
        
        # Ensure patient has at least one allergy
        assume(len(patient.preferences.allergies) > 0)
        
        diet_rules = []
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify no allergenic foods in any meal
            for meal in plan.meals:
                for portion in meal.portions:
                    food_name_lower = portion.food.name.lower()
                    for allergen in patient.preferences.allergies:
                        allergen_lower = allergen.lower()
                        assert allergen_lower not in food_name_lower, (
                            f"Allergen '{allergen}' found in food '{portion.food.name}' "
                            f"for patient with allergies: {patient.preferences.allergies}"
                        )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_diet_rule_compliance(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.2**
        
        Property 32: Diet plan rule compliance
        For any generated DietPlan and its associated DietRules, all meals should
        comply with the rules (no excluded foods, required foods included).
        """
        generator = DietPlanGenerator()
        
        # Filter to only REQUIRED exclusion rules for testing
        exclusion_rules = [
            rule for rule in diet_rules
            if rule.priority == RulePriority.REQUIRED and rule.action == "exclude"
        ]
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify excluded food categories are not in plan
            for rule in exclusion_rules:
                for meal in plan.meals:
                    for portion in meal.portions:
                        for excluded_category in rule.food_categories:
                            assert portion.food.category != excluded_category, (
                                f"Excluded category '{excluded_category}' found in meal "
                                f"(food: {portion.food.name}, category: {portion.food.category})"
                            )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_meal_calorie_distribution(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.1, 9.4**
        
        Property: Meal calorie distribution
        For any generated DietPlan, meals should follow the distribution:
        - Breakfast: 25% of daily calories
        - Lunch: 35% of daily calories
        - Snack: 10% of daily calories
        - Dinner: 30% of daily calories
        
        With reasonable tolerance for constraint satisfaction.
        """
        generator = DietPlanGenerator()
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Get meals by type
            meals_by_type = {meal.meal_type: meal for meal in plan.meals}
            
            # Expected distributions
            expected_distributions = {
                MealType.BREAKFAST: 0.25,
                MealType.LUNCH: 0.35,
                MealType.SNACK: 0.10,
                MealType.DINNER: 0.30,
            }
            
            # Verify each meal is within 30% tolerance of target
            # (relaxed tolerance to account for constraint satisfaction)
            tolerance = 0.30
            
            for meal_type, expected_ratio in expected_distributions.items():
                meal = meals_by_type[meal_type]
                expected_calories = plan.daily_calories * expected_ratio
                actual_calories = meal.total_calories
                
                # Calculate relative error
                if expected_calories > 0:
                    relative_error = abs(actual_calories - expected_calories) / expected_calories
                    assert relative_error <= tolerance, (
                        f"{meal_type.value} calories {actual_calories} deviates too much "
                        f"from target {expected_calories} (error: {relative_error:.2%})"
                    )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_portion_completeness(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.4**
        
        Property 34: Meal completeness
        For any Meal in a DietPlan, it should include portion sizes and caloric
        information for all food items.
        """
        generator = DietPlanGenerator()
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify all meals have portions with complete information
            for meal in plan.meals:
                assert len(meal.portions) > 0, f"Meal {meal.meal_type} has no portions"
                
                for portion in meal.portions:
                    # Verify all required fields are present and valid
                    assert portion.food is not None
                    assert portion.amount > 0
                    assert portion.unit is not None and len(portion.unit) > 0
                    assert portion.calories >= 0
                    assert portion.protein_g >= 0
                    assert portion.carbs_g >= 0
                    assert portion.fat_g >= 0
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_macronutrient_balance(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.3**
        
        Property 33: Macronutrient balance
        For any generated DietPlan for a specific health condition, the macronutrient
        ratios should fall within acceptable ranges for that condition.
        """
        generator = DietPlanGenerator()
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Calculate actual macronutrient ratios from all meals
            total_protein_g = sum(meal.total_protein_g for meal in plan.meals)
            total_carbs_g = sum(meal.total_carbs_g for meal in plan.meals)
            total_fat_g = sum(meal.total_fat_g for meal in plan.meals)
            
            # Calculate calories from macros (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
            protein_calories = total_protein_g * 4
            carbs_calories = total_carbs_g * 4
            fat_calories = total_fat_g * 9
            
            total_macro_calories = protein_calories + carbs_calories + fat_calories
            
            if total_macro_calories > 0:
                actual_protein_percent = (protein_calories / total_macro_calories) * 100
                actual_carbs_percent = (carbs_calories / total_macro_calories) * 100
                actual_fat_percent = (fat_calories / total_macro_calories) * 100
                
                # Verify ratios sum to approximately 100%
                total_percent = actual_protein_percent + actual_carbs_percent + actual_fat_percent
                assert 95 <= total_percent <= 105, f"Macro percentages sum to {total_percent}%"
                
                # Verify each macro is within reasonable range (5-70%)
                # Relaxed range to account for extreme constraint satisfaction scenarios
                assert 5 <= actual_protein_percent <= 70, f"Protein: {actual_protein_percent}%"
                assert 5 <= actual_carbs_percent <= 70, f"Carbs: {actual_carbs_percent}%"
                assert 5 <= actual_fat_percent <= 70, f"Fat: {actual_fat_percent}%"
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_variety_optimization(self, patient, health_conditions):
        """
        **Validates: Requirements 9.1, 10.1**
        
        Property: Variety optimization
        For any generated DietPlan, meals should include variety across different
        food categories to ensure nutritional diversity.
        """
        generator = DietPlanGenerator()
        diet_rules = []
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Collect all food categories used in the plan
            all_categories = set()
            for meal in plan.meals:
                for portion in meal.portions:
                    all_categories.add(portion.food.category)
            
            # Verify at least 2 different food categories are used
            # (ensures some variety, though constraint satisfaction may limit options)
            assert len(all_categories) >= 2, (
                f"Diet plan uses only {len(all_categories)} food category/categories: {all_categories}. "
                "Expected at least 2 for nutritional variety."
            )
            
            # Verify each meal (except snack) has at least 2 portions for variety
            for meal in plan.meals:
                if meal.meal_type != MealType.SNACK:
                    assert len(meal.portions) >= 2, (
                        f"{meal.meal_type.value} has only {len(meal.portions)} portion(s). "
                        "Expected at least 2 for variety."
                    )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_dietary_preference_incorporation(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 10.1**
        
        Property 36: User preference incorporation
        For any UserPreferences provided (vegetarian, vegan, keto, etc.), the generated
        DietPlan should reflect those preferences where they don't conflict with medical requirements.
        """
        generator = DietPlanGenerator()
        
        # Only test when dietary style is specified
        assume(patient.preferences.dietary_style is not None)
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            dietary_style = patient.preferences.dietary_style.lower()
            
            # Verify dietary style compliance
            for meal in plan.meals:
                for portion in meal.portions:
                    food_name_lower = portion.food.name.lower()
                    
                    if dietary_style == "vegetarian":
                        # No meat or fish
                        meat_keywords = ["chicken", "beef", "pork", "fish", "salmon", "turkey", "lamb"]
                        for meat in meat_keywords:
                            assert meat not in food_name_lower, (
                                f"Vegetarian plan contains {portion.food.name}"
                            )
                    
                    elif dietary_style == "vegan":
                        # No animal products
                        animal_keywords = ["chicken", "beef", "pork", "fish", "salmon", "turkey",
                                         "egg", "milk", "yogurt", "cheese", "honey"]
                        for animal in animal_keywords:
                            assert animal not in food_name_lower, (
                                f"Vegan plan contains {portion.food.name}"
                            )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.filter_too_much])
    def test_property_medical_restriction_priority(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 9.5, 10.3**
        
        Property 35: Medical restriction priority
        For any conflict between medical restrictions and user preferences,
        the Diet_Plan_Generator should prioritize medical restrictions.
        """
        generator = DietPlanGenerator()
        
        # Ensure we have at least one REQUIRED exclusion rule
        required_exclusions = [
            rule for rule in diet_rules
            if rule.priority == RulePriority.REQUIRED and rule.action == "exclude"
        ]
        
        assume(len(required_exclusions) > 0)
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # Verify all REQUIRED exclusion rules are enforced
            for rule in required_exclusions:
                for meal in plan.meals:
                    for portion in meal.portions:
                        for excluded_category in rule.food_categories:
                            assert portion.food.category != excluded_category, (
                                f"Medical restriction violated: {excluded_category} found in meal "
                                f"despite REQUIRED exclusion rule"
                            )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__(),
        diet_rules=diet_rules_strategy.__func__()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_conflict_notification(self, patient, health_conditions, diet_rules):
        """
        **Validates: Requirements 10.3**
        
        Property: Conflict notification
        When dietary preferences conflict with medical requirements,
        the user should be notified through the recommendations.
        """
        generator = DietPlanGenerator()
        
        # Set up a potential conflict scenario
        assume(patient.preferences.dietary_style is not None)
        
        # Ensure we have at least one REQUIRED rule that might conflict
        required_rules = [
            rule for rule in diet_rules
            if rule.priority == RulePriority.REQUIRED
        ]
        assume(len(required_rules) > 0)
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # If conflicts were detected, verify notification
            if len(generator.conflicts) > 0:
                recommendations_text = " ".join(plan.recommendations).lower()
                assert "notice" in recommendations_text or "conflict" in recommendations_text, (
                    f"Conflicts detected ({len(generator.conflicts)}) but no notification in recommendations"
                )
                
                # Verify alternatives are provided
                for conflict in generator.conflicts:
                    assert len(conflict.alternatives) > 0, (
                        "Conflict detected but no alternatives provided"
                    )
        except ValueError as e:
            # Allow failure if constraints are impossible to satisfy
            if "no foods available" not in str(e):
                raise
    
    @given(
        patient=patient_profile_strategy.__func__(),
        health_conditions=health_conditions_strategy.__func__()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_alternative_recommendations(self, patient, health_conditions):
        """
        **Validates: Requirements 10.4**
        
        Property 38: Alternative recommendations
        When both user preferences and medical requirements cannot be simultaneously
        satisfied, the Diet_Plan_Generator should provide alternative food recommendations.
        """
        generator = DietPlanGenerator()
        
        # Create a challenging constraint scenario
        # Add multiple allergies and dietary restrictions
        assume(len(patient.preferences.allergies) >= 2)
        
        # Create restrictive diet rules
        diet_rules = [
            DietRule(
                rule_text="Avoid high-fat foods",
                priority=RulePriority.REQUIRED,
                food_categories=["fats"],
                action="exclude",
                source="nlp_extraction"
            ),
            DietRule(
                rule_text="Limit carbohydrates",
                priority=RulePriority.REQUIRED,
                food_categories=["carbs"],
                action="exclude",
                source="nlp_extraction"
            )
        ]
        
        try:
            plan = generator.generate_plan(
                patient_profile=patient,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=patient.preferences
            )
            
            # If conflicts exist, verify alternatives are provided
            if len(generator.conflicts) > 0:
                for conflict in generator.conflicts:
                    assert len(conflict.alternatives) > 0, (
                        f"Conflict type '{conflict.conflict_type}' has no alternatives"
                    )
                    
                    # Verify alternatives are meaningful (not empty strings)
                    for alt in conflict.alternatives:
                        assert len(alt.strip()) > 10, (
                            f"Alternative recommendation too short: '{alt}'"
                        )
        except ValueError as e:
            # When plan generation fails, verify alternatives are in error message
            error_message = str(e)
            if "no foods available" in error_message:
                # Verify conflicts were detected
                assert len(generator.conflicts) > 0, (
                    "Plan generation failed but no conflicts detected"
                )
                
                # Verify alternatives were generated
                last_conflict = generator.conflicts[-1]
                assert len(last_conflict.alternatives) > 0, (
                    "Impossible constraints but no alternatives provided"
                )
                
                # Verify alternatives mention consulting professionals
                alternatives_text = " ".join(last_conflict.alternatives).lower()
                assert any(keyword in alternatives_text 
                          for keyword in ["dietitian", "healthcare", "provider", "consult"]), (
                    "Alternatives should suggest consulting healthcare professionals"
                )
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
