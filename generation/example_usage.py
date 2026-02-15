"""
Example usage of the Diet Plan Generator.

This script demonstrates how to use the DietPlanGenerator class to create
personalized diet plans based on patient profiles, health conditions, and
dietary preferences.
"""

from datetime import datetime
from ai_diet_planner.generation.diet_planner import DietPlanGenerator
from ai_diet_planner.models import (
    PatientProfile,
    UserPreferences,
    HealthCondition,
    DietRule,
    ConditionType,
    RulePriority,
    MetricType,
)


def example_basic_diet_plan():
    """Generate a basic diet plan for a healthy individual."""
    print("=" * 80)
    print("Example 1: Basic Diet Plan for Healthy Individual")
    print("=" * 80)
    
    # Create patient profile
    patient = PatientProfile(
        patient_id="patient-001",
        age=30,
        gender="female",
        height_cm=165,
        weight_kg=60,
        activity_level="moderate",
        preferences=UserPreferences(
            dietary_style=None,
            allergies=[],
            dislikes=[],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )
    
    # Initialize generator
    generator = DietPlanGenerator()
    
    # Generate plan
    plan = generator.generate_plan(
        patient_profile=patient,
        health_conditions=[],
        diet_rules=[],
        preferences=patient.preferences
    )
    
    # Display results
    print(f"\nPatient ID: {plan.patient_id}")
    print(f"Daily Calories: {plan.daily_calories} kcal")
    print(f"Macronutrient Targets:")
    print(f"  - Protein: {plan.macronutrient_targets.protein_percent}%")
    print(f"  - Carbs: {plan.macronutrient_targets.carbs_percent}%")
    print(f"  - Fat: {plan.macronutrient_targets.fat_percent}%")
    
    print("\nDaily Meal Plan:")
    for meal in plan.meals:
        print(f"\n{meal.meal_type.value.upper()}:")
        print(f"  Total: {meal.total_calories} kcal | "
              f"Protein: {meal.total_protein_g}g | "
              f"Carbs: {meal.total_carbs_g}g | "
              f"Fat: {meal.total_fat_g}g")
        for portion in meal.portions:
            print(f"    - {portion.food.name}: {portion.amount}{portion.unit} "
                  f"({portion.calories} kcal)")
    
    print("\nRecommendations:")
    for i, rec in enumerate(plan.recommendations, 1):
        print(f"  {i}. {rec}")


def example_diabetes_diet_plan():
    """Generate a diet plan for a patient with diabetes."""
    print("\n" + "=" * 80)
    print("Example 2: Diet Plan for Diabetes Patient")
    print("=" * 80)
    
    # Create patient profile
    patient = PatientProfile(
        patient_id="patient-002",
        age=45,
        gender="male",
        height_cm=178,
        weight_kg=85,
        activity_level="light",
        preferences=UserPreferences(
            dietary_style=None,
            allergies=[],
            dislikes=[],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )
    
    # Health conditions
    health_conditions = [
        HealthCondition(
            condition_type=ConditionType.DIABETES_TYPE2,
            confidence=0.92,
            detected_at=datetime.now(),
            contributing_metrics=[MetricType.GLUCOSE, MetricType.HBA1C]
        )
    ]
    
    # Initialize generator
    generator = DietPlanGenerator()
    
    # Generate plan
    plan = generator.generate_plan(
        patient_profile=patient,
        health_conditions=health_conditions,
        diet_rules=[],
        preferences=patient.preferences
    )
    
    # Display results
    print(f"\nPatient ID: {plan.patient_id}")
    print(f"Health Conditions: {[c.condition_type.value for c in plan.health_conditions]}")
    print(f"Daily Calories: {plan.daily_calories} kcal")
    print(f"Macronutrient Targets (adjusted for diabetes):")
    print(f"  - Protein: {plan.macronutrient_targets.protein_percent}%")
    print(f"  - Carbs: {plan.macronutrient_targets.carbs_percent}%")
    print(f"  - Fat: {plan.macronutrient_targets.fat_percent}%")
    
    print("\nKey Recommendations:")
    for rec in plan.recommendations[:3]:
        print(f"  - {rec}")


def example_vegetarian_with_allergies():
    """Generate a diet plan for a vegetarian with food allergies."""
    print("\n" + "=" * 80)
    print("Example 3: Vegetarian Diet Plan with Allergies")
    print("=" * 80)
    
    # Create patient profile
    patient = PatientProfile(
        patient_id="patient-003",
        age=28,
        gender="female",
        height_cm=160,
        weight_kg=55,
        activity_level="active",
        preferences=UserPreferences(
            dietary_style="vegetarian",
            allergies=["eggs", "milk"],
            dislikes=["mushrooms"],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )
    
    # Initialize generator
    generator = DietPlanGenerator()
    
    # Generate plan
    plan = generator.generate_plan(
        patient_profile=patient,
        health_conditions=[],
        diet_rules=[],
        preferences=patient.preferences
    )
    
    # Display results
    print(f"\nPatient ID: {plan.patient_id}")
    print(f"Dietary Style: {patient.preferences.dietary_style}")
    print(f"Allergies: {', '.join(patient.preferences.allergies)}")
    print(f"Daily Calories: {plan.daily_calories} kcal")
    
    print("\nSample Meals:")
    for meal in plan.meals[:2]:  # Show first 2 meals
        print(f"\n{meal.meal_type.value.upper()}:")
        for portion in meal.portions:
            print(f"  - {portion.food.name}: {portion.amount}{portion.unit}")


def example_obesity_weight_loss():
    """Generate a weight loss diet plan for an obese patient."""
    print("\n" + "=" * 80)
    print("Example 4: Weight Loss Plan for Obesity")
    print("=" * 80)
    
    # Create patient profile
    patient = PatientProfile(
        patient_id="patient-004",
        age=40,
        gender="male",
        height_cm=175,
        weight_kg=105,  # BMI ~34 (Obesity Class 1)
        activity_level="sedentary",
        preferences=UserPreferences(
            dietary_style=None,
            allergies=[],
            dislikes=[],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )
    
    # Health conditions
    health_conditions = [
        HealthCondition(
            condition_type=ConditionType.OBESITY_CLASS2,
            confidence=0.95,
            detected_at=datetime.now(),
            contributing_metrics=[MetricType.BMI]
        )
    ]
    
    # Initialize generator
    generator = DietPlanGenerator()
    
    # Calculate baseline calories (without deficit)
    baseline_calories = generator.calculate_daily_calories(
        age=patient.age,
        gender=patient.gender,
        weight_kg=patient.weight_kg,
        height_cm=patient.height_cm,
        activity_level=patient.activity_level
    )
    
    # Generate plan (will include caloric deficit)
    plan = generator.generate_plan(
        patient_profile=patient,
        health_conditions=health_conditions,
        diet_rules=[],
        preferences=patient.preferences
    )
    
    # Display results
    print(f"\nPatient ID: {plan.patient_id}")
    print(f"Health Conditions: {[c.condition_type.value for c in plan.health_conditions]}")
    print(f"Baseline Calories (maintenance): {baseline_calories} kcal")
    print(f"Target Calories (deficit): {plan.daily_calories} kcal")
    print(f"Daily Deficit: {baseline_calories - plan.daily_calories} kcal")
    print(f"\nMacronutrient Targets (high protein for satiety):")
    print(f"  - Protein: {plan.macronutrient_targets.protein_percent}%")
    print(f"  - Carbs: {plan.macronutrient_targets.carbs_percent}%")
    print(f"  - Fat: {plan.macronutrient_targets.fat_percent}%")
    
    print("\nWeight Loss Recommendations:")
    weight_loss_recs = [r for r in plan.recommendations if "weight" in r.lower() or "caloric" in r.lower()]
    for rec in weight_loss_recs:
        print(f"  - {rec}")


def example_with_medical_restrictions():
    """Generate a diet plan with medical dietary restrictions."""
    print("\n" + "=" * 80)
    print("Example 5: Diet Plan with Medical Restrictions")
    print("=" * 80)
    
    # Create patient profile
    patient = PatientProfile(
        patient_id="patient-005",
        age=55,
        gender="female",
        height_cm=162,
        weight_kg=70,
        activity_level="light",
        preferences=UserPreferences(
            dietary_style=None,
            allergies=[],
            dislikes=[],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )
    
    # Health conditions
    health_conditions = [
        HealthCondition(
            condition_type=ConditionType.HYPERTENSION_STAGE1,
            confidence=0.88,
            detected_at=datetime.now(),
            contributing_metrics=[MetricType.BLOOD_PRESSURE_SYSTOLIC]
        ),
        HealthCondition(
            condition_type=ConditionType.HYPERLIPIDEMIA,
            confidence=0.85,
            detected_at=datetime.now(),
            contributing_metrics=[MetricType.CHOLESTEROL_TOTAL, MetricType.CHOLESTEROL_LDL]
        )
    ]
    
    # Medical dietary rules
    diet_rules = [
        DietRule(
            rule_text="Limit sodium intake for blood pressure management",
            priority=RulePriority.REQUIRED,
            food_categories=["sodium"],
            action="limit",
            source="nlp_extraction"
        ),
        DietRule(
            rule_text="Reduce saturated fat intake",
            priority=RulePriority.RECOMMENDED,
            food_categories=["fats"],
            action="limit",
            source="nlp_extraction"
        )
    ]
    
    # Initialize generator
    generator = DietPlanGenerator()
    
    # Generate plan
    plan = generator.generate_plan(
        patient_profile=patient,
        health_conditions=health_conditions,
        diet_rules=diet_rules,
        preferences=patient.preferences
    )
    
    # Display results
    print(f"\nPatient ID: {plan.patient_id}")
    print(f"Health Conditions:")
    for condition in plan.health_conditions:
        print(f"  - {condition.condition_type.value} (confidence: {condition.confidence:.2f})")
    
    print(f"\nMacronutrient Targets (adjusted for hyperlipidemia):")
    print(f"  - Protein: {plan.macronutrient_targets.protein_percent}%")
    print(f"  - Carbs: {plan.macronutrient_targets.carbs_percent}%")
    print(f"  - Fat: {plan.macronutrient_targets.fat_percent}% (reduced)")
    
    print("\nKey Medical Recommendations:")
    medical_recs = [r for r in plan.recommendations if "sodium" in r.lower() or "fat" in r.lower() or "cholesterol" in r.lower()]
    for rec in medical_recs:
        print(f"  - {rec}")


if __name__ == "__main__":
    # Run all examples
    example_basic_diet_plan()
    example_diabetes_diet_plan()
    example_vegetarian_with_allergies()
    example_obesity_weight_loss()
    example_with_medical_restrictions()
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
