from zope.interface import implements
from Products.CMFPlone.interfaces import INonInstallable as IPortalCreationNonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable

class HiddenProducts(object):
    """This hides the upgrade profiles from the quick installer tool."""
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return ['Products.Gloworm.upgrades']


class HiddenProfiles(object):
    implements(IPortalCreationNonInstallable)
    
    def getNonInstallableProfiles(self):
        """
        Prevents the uninstall profile from showing up in the profile list
        when creating a Plone site. 
        """
        return [u'Products.Gloworm:uninstall',
                u'Products.Gloworm.upgrades:1to2']
