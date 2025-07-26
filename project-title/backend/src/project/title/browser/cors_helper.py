"""
CORS Helper for Classroom Management Platform

Provides consistent CORS header handling across all browser views
to support both development (localhost:3000) and Docker (project-title.localhost) environments.
"""

import logging

logger = logging.getLogger(__name__)

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    'http://localhost:3000',           # Development Volto frontend
    'http://project-title.localhost',  # Docker stack via Traefik
    'https://project-title.localhost', # Docker stack with SSL
]


def set_cors_headers(request, response):
    """
    Set appropriate CORS headers based on request origin
    
    Args:
        request: The Plone request object
        response: The Plone response object
    """
    origin = request.getHeader('Origin')
    
    # Set CORS headers
    if origin in ALLOWED_ORIGINS:
        response.setHeader('Access-Control-Allow-Origin', origin)
    else:
        # Fallback to localhost:3000 for development
        response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
    
    response.setHeader('Access-Control-Allow-Credentials', 'true')
    response.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization')
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response.setStatus(200)
        return True
    
    return False


def cors_enabled_view(view_method):
    """
    Decorator to automatically add CORS headers to browser view methods
    
    Usage:
        @cors_enabled_view
        def __call__(self):
            # Your view logic here
            pass
    """
    def wrapper(self):
        # Set CORS headers
        is_preflight = set_cors_headers(self.request, self.request.response)
        
        # Handle preflight requests
        if is_preflight:
            return ''
        
        # Call the original view method
        return view_method(self)
    
    return wrapper 