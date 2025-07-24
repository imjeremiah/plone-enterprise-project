#!/usr/bin/env python
"""Configure OAuth in Plone"""

import os
import json
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction

# Get the Plone site
app = globals().get('app')
plone_site = app.Plone

# Configure OAuth
client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
secret = os.environ.get('AUTHOMATIC_SECRET', 'dev-secret')

if client_id and client_secret:
    registry = getUtility(IRegistry)
    
    oauth_config = {
        'google': {
            'class_': 'authomatic.providers.oauth2.Google',
            'consumer_key': client_id,
            'consumer_secret': client_secret,
            'scope': ['profile', 'email'],
        }
    }
    
    # Set the configuration
    registry['pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.json_config'] = json.dumps(oauth_config)
    registry['pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.secret'] = secret
    
    print('OAuth configuration applied successfully')
    print(f'Client ID: {client_id[:20]}...')
    
    # Commit
    transaction.commit()
else:
    print('OAuth credentials not found in environment') 