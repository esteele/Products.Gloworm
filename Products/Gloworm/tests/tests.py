import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from transaction import commit


from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import Products.Gloworm

class GlowormTestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             Products.Gloworm)
            #fiveconfigure.debug_mode = True

            # starting with 2.10.4 product initialization gets delayed for
            # instance startup and is never called when running tests;  hence
            # we have to initialize the package method manually...
            from OFS.Application import install_package
            app = ztc.app()
            install_package(app, Products.Gloworm, Products.Gloworm.initialize)
            # create a starting point for the tests...
            commit()
            ztc.close(app)


        @classmethod
        def tearDown(cls):
            pass
    
class GlowormWithoutDebugModeEnabledTestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             Products.Gloworm)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
            
def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='Products.Gloworm',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='Products.Gloworm.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='Products.Gloworm',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='Products.Gloworm',
        #    test_class=TestCase),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
