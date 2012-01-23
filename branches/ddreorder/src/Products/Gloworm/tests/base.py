import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from transaction import commit


from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
import Products.Gloworm

# there is no install package in Zope 2.9
TEST_INSTALL =True
if not hasattr(ztc, 'installPackage'):
    TEST_INSTALL = False

ptc.setupPloneSite()

@onsetup
def setup_product():
    """Set up the additional products required for this package.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for dependent packages.
    
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.Gloworm)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    if TEST_INSTALL:
        ztc.installPackage('Products.Gloworm')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need.Then, we let PloneTestCase set up this 
# product on installation.

setup_product()
ptc.setupPloneSite(products=['Products.Gloworm'])

# Manually call initialize() so that the monkey patch gets installed
Products.Gloworm.initialize(ztc.app)

class GlowormTestCase(ptc.PloneTestCase):
    def afterSetUp(self):
        # Turn debug mode on
        fiveconfigure.debug_mode = True
    
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
