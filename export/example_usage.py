"""
Example usage of the ReportExporter class.

This script demonstrates how to export diet plans to PDF and JSON formats.
"""

from datetime import datetime
from pathlib import Path

from ai_diet_planner.export.report_exporter import ReportExporter
from ai_diet_planner.models import (
    DietPlan,
    Meal,
    Portion,
    Food,
    MacronutrientRatios,
    HealthCondition,
    DietaryRestriction,
    PatientProfile,
    UserPreferences,
    MealType,
    ConditionType,
    MetricType,
)


def create_sample_diet_plan():
    """Create a sample diet plan for demonstration."""
    
    # Create sample foods
    chicken = Food(
        name="Grilled Chicken Breast",
        calories=165.0,
        protein_g=31.0,
        carbs_g=0.0,
        fat_g=3.6,
        fiber_g=0.0,
        sodium_mg=74.0,
        sugar_g=0.0,
        category="proteins",
        fdc_id="171477"
    )
    
    rice = Food(
        name="Brown Rice",
        calories=112.0,
        protein_g=2.6,
        carbs_g=23.5,
        fat_g=0.9,
        fiber_g=1.8,
        sodium_mg=5.0,
        sugar_g=0.4,
        category="carbs"
    )
    
    broccoli = Food(
        name="Steamed Broccoli",
        calories=55.0,
        protein_g=3.7,
        carbs_g=11.2,
        fat_g=0.6,
        fiber_g=3.8,
        sodium_mg=41.0,
        sugar_g=2.2,
        category="vegetables"
    )
    
    oatmeal = Food(
        name="Oatmeal",
        calories=389.0,
        protein_g=16.9,
        carbs_g=66.3,
        fat_g=6.9,
        fiber_g=10.6,
        sodium_mg=2.0,
        sugar_g=0.0,
        category="carbs"
    )
    
    banana = Food(
        name="Banana",
        calories=89.0,
        protein_g=1.1,
        carbs_g=22.8,
        fat_g=0.3,
        fiber_g=2.6,
        sodium_mg=1.0,
        sugar_g=12.2,
        category="fruits"
    )
    
    salmon = Food(
        name="Baked Salmon",
        calories=206.0,
        protein_g=22.0,
        carbs_g=0.0,
        fat_g=12.4,
        fiber_g=0.0,
        sodium_mg=59.0,
        sugar_g=0.0,
        category="proteins"
    )
    
    # Create portions
    breakfast_portions = [
        Portion(
            food=oatmeal,
            amount=50.0,
            unit="g",
            calories=194.5,
            protein_g=8.45,
            carbs_g=33.15,
            fat_g=3.45
        ),
        Portion(
            food=banana,
            amount=1.0,
            unit="piece",
            calories=89.0,
            protein_g=1.1,
            carbs_g=22.8,
            fat_g=0.3
        )
    ]
    
    lunch_portions = [
        Portion(
            food=chicken,
            amount=150.0,
            unit="g",
            calories=247.5,
            protein_g=46.5,
            carbs_g=0.0,
            fat_g=5.4
        ),
        Portion(
            food=rice,
            amount=150.0,
            unit="g",
            calories=168.0,
            protein_g=3.9,
            carbs_g=35.25,
            fat_g=1.35
        ),
        Portion(
            food=broccoli,
            amount=100.0,
            unit="g",
            calories=55.0,
            protein_g=3.7,
            carbs_g=11.2,
            fat_g=0.6
        )
    ]
    
    snack_portions = [
        Portion(
            food=banana,
            amount=1.0,
            unit="piece",
            calories=89.0,
            protein_g=1.1,
            carbs_g=22.8,
            fat_g=0.3
        )
    ]
    
    dinner_portions = [
        Portion(
            food=salmon,
            amount=150.0,
            unit="g",
            calories=309.0,
            protein_g=33.0,
            carbs_g=0.0,
            fat_g=18.6
        ),
        Portion(
            food=broccoli,
            amount=150.0,
            unit="g",
            calories=82.5,
            protein_g=5.55,
            carbs_g=16.8,
            fat_g=0.9
        )
    ]
    
    # Create meals
    breakfast = Meal(
        meal_type=MealType.BREAKFAST,
        portions=breakfast_portions,
        total_calories=283.5,
        total_protein_g=9.55,
        total_carbs_g=55.95,
        total_fat_g=3.75
    )
    
    lunch = Meal(
        meal_type=MealType.LUNCH,
        portions=lunch_portions,
        total_calories=470.5,
        total_protein_g=54.1,
        total_carbs_g=46.45,
        total_fat_g=7.35
    )
    
    snack = Meal(
        meal_type=MealType.SNACK,
        portions=snack_portions,
        total_calories=89.0,
        total_protein_g=1.1,
        total_carbs_g=22.8,
        total_fat_g=0.3
    )
    
    dinner = Meal(
        meal_type=MealType.DINNER,
        portions=dinner_portions,
        total_calories=391.5,
        total_protein_g=38.55,
        total_carbs_g=16.8,
        total_fat_g=19.5
    )
    
    # Create health condition
    health_condition = HealthCondition(
        condition_type=ConditionType.DIABETES_TYPE2,
        confidence=0.85,
        detected_at=datetime.now(),
        contributing_metrics=[MetricType.GLUCOSE, MetricType.HBA1C]
    )
    
    # Create dietary restriction
    dietary_restriction = DietaryRestriction(
        restriction_type="allergy",
        restricted_items=["peanuts", "tree nuts"],
        severity="strict"
    )
    
    # Create diet plan
    diet_plan = DietPlan(
        plan_id="plan_20240115_001",
        patient_id="patient_456",
        generated_at=datetime.now(),
        daily_calories=1234.5,
        macronutrient_targets=MacronutrientRatios(
            protein_percent=30.0,
            carbs_percent=40.0,
            fat_percent=30.0
        ),
        meals=[breakfast, lunch, snack, dinner],
        restrictions=[dietary_restriction],
        recommendations=[
            "Increase fiber intake to 25-30g per day",
            "Stay hydrated with 8-10 glasses of water daily",
            "Monitor blood glucose levels regularly",
            "Avoid refined sugars and processed foods"
        ],
        health_conditions=[health_condition]
    )
    
    return diet_plan


def create_sample_patient_profile():
    """Create a sample patient profile for demonstration."""
    
    return PatientProfile(
        patient_id="patient_456",
        age=45,
        gender="male",
        height_cm=175.0,
        weight_kg=80.0,
        activity_level="moderate",
        preferences=UserPreferences(
            dietary_style="balanced",
            allergies=["peanuts", "tree nuts"],
            dislikes=["liver", "oysters"],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )


def main():
    """Main function to demonstrate ReportExporter usage."""
    
    print("AI NutriCare System - Report Exporter Example")
    print("=" * 50)
    print()
    
    # Create sample data
    print("Creating sample diet plan...")
    diet_plan = create_sample_diet_plan()
    patient_profile = create_sample_patient_profile()
    
    # Initialize exporter
    exporter = ReportExporter()
    
    # Export to PDF
    print("\nExporting to PDF...")
    pdf_bytes = exporter.export_pdf(diet_plan, patient_info=patient_profile)
    
    # Save PDF to file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = output_dir / "diet_plan_report.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    print(f"✓ PDF exported successfully: {pdf_path}")
    print(f"  File size: {len(pdf_bytes) / 1024:.2f} KB")
    
    # Export to JSON
    print("\nExporting to JSON...")
    json_str = exporter.export_json(diet_plan)
    
    # Save JSON to file
    json_path = output_dir / "diet_plan_data.json"
    with open(json_path, "w") as f:
        f.write(json_str)
    
    print(f"✓ JSON exported successfully: {json_path}")
    print(f"  File size: {len(json_str) / 1024:.2f} KB")
    
    # Validate JSON schema
    print("\nValidating JSON schema...")
    is_valid = exporter.validate_json_schema(json_str)
    
    if is_valid:
        print("✓ JSON schema validation passed")
    else:
        print("✗ JSON schema validation failed")
    
    print("\n" + "=" * 50)
    print("Export complete!")
    print(f"\nOutput files saved to: {output_dir.absolute()}")
    print("\nYou can now:")
    print("  1. Open the PDF to view the formatted diet plan report")
    print("  2. Use the JSON data for integration with other systems")


if __name__ == "__main__":
    main()
