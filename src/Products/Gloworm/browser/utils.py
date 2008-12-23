import binascii
from plone.app.customerize import registration
from zope.interface import providedBy
from new import classobj
from zope.component import queryMultiAdapter, getGlobalSiteManager
from zope.interface import classImplements
from zope.viewlet.interfaces import IViewletManager

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

def findViewletManager(self, name):
    managerObj = queryMultiAdapter((self.context, self.request, self), IViewletManager, name)
    if not managerObj:
        # Here's where we go totally off the deep end...
        # Since we can't find this viewlet manager with the basic (self.context, self.request, self)
        # multiadapter lookup, this must be some sort of custom manager, registered to other interfaces.
        # In order to find it, we need to do a bit of reverse engineering...
    
        # Since Plone's generic setup process for viewlets constrains us to one viewlet manager / name,
        # we're going to assume that the adapter with this name, and a provided interface that is or extends IViewletManger
        # is the one we're looking for. 
        # So, start with a search of the adapter registry...
    
        reg = [reg for reg in getGlobalSiteManager().registeredAdapters() if reg.name == name][0]

        # So far, I think we're stuck with context and request being the first two interfaces.
        providedClasses = [self.context, self.request]

        # Now, we take a look at the required interfaces...
        # And create some dummy classes that implement them.                    
        for iface in reg.required[2:]:
            tempClass = classobj('dummy', (object,), {})
            classImplements(tempClass, iface)
            providedClasses.append(tempClass())

        # Now just do a basic multiadapter lookup using our new objects providing the correct interfaces...
        managerObj = queryMultiAdapter(tuple(providedClasses), reg.provided, name)
    return managerObj