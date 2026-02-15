"""
Diet and nutrition data models for the AI NutriCare System.

This module contains data classes for diet rules, food items, meals,
and complete diet plans.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .enums import RulePriority, MealType
from .health_data import HealthCondition


@dataclass
class DietRule:
    """
    A dietary rule extracted from medical analysis or user preferences.
    
    Attributes:
        rule_text: Human-readable description of the rule
        priority: Priority level of the rule
        food_categories: List of food categories this rule applies to
        action: The action to take (include, exclude, limit)
        source: Where the rule came from (ml_analysis, nlp_extraction, user_preference)
    """
    
    rule_text: str
    priority: RulePriority
    food_categories: List[str]
    action: str
    source: str


@dataclass
class DietaryRestriction:
    """
    A dietary restriction that must be enforced in diet plans.
    
    Attributes:
        restriction_type: Type of restriction (allergy, intolerance, medical, religious)
        restricted_items: List of food items or ingredients to restrict
        severity: How strictly to enforce (strict, moderate)
    """
    
    restriction_type: str
    restricted_items: List[str]
    severity: str


@dataclass
class Food:
    """
    A food item with nutritional information.
    
    Attributes:
        name: Name of the food item
        fdc_id: Optional USDA FoodData Central ID
        calories: Calories per standard serving
        protein_g: Protein in grams
        carbs_g: Carbohydrates in grams
        fat_g: Fat in grams
        fiber_g: Fiber in grams
        sodium_mg: Sodium in milligrams
        sugar_g: Sugar in grams
        category: Food category (proteins, carbs, dairy, etc.)
    """
    
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float
    sugar_g: float
    category: str
    fdc_id: Optional[str] = None


@dataclass
class Portion:
    """
    A specific portion of a food item.
    
    Attributes:
        food: The food item
        amount: Quantity of the portion
        unit: Unit of measurement (g, ml, cup, piece)
        calories: Total calories in this portion
        protein_g: Total protein in grams
        carbs_g: Total carbohydrates in grams
        fat_g: Total fat in grams
    """
    
    food: Food
    amount: float
    unit: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


@dataclass
class Meal:
    """
    A meal consisting of multiple food portions.
    
    Attributes:
        meal_type: Type of meal (breakfast, lunch, snack, dinner)
        portions: List of food portions in the meal
        total_calories: Total calories in the meal
        total_protein_g: Total protein in grams
        total_carbs_g: Total carbohydrates in grams
        total_fat_g: Total fat in grams
    """
    
    meal_type: MealType
    portions: List[Portion]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


@dataclass
class MacronutrientRatios:
    """
    Target macronutrient ratios for a diet plan.
    
    Attributes:
        protein_percent: Target percentage of calories from protein
        carbs_percent: Target percentage of calories from carbohydrates
        fat_percent: Target percentage of calories from fat
    """
    
    protein_percent: float
    carbs_percent: float
    fat_percent: float


@dataclass
class DietPlan:
    """
    A complete personalized diet plan.
    
    Attributes:
        plan_id: Unique identifier for the diet plan
        patient_id: ID of the patient this plan is for
        generated_at: Timestamp when the plan was generated
        daily_calories: Target daily caloric intake
        macronutrient_targets: Target macronutrient ratios
        meals: List of meals in the daily plan
        restrictions: List of dietary restrictions applied
        recommendations: List of dietary recommendations
        health_conditions: List of health conditions considered
    """
    
    plan_id: str
    patient_id: str
    generated_at: datetime
    daily_calories: float
    macronutrient_targets: MacronutrientRatios
    meals: List[Meal]
    restrictions: List[DietaryRestriction]
    recommendations: List[str]
    health_conditions: List[HealthCondition]
