"""
Core data models for the AI NutriCare System.

This module contains all data classes and enums used throughout the system.
"""

from .enums import (
    MetricType,
    AlertSeverity,
    ConditionType,
    RulePriority,
    MealType,
)

from .health_data import (
    HealthMetric,
    StructuredHealthData,
    TextualNote,
    Alert,
    HealthCondition,
)

from .diet_data import (
    DietRule,
    DietaryRestriction,
    Food,
    Portion,
    Meal,
    MacronutrientRatios,
    DietPlan,
)

from .patient_data import (
    UserPreferences,
    PatientProfile,
)

__all__ = [
    # Enums
    "MetricType",
    "AlertSeverity",
    "ConditionType",
    "RulePriority",
    "MealType",
    # Health data
    "HealthMetric",
    "StructuredHealthData",
    "TextualNote",
    "Alert",
    "HealthCondition",
    # Diet data
    "DietRule",
    "DietaryRestriction",
    "Food",
    "Portion",
    "Meal",
    "MacronutrientRatios",
    "DietPlan",
    # Patient data
    "UserPreferences",
    "PatientProfile",
]
