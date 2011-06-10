from zope.component import getMultiAdapter, getAdapters, queryMultiAdapter
from zope.interface import implements, alsoProvides
from zope.publisher.base import DebugFlags
from zope.viewlet.interfaces import IViewlet, IViewletManager
from archetypes.kss.interfaces import IInlineEditingEnabled
from kss.core.BeautifulSoup import BeautifulSoup
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import IContentish, IDynamicType

from Products.Gloworm.browser.interfaces import IInspectorView, IGlowormLayer, IAmIgnoredByGloworm
from Products.Gloworm.browser.utils import findTemplateViewRegistrationFromHash, getProvidedForViewlet, hashViewletInfo, findViewletManager

from Products.Five.fiveconfigure import debug_mode as DebugModeActive
import re
import logging

logger = logging.getLogger('Products.Gloworm')

class InspectorView(BrowserView):
    implements(IInspectorView)
    
    glowormPanelTemplate = ViewPageTemplateFile('glowormPanel.pt')
    
    def __call__(self):
        if DebugModeActive:
            alsoProvides(self.request, IGlowormLayer)
            
            # TODO What was this for again?
            from plone.app.layout.globals.interfaces import IViewView
            alsoProvides(self.request, IViewView)
            
            # Apply debug flags to the request
            self.request.debug = DebugFlags()
            self.request.debug.showTAL = True
            self.request.debug.sourceAnnotations = True
            
            # Find the actual content object in the context
            # Calling @@inspect on object/view results in view being self.context
            contentObject = self.context
            while not IDynamicType.providedBy(contentObject):
                contentObject = contentObject.aq_inner.aq_parent
            
            context_state = getMultiAdapter((contentObject, self.request), name='plone_context_state')
            templateId = context_state.view_template_id()
            template = contentObject.unrestrictedTraverse(templateId)
            # template = contentObject.unrestrictedTraverse(templateId and '@@%s' % templateId)

            renderedTemplate = template()
            # Insert the GloWorm panel and wrap the page content in a wrapper div so that we
            # can break the two into two different panels. To do that, we're forced to
            # do some ill-conceived html parsing. BeautifulSoup appears to be changing pages
            # with the TAL included, closing some tags that it shouldn't be and that breaks
            # the page layout. Javascript methods do the same. So, for now, we're stuck with
            # REGEX.
            
            glowormPanel = self.glowormPanelTemplate(self.context, self.request)
            regexp = r"(\</?body[^\>]*\>)([\S\s]*)(</body>)"
            replace = r"""
            \1
            <div id='glowormPageWrapper' class='kssattr-insideInspectableArea-True'>
            \2
            </div> <!-- Close glowormPageWrapper -->
            %s
            \3
            """ % glowormPanel
            
            updatedTemplate = re.sub(regexp, replace, renderedTemplate)
            
            # For cross-browser compatability (ie. everything, not just Firefox), we need to:
            # 1) Remove anything before the doctype
            docString = re.search(r'(<!DOCTYPE[^\>]*\>)', updatedTemplate).group()
            # 2) Remove anything between the doctype and <html> declaration
            # 3) Remove anything after the closing </html>
            htmlBlock = re.search(r'\<html[\S\s]*\<\/html>', updatedTemplate).group()
            updatedTemplate = docString + htmlBlock
            # 4) Insert the metal and tal namespaces into the html declaration
            updatedTemplate = re.sub(r"(\<html[^\>]*)([\>])", r"""\1 xmlns:metal="http://xml.zope.org/namespaces/metal" xmlns:tal="http://xml.zope.org/namespaces/tal"\2""", updatedTemplate)
            
            return updatedTemplate
        else:
            return "Please enable Zope debug/development mode to continue."
    
    def saveTemplateEdits(self, viewlet):
        logger.debug("saving template edits for viewlet %s" % viewlet)

class GlowormPanelHeader(ViewletBase):
    index = ViewPageTemplateFile('glowormPanelHeader.pt')
    
    def update(self):
        self.close_url = self.context.absolute_url()

class GlowormPanelBody(ViewletBase):
    index = ViewPageTemplateFile('glowormPanelBody.pt')
    
    def update(self):
        self.portal_type = self.context.getPortalTypeName()
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

class GlowormInspectLink(ViewletBase):
    implements(IAmIgnoredByGloworm)
    index = ViewPageTemplateFile('glowormInspectLink.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        self.url = '%s/@@inspect' % context_state.object_url()

class GlowormHtmlHeadIncludes(ViewletBase):
    implements(IAmIgnoredByGloworm)
    index = ViewPageTemplateFile('glowormHtmlHeadIncludes.pt')
    
    def update(self):
        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        self.baseurl = portal_state.portal_url()

class GlowormPanelNavTree(ViewletBase):
    index = ViewPageTemplateFile('glowormPanelNavTree.pt')
    
    def update(self):
        
        # Tell BeautifulSoup that viewlets and viewletmanagers can be nested.
        BeautifulSoup.NESTABLE_TAGS['tal:viewlet']=['tal:viewletmanager']
        BeautifulSoup.NESTABLE_TAGS['tal:viewletmanager']=['tal:viewlet']
        
        # Render the current page and strip out everything but the <tal:viewletmanager> and <tal:viewlet> tags.
        # TODO We probably don't need BeautifulSoup anymore since we've got such a simple parsetree.
        
        # We need the GloWorm specific browser layer in there so that we can see the tal:viewlet* tags.
        alsoProvides(self.request, IGlowormLayer)
        
        # Find the object providing IDynamicType, that's what we want to inspect
        # Otherwise, we get errors relating to getTypeInfo() 
        contentObject = self.context
        while not IDynamicType.providedBy(contentObject):
            contentObject = contentObject.aq_inner.aq_parent
        
        context_state = getMultiAdapter((contentObject, self.request), name='plone_context_state')
        templateId = context_state.view_template_id()
        # There are instances in which the enclosing view is named 'index' that calling a traverse to 'index' 
        # actually gets this viewlet's index method. Prepending the '@@' seems to take care of that.
        # So, either traverse to @@templateId or nothing depending on the value of templateId.
        try:
            template = contentObject.unrestrictedTraverse(templateId and '@@%s' % templateId)
        except AttributeError:
            # The template isn't a view, just call it without the @@
            template = contentObject.unrestrictedTraverse(templateId)

        renderedTemplate = template()
        
        strippedHTML = ''.join((re.findall('(<\/?tal:viewlet/?[^\>]*>)', renderedTemplate)))
        
        # Soupify the simplified HTML
        soup = BeautifulSoup(strippedHTML)
        self.documentTree = []
        self.outstr = ""
        
        def getChildViewletManagers(node):
            """ Find all viewletmanagers within this node """
            all = node.findAll('tal:viewletmanager')
            stripped = []
            self.outstr += "<ol class='viewletmanager-tree'>"
            for v in all:
                if not(stripped and v.findParent('tal:viewletmanager') and stripped[-1] in v.findParents('tal:viewletmanager')):
                    rawname = v.attrs[0][1][27:] # 27 = len('kssattr-viewletmanagername-')
                    # Break off any extra class names
                    # TODO We should really be safe and check for classes before and after.
                    rawname = rawname.split(' ',1)[0]
                    name = rawname.replace('-','.')
                    # Get the viewletmanager object
                    managerObj = findViewletManager(self, name)
                    if managerObj and not IAmIgnoredByGloworm.providedBy(managerObj):
                        self.outstr += "<li><a href='#' title='Viewlet Manager %s' class='inspectViewletManager kssattr-forviewletmanager-%s'>%s</a>" % (name, name.replace('.', '-'), name)
                        
                        # Look up the viewlets attached to this viewlet manager.
                        # We do it this way because calling viewletManager.viewlets won't see the hidden viewlets...
                        containedViewlets = getAdapters((self.context, self.request, managerObj.__parent__, managerObj),IViewlet)
                        containedViewlets = managerObj.sort([vl for vl in containedViewlets])
                        
                        stripped.append(v)
                        getChildViewlets(v, containedViewlets)
                        self.outstr += "</li>"
            self.outstr += "</ol>"
            return stripped
        
        def getChildViewlets(node, allViewlets=[]):
            """ Find all viewlets within this node """
            all = node.findAll('tal:viewlet')
            stripped = []
            self.outstr += "<ol class='viewlet-tree'>"
            
            def writeHiddenViewlet(viewlet):
                """ Create a list item HTML bit for a hidden viewlet """
                name = viewlet[0]
                managerObj = viewlet[1].manager
                viewletHash = hashViewletInfo(name, managerObj.__name__, getProvidedForViewlet(name, managerObj))
                return "<li><a href='#' title='Hidden viewlet %s' class='viewletMoreInfo hiddenViewlet kssattr-forviewlet-%s'>%s</a></li>" % (name, viewletHash, name)
            
            for v in all:
                if not(stripped and v.findParent('tal:viewlet') and stripped[-1] in v.findParents('tal:viewlet')):
                    viewletHash = v.attrs[0][1][20:] # 20 = len('kssattr-viewlethash-')
                    # Break off any extra class names
                    # TODO We should really be safe and check for classes before and after.
                    viewletHash = viewletHash.split(' ',1)[0]
                    reg = findTemplateViewRegistrationFromHash(viewletHash)
                    if reg:
                        while allViewlets and reg.name != allViewlets[0][0]:
                            self.outstr += writeHiddenViewlet(allViewlets[0])
                            allViewlets.pop(0)
                        
                        if not IAmIgnoredByGloworm.providedBy(allViewlets[0][1]):
                            self.outstr += "<li><a href='#' title='Visible viewlet %s' class='viewletMoreInfo kssattr-forviewlet-%s'>%s</a>" % (reg.name, viewletHash, reg.name)
                            stripped.append(v)
                            getChildViewletManagers(v)
                            self.outstr += "</li>"
                        allViewlets.pop(0) # Remove the current viewlet from the allViewlets list
            
            # Collect any remaining hidden viewletss
            if allViewlets:
                for vlt in allViewlets:
                    self.outstr += writeHiddenViewlet(vlt)
            self.outstr += "</ol>"
            return stripped
        
        getChildViewletManagers(soup)


class DisableInlineEditingView(BrowserView):
    """ Disable inline editing for the Gloworm Inspector view. """
    implements(IInlineEditingEnabled)
    
    def __call__(self):
        return False