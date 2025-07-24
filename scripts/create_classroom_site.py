"""
Create Classroom Management Site for Phase 2 Implementation

This script creates a dedicated Plone site for testing and developing
our classroom management features including SeatingChart content type.
"""

from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.GenericSetup.tool import SetupTool
from project.title.interfaces import IBrowserLayer
from Testing.makerequest import makerequest
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides

import os
import transaction


truthy = frozenset(("t", "true", "y", "yes", "on", "1"))


def asbool(s):
    """Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


DELETE_EXISTING = asbool(os.getenv("DELETE_EXISTING"))
EXAMPLE_CONTENT = asbool(os.getenv("EXAMPLE_CONTENT", "1"))

app = makerequest(globals()["app"])

request = app.REQUEST

ifaces = [IBrowserLayer]
for iface in directlyProvidedBy(request):
    ifaces.append(iface)

directlyProvides(request, *ifaces)

admin = app.acl_users.getUserById("admin")
admin = admin.__of__(app.acl_users)
newSecurityManager(None, admin)

# Classroom Management Site Configuration
site_id = "classroom"
payload = {
    "title": "K-12 Classroom Management Platform",
    "profile_id": _DEFAULT_PROFILE,
    "distribution_name": "volto",
    "setup_content": False,
    "default_language": "en",
    "portal_timezone": "UTC",
}

if site_id in app.objectIds() and DELETE_EXISTING:
    app.manage_delObjects([site_id])
    transaction.commit()
    app._p_jar.sync()

if site_id not in app.objectIds():
    print(f"🎯 Creating classroom management site: {site_id}")
    site = addPloneSite(app, site_id, **payload)
    transaction.commit()

    portal_setup: SetupTool = site.portal_setup
    print("📚 Installing classroom management features...")
    portal_setup.runAllImportStepsFromProfile("profile-project.title:default")
    transaction.commit()

    if EXAMPLE_CONTENT:
        print("📝 Adding example classroom content...")
        portal_setup.runAllImportStepsFromProfile("profile-project.title:initial")
        transaction.commit()
    
    print("✅ Classroom management site created successfully!")
    print(f"🌐 Access at: http://localhost:8080/{site_id}")
    app._p_jar.sync()
else:
    print(f"⚠️  Site '{site_id}' already exists. Use DELETE_EXISTING=1 to recreate.") 