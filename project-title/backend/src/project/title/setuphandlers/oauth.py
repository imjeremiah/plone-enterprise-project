# -*- coding: utf-8 -*-
"""OAuth configuration setup handlers"""
from plone import api
import json
import os
import logging

logger = logging.getLogger(__name__)


def configure_oauth_provider(context):
    """Configure Google OAuth provider if environment variables are set"""
    
    # Import here to avoid circular imports
    from ..auth import setup_authomatic_plugin, validate_oauth_config
    
    logger.info("Configuring OAuth provider...")
    
    # Validate configuration first
    if validate_oauth_config():
        setup_authomatic_plugin(context)
        logger.info("OAuth provider configuration complete")
    else:
        logger.warning("OAuth provider not configured - missing credentials") 