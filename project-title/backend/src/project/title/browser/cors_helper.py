"""
CORS Helper for Classroom Management Platform - SECURITY HARDENED

Provides consistent CORS header handling across all browser views
with enhanced security validation and protection against CORS attacks.
Integrates with the security module for production-ready origin validation.
"""

import logging
from ..security import (
    validate_cors_origin,
    get_security_headers,
    PRODUCTION_SECURITY_CONFIG,
)

logger = logging.getLogger(__name__)

# Development origins (used when production config not available)
DEVELOPMENT_ORIGINS = [
    "http://localhost:3000",  # Development Volto frontend
    "http://localhost:8080",  # Development backend
    "http://project-title.localhost",  # Docker stack via Traefik
    "https://project-title.localhost",  # Docker stack with SSL
]


def set_cors_headers(request, response):
    """
    Set appropriate CORS headers with security validation

    Args:
        request: The Plone request object
        response: The Plone response object

    Returns:
        bool: True if preflight request, False otherwise
    """
    origin = request.getHeader("Origin")

    # Apply security headers first
    try:
        security_headers = get_security_headers()
        for header, value in security_headers.items():
            response.setHeader(header, value)
    except Exception as e:
        logger.warning(f"Failed to apply security headers: {e}")

    # Validate CORS origin
    if origin:
        # Get allowed origins from production config or fallback to development
        allowed_origins = PRODUCTION_SECURITY_CONFIG.get(
            "cors_origins", DEVELOPMENT_ORIGINS
        )

        if validate_cors_origin(origin, allowed_origins):
            # Origin is valid - set CORS headers
            response.setHeader("Access-Control-Allow-Origin", origin)
            response.setHeader("Access-Control-Allow-Credentials", "true")
            response.setHeader(
                "Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE"
            )
            response.setHeader(
                "Access-Control-Allow-Headers",
                "Content-Type, Accept, Authorization, X-Requested-With",
            )
            response.setHeader("Access-Control-Max-Age", "86400")  # 24 hours
        else:
            # Origin not allowed - log security warning
            logger.warning(f"CORS violation: Rejected origin {origin}")
            # Don't set CORS headers for invalid origins

    # Handle preflight requests
    if request.get("REQUEST_METHOD") == "OPTIONS":
        response.setStatus(200)
        return True

    return False


def cors_enabled_view(view_method):
    """
    Decorator to automatically add CORS headers and security headers to browser view methods

    Usage:
        @cors_enabled_view
        def __call__(self):
            # Your view logic here
            pass
    """

    def wrapper(self):
        # Set CORS headers and security headers
        is_preflight = set_cors_headers(self.request, self.request.response)

        # Handle preflight requests
        if is_preflight:
            return ""

        # Call the original view method
        return view_method(self)

    return wrapper


def secure_api_view(rate_limit_action=None, rate_limit_per_hour=60):
    """
    Enhanced decorator for API views with rate limiting and security

    Args:
        rate_limit_action: Action name for rate limiting
        rate_limit_per_hour: Maximum requests per hour

    Usage:
        @secure_api_view(rate_limit_action='api_hall_pass', rate_limit_per_hour=20)
        def __call__(self):
            # Your API logic here
            pass
    """

    def decorator(view_method):
        def wrapper(self):
            from ..security import check_rate_limit
            from plone import api
            import json

            # Apply CORS and security headers
            is_preflight = set_cors_headers(self.request, self.request.response)
            if is_preflight:
                return ""

            # Check rate limiting if specified
            if rate_limit_action:
                user = api.user.get_current()
                if user:
                    user_id = user.getId()
                    if not check_rate_limit(
                        user_id, rate_limit_action, rate_limit_per_hour
                    ):
                        self.request.response.setStatus(429)
                        return json.dumps(
                            {
                                "error": "Rate limit exceeded",
                                "message": f"Too many {rate_limit_action} requests. Please wait before trying again.",
                            }
                        )

            # Call the original view method
            return view_method(self)

        return wrapper

    return decorator
