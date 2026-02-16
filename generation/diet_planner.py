"""
Diet Plan Generator for the AI NutriCare System.

This module implements the DietPlanGenerator class that creates personalized
diet plans based on health conditions, dietary rules, and user preferences.
It integrates with USDA FoodData Central API for food database access.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests

from ..models import (
    HealthCondition,
    DietRule,
    UserPreferences,
    DietPlan,
    Meal,
    Portion,
    Food,
    MacronutrientRatios,
    DietaryRestriction,
    MealType,
    ConditionType,
    RulePriority,
    PatientProfile,
)


class ConflictResolution:
    """
    Represents a conflict between medical restrictions and user preferences.
    
    Attributes:
        conflict_type: Type of conflict (e.g., "allergy_vs_preference", "medical_vs_dietary_style")
        medical_requirement: The medical restriction that takes priority
        user_preference: The user preference that conflicts
        resolution: How the conflict was resolved
        alternatives: List of alternative recommendations
    """
    def __init__(
        self,
        conflict_type: str,
        medical_requirement: str,
        user_preference: str,
        resolution: str,
        alternatives: List[str]
    ):
        self.conflict_type = conflict_type
        self.medical_requirement = medical_requirement
        self.user_preference = user_preference
        self.resolution = resolution
        self.alternatives = alternatives


class DietPlanGenerator:
    """
    Generates personalized diet plans combining ML insights, NLP rules, and user preferences.
    
    This class implements:
    - Daily caloric needs calculation using Mifflin-St Jeor equation
    - Macronutrient target calculation based on health conditions
    - Integration with USDA FoodData Central API
    - Constraint satisfaction for dietary restrictions
    - Meal generation with portion sizing
    """
    
    def __init__(self, food_database_api_key: Optional[str] = None):
        """
        Initialize the diet plan generator.
        
        Args:
            food_database_api_key: Optional API key for USDA FoodData Central.
                                   If None, uses a built-in food database.
        """
        self.api_key = food_database_api_key
        self.usda_api_base = "https://api.nal.usda.gov/fdc/v1"
        
        # Built-in food database for when API is not available
        self._init_builtin_food_database()
        
        # Track conflicts for user notification
        self.conflicts: List[ConflictResolution] = []
    
    def _init_builtin_food_database(self):
        """Initialize a built-in food database with common foods."""
        self.builtin_foods = {
            # Proteins
            "chicken_breast": Food(
                name="Chicken Breast (grilled)",
                calories=165,
                protein_g=31,
                carbs_g=0,
                fat_g=3.6,
                fiber_g=0,
                sodium_mg=74,
                sugar_g=0,
                category="proteins",
                fdc_id="171477"
            ),
            "salmon": Food(
                name="Salmon (baked)",
                calories=206,
                protein_g=22,
                carbs_g=0,
                fat_g=12,
                fiber_g=0,
                sodium_mg=59,
                sugar_g=0,
                category="proteins",
                fdc_id="175167"
            ),
            "eggs": Food(
                name="Eggs (boiled)",
                calories=155,
                protein_g=13,
                carbs_g=1.1,
                fat_g=11,
                fiber_g=0,
                sodium_mg=124,
                sugar_g=1.1,
                category="proteins",
                fdc_id="173424"
            ),
            "tofu": Food(
                name="Tofu (firm)",
                calories=144,
                protein_g=17,
                carbs_g=3,
                fat_g=9,
                fiber_g=2,
                sodium_mg=14,
                sugar_g=0,
                category="proteins",
                fdc_id="174276"
            ),
            # Carbohydrates
            "brown_rice": Food(
                name="Brown Rice (cooked)",
                calories=112,
                protein_g=2.6,
                carbs_g=24,
                fat_g=0.9,
                fiber_g=1.8,
                sodium_mg=5,
                sugar_g=0.4,
                category="carbs",
                fdc_id="168878"
            ),
            "quinoa": Food(
                name="Quinoa (cooked)",
                calories=120,
                protein_g=4.4,
                carbs_g=21,
                fat_g=1.9,
                fiber_g=2.8,
                sodium_mg=7,
                sugar_g=0.9,
                category="carbs",
                fdc_id="168917"
            ),
            "oatmeal": Food(
                name="Oatmeal (cooked)",
                calories=71,
                protein_g=2.5,
                carbs_g=12,
                fat_g=1.5,
                fiber_g=1.7,
                sodium_mg=49,
                sugar_g=0.4,
                category="carbs",
                fdc_id="173904"
            ),
            "sweet_potato": Food(
                name="Sweet Potato (baked)",
                calories=90,
                protein_g=2,
                carbs_g=21,
                fat_g=0.2,
                fiber_g=3.3,
                sodium_mg=36,
                sugar_g=6.5,
                category="carbs",
                fdc_id="168482"
            ),
            # Vegetables
            "broccoli": Food(
                name="Broccoli (steamed)",
                calories=35,
                protein_g=2.4,
                carbs_g=7,
                fat_g=0.4,
                fiber_g=3.3,
                sodium_mg=41,
                sugar_g=1.4,
                category="vegetables",
                fdc_id="170379"
            ),
            "spinach": Food(
                name="Spinach (cooked)",
                calories=23,
                protein_g=2.9,
                carbs_g=3.8,
                fat_g=0.3,
                fiber_g=2.4,
                sodium_mg=70,
                sugar_g=0.4,
                category="vegetables",
                fdc_id="168462"
            ),
            "carrots": Food(
                name="Carrots (raw)",
                calories=41,
                protein_g=0.9,
                carbs_g=10,
                fat_g=0.2,
                fiber_g=2.8,
                sodium_mg=69,
                sugar_g=4.7,
                category="vegetables",
                fdc_id="170393"
            ),
            # Fruits
            "apple": Food(
                name="Apple (medium)",
                calories=95,
                protein_g=0.5,
                carbs_g=25,
                fat_g=0.3,
                fiber_g=4.4,
                sodium_mg=2,
                sugar_g=19,
                category="fruits",
                fdc_id="171688"
            ),
            "banana": Food(
                name="Banana (medium)",
                calories=105,
                protein_g=1.3,
                carbs_g=27,
                fat_g=0.4,
                fiber_g=3.1,
                sodium_mg=1,
                sugar_g=14,
                category="fruits",
                fdc_id="173944"
            ),
            "berries": Food(
                name="Mixed Berries",
                calories=57,
                protein_g=1.1,
                carbs_g=14,
                fat_g=0.5,
                fiber_g=3.6,
                sodium_mg=1,
                sugar_g=8,
                category="fruits",
                fdc_id="171711"
            ),
            # Dairy
            "greek_yogurt": Food(
                name="Greek Yogurt (plain, low-fat)",
                calories=100,
                protein_g=17,
                carbs_g=6,
                fat_g=1.5,
                fiber_g=0,
                sodium_mg=56,
                sugar_g=6,
                category="dairy",
                fdc_id="170903"
            ),
            "milk": Food(
                name="Milk (low-fat)",
                calories=102,
                protein_g=8,
                carbs_g=12,
                fat_g=2.4,
                fiber_g=0,
                sodium_mg=107,
                sugar_g=13,
                category="dairy",
                fdc_id="746776"
            ),
            # Fats
            "avocado": Food(
                name="Avocado (half)",
                calories=120,
                protein_g=1.5,
                carbs_g=6,
                fat_g=11,
                fiber_g=5,
                sodium_mg=5,
                sugar_g=0.5,
                category="fats",
                fdc_id="171705"
            ),
            "olive_oil": Food(
                name="Olive Oil (1 tbsp)",
                calories=119,
                protein_g=0,
                carbs_g=0,
                fat_g=13.5,
                fiber_g=0,
                sodium_mg=0,
                sugar_g=0,
                category="fats",
                fdc_id="171413"
            ),
            "almonds": Food(
                name="Almonds (1 oz)",
                calories=164,
                protein_g=6,
                carbs_g=6,
                fat_g=14,
                fiber_g=3.5,
                sodium_mg=0,
                sugar_g=1.2,
                category="fats",
                fdc_id="170567"
            ),
        }
    
    def calculate_daily_calories(
        self,
        age: int,
        gender: str,
        weight_kg: float,
        height_cm: float,
        activity_level: str
    ) -> float:
        """
        Calculate daily caloric needs using the Mifflin-St Jeor equation.
        
        The Mifflin-St Jeor equation:
        - Men: BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age(years) + 5
        - Women: BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age(years) - 161
        
        Then multiply by activity factor:
        - sedentary: 1.2
        - light: 1.375
        - moderate: 1.55
        - active: 1.725
        - very_active: 1.9
        
        Args:
            age: Age in years
            gender: Gender ("male" or "female")
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            activity_level: Activity level (sedentary, light, moderate, active, very_active)
        
        Returns:
            Daily caloric needs in kcal
        
        Raises:
            ValueError: If invalid gender or activity level provided
        """
        # Calculate Basal Metabolic Rate (BMR)
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
        
        if gender.lower() in ["male", "m"]:
            bmr += 5
        elif gender.lower() in ["female", "f"]:
            bmr -= 161
        else:
            raise ValueError(f"Invalid gender: {gender}. Must be 'male' or 'female'")
        
        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        
        activity_level_lower = activity_level.lower()
        if activity_level_lower not in activity_multipliers:
            raise ValueError(
                f"Invalid activity level: {activity_level}. "
                f"Must be one of: {', '.join(activity_multipliers.keys())}"
            )
        
        # Calculate Total Daily Energy Expenditure (TDEE)
        tdee = bmr * activity_multipliers[activity_level_lower]
        
        return round(tdee, 2)
    
    def calculate_macronutrient_targets(
        self,
        health_conditions: List[HealthCondition]
    ) -> MacronutrientRatios:
        """
        Calculate macronutrient target ratios based on health conditions.
        
        Default ratios (healthy individual):
        - Protein: 30%
        - Carbs: 40%
        - Fat: 30%
        
        Condition-specific adjustments:
        - Diabetes: Lower carbs (40% carbs, 30% protein, 30% fat) with focus on low GI
        - Hypertension: Standard ratios with low sodium focus
        - Hyperlipidemia: Lower fat (25% fat, 30% protein, 45% carbs)
        - Obesity: Higher protein for satiety (35% protein, 35% carbs, 30% fat)
        
        Args:
            health_conditions: List of detected health conditions
        
        Returns:
            MacronutrientRatios with target percentages
        """
        # Default ratios
        protein_percent = 30.0
        carbs_percent = 40.0
        fat_percent = 30.0
        
        # Check for specific conditions and adjust
        condition_types = [c.condition_type for c in health_conditions]
        
        # Diabetes: Lower carbs, focus on low glycemic index
        if any(ct in [ConditionType.DIABETES_TYPE1, ConditionType.DIABETES_TYPE2, 
                      ConditionType.PREDIABETES] for ct in condition_types):
            protein_percent = 30.0
            carbs_percent = 40.0
            fat_percent = 30.0
        
        # Hyperlipidemia: Lower fat
        if ConditionType.HYPERLIPIDEMIA in condition_types:
            protein_percent = 30.0
            carbs_percent = 45.0
            fat_percent = 25.0
        
        # Obesity: Higher protein for satiety
        if any(ct in [ConditionType.OBESITY_CLASS1, ConditionType.OBESITY_CLASS2,
                      ConditionType.OBESITY_CLASS3] for ct in condition_types):
            protein_percent = 35.0
            carbs_percent = 35.0
            fat_percent = 30.0
        
        # If multiple conditions, prioritize obesity adjustments
        if (any(ct in [ConditionType.OBESITY_CLASS1, ConditionType.OBESITY_CLASS2,
                       ConditionType.OBESITY_CLASS3] for ct in condition_types) and
            ConditionType.HYPERLIPIDEMIA in condition_types):
            protein_percent = 35.0
            carbs_percent = 40.0
            fat_percent = 25.0
        
        return MacronutrientRatios(
            protein_percent=protein_percent,
            carbs_percent=carbs_percent,
            fat_percent=fat_percent
        )
    
    def _detect_and_resolve_conflicts(
        self,
        diet_rules: List[DietRule],
        preferences: UserPreferences,
        health_conditions: List[HealthCondition]
    ) -> Tuple[List[DietRule], List[ConflictResolution]]:
        """
        Detect conflicts between medical restrictions and user preferences.
        Prioritize medical restrictions and generate alternative recommendations.
        
        Args:
            diet_rules: List of dietary rules from medical analysis
            preferences: User dietary preferences and allergies
            health_conditions: List of detected health conditions
        
        Returns:
            Tuple of (resolved_diet_rules, conflicts_detected)
        """
        conflicts = []
        resolved_rules = diet_rules.copy()
        
        # Extract medical restrictions (REQUIRED priority)
        medical_restrictions = [
            rule for rule in diet_rules
            if rule.priority == RulePriority.REQUIRED
        ]
        
        # Check for conflicts with dietary style
        if preferences.dietary_style:
            dietary_style = preferences.dietary_style.lower()
            
            # Check if medical restrictions conflict with dietary style
            for rule in medical_restrictions:
                if rule.action == "include":
                    # Medical requirement to include certain foods
                    rule_text_lower = rule.rule_text.lower()
                    
                    # Vegetarian conflicts - check for meat/fish requirements
                    if dietary_style == "vegetarian":
                        meat_keywords = ["meat", "chicken", "fish", "beef", "pork", "salmon", "turkey", "lamb"]
                        if any(meat in rule_text_lower for meat in meat_keywords):
                            alternatives = self._generate_protein_alternatives(
                                exclude_animal=True,
                                exclude_dairy=False
                            )
                            conflicts.append(ConflictResolution(
                                conflict_type="medical_vs_dietary_style",
                                medical_requirement=rule.rule_text,
                                user_preference=f"Vegetarian diet preference",
                                resolution="Medical requirement prioritized. Vegetarian protein sources recommended.",
                                alternatives=alternatives
                            ))
                    
                    # Vegan conflicts - check for any animal product requirements
                    elif dietary_style == "vegan":
                        animal_keywords = ["meat", "chicken", "fish", "dairy", "egg", "milk", "yogurt", "cheese", "beef", "pork", "salmon"]
                        if any(animal in rule_text_lower for animal in animal_keywords):
                            alternatives = self._generate_protein_alternatives(
                                exclude_animal=True,
                                exclude_dairy=True
                            )
                            conflicts.append(ConflictResolution(
                                conflict_type="medical_vs_dietary_style",
                                medical_requirement=rule.rule_text,
                                user_preference=f"Vegan diet preference",
                                resolution="Medical requirement prioritized. Plant-based alternatives recommended.",
                                alternatives=alternatives
                            ))
        
        # Check for impossible constraint scenarios
        # Count how many food categories are restricted
        restricted_categories = set()
        for rule in medical_restrictions:
            if rule.action == "exclude":
                restricted_categories.update(rule.food_categories)
        
        # Add allergy-based restrictions
        for allergy in preferences.allergies:
            allergy_lower = allergy.lower()
            # Map common allergies to categories
            if allergy_lower in ["milk", "cheese", "yogurt", "dairy"]:
                restricted_categories.add("dairy")
            elif allergy_lower in ["eggs", "egg"]:
                restricted_categories.add("proteins")
            elif allergy_lower in ["nuts", "almonds", "peanuts"]:
                restricted_categories.add("fats")
        
        # Add dietary style restrictions
        if preferences.dietary_style:
            if preferences.dietary_style.lower() == "vegan":
                restricted_categories.add("dairy")
        
        # Check if too many categories are restricted
        total_categories = len(["proteins", "carbs", "dairy", "fats", "vegetables", "fruits"])
        if len(restricted_categories) >= total_categories - 1:
            # Almost all categories restricted - impossible scenario
            alternatives = self._generate_flexible_alternatives(
                restricted_categories,
                health_conditions
            )
            conflicts.append(ConflictResolution(
                conflict_type="impossible_constraints",
                medical_requirement=f"Multiple medical restrictions: {', '.join(restricted_categories)}",
                user_preference=f"Dietary preferences: {preferences.dietary_style or 'None'}, Allergies: {', '.join(preferences.allergies) if preferences.allergies else 'None'}",
                resolution="Constraints are too restrictive. Consider consulting with a dietitian for personalized guidance.",
                alternatives=alternatives
            ))
        
        return resolved_rules, conflicts
    
    def _generate_protein_alternatives(
        self,
        exclude_animal: bool,
        exclude_dairy: bool
    ) -> List[str]:
        """
        Generate alternative protein source recommendations.
        
        Args:
            exclude_animal: Whether to exclude animal-based proteins
            exclude_dairy: Whether to exclude dairy-based proteins
        
        Returns:
            List of alternative protein recommendations
        """
        alternatives = []
        
        if exclude_animal and exclude_dairy:
            # Vegan protein sources
            alternatives = [
                "Tofu and tempeh (complete plant proteins)",
                "Legumes: lentils, chickpeas, black beans (high in protein and fiber)",
                "Quinoa (complete protein grain)",
                "Nuts and seeds: almonds, chia seeds, hemp seeds",
                "Nutritional yeast (B12 fortified)",
                "Plant-based protein powders (pea, rice, hemp)"
            ]
        elif exclude_animal and not exclude_dairy:
            # Vegetarian protein sources
            alternatives = [
                "Greek yogurt and cottage cheese (high protein dairy)",
                "Eggs (complete protein source)",
                "Tofu and tempeh",
                "Legumes: lentils, chickpeas, black beans",
                "Quinoa and other whole grains",
                "Nuts, seeds, and nut butters"
            ]
        else:
            # General alternatives
            alternatives = [
                "Lean poultry: chicken breast, turkey",
                "Fish: salmon, tuna, cod (omega-3 rich)",
                "Eggs (versatile and affordable)",
                "Greek yogurt and cottage cheese",
                "Legumes and beans",
                "Tofu and plant-based proteins"
            ]
        
        return alternatives
    
    def _generate_flexible_alternatives(
        self,
        restricted_categories: set,
        health_conditions: List[HealthCondition]
    ) -> List[str]:
        """
        Generate flexible alternative recommendations when constraints are too restrictive.
        
        Args:
            restricted_categories: Set of restricted food categories
            health_conditions: List of health conditions
        
        Returns:
            List of alternative recommendations
        """
        alternatives = [
            "Consult with a registered dietitian for personalized meal planning",
            "Consider working with your healthcare provider to review dietary restrictions",
            "Explore specialty foods and supplements to meet nutritional needs",
        ]
        
        # Add condition-specific alternatives
        condition_types = [c.condition_type for c in health_conditions]
        
        if any(ct in [ConditionType.DIABETES_TYPE1, ConditionType.DIABETES_TYPE2]
               for ct in condition_types):
            alternatives.append(
                "For diabetes management: Focus on portion control and meal timing even with limited food options"
            )
        
        if any(ct in [ConditionType.OBESITY_CLASS1, ConditionType.OBESITY_CLASS2, ConditionType.OBESITY_CLASS3]
               for ct in condition_types):
            alternatives.append(
                "For weight management: Prioritize calorie control within available food options"
            )
        
        alternatives.append(
            "Consider meal replacement shakes or nutritional supplements if whole food options are severely limited"
        )
        
        return alternatives

    
    def _filter_foods_by_restrictions(
        self,
        foods: Dict[str, Food],
        restrictions: List[DietaryRestriction],
        preferences: UserPreferences
    ) -> Dict[str, Food]:
        """
        Filter food database by dietary restrictions and allergies.
        
        Args:
            foods: Dictionary of available foods
            restrictions: List of dietary restrictions
            preferences: User preferences including allergies
        
        Returns:
            Filtered dictionary of allowed foods
        """
        allowed_foods = {}
        
        # Collect all restricted items and categories
        restricted_items = set()
        restricted_categories = set()
        
        for restriction in restrictions:
            for item in restriction.restricted_items:
                item_lower = item.lower()
                restricted_items.add(item_lower)
                # Also treat as category if it matches common categories
                if item_lower in ["proteins", "carbs", "dairy", "fats", "vegetables", "fruits"]:
                    restricted_categories.add(item_lower)
        
        # Add allergies from preferences
        restricted_items.update(allergy.lower() for allergy in preferences.allergies)
        
        # Filter foods
        for food_key, food in foods.items():
            food_name_lower = food.name.lower()
            food_category_lower = food.category.lower()
            
            # Check if food category is restricted
            if food_category_lower in restricted_categories:
                continue
            
            # Check if food contains any restricted items
            is_restricted = any(
                restricted_item in food_name_lower
                for restricted_item in restricted_items
            )
            
            if not is_restricted:
                # Check dietary style preferences
                if preferences.dietary_style:
                    style = preferences.dietary_style.lower()
                    
                    # Vegetarian: exclude meat and fish
                    if style == "vegetarian":
                        if food.category == "proteins" and any(
                            meat in food_name_lower
                            for meat in ["chicken", "beef", "pork", "fish", "salmon", "turkey"]
                        ):
                            continue
                    
                    # Vegan: exclude all animal products
                    elif style == "vegan":
                        if food.category in ["proteins", "dairy"] and any(
                            animal in food_name_lower
                            for animal in ["chicken", "beef", "pork", "fish", "salmon", 
                                         "turkey", "egg", "milk", "yogurt", "cheese"]
                        ):
                            continue
                
                allowed_foods[food_key] = food
        
        return allowed_foods
    
    def _select_foods_for_meal(
        self,
        meal_type: MealType,
        target_calories: float,
        macro_targets: MacronutrientRatios,
        available_foods: Dict[str, Food],
        health_conditions: List[HealthCondition]
    ) -> List[Portion]:
        """
        Select foods for a specific meal to meet caloric and macronutrient targets.
        
        Args:
            meal_type: Type of meal (breakfast, lunch, snack, dinner)
            target_calories: Target calories for this meal
            macro_targets: Target macronutrient ratios
            available_foods: Dictionary of allowed foods
            health_conditions: List of health conditions for special considerations
        
        Returns:
            List of food portions for the meal
        """
        portions = []
        
        # Calculate target macros in grams
        target_protein_g = (target_calories * macro_targets.protein_percent / 100) / 4  # 4 cal/g
        target_carbs_g = (target_calories * macro_targets.carbs_percent / 100) / 4  # 4 cal/g
        target_fat_g = (target_calories * macro_targets.fat_percent / 100) / 9  # 9 cal/g
        
        # Meal-specific food selection
        if meal_type == MealType.BREAKFAST:
            # Breakfast: carbs, protein, some fat
            food_keys = ["oatmeal", "eggs", "greek_yogurt", "berries", "banana", "almonds"]
        elif meal_type == MealType.LUNCH:
            # Lunch: balanced meal with protein, carbs, vegetables
            food_keys = ["chicken_breast", "salmon", "tofu", "brown_rice", "quinoa", 
                        "broccoli", "spinach", "avocado"]
        elif meal_type == MealType.SNACK:
            # Snack: light, nutritious
            food_keys = ["apple", "almonds", "greek_yogurt", "carrots"]
        else:  # DINNER
            # Dinner: protein, vegetables, moderate carbs
            food_keys = ["salmon", "chicken_breast", "tofu", "sweet_potato", 
                        "broccoli", "spinach", "olive_oil"]
        
        # Filter to available foods
        meal_foods = {k: available_foods[k] for k in food_keys if k in available_foods}
        
        if not meal_foods:
            # Fallback: use any available foods
            meal_foods = available_foods
        
        # Simple portion calculation: distribute calories across selected foods
        remaining_calories = target_calories
        
        # Select 2-4 foods per meal (except snack which gets 1-2)
        num_foods = 2 if meal_type == MealType.SNACK else 3
        selected_foods = list(meal_foods.values())[:num_foods]
        
        for i, food in enumerate(selected_foods):
            # Allocate calories proportionally
            if i == len(selected_foods) - 1:
                # Last food gets remaining calories
                food_calories = remaining_calories
            else:
                # Distribute evenly
                food_calories = target_calories / len(selected_foods)
            
            # Calculate portion size to meet calorie target
            if food.calories > 0:
                portion_multiplier = food_calories / food.calories
            else:
                portion_multiplier = 1.0
            
            # Create portion
            portion = Portion(
                food=food,
                amount=round(100 * portion_multiplier, 1),  # Base serving is 100g
                unit="g",
                calories=round(food.calories * portion_multiplier, 1),
                protein_g=round(food.protein_g * portion_multiplier, 1),
                carbs_g=round(food.carbs_g * portion_multiplier, 1),
                fat_g=round(food.fat_g * portion_multiplier, 1)
            )
            
            portions.append(portion)
            remaining_calories -= portion.calories
        
        return portions
    
    def generate_plan(
        self,
        patient_profile: PatientProfile,
        health_conditions: List[HealthCondition],
        diet_rules: List[DietRule],
        preferences: UserPreferences
    ) -> DietPlan:
        """
        Generate a personalized daily diet plan.
        
        This is the main entry point for diet plan generation. It:
        1. Calculates daily caloric needs
        2. Determines macronutrient targets based on health conditions
        3. Detects and resolves conflicts between medical restrictions and preferences
        4. Filters foods by restrictions and allergies
        5. Generates meals for breakfast, lunch, snack, and dinner
        6. Ensures compliance with all dietary rules
        
        Args:
            patient_profile: Patient demographic and preference information
            health_conditions: Detected health conditions from ML analysis
            diet_rules: Dietary rules extracted from medical notes
            preferences: User dietary preferences and allergies
        
        Returns:
            Complete DietPlan with all meals and nutritional information
        
        Raises:
            ValueError: If unable to generate plan due to conflicting constraints
        """
        # Reset conflicts for this plan generation
        self.conflicts = []
        
        # Detect and resolve conflicts between medical restrictions and preferences
        resolved_rules, conflicts = self._detect_and_resolve_conflicts(
            diet_rules,
            preferences,
            health_conditions
        )
        self.conflicts = conflicts
        
        # Calculate daily caloric needs
        daily_calories = self.calculate_daily_calories(
            age=patient_profile.age,
            gender=patient_profile.gender,
            weight_kg=patient_profile.weight_kg,
            height_cm=patient_profile.height_cm,
            activity_level=patient_profile.activity_level
        )
        
        # Adjust for weight loss if obesity is present
        condition_types = [c.condition_type for c in health_conditions]
        if any(ct in [ConditionType.OBESITY_CLASS1, ConditionType.OBESITY_CLASS2,
                      ConditionType.OBESITY_CLASS3] for ct in condition_types):
            # Create 500-750 calorie deficit for weight loss
            daily_calories -= 600
        
        # Calculate macronutrient targets
        macro_targets = self.calculate_macronutrient_targets(health_conditions)
        
        # Convert diet rules to restrictions (prioritize REQUIRED rules)
        restrictions = []
        for rule in resolved_rules:
            if rule.priority == RulePriority.REQUIRED and rule.action == "exclude":
                restrictions.append(
                    DietaryRestriction(
                        restriction_type="medical",
                        restricted_items=rule.food_categories,
                        severity="strict"
                    )
                )
        
        # Filter foods by restrictions
        available_foods = self._filter_foods_by_restrictions(
            self.builtin_foods,
            restrictions,
            preferences
        )
        
        if not available_foods:
            # Generate alternatives for impossible constraint scenario
            alternatives = self._generate_flexible_alternatives(
                set(r.restricted_items[0] for r in restrictions if r.restricted_items),
                health_conditions
            )
            
            # Add conflict notification
            self.conflicts.append(ConflictResolution(
                conflict_type="impossible_constraints",
                medical_requirement="All food categories restricted by medical requirements",
                user_preference=f"Dietary style: {preferences.dietary_style}, Allergies: {preferences.allergies}",
                resolution="Unable to generate diet plan with current constraints",
                alternatives=alternatives
            ))
            
            raise ValueError(
                "Unable to generate diet plan: no foods available after applying restrictions. "
                f"Conflicts detected: {len(self.conflicts)}. "
                "Please review dietary restrictions and allergies, or consult with a dietitian. "
                f"Alternatives: {'; '.join(alternatives[:3])}"
            )
        
        # Meal calorie distribution
        meal_calories = {
            MealType.BREAKFAST: daily_calories * 0.25,
            MealType.LUNCH: daily_calories * 0.35,
            MealType.SNACK: daily_calories * 0.10,
            MealType.DINNER: daily_calories * 0.30,
        }
        
        # Generate meals
        meals = []
        for meal_type, target_calories in meal_calories.items():
            portions = self._select_foods_for_meal(
                meal_type=meal_type,
                target_calories=target_calories,
                macro_targets=macro_targets,
                available_foods=available_foods,
                health_conditions=health_conditions
            )
            
            # Calculate meal totals
            total_calories = sum(p.calories for p in portions)
            total_protein = sum(p.protein_g for p in portions)
            total_carbs = sum(p.carbs_g for p in portions)
            total_fat = sum(p.fat_g for p in portions)
            
            meal = Meal(
                meal_type=meal_type,
                portions=portions,
                total_calories=round(total_calories, 1),
                total_protein_g=round(total_protein, 1),
                total_carbs_g=round(total_carbs, 1),
                total_fat_g=round(total_fat, 1)
            )
            
            meals.append(meal)
        
        # Generate recommendations (including conflict resolutions)
        recommendations = self._generate_recommendations(health_conditions, resolved_rules)
        
        # Add conflict notifications to recommendations
        if self.conflicts:
            recommendations.insert(0, f"⚠️ NOTICE: {len(self.conflicts)} dietary conflict(s) detected and resolved:")
            for i, conflict in enumerate(self.conflicts, 1):
                recommendations.insert(i, f"  {i}. {conflict.resolution}")
                if conflict.alternatives:
                    recommendations.insert(i + 1, f"     Alternatives: {'; '.join(conflict.alternatives[:2])}")
        
        # Create diet plan
        diet_plan = DietPlan(
            plan_id=str(uuid.uuid4()),
            patient_id=patient_profile.patient_id,
            generated_at=datetime.now(),
            daily_calories=round(daily_calories, 1),
            macronutrient_targets=macro_targets,
            meals=meals,
            restrictions=restrictions,
            recommendations=recommendations,
            health_conditions=health_conditions
        )
        
        return diet_plan
    
    def _generate_recommendations(
        self,
        health_conditions: List[HealthCondition],
        diet_rules: List[DietRule]
    ) -> List[str]:
        """
        Generate dietary recommendations based on health conditions and rules.
        
        Args:
            health_conditions: List of detected health conditions
            diet_rules: List of dietary rules
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Condition-specific recommendations
        condition_types = [c.condition_type for c in health_conditions]
        
        if any(ct in [ConditionType.DIABETES_TYPE1, ConditionType.DIABETES_TYPE2,
                      ConditionType.PREDIABETES] for ct in condition_types):
            recommendations.append(
                "Focus on low glycemic index foods to manage blood sugar levels"
            )
            recommendations.append(
                "Monitor carbohydrate intake and spread throughout the day"
            )
        
        if any(ct in [ConditionType.HYPERTENSION_STAGE1, ConditionType.HYPERTENSION_STAGE2]
               for ct in condition_types):
            recommendations.append(
                "Limit sodium intake to less than 2300mg per day"
            )
            recommendations.append(
                "Increase potassium-rich foods like bananas, spinach, and sweet potatoes"
            )
        
        if ConditionType.HYPERLIPIDEMIA in condition_types:
            recommendations.append(
                "Choose lean proteins and limit saturated fats"
            )
            recommendations.append(
                "Increase fiber intake with whole grains, fruits, and vegetables"
            )
        
        if any(ct in [ConditionType.OBESITY_CLASS1, ConditionType.OBESITY_CLASS2,
                      ConditionType.OBESITY_CLASS3] for ct in condition_types):
            recommendations.append(
                "Maintain a caloric deficit for gradual weight loss (1-2 lbs per week)"
            )
            recommendations.append(
                "Increase physical activity to support weight management"
            )
        
        if ConditionType.ANEMIA in condition_types:
            recommendations.append(
                "Include iron-rich foods like spinach, lean meats, and legumes"
            )
            recommendations.append(
                "Pair iron sources with vitamin C for better absorption"
            )
        
        # Add recommendations from diet rules
        for rule in diet_rules:
            if rule.priority == RulePriority.RECOMMENDED:
                recommendations.append(rule.rule_text)
        
        # General recommendations
        recommendations.append("Stay hydrated with at least 8 glasses of water daily")
        recommendations.append("Eat meals at regular times to maintain stable energy levels")
        
        return recommendations


    def generate_weekly_plan(
        self,
        patient_profile: PatientProfile,
        health_conditions: List[HealthCondition],
        diet_rules: List[DietRule],
        preferences: UserPreferences
    ) -> List[DietPlan]:
        """
        Generate a 7-day weekly diet plan with varied meals.

        Creates 7 different daily diet plans with meal variety to prevent
        monotony while maintaining nutritional targets and dietary restrictions.

        Args:
            patient_profile: Patient demographic and preference information
            health_conditions: Detected health conditions from ML analysis
            diet_rules: Dietary rules extracted from medical notes
            preferences: User dietary preferences and allergies

        Returns:
            List of 7 DietPlan objects, one for each day of the week

        Raises:
            ValueError: If unable to generate plans due to conflicting constraints
        """
        weekly_plans = []
        used_foods = set()  # Track foods used to ensure variety

        for day in range(7):
            # Generate daily plan
            daily_plan = self.generate_plan(
                patient_profile=patient_profile,
                health_conditions=health_conditions,
                diet_rules=diet_rules,
                preferences=preferences
            )
            
            # Track which foods were used
            for meal in daily_plan.meals:
                for portion in meal.portions:
                    used_foods.add(portion.food.name)
            
            # Add day identifier to plan
            daily_plan.plan_id = f"{daily_plan.plan_id}_day{day + 1}"
            
            weekly_plans.append(daily_plan)
        
        return weekly_plans

