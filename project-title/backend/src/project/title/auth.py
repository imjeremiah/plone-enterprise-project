"""
OAuth Authentication Configuration for Project Title

This module provides helper functions for Google OAuth integration.
pas.plugins.authomatic will be configured through the Plone control panel.
"""

import os
import logging
import json

logger = logging.getLogger("project.title.auth")


def get_authomatic_config():
    """
    Returns the authomatic configuration for OAuth providers.
    Uses environment variables for production deployment.
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        logger.warning("Google OAuth credentials not found in environment")
        return None

    config = {
        "google": {
            "class_": "authomatic.providers.oauth2.Google",
            "consumer_key": client_id,
            "consumer_secret": client_secret,
            "scope": ["profile", "email"],
            "access_headers": {"User-Agent": "Project Title Educational Platform"},
        }
    }

    logger.info("Google OAuth configuration loaded from environment")
    return config


def setup_authomatic_plugin(context):
    """
    Configure pas.plugins.authomatic with OAuth settings.
    This is called during product installation.
    """
    from plone import api

    config = get_authomatic_config()
    if not config:
        logger.warning("Skipping OAuth setup - no credentials in environment")
        return

    api.portal.get()

    # Set the authomatic configuration in the registry
    try:
        api.portal.set_registry_record(
            "pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.json_config",
            json.dumps(config),
        )

        # Set the secret
        secret = os.environ.get("AUTHOMATIC_SECRET", "development-secret-change-this")
        api.portal.set_registry_record(
            "pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.secret",
            secret,
        )

        logger.info("✅ OAuth configuration applied to Plone registry")

    except Exception as e:
        logger.error(f"Failed to configure OAuth: {str(e)}")


def validate_oauth_config():
    """
    Validates OAuth configuration and logs status.
    """
    config = get_authomatic_config()

    if not config:
        logger.warning(
            "⚠️  OAuth not configured! "
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )
        return False

    logger.info("✅ OAuth configuration validated")
    return True
