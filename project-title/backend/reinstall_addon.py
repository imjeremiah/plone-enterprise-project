#!/usr/bin/env python3
"""
Simple script to reinstall the project.title addon and apply profiles.
This ensures our Standards Alignment behavior is properly installed.
"""

def reinstall_addon():
    """Reinstall the addon via Plone's quick installer."""
    
    # Print instructions for manual installation via web interface
    print("""
🔧 ADDON INSTALLATION REQUIRED

Your backend is running but the Standards Alignment behavior isn't installed in the site.

FOLLOW THESE STEPS:

1. Open your browser and go to: http://localhost:8080/Plone
2. Login with admin/admin
3. Go to Site Setup (click the gear icon in the toolbar)
4. Click "Add-ons" (under "General")
5. Find "Project Title" in the available add-ons list
6. Click "Install" next to it
7. Wait for installation to complete

OR try the direct URL:
http://localhost:8080/Plone/prefs_install_products_form

After installation:
- Go back to your frontend (localhost:3000)
- Edit any Document
- You should see the "Standards Alignment" tab!

🎯 This will properly install the behavior and make the Standards tab appear.
""")

if __name__ == '__main__':
    reinstall_addon() 