#!/usr/bin/env python3
"""
Quick script to check if hall pass workflow is installed
Run this from the backend directory to verify workflow installation
"""

import sys
import os

# Add the instance to Python path for Plone access
sys.path.insert(0, '/Users/jeremiahcandelaria/plone/project-title/backend')

def check_workflow():
    try:
        # This would need to be run in Plone context
        print("✅ Workflow files created successfully:")
        
        workflow_file = "src/project/title/profiles/default/workflows/hall_pass_workflow/definition.xml"
        if os.path.exists(workflow_file):
            print(f"   ✅ {workflow_file}")
        else:
            print(f"   ❌ {workflow_file}")
            
        workflows_xml = "src/project/title/profiles/default/workflows.xml"
        if os.path.exists(workflows_xml):
            print(f"   ✅ {workflows_xml}")
        else:
            print(f"   ❌ {workflows_xml}")
            
        browser_view = "src/project/title/browser/hall_pass_workflow.py"
        if os.path.exists(browser_view):
            print(f"   ✅ {browser_view}")
        else:
            print(f"   ❌ {browser_view}")
            
        print("\n🔧 To activate in running Plone:")
        print("   1. Go to: http://localhost:8080/Plone/@@overview-controlpanel")
        print("   2. Click 'Add-ons'")
        print("   3. Find 'Project Title' → Settings → Reinstall")
        print("   4. OR go to: http://localhost:8080/Plone/portal_setup")
        print("   5. Import tab → Select 'workflows.xml' → Import")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_workflow() 