"""
Patient profile and preferences data models for the AI NutriCare System.

This module contains data classes for patient information and user preferences.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class UserPreferences:
    """
    User dietary preferences and restrictions.
    
    Attributes:
        dietary_style: Optional dietary style (vegetarian, vegan, keto, paleo, etc.)
        allergies: List of food allergies
        dislikes: List of foods the user dislikes
        cultural_preferences: List of cultural dietary preferences
    """
    
    dietary_style: Optional[str] = None
    allergies: List[str] = None
    dislikes: List[str] = None
    cultural_preferences: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists for None values."""
        if self.allergies is None:
            self.allergies = []
        if self.dislikes is None:
            self.dislikes = []
        if self.cultural_preferences is None:
            self.cultural_preferences = []


@dataclass
class PatientProfile:
    """
    Complete patient profile with demographics and preferences.
    
    Attributes:
        patient_id: Unique identifier for the patient
        age: Patient age in years
        gender: Patient gender
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        activity_level: Activity level (sedentary, light, moderate, active, very_active)
        preferences: User dietary preferences
        created_at: Timestamp when the profile was created
    """
    
    patient_id: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    preferences: UserPreferences
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set created_at to current time if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
