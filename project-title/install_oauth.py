#!/usr/bin/env python
"""Install and configure OAuth for Plone"""

import os
import json
import transaction
from plone import api

# Get the Plone site
app = globals().get('app')
plone_site = app.Plone

# Install pas.plugins.authomatic
try:
    # Check if already installed
    qi = api.portal.get_tool('portal_quickinstaller')
    if not qi.isProductInstalled('pas.plugins.authomatic'):
        print("Installing pas.plugins.authomatic...")
        qi.installProduct('pas.plugins.authomatic')
        print("✅ pas.plugins.authomatic installed successfully")
    else:
        print("✅ pas.plugins.authomatic already installed")
        
    # Configure OAuth
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    secret = os.environ.get('AUTHOMATIC_SECRET', 'dev-secret')
    
    if client_id and client_secret:
        print("Configuring OAuth...")
        
        oauth_config = {
            'google': {
                'display': {
                    'title': 'Google',
                    'cssclasses': {
                        'button': 'btn btn-primary',
                        'icon': 'glyphicon glyphicon-google'
                    }
                },
                'class_': 'authomatic.providers.oauth2.Google',
                'consumer_key': client_id,
                'consumer_secret': client_secret,
                'scope': ['profile', 'email'],
                'access_headers': {'User-Agent': 'Plone/6.1'}
            }
        }
        
        # Set the configuration
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        
        registry = getUtility(IRegistry)
        registry['pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.json_config'] = json.dumps(oauth_config)
        registry['pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.secret'] = secret
        
        print("✅ OAuth configuration applied")
        print(f"   Client ID: {client_id[:20]}...")
        
    else:
        print("❌ OAuth credentials not found in environment")
        
    # Commit the transaction
    transaction.commit()
    print("✅ All changes committed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    transaction.abort() 