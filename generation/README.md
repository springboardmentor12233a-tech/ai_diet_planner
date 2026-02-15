# Diet Plan Generation Module

This module provides personalized diet plan generation based on patient health conditions, dietary rules, and user preferences.

## Overview

The `DietPlanGenerator` class creates customized daily meal plans that:
- Calculate daily caloric needs using the Mifflin-St Jeor equation
- Adjust macronutrient ratios based on health conditions
- Respect dietary restrictions and allergies
- Support various dietary styles (vegetarian, vegan, etc.)
- Integrate with USDA FoodData Central API for comprehensive food database

## Features

### Caloric Needs Calculation

Uses the **Mifflin-St Jeor equation** to calculate Basal Metabolic Rate (BMR):

- **Men**: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
- **Women**: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161

Then multiplies by activity factor:
- Sedentary: 1.2
- Light: 1.375
- Moderate: 1.55
- Active: 1.725
- Very Active: 1.9

### Condition-Specific Macronutrient Targets

| Condition | Protein | Carbs | Fat | Notes |
|-----------|---------|-------|-----|-------|
| Healthy | 30% | 40% | 30% | Balanced diet |
| Diabetes | 30% | 40% | 30% | Focus on low glycemic index |
| Hypertension | 30% | 40% | 30% | Low sodium emphasis |
| Hyperlipidemia | 30% | 45% | 25% | Reduced saturated fat |
| Obesity | 35% | 35% | 30% | Higher protein for satiety |

### Meal Structure

Daily calories are distributed across four meals:
- **Breakfast**: 25% of daily calories
- **Lunch**: 35% of daily calories
- **Snack**: 10% of daily calories
- **Dinner**: 30% of daily calories

## Usage

### Basic Example

```python
from ai_diet_planner.generation import DietPlanGenerator
from ai_diet_planner.models import PatientProfile, UserPreferences

# Create patient profile
patient = PatientProfile(
    patient_id="patient-001",
    age=30,
    gender="female",
    height_cm=165,
    weight_kg=60,
    activity_level="moderate",
    preferences=UserPreferences(),
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

# Access plan details
print(f"Daily Calories: {plan.daily_calories}")
print(f"Number of Meals: {len(plan.meals)}")
```

### With Health Conditions

```python
from ai_diet_planner.models import HealthCondition, ConditionType, MetricType

health_conditions = [
    HealthCondition(
        condition_type=ConditionType.DIABETES_TYPE2,
        confidence=0.92,
        detected_at=datetime.now(),
        contributing_metrics=[MetricType.GLUCOSE, MetricType.HBA1C]
    )
]

plan = generator.generate_plan(
    patient_profile=patient,
    health_conditions=health_conditions,
    diet_rules=[],
    preferences=patient.preferences
)
```

### With Dietary Restrictions

```python
# Vegetarian with allergies
patient.preferences.dietary_style = "vegetarian"
patient.preferences.allergies = ["eggs", "milk"]

plan = generator.generate_plan(
    patient_profile=patient,
    health_conditions=[],
    diet_rules=[],
    preferences=patient.preferences
)
```

### With Medical Dietary Rules

```python
from ai_diet_planner.models import DietRule, RulePriority

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
    patient_profile=patient,
    health_conditions=[],
    diet_rules=diet_rules,
    preferences=patient.preferences
)
```

## API Reference

### DietPlanGenerator

#### `__init__(food_database_api_key: Optional[str] = None)`

Initialize the diet plan generator.

**Parameters:**
- `food_database_api_key`: Optional API key for USDA FoodData Central. If None, uses built-in food database.

#### `calculate_daily_calories(age, gender, weight_kg, height_cm, activity_level) -> float`

Calculate daily caloric needs using Mifflin-St Jeor equation.

**Parameters:**
- `age`: Age in years
- `gender`: "male" or "female"
- `weight_kg`: Weight in kilograms
- `height_cm`: Height in centimeters
- `activity_level`: "sedentary", "light", "moderate", "active", or "very_active"

**Returns:** Daily caloric needs in kcal

**Raises:** `ValueError` if invalid gender or activity level

#### `calculate_macronutrient_targets(health_conditions) -> MacronutrientRatios`

Calculate macronutrient target ratios based on health conditions.

**Parameters:**
- `health_conditions`: List of HealthCondition objects

**Returns:** MacronutrientRatios with target percentages

#### `generate_plan(patient_profile, health_conditions, diet_rules, preferences) -> DietPlan`

Generate a personalized daily diet plan.

**Parameters:**
- `patient_profile`: PatientProfile with demographics and preferences
- `health_conditions`: List of detected health conditions
- `diet_rules`: List of dietary rules from medical analysis
- `preferences`: UserPreferences including allergies and dietary style

**Returns:** Complete DietPlan with all meals and nutritional information

**Raises:** `ValueError` if unable to generate plan due to conflicting constraints

## Built-in Food Database

The module includes a built-in food database with common foods across categories:

- **Proteins**: Chicken breast, salmon, eggs, tofu
- **Carbohydrates**: Brown rice, quinoa, oatmeal, sweet potato
- **Vegetables**: Broccoli, spinach, carrots
- **Fruits**: Apple, banana, mixed berries
- **Dairy**: Greek yogurt, low-fat milk
- **Fats**: Avocado, olive oil, almonds

Each food item includes complete nutritional information:
- Calories
- Protein (g)
- Carbohydrates (g)
- Fat (g)
- Fiber (g)
- Sodium (mg)
- Sugar (g)

## Testing

Run the test suite:

```bash
pytest ai_diet_planner/generation/test_diet_planner.py -v
```

Run example usage:

```bash
python ai_diet_planner/generation/example_usage.py
```

## Requirements Validation

This implementation validates the following requirements:

- **Requirement 9.1**: Generates daily diet plan with breakfast, lunch, snack, and dinner
- **Requirement 9.3**: Balances macronutrients according to health conditions
- **Requirement 9.4**: Includes portion sizes and caloric information
- **Requirement 9.5**: Prioritizes medical restrictions over preferences
- **Requirement 10.1**: Incorporates dietary preferences (vegetarian, vegan, etc.)
- **Requirement 10.2**: Excludes allergenic foods from diet plan

## Future Enhancements

- Integration with live USDA FoodData Central API
- Support for multi-day meal plans with variety optimization
- Recipe suggestions and meal preparation instructions
- Grocery list generation
- Nutritional supplement recommendations
- Integration with fitness tracking for dynamic calorie adjustment
