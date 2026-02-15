"""
Enumerations for the AI NutriCare System.

This module defines all enum types used throughout the system for type safety
and standardization of categorical values.
"""

from enum import Enum


class MetricType(Enum):
    """Types of health metrics that can be extracted from medical reports."""
    
    GLUCOSE = "glucose"
    CHOLESTEROL_TOTAL = "cholesterol_total"
    CHOLESTEROL_LDL = "cholesterol_ldl"
    CHOLESTEROL_HDL = "cholesterol_hdl"
    TRIGLYCERIDES = "triglycerides"
    BMI = "bmi"
    BLOOD_PRESSURE_SYSTOLIC = "bp_systolic"
    BLOOD_PRESSURE_DIASTOLIC = "bp_diastolic"
    HEMOGLOBIN = "hemoglobin"
    HBA1C = "hba1c"


class AlertSeverity(Enum):
    """Severity levels for health metric alerts."""
    
    CRITICAL = "critical"  # Red flag requiring immediate attention
    WARNING = "warning"    # Yellow flag suggesting monitoring
    NORMAL = "normal"      # Green flag indicating healthy range


class ConditionType(Enum):
    """Types of health conditions that can be detected."""
    
    DIABETES_TYPE1 = "diabetes_type1"
    DIABETES_TYPE2 = "diabetes_type2"
    PREDIABETES = "prediabetes"
    HYPERTENSION_STAGE1 = "hypertension_stage1"
    HYPERTENSION_STAGE2 = "hypertension_stage2"
    HYPERLIPIDEMIA = "hyperlipidemia"
    OBESITY_CLASS1 = "obesity_class1"
    OBESITY_CLASS2 = "obesity_class2"
    OBESITY_CLASS3 = "obesity_class3"
    ANEMIA = "anemia"


class RulePriority(Enum):
    """Priority levels for dietary rules."""
    
    REQUIRED = "required"        # Medical restrictions, allergies
    RECOMMENDED = "recommended"  # Health-based guidelines
    OPTIONAL = "optional"        # Preferences


class MealType(Enum):
    """Types of meals in a daily diet plan."""
    
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACK = "snack"
    DINNER = "dinner"
