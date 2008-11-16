from zope.interface import providedBy
import binascii
from zope.component import getGlobalSiteManager
from Globals import DevelopmentMode
from plone.app.gloworm.browser.interfaces import IGlowormLayer

import logging
logger = logging.getLogger('plone.app.gloworm')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    
    # Monkey patch Products.PageTemplates.PageTemplate.PageTemplate so that we can use the showTAL debug flag.
    # At some point this might not be necessary if https://bugs.launchpad.net/zope2/+bug/229549
    # is accepted.
    
    def pt_render(self, source=False, extra_context={}):
        c = self.pt_getContext()
        c.update(extra_context)
        # Fix would belong here...
        debug = getattr(c['request'], 'debug', None)
        if debug is not None:
            showtal = getattr(debug, 'showTAL', False)
            sourceAnnotations = getattr(debug, 'sourceAnnotations', False)
        else:
            showtal = sourceAnnotations = False
        return super(PageTemplate, self).pt_render(c, source=source, sourceAnnotations=sourceAnnotations,
                   showtal=showtal)
    
    from Products.PageTemplates.PageTemplate import PageTemplate
    PageTemplate.pt_render = pt_render
    logger.info('PageTemplate.pt_render Monkey patch installed.')
    
    # Monkey patch viewlet manager rendering to include our tal blocks. If we can get viewlet
    # manager adaptation working properly, this will go away.
    
    def render(self):
        if self.template:
            print "skipping viewlet tag for %s" % self.__name__
            return self.template(viewlets=self.viewlets)
        else:
            # Check to see if we're in the GloWorm view. Otherwise, don't include the custom tal blocks.
            glowormActive = IGlowormLayer.providedBy(self.request)
            outstr = ""
            if glowormActive:
                manager_name = self.__name__
                managerInterface = list(providedBy(self).flattened())[0]
                logger.debug("Creating viewletmanager tag for %s" % manager_name)
                outstr += "<tal:viewletmanager class='kssattr-viewletmanagername-%s GloWormViewletManagerBlock'>" % manager_name.replace('.', '-')

            for viewlet in self.viewlets:
                if glowormActive:
                    # customized viewlet TTWViewletRenderer don't have a __name__ attached, grab it from the template id
                    if hasattr(viewlet, '__name__'):
                        view_name = viewlet.__name__
                    else:
                        view_name = viewlet.template.id.split('-')[-1]
                    # Get the "provided" interfaces for this viewlet manager.
                    # TODO: Do this lookup properly.
                    regs = [regs for regs in getGlobalSiteManager().registeredAdapters() if regs.name == view_name and regs.required[-1].isOrExtends(managerInterface)]
                    if regs:
                        reg = regs[0]
                        provided = ','.join([a.__identifier__ for a in reg.required])
                        # logger.debug("%s - provided: %s" % (view_name, provided))
                        hashedInfo = binascii.b2a_hex("%s\n%s\n%s" % (view_name, manager_name, provided))
                        outstr += u"<tal:viewlet class='kssattr-viewlethash-%s GloWormViewletBlock'>\n%s\n</tal:viewlet>\n" % (hashedInfo, viewlet.render())
                    else:
                        logger.debug("Unable to create hash for %s" % view_name)
                else:
                    outstr += viewlet.render()

            if glowormActive:
                outstr += "</tal:viewletmanager>"

            return outstr

    from plone.app.viewletmanager.manager import BaseOrderedViewletManager
    # Only install the monkey patch if we're running in debug mode since that's one of the prereqs for running GloWorm. 
    # It's an attempt to minimize the effects this monkeypatch has on the system until we can get some sort of adaptation working properly.
    if DevelopmentMode:
        BaseOrderedViewletManager.render = render
    logger.info('BaseOrderedViewletManager.render monkey patch installed.')
