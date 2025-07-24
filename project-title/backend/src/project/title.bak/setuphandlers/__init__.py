# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "project.title:uninstall",
        ]


def post_install(context):
    """Post install script"""
    if context.readDataFile('project.title-marker.txt') is None:
        return
    
    # Configure OAuth
    from .oauth import configure_oauth_provider
    configure_oauth_provider(context) 