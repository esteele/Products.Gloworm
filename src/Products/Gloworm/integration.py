from zope.interface import implements
from Products.CMFPlone.interfaces import INonInstallable

class HiddenProfiles(object):
    implements(INonInstallable)
    
    def getNonInstallableProfiles(self):
        """
        Prevents the uninstall profile from showing up in the profile list
        when creating a Plone site. 
        """
        return [u'Products.Gloworm:uninstall']
