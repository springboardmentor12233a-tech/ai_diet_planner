"""Utility modules for AI NutriCare System."""

from .error_handler import (
    ErrorCategory,
    NutriCareError,
    InputValidationError,
    ProcessingError,
    DataError,
    SystemError,
    ErrorHandler,
    retry_with_backoff
)
from .fallback import FallbackStrategies
from .security import (
    RateLimiter,
    rate_limit,
    InputSanitizer,
    APIKeyAuth,
    require_api_key,
    SecurityHeaders,
    CORSConfig
)

__all__ = [
    'ErrorCategory',
    'NutriCareError',
    'InputValidationError',
    'ProcessingError',
    'DataError',
    'SystemError',
    'ErrorHandler',
    'retry_with_backoff',
    'FallbackStrategies',
    'RateLimiter',
    'rate_limit',
    'InputSanitizer',
    'APIKeyAuth',
    'require_api_key',
    'SecurityHeaders',
    'CORSConfig'
]
