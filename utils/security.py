"""
Security utilities for AI NutriCare System.

Provides:
- Rate limiting
- Input sanitization
- CORS configuration
- Security headers
- API key authentication
"""

import hashlib
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from functools import wraps


class RateLimiter:
    """Rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds (default: 1 hour)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            identifier: Unique identifier (e.g., IP address, API key)
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        cutoff = now - self.time_window
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        now = time.time()
        cutoff = now - self.time_window
        
        # Count recent requests
        recent = sum(1 for req_time in self.requests[identifier] if req_time > cutoff)
        return max(0, self.max_requests - recent)
    
    def get_reset_time(self, identifier: str) -> Optional[datetime]:
        """Get time when rate limit resets."""
        if not self.requests[identifier]:
            return None
        
        oldest = min(self.requests[identifier])
        reset_time = datetime.fromtimestamp(oldest + self.time_window)
        return reset_time


def rate_limit(max_requests: int = 100, time_window: int = 3600):
    """
    Decorator for rate limiting functions.
    
    Args:
        max_requests: Maximum requests allowed
        time_window: Time window in seconds
    """
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use first argument as identifier (e.g., user_id, ip_address)
            identifier = str(args[0]) if args else "default"
            
            if not limiter.is_allowed(identifier):
                raise PermissionError(
                    f"Rate limit exceeded. Try again later. "
                    f"Remaining: {limiter.get_remaining(identifier)}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class InputSanitizer:
    """Input sanitization and validation."""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS: Set[str] = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.txt'}
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'<iframe[^>]*>',  # Iframes
        r'eval\s*\(',  # Eval calls
        r'exec\s*\(',  # Exec calls
    ]
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            filename = name[:250] + '.' + ext
        
        return filename
    
    @staticmethod
    def validate_file(file_path: str) -> tuple[bool, str]:
        """
        Validate file for security issues.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, "File does not exist"
        
        # Check file extension
        if path.suffix.lower() not in InputSanitizer.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed: {', '.join(InputSanitizer.ALLOWED_EXTENSIONS)}"
        
        # Check file size
        if path.stat().st_size > InputSanitizer.MAX_FILE_SIZE:
            max_mb = InputSanitizer.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
        
        # Check for path traversal
        try:
            path.resolve().relative_to(Path.cwd())
        except ValueError:
            return False, "Invalid file path"
        
        return True, ""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text input to prevent XSS and injection attacks.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Remove dangerous patterns
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        if len(text) > 100000:  # 100KB
            text = text[:100000]
        
        return text
    
    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """
        Sanitize input for SQL queries (use parameterized queries instead when possible).
        
        Args:
            value: Input value
            
        Returns:
            Sanitized value
        """
        # Remove SQL injection patterns
        dangerous_sql = [
            r';\s*DROP\s+TABLE',
            r';\s*DELETE\s+FROM',
            r';\s*UPDATE\s+',
            r';\s*INSERT\s+INTO',
            r'UNION\s+SELECT',
            r'--',
            r'/\*',
            r'\*/',
        ]
        
        for pattern in dangerous_sql:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value


class APIKeyAuth:
    """API key authentication."""
    
    def __init__(self, api_keys: Optional[List[str]] = None):
        """
        Initialize API key authentication.
        
        Args:
            api_keys: List of valid API keys (hashed)
        """
        self.api_keys = set(api_keys) if api_keys else set()
    
    def add_key(self, api_key: str) -> None:
        """Add API key (stores hash)."""
        key_hash = self._hash_key(api_key)
        self.api_keys.add(key_hash)
    
    def remove_key(self, api_key: str) -> None:
        """Remove API key."""
        key_hash = self._hash_key(api_key)
        self.api_keys.discard(key_hash)
    
    def validate_key(self, api_key: str) -> bool:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        key_hash = self._hash_key(api_key)
        return key_hash in self.api_keys
    
    @staticmethod
    def _hash_key(api_key: str) -> str:
        """Hash API key using SHA-256."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def generate_key() -> str:
        """Generate new API key."""
        import secrets
        return secrets.token_urlsafe(32)


def require_api_key(auth: APIKeyAuth):
    """
    Decorator to require API key authentication.
    
    Args:
        auth: APIKeyAuth instance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract API key from kwargs
            api_key = kwargs.get('api_key')
            
            if not api_key:
                raise PermissionError("API key required")
            
            if not auth.validate_key(api_key):
                raise PermissionError("Invalid API key")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """
        Get recommended security headers.
        
        Returns:
            Dictionary of security headers
        """
        return {
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Strict transport security (HTTPS only)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # Content security policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            ),
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }


class CORSConfig:
    """CORS configuration."""
    
    def __init__(
        self,
        allowed_origins: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None,
        max_age: int = 3600
    ):
        """
        Initialize CORS configuration.
        
        Args:
            allowed_origins: List of allowed origins (default: localhost only)
            allowed_methods: List of allowed HTTP methods
            allowed_headers: List of allowed headers
            max_age: Max age for preflight cache in seconds
        """
        self.allowed_origins = allowed_origins or ['http://localhost:8501']
        self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE']
        self.allowed_headers = allowed_headers or ['Content-Type', 'Authorization']
        self.max_age = max_age
    
    def get_headers(self, origin: str) -> Dict[str, str]:
        """
        Get CORS headers for origin.
        
        Args:
            origin: Request origin
            
        Returns:
            Dictionary of CORS headers
        """
        if origin not in self.allowed_origins and '*' not in self.allowed_origins:
            return {}
        
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': ', '.join(self.allowed_methods),
            'Access-Control-Allow-Headers': ', '.join(self.allowed_headers),
            'Access-Control-Max-Age': str(self.max_age),
        }
