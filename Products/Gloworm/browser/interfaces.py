from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager
from zope.publisher.interfaces.browser import IBrowserRequest

class IGlowormPanel(IViewletManager):
    """A viewlet manager that displays the gloworm panel
    """
    pass
    
class IInspectorView(Interface):
    pass

class IGlowormCommands(Interface):
    def resizePanel(self):
        """ Update the size of the GloWorm panel (and page content wrapper) to fit its current contents. """

class IGlowormLayer(IBrowserRequest):
    pass

class IAmIgnoredByGloworm(Interface):
    """ An item that the GloWorm inspector will ignore. """
    pass