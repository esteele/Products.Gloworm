# -*- coding: utf-8 -*-

__author__ = """WebLion <support@weblion.psu.edu>"""
__docformat__ = 'plaintext'

#
# Test-cases for product install/uninstall/reinstall
#

from Products.CMFCore.utils import getToolByName
import Products.Gloworm
from Products.Gloworm.tests.base import GlowormTestCase
from Products.Five.fiveconfigure import debug_mode as DebugModeActive

class testInstall(GlowormTestCase):
    def afterSetUp(self):
        self.setRoles(('Manager',))
        
    def testCheckDebugMode(self):
        self.failUnless(DebugModeActive == True, 'Debug Mode is not enabled, GloWorm was not activated.')
        
    def testInstallMonkeyPatch(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate, manage_addPageTemplate
        manage_addPageTemplate(self.app, 'test', 
                               text='<div tal:content="string:foo">bar</div>', 
                               encoding='ascii')
        zpt = self.app['test']
        from zope.publisher.base import DebugFlags
        self.app.REQUEST.debug = DebugFlags()
        self.assertEqual(zpt.pt_render(), u'<div>foo</div>\n')
        self.app.REQUEST.debug.showTAL = True
        self.assertEqual(zpt.pt_render(), u'<div tal:content="string:foo">foo</div>\n')

    def testInspectFrontPage(self):
        """ Simple test to ensure that the @@inspect view at least initializes without errors for the front-page of the site. """
        self.app.plone['front-page'].unrestrictedTraverse('@@inspect')()


class testUninstall(GlowormTestCase):
    def afterSetUp(self):
        pass



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testInstall))
    suite.addTest(makeSuite(testUninstall))
    return suite