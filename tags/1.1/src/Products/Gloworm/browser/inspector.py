from zope.component import getAdapters
from zope.component import getSiteManager
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implements, providedBy, alsoProvides
from zope.pagetemplate.pagetemplate import PTRuntimeError
from zope.traversing.interfaces import TraversalError
from zope.viewlet.interfaces import IViewlet, IViewletManager

from five.customerize.interfaces import IViewTemplateContainer
from five.customerize.browser import mangleAbsoluteFilename
from five.customerize.utils import findViewletTemplate

from plone.app.customerize import registration
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.portlets.utils import unhashPortletInfo

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Gloworm.browser.utils import findTemplateViewRegistrationFromHash, hashViewletInfo, unhashViewletInfo, findViewletManager
from Products.Gloworm.browser.interfaces import IGlowormLayer, IAmIgnoredByGloworm

try:
    from Products.Five.browser.pagetemplatefile import BoundPageTemplate
except ImportError:
    def BoundPageTemplate(template, view):
        return template.__of__(view)

import transaction
import binascii
import logging

logger = logging.getLogger('Products.Gloworm')

class InspectorKSS(PloneKSSView):
    implements(IPloneKSSView)
    
    def inspectElement(self,
                      insideInspectableArea=False,
                      talcontent=None,
                      talattributes=None,
                      talcondition=None,
                      metaldefmacro=None,
                      metalusemacro=None,
                      fieldname=None,
                      portlethash=None,
                      viewlethash=None,
                      sourceAnnotation=None):
        """ Get details about a particular html element. """
        # Make sure we're not clicking inside the inspector div since KSS doesn't seem to provide a
        # way to block processing of other rules.
        if insideInspectableArea:
            logger.debug("in inspectElement")
            
            parsedTalAttributes = []
            if talattributes:
                # logger.debug("talattributes: %s" % talattributes)
                # If there's only one item in the list being returned by the KSS method,
                # it's passing it as a string instead of a list/array. Not sure why.
                # Sniff the type and make it a list if needed.
                if isinstance(talattributes, basestring):
                    talattributes = (talattributes,)
                for attr in talattributes:
                    # logger.debug("attr: %s" % attr)
                    attribute = {}
                    attribute['name'], attribute['expression'], attribute['result'] = attr.split(',')
                    parsedTalAttributes.append(attribute)
            
            unhashedPortletInfo = {}
            if portlethash:
                unhashedPortletInfo = unhashPortletInfo(portlethash)
            
            unhashedViewletInfo = {}
            if viewlethash:
                unhashedViewletInfo = unhashViewletInfo(viewlethash)
            
            if sourceAnnotation:
                sourceAnnotation = sourceAnnotation.strip(' =\n')
            
            template = ViewPageTemplateFile('panel_inspect_element.pt')
            # Wrap it so that Zope knows in what context it's being called
            # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
            template = BoundPageTemplate(template, self)
            out = template(metalUseMacro = metalusemacro,
                           metalDefMacro = metaldefmacro,
                           fieldName = fieldname,
                           talContent = talcontent,
                           talAttributes = parsedTalAttributes,
                           talCondition = talcondition,
                           portletInfo = unhashedPortletInfo,
                           viewletInfo = unhashedViewletInfo,
                           sourceAnnotation = sourceAnnotation
                           )
            
            # Dump the output to the inspector panel
            self.updatePanelBodyContent(out)
            
            # Highlight this element
            ksscore = self.getCommandSet('core')
            self.highlightElement(ksscore.getSameNodeSelector())
            
            # And in the nav tree (Should this be here or in the nav tree viewlet code?)
            if viewlethash:
                self.highlightInNavTree(ksscore.getCssSelector('#glowormPanelNavTree .kssattr-forviewlet-%s' % viewlethash))
        
        return self.render()
    
    def inspectContentObject(self):
        """ Display detailed information about the current content object """
        logger.debug("in inspectViewlet")
        
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        
        template = ViewPageTemplateFile('panel_inspect_content_object.pt')
        # Wrap it so that Zope knows in what context it's being called
        # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
        template = BoundPageTemplate(template, self)
        out = template(contentObject = self.context,
                       parent = context_state.parent(),
                       skinName = self.context.getCurrentSkinName(),
                       templateName = context_state.view_template_id()
                      )
        
        # Dump the output to the inspector panel
        self.updatePanelBodyContent(out)
        
        # Highlight the element
        ksscore = self.getCommandSet('core')
        self.highlightElement(ksscore.getCssSelector('#glowormPageWrapper'))
        
        # And in the nav tree (Should this be here or in the nav tree viewlet code?)
        self.highlightInNavTree(ksscore.getCssSelector('#glowormPanelNavTree .inspectContentObject'))
        
        return self.render()
    
    def inspectField(self, fieldname):
        """ Display detailed information about one of current content object's fields
        """
        field = self.context.getField(fieldname)
        template = ViewPageTemplateFile('panel_inspect_field.pt')
        # Wrap it so that Zope knows in what context it's being called
        # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
        template = BoundPageTemplate(template, self)
        out = template(fieldName = fieldname,
                       type = field.type,
                       widget = type(field.widget).__name__,
                       accessor = field.accessor,
                       mutator = field.mutator,
                       readPermission = field.read_permission,
                       writePermission = field.write_permission
                      )
        
        # Dump the output to the inspector panel
        self.updatePanelBodyContent(out)
        
        # Highlight the element
        ksscore = self.getCommandSet('core')
        self.highlightElement(ksscore.getCssSelector('.kssattr-atfieldname-%s' % fieldname))
        
        return self.render()
    
    def inspectViewlet(self, viewlethash):
        """ Display detailed information about a particular viewlet. """
        logger.debug("in inspectViewlet")
        
        # Unhash the viewlet info
        unhashedViewletInfo = unhashViewletInfo(viewlethash)
        # Get the registration information for this viewlet
        reg = findTemplateViewRegistrationFromHash(viewlethash)
        
        viewName = unhashedViewletInfo['viewletName']
        managerName = unhashedViewletInfo['managerName']
        cls = registration.getViewClassFromRegistration(reg)
        className = "%s.%s" % (cls.__module__, cls.__name__)
        try:
            viewRegistrationInfo = list(registration.templateViewRegistrationInfos([reg]))[0]
        except IndexError:
            # For some reason, there's no registration with portal_view_cusomtizations,
            # this appears to happen when there's no template defined for the viewlet and it instead
            # uses a "render" method.
            customizationExists = False
            customizationAllowed = False
            templatePath = ""
        else:
            template = viewRegistrationInfo['zptfile']
            templatePath = registration.generateIdFromRegistration(reg)
            container = queryUtility(IViewTemplateContainer)
            customizationExists = templatePath in container
            customizationAllowed = True
        
        # Get the names of the hidden viewlets
        storage = getUtility(IViewletSettingsStorage)
        hiddenViewlets = frozenset(storage.getHidden(managerName, self.context.getCurrentSkinName()))
        isVisible = viewName not in hiddenViewlets
        
        template = ViewPageTemplateFile('panel_inspect_viewlet.pt')
        # Wrap it so that Zope knows in what context it's being called
        # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
        template = BoundPageTemplate(template, self)
        out = template(viewName = viewName,
                       managerName = managerName,
                       template = template,
                       className = className,
                       templatePath = templatePath,
                       customizationExists = customizationExists,
                       customizationAllowed = customizationAllowed,
                       visible = isVisible,
                       viewletHash = viewlethash)
        
        # Dump the output to the output panel
        self.updatePanelBodyContent(out)
        
        # Highlight this element
        ksscore = self.getCommandSet('core')
        self.highlightElement(ksscore.getCssSelector('.kssattr-viewlethash-%s' % viewlethash))
        
        # And in the nav tree (Should this be here or in the nav tree viewlet code?)
        self.highlightInNavTree(ksscore.getCssSelector('#glowormPanelNavTree .kssattr-forviewlet-%s' % viewlethash))
        
        return self.render()
    
    def customizeViewlet(self, viewlethash):
        """ Display an edit form for modifiying a viewlet's template """
        logger.debug("in customizeViewlet")
        
        # Unhash the viewlet info
        unhashedViewletInfo = unhashViewletInfo(viewlethash)
        
        # Get the viewlet's registration information from portal_view_customizations
        container = queryUtility(IViewTemplateContainer)
        reg = findTemplateViewRegistrationFromHash(viewlethash)
        regInfo = list(registration.templateViewRegistrationInfos([reg]))[0]
        
        # TODO We should be looking at regInfo['customized'] to determine whether or not a customization exists.
        # It never seems to have a value though... check on this.
        templateName = registration.generateIdFromRegistration(reg)
        
        # Check to see if the viewlet has already been customized. Get the template code accordingly.
        if templateName not in container.objectIds():
            viewzpt = registration.customizeTemplate(reg)
            sm = getSiteManager(self.context)
            sm.registerAdapter(viewzpt, required= reg.required, provided = reg.provided, name=reg.name)
        else:
            viewzpt = container[templateName]
        templateCode = viewzpt.read()
        template = ViewPageTemplateFile('panel_customize_viewlet.pt')
        # Wrap it so that Zope knows in what context it's being called
        # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
        template = BoundPageTemplate(template, self)
        out = template(templateURL = viewzpt.absolute_url(),
                       viewletHash = viewlethash,
                       templateCode = templateCode)
        
        # Dump the output to the output panel
        self.updatePanelBodyContent(out)
        
        # Force a resize update of the panel so that the form elements are sized to the dimensions of the panel.
        kssglo = self.getCommandSet('gloWorm')
        kssglo.forceGlowormPanelResize()
        
        return self.render()
    
    def saveViewletTemplate(self, viewlethash, newContent):
        """ Update portal_view_customizations with the new version of the template. """
        logger.debug("in saveViewletTemplate")
        
        # Hide the error message
        self.hideTemplateErrorMessage()
        
        # Unhash the viewlet info. Pull out what we need.
        unhashedInfo = unhashViewletInfo(viewlethash)
        viewletName = unhashedInfo['viewletName']
        # Find the template in portal_view_customizations, save the new version
        container = queryUtility(IViewTemplateContainer)
        
        reg = findTemplateViewRegistrationFromHash(viewlethash)
        templateName = registration.generateIdFromRegistration(reg)
        
        try:
            container[templateName].write(newContent)
            result = self._renderCustomizedViewlet(viewlethash, templateName)
        except PTRuntimeError:
            message = container[templateName].pt_errors(self)[1]
            transaction.abort()
            return self.showTemplateErrorMessage(message)
        except TraversalError, e:
            transaction.abort()
            viewlet, err = e
            return self.showTemplateErrorMessage("TraversalError: %s" % err)
        else:
            return self._renderCustomizedViewlet(viewlethash, templateName)
    
    def _renderCustomizedViewlet(self, viewlethash, templateName):
        """ Rerender the viewlets to show the new code """
        # Unhash the viewlet info. Pull out what we need.
        unhashedInfo = unhashViewletInfo(viewlethash)
        managerName = unhashedInfo['managerName']
        viewletName = unhashedInfo['viewletName']
        
        ksscore = self.getCommandSet('core')
        
        # Find the viewletmangager instance, tell it to update its rendering, and replace the contents of the selected div with that new html
        # We can't do this with a refreshViewlet or refreshProvider because then we lose the <tal:viewletmanager> and <tal:viewlet> blocks.
        # selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + managerName.replace('.', '-'))
        viewletManager = findViewletManager(self, managerName)
        viewletManager.update()
        
        vlt = ksscore.getCssSelector('.kssattr-viewlethash-%s' % viewlethash)
        # Get the viewlet.
        # TODO: Is there a better way to do this?
        for viewlet in viewletManager.viewlets:
            if hasattr(viewlet, 'template') and viewlet.template.__name__ == templateName:
                # Turn on the debug flags for the viewlet's request, so that we have our tal: content
                self._turnOnTalRenderingForObjectsRequest(viewlet)
                ksscore.replaceInnerHTML(vlt, viewlet.render())
                break
        return self.render()
    
    def discardViewletCustomizations(self, viewlethash):
        """ Remove the customized template for a particular viewlet """
        # Unhash the viewlet info
        unhashedViewletInfo = unhashViewletInfo(viewlethash)
        
        # Get the viewlet's registration information from portal_view_customizations
        container = queryUtility(IViewTemplateContainer)
        reg = findTemplateViewRegistrationFromHash(viewlethash)
        templateName = registration.generateIdFromRegistration(reg)
        
        container.manage_delObjects([templateName])
        self._redrawViewletManager(unhashedViewletInfo['managerName'])
        return self.inspectViewlet(viewlethash)
    
    def showMoveViewletForm(self, viewlethash):
        """ Show the form for moving a viewlet between managers. """
        
        unhashedViewletInfo = unhashViewletInfo(viewlethash)
        reg = findTemplateViewRegistrationFromHash(viewlethash)
        viewRegistrationInfo = list(registration.templateViewRegistrationInfos([reg]))[0]
        
        managerName = unhashedViewletInfo['managerName']
        managerNames = self._getAllViewletManagerNames()
        managerNames.sort()
        # Remove the viewlet's current viewlet manager and the gloworm panel from the choices.
        managerNames.remove(unhashedViewletInfo['managerName'])
        managerNames.remove('gloworm.glowormPanel')
        
        template = ViewPageTemplateFile('panel_move_viewlet.pt')
        # Wrap it so that Zope knows in what context it's being called
        # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
        template = BoundPageTemplate(template, self)
        
        out = template(viewlethash=viewlethash,
                       viewletName = unhashedViewletInfo['viewletName'],
                       managerNames = managerNames)
        # Dump the output to the inspector panel
        self.updatePanelBodyContent(out)
        
        return self.render()
    
    def moveViewletToViewletManager(self, viewlethash, toManagerName):
        """ Register the viewlet as belonging to the specified viewlet manager """
        # Unhash the viewlet info. Pull out what we need.
        unhashedInfo = unhashViewletInfo(viewlethash)
        fromManagerName = unhashedInfo['managerName']
        viewletName = unhashedInfo['viewletName']
        
        reg = findTemplateViewRegistrationFromHash(viewlethash)
        
        fromViewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, fromManagerName)
        fromManagerInterface = list(providedBy(fromViewletManager).flattened())[0]
        toViewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, toManagerName)
        toManagerInterface = list(providedBy(toViewletManager).flattened())[0]
        
        # Create a new tuple of the "required" interfaces.
        reqList = list(reg.required)
        pos = reqList.index(fromManagerInterface)
        reqList[pos] = toManagerInterface
        reqs = tuple(reqList)
        
        registration.createTTWViewTemplate(reg)
        attr, pt = findViewletTemplate(reg.factory)
        reg.factory.template = mangleAbsoluteFilename(pt.filename)
        
        # Register the new adapter
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(name=viewletName, required=reqs, provided=reg.provided, factory=reg.factory)
        
        # "Customize" it to force persistence
        reqstr = ','.join([a.__identifier__ for a in reqs])
        toreg = registration.findTemplateViewRegistration(reqstr, viewletName)
        viewzpt = registration.customizeTemplate(toreg)
        
        sm = getSiteManager(self.context)
        sm.registerAdapter(viewzpt, required=toreg.required, provided=toreg.provided, name=toreg.name)
        
        # Hide the original
        self.hideViewlet(viewlethash)
        
        # Rerender the new one
        # We can't do this with a refreshProvider call because then we lose the <tal:viewletmanager> block.
        toViewletManager.update()
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + toManagerName.replace('.', '-'))
        ksscore.replaceInnerHTML(selector, toViewletManager.render())
        
        # Inspect the new viewlet
        return self.inspectViewlet(hashViewletInfo(viewletName, toManagerName, unhashedInfo['provided']))
    
    def inspectViewletManager(self, managerName):
        """ Display information about a particular viewlet manager """
        logger.debug("in inspectViewletManager")
        # Get the viewletmanager object
        managerName = managerName.replace('-', '.')
        viewletManager = findViewletManager(self, managerName)
        
        # Gather information for the viewlet hashes
        managerInterface = list(providedBy(viewletManager).flattened())[0]
        
        # Look up the viewlets attached to this viewlet manager.
        # We do it this way because calling viewletManager.viewlets won't see the hidden viewlets...
        viewlets = getAdapters((self.context, self.request, viewletManager.__parent__, viewletManager),IViewlet)
        
        # Get the names of the hidden viewlets
        storage = getUtility(IViewletSettingsStorage)
        hidden = frozenset(storage.getHidden(managerName, self.context.getCurrentSkinName()))
        
        # Generate the output
        sortedViewlets = viewletManager.sort(viewlets)
        
        containedViewlets = []
        for viewletname, viewletObj in sortedViewlets:
            containedViewlet = {}
            if not IAmIgnoredByGloworm.providedBy(viewletObj):
            
                # generate viewlet hashes...
                # TODO factor this up.
            
                # Get the "provided" interfaces for this viewlet manager.
                # TODO: Do this lookup properly.
                regs = [regs for regs in getGlobalSiteManager().registeredAdapters() 
                        if regs.name == viewletname
                        and regs.required[-1].isOrExtends(managerInterface)]
                if regs:
                    reg = regs[0]
                    provided = ','.join([a.__identifier__ for a in reg.required])
                    # logger.debug("%s - provided: %s" % (viewletName, provided))
                    hashedInfo = binascii.b2a_hex("%s\n%s\n%s" % (viewletname, managerName, provided))
                else:
                    hashedInfo = ""
                    logger.debug("Unable to create hash for %s" % viewletname)
            
                # Give the viewlet a class name depending on the visibility
                classname = viewletname in hidden and 'hiddenViewlet' or 'visibleViewlet'
                logger.debug(classname)
                containedViewlet['className'] = classname
                containedViewlet['hashedInfo'] = hashedInfo
                containedViewlet['name'] = viewletname
                containedViewlets.append(containedViewlet)
        
        # Determine whether the contained viewlets can be sorted.
        skinname = self.context.getCurrentSkinName()
        canOrder = bool(storage.getOrder(managerName, skinname))
        
        template = ViewPageTemplateFile('panel_inspect_viewlet_manager.pt')
        # Wrap it so that Zope knows in what context it's being called
        # Otherwise, we get an "AttributeError: 'str' object has no attribute 'other'" error
        template = BoundPageTemplate(template, self)
        out = template(managerName = managerName,
                       safeManagerName = managerName.replace('.', '-'),
                       containedViewlets = containedViewlets,
                       canOrder = canOrder
                       )
        
        # Dump the output to the output panel
        self.updatePanelBodyContent(out)
        
        # Highlight the element
        ksscore = self.getCommandSet('core')
        self.highlightElement(ksscore.getCssSelector('.kssattr-viewletmanagername-%s' % managerName.replace('.', '-')))
        
        # And in the nav tree (Should this be here or in the nav tree viewlet code?)
        self.highlightInNavTree(ksscore.getCssSelector('#glowormPanelNavTree .kssattr-forviewletmanager-%s' % managerName.replace('.', '-')))
        
        return self.render()
    
    
    def hideViewlet(self, viewlethash, managerName = None):
        """ Hide the selected viewlet """
        logger.debug("in hide_viewlet")

        # Grab the information we need from the viewlet hash
        unhashedInfo = unhashViewletInfo(viewlethash)
        manageViewletsView = getMultiAdapter((self.context, self.request), name='manage-viewlets')
        manageViewletsView.hide(unhashedInfo['managerName'], unhashedInfo['viewletName'])
        self._redrawViewletManager(unhashedInfo['managerName'])

        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('#glowormPanel .kssattr-viewlethash-%s' % viewlethash)
        ksscore.removeClass(selector, 'visibleViewlet')
        ksscore.addClass(selector, 'hiddenViewlet')
        
        # Update the nav tree
        zope = self.getCommandSet('zope')
        zope.refreshViewlet('#glowormPanelNavTree', 'gloworm.glowormPanel', 'glowormPanelNavTree')
        
        # Update the viewlet listing in the GloWorm panel
        if managerName:
            self.inspectViewletManager(unhashViewletInfo(viewlethash)['managerName'].replace('.', '-'))
        else:
            self.inspectViewlet(viewlethash)
        
        return self.render()
    
    def showViewlet(self, viewlethash, managerName = None):
        """ Show the selected viewlet """
        logger.debug("in hide_viewlet")
        # Grab the information we need from the viewlet hash
        unhashedInfo = unhashViewletInfo(viewlethash)
        manageViewletsView = getMultiAdapter((self.context, self.request), name='manage-viewlets')
        manageViewletsView.show(unhashedInfo['managerName'], unhashedInfo['viewletName'])
        self._redrawViewletManager(unhashedInfo['managerName'])

        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('#glowormPanel .kssattr-viewlethash-%s' % viewlethash)
        ksscore.removeClass(selector, 'hiddenViewlet')
        ksscore.addClass(selector, 'visibleViewlet')
        
        # Update the nav tree
        zope = self.getCommandSet('zope')
        zope.refreshViewlet('#glowormPanelNavTree', 'gloworm.glowormPanel', 'glowormPanelNavTree')
        
        # Update the viewlet listing in the GloWorm panel
        if managerName:
            self.inspectViewletManager(unhashViewletInfo(viewlethash)['managerName'].replace('.', '-'))
        else:
            self.inspectViewlet(viewlethash)
        
        return self.render()
    
    def moveViewletByDelta(self, viewlethash, delta):
        """ Move the viewlet within its viewlet manager """
        logger.debug("in moveViewletByDelta")
        
        # Grab the information we need from the viewlet hash
        unhashedInfo = unhashViewletInfo(viewlethash)
        managerName = unhashedInfo['managerName']
        viewletName = unhashedInfo['viewletName']
        
        # Make sure delta is an integer, KSS apparently passes it in as a string.
        logger.debug("Converting %s to an integer" % delta)
        delta = int(delta)
        logger.debug("Moving viewlet by %s" % delta)
        
        # Get the viewletmanager object
        viewletManager = findViewletManager(self, managerName)
        
        # Get the order of the viewlets managed by this viewlet manager
        viewletManager.update()
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        order = list(storage.getOrder(managerName, skinname))
        
        viewlet_index = order.index(viewletName)
        
        # Move the viewlet to its new position
        newpos = max(0, viewlet_index + delta) and min(viewlet_index + delta, len(order))
        del order[viewlet_index]
        order.insert(newpos, viewletName)
        storage = getUtility(IViewletSettingsStorage)
        storage.setOrder(managerName, skinname, order)
        
        # Update the page display
        self._redrawViewletManager(managerName)
        
        zope = self.getCommandSet('zope')
        zope.refreshViewlet('#glowormPanelNavTree', 'gloworm.glowormPanel', 'glowormPanelNavTree')
        # Make sure the manager is still shown in the nav tree after reloading
        ksscore = self.getCommandSet('core')
        self.highlightInNavTree(ksscore.getCssSelector('#glowormPanelNavTree .kssattr-forviewletmanager-%s' % managerName.replace('.', '-')))
        
        # Update the viewlet listing in the GloWorm panel
        self.inspectViewletManager(managerName)
        
        return self.render()
    
    def updatePanelBodyContent(self, content):
        """ Overwrite the current text in the GloWorm panel body """
        logger.debug("updatePanelBodyContent")
        ksscore = self.getCommandSet('core')
        panel = ksscore.getCssSelector('#glowormPanelBody')
        ksscore.replaceInnerHTML(panel, content)
    
    def highlightElement(self, selector):
        """ Highlight the element defined by the passed selector.
        """
        # Remove highlights from previously-clicked elements
        ksscore = self.getCommandSet('core')
        ksscore.removeClass(ksscore.getCssSelector('.currentlySelectedElement'), 'currentlySelectedElement')
        
        # Highlight this element
        ksscore.addClass(selector, 'currentlySelectedElement')
        
        # Scroll the content area
        # Check for a value for the selector before attempting to scroll,
        # otherwise, odd things happen when clicking on elements in the content pane.
        if selector.value:
            kssglo = self.getCommandSet('gloWorm')
            newSelectorString = '#glowormPageWrapper %s' % selector.value
            kssglo.scrollContentArea(ksscore.getCssSelector(newSelectorString))
    
    
    def highlightInNavTree(self, selector):
        """ Hightlight the element in the navigation tree
        """
        ksscore = self.getCommandSet('core')
        ksscore.addClass(selector, 'currentlySelectedElement')
        kssglo = self.getCommandSet('gloWorm')
        kssglo.scrollNavTree(selector)
    
    def _getAllViewletManagers(self):
        """ Get all defined viewlet managers
        """
        return [regs for regs in getGlobalSiteManager().registeredAdapters() if regs.provided.isOrExtends(IViewletManager)]
    
    def _getAllViewletManagerNames(self):
        """ Get the names of all defined viewlet managers """
        return [v.name for v in self._getAllViewletManagers()]
    
    def _redrawViewletManager(self, managerName):
        # Get the viewlet manager, update, and rerender it
        # We can't do this with a refreshProvider call because then we lose the <tal:viewletmanager> block.\
        viewletManager = findViewletManager(self, managerName)
        viewletManager.update()
        
        # Apply all of the bits we need for inline tal
        self._turnOnTalRenderingForObjectsRequest(viewletManager)
        
        # Update the display
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + managerName.replace('.', '-'))
        ksscore.replaceInnerHTML(selector, viewletManager.render())
        return self.render()
    
    def _turnOnTalRenderingForObjectsRequest(self, obj):
        """ Turn on the debug flags for the object's request, so that we have our tal: content """
        # obj.request.debug = DebugFlags()
        # obj.request.debug.showTAL = True
        # obj.request.debug.sourceAnnotations = True
        alsoProvides(obj.request, IGlowormLayer)
    
    def showTemplateErrorMessage(self, error):
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('#editableTemplateErrorMessage')
        ksscore.addClass(selector, 'visible')
        ksscore.replaceInnerHTML(ksscore.getCssSelector('#editableTemplateErrorMessage'), error)
        # kssglo = self.getCommandSet('gloWorm')
        # kssglo.showErrorMessage(error)
        
        # Force a resize update of the panel so that the form elements are sized to the dimensions of the panel.
        kssglo = self.getCommandSet('gloWorm')
        kssglo.forceGlowormPanelResize()
        
        return self.render()
    
    def hideTemplateErrorMessage(self):
        ksscore = self.getCommandSet('core')
        ksscore.removeClass(ksscore.getCssSelector('#editableTemplateErrorMessage'), 'visible')
        # Force a resize update of the panel so that the form elements are sized to the dimensions of the panel.
        kssglo = self.getCommandSet('gloWorm')
        kssglo.forceGlowormPanelResize()
