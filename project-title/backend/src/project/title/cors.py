"""
CORS Configuration for project.title

This module provides CORS configuration for plone.rest
"""

from plone.rest.cors import CORSPolicy as BaseCORSPolicy
from zope.component import adapter
from zope.interface import implementer
from plone.rest.interfaces import ICORSPolicy
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(ICORSPolicy)
@adapter(Interface, IBrowserRequest)
class CORSPolicy(BaseCORSPolicy):
    """Custom CORS policy that configures allowed origins for development"""

    def __init__(self, context, request):
        super().__init__(context, request)
        # Set CORS configuration directly
        self.allow_origin = ["http://localhost:3000"]
        self.allow_methods = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
        self.allow_credentials = True
        self.allow_headers = [
            "Accept",
            "Authorization",
            "Content-Type",
            "X-Requested-With",
        ]
        self.expose_headers = ["Content-Length", "X-JSON-Schema"]
        self.max_age = 3600
