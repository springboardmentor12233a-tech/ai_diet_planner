"""
AI NutriCare System - Main Package

A comprehensive system for processing medical reports and generating
personalized diet plans based on health analysis.
"""

__version__ = "1.0.0"
__author__ = "AI NutriCare Team"

# Make main components easily accessible
from .main import AINutriCareOrchestrator, PipelineResult

__all__ = [
    'AINutriCareOrchestrator',
    'PipelineResult',
]
