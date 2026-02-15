"""
NLP module for the AI NutriCare System.

This module provides natural language processing capabilities for interpreting
medical notes and prescriptions.
"""

from .text_interpreter import NLPTextInterpreter, NLPBackend

__all__ = [
    "NLPTextInterpreter",
    "NLPBackend",
]
