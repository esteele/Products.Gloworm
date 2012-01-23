from kss.core import CommandSet
from interfaces import IGlowormCommands
from zope.interface import implements

import logging
logger = logging.getLogger('Products.Gloworm')

class GlowormCommands(CommandSet):
    implements(IGlowormCommands)
        
    def showErrorMessage(self, message=""):
        """ Show an error message panel """
        command = self.commands.addCommand('showErrorMessage')
        data = command.addParam('message', message)
        logger.debug("in GlowormCommands.showErrorMessage")
    
    def forceGlowormPanelResize(self, message=""):
        """ Fire the resize event of the GloWorm panel """
        command = self.commands.addCommand('forceGlowormPanelResize')
        logger.debug("in GlowormCommands.forceGlowormPanelResize")
    
    def scrollNavTree(self, selector):
        """ Scroll the nav tree to show the selected element
        """
        command = self.commands.addCommand('scrollNavTree', selector)
        logger.debug("in GlowormCommands.scrollNavTree")
    
    def scrollContentArea(self, selector):
        """ Scroll the content area to show the selected element
        """
        command = self.commands.addCommand('scrollContentArea', selector)
        logger.debug("in GlowormCommands.scrollContentArea")
