"""
Centralized error handling and recovery for AI NutriCare System.

This module provides:
- Error categorization and logging
- Retry logic with exponential backoff
- Graceful degradation strategies
- User-facing error messages
"""

import logging
import time
import traceback
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

T = TypeVar('T')


class ErrorCategory(Enum):
    """Categories of errors in the system."""
    INPUT_VALIDATION = "input_validation"
    PROCESSING = "processing"
    DATA = "data"
    SYSTEM = "system"


class NutriCareError(Exception):
    """Base exception for AI NutriCare System."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.context = context or {}
        self.user_message = user_message or self._default_user_message()
        self.timestamp = datetime.now()
        self.stack_trace = traceback.format_exc()
    
    def _default_user_message(self) -> str:
        """Generate default user-facing error message."""
        return "An error occurred while processing your request. Please try again."


class InputValidationError(NutriCareError):
    """Error during input validation."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, user_message: Optional[str] = None):
        super().__init__(message, ErrorCategory.INPUT_VALIDATION, context, user_message)
    
    def _default_user_message(self) -> str:
        return "Invalid input provided. Please check your data and try again."


class ProcessingError(NutriCareError):
    """Error during data processing."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, user_message: Optional[str] = None):
        super().__init__(message, ErrorCategory.PROCESSING, context, user_message)
    
    def _default_user_message(self) -> str:
        return "Error processing your data. Please try again or contact support."


class DataError(NutriCareError):
    """Error related to data operations."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, user_message: Optional[str] = None):
        super().__init__(message, ErrorCategory.DATA, context, user_message)
    
    def _default_user_message(self) -> str:
        return "Error accessing or storing data. Please try again."


class SystemError(NutriCareError):
    """System-level error."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, user_message: Optional[str] = None):
        super().__init__(message, ErrorCategory.SYSTEM, context, user_message)
    
    def _default_user_message(self) -> str:
        return "System error occurred. Please try again later or contact support."


class ErrorHandler:
    """Centralized error handler with logging and recovery strategies."""
    
    def __init__(self, logger_name: str = "nutricare"):
        self.logger = logging.getLogger(logger_name)
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error with timestamp, context, and stack trace.
        
        Args:
            error: The exception to log
            context: Additional context information
        """
        context = context or {}
        
        if isinstance(error, NutriCareError):
            log_data = {
                'timestamp': error.timestamp.isoformat(),
                'category': error.category.value,
                'message': error.message,
                'context': {**error.context, **context},
                'stack_trace': error.stack_trace
            }
            self.logger.error(f"NutriCare Error: {log_data}")
        else:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'category': ErrorCategory.SYSTEM.value,
                'message': str(error),
                'context': context,
                'stack_trace': traceback.format_exc()
            }
            self.logger.error(f"Unexpected Error: {log_data}")
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        fallback: Optional[Callable[[], T]] = None
    ) -> Optional[T]:
        """
        Handle error with logging and optional fallback.
        
        Args:
            error: The exception to handle
            context: Additional context information
            fallback: Optional fallback function to execute
            
        Returns:
            Result from fallback function if provided, None otherwise
        """
        self.log_error(error, context)
        
        if fallback:
            try:
                self.logger.info("Executing fallback strategy")
                return fallback()
            except Exception as fallback_error:
                self.logger.error(f"Fallback failed: {fallback_error}")
                return None
        
        return None
    
    def get_user_message(self, error: Exception) -> str:
        """
        Get user-facing error message.
        
        Args:
            error: The exception
            
        Returns:
            User-friendly error message
        """
        if isinstance(error, NutriCareError):
            return error.user_message
        return "An unexpected error occurred. Please try again."


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger = logging.getLogger("nutricare.retry")
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger = logging.getLogger("nutricare.retry")
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            # If we get here, all retries failed
            raise cast(Exception, last_exception)
        
        return wrapper
    return decorator
