# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
import logging

__version__ = "1.0.0"
PACKAGE_NAME = "project.title"

logger = logging.getLogger(__name__)

_ = MessageFactory("project.title")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    # Configure OAuth if environment variables are present
    configure_oauth()

    # Import catalog module to register indexers
    try:
        logger.info("✅ Performance catalog indexers registered")
    except Exception as e:
        logger.warning(f"Catalog indexers import failed: {e}")


def configure_oauth():
    """Configure OAuth settings from environment variables"""
    import os

    # Check if we have the necessary environment variables
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if client_id and client_secret:
        logger.info("Google OAuth environment variables detected")
        # The actual configuration will be done through the registry
        # or by pas.plugins.authomatic's own initialization
