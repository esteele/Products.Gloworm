import binascii
from plone.app.customerize import registration
from zope.component import getGlobalSiteManager
from zope.interface import providedBy

def hashViewletInfo(viewletName, managerName, provided):
    """ Create a hashed version of the viewlet's vitals so that we can do lookups later. """
    return binascii.b2a_hex("%s\n%s\n%s" % (viewletName, managerName, provided))

def unhashViewletInfo(hash):
    """ Pull values out of the hashed "info" variable being passed in by KSS """
    concat_txt = binascii.a2b_hex(hash)
    viewletName, managerName, provided = concat_txt.splitlines()
    # Turn provided into the tuple of strings that plone.app.customerize is looking for.
    info = dict(viewletName=viewletName, managerName=managerName, provided=provided, hash=hash)
    return info

def findTemplateViewRegistrationFromHash(hash):
    """ Get the view registration information from plone.app.customerize """
    unhashedInfo = unhashViewletInfo(hash)
    return registration.findTemplateViewRegistration(unhashedInfo['provided'], unhashedInfo['viewletName'])
    
def getProvidedForViewlet(viewletName, manager):
    """ Get the "provided" interfaces for this viewlet manager. """
    # TODO: Is there a more "proper" way to do this?
    managerInterface = list(providedBy(manager).flattened())[0]
    regs = [regs for regs in getGlobalSiteManager().registeredAdapters() if regs.name == viewletName and regs.required[-1].isOrExtends(managerInterface)]
    if regs:
        reg = regs[0]
        return ','.join([a.__identifier__ for a in reg.required])
    return None