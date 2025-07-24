#!/usr/bin/env python
"""
OAuth Setup Script for Plone
Run this after pas.plugins.authomatic is installed
"""

import os
import sys

# Configuration from environment
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
AUTHOMATIC_SECRET = os.environ.get('AUTHOMATIC_SECRET', 'your-secret-key-here')

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("ERROR: Google OAuth credentials not found in environment!")
    print("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    sys.exit(1)

# OAuth configuration for pas.plugins.authomatic
oauth_config = f'''{{
    "google": {{
        "display": {{
            "title": "Google",
            "cssclasses": {{
                "button": "btn btn-primary",
                "icon": "glyphicon glyphicon-google"
            }}
        }},
        "class_": "authomatic.providers.oauth2.Google",
        "consumer_key": "{GOOGLE_CLIENT_ID}",
        "consumer_secret": "{GOOGLE_CLIENT_SECRET}",
        "scope": ["profile", "email"],
        "access_headers": {{"User-Agent": "Plone/6.1"}}
    }}
}}'''

print("=" * 70)
print("OAUTH CONFIGURATION FOR PLONE")
print("=" * 70)
print()
print("Follow these steps to configure OAuth in Plone:")
print()
print("1. Go to: http://project-title.localhost/@@authomatic-controlpanel")
print("   (Login as admin if prompted)")
print()
print("2. In the 'JSON Configuration' field, paste this configuration:")
print()
print(oauth_config)
print()
print("3. In the 'Secret' field, enter:")
print(f"   {AUTHOMATIC_SECRET}")
print()
print("4. Click 'Save' at the bottom of the page")
print()
print("5. Test by going to: http://project-title.localhost/login")
print("   and clicking 'Sign in with Google'")
print()
print("=" * 70)
print()
print("Your OAuth Redirect URI for Google Console is:")
print("http://project-title.localhost/@@authomatic-handler/google")
print() 