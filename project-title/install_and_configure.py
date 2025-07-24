#!/usr/bin/env python
"""Install and configure OAuth in one go"""

import os
import json
import transaction
from plone import api

print("🚀 Starting OAuth installation and configuration...")

try:
    # Set up with admin privileges
    with api.env.adopt_user(username='admin'):
        print("🔧 Installing pas.plugins.authomatic...")
        
        # Install the add-on
        try:
            api.addon.install('pas.plugins.authomatic')
            print("✅ pas.plugins.authomatic installed successfully")
        except Exception as e:
            if "already installed" in str(e).lower():
                print("✅ pas.plugins.authomatic already installed")
            else:
                print(f"⚠️  Installation note: {e}")
        
        # Configure OAuth
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        secret = os.environ.get('AUTHOMATIC_SECRET', 'dev-secret')
        
        print(f"🔑 Found credentials: {bool(client_id)} / {bool(client_secret)}")
        
        if client_id and client_secret:
            print("🔧 Configuring OAuth settings...")
            
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
            
            # Set the configuration in registry
            api.portal.set_registry_record(
                'pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.json_config',
                json.dumps(oauth_config)
            )
            api.portal.set_registry_record(
                'pas.plugins.authomatic.interfaces.IPasPluginsAuthomaticSettings.secret',
                secret
            )
            
            print("✅ OAuth configuration applied to registry")
            print(f"   Client ID: {client_id[:20]}...")
            print(f"   Secret: {secret[:10]}...")
            
        else:
            print("❌ OAuth credentials not found in environment")
            print("   GOOGLE_CLIENT_ID present:", bool(client_id))
            print("   GOOGLE_CLIENT_SECRET present:", bool(client_secret))
        
        # Commit the transaction
        transaction.commit()
        print("✅ All changes committed to database")
        print("")
        print("🎉 OAuth setup complete!")
        print("   Test at: http://project-title.localhost/login")
        print("   Click 'Sign in with Google' button")

except Exception as e:
    print(f"❌ Error during setup: {e}")
    import traceback
    traceback.print_exc()
    transaction.abort()
    print("🔄 Transaction rolled back") 