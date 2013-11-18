from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.testing import z2
from Products.Five import fiveconfigure

from plone.app.multilingual.testing import PloneAppMultilingualLayer

class SlcXliffLayer(PloneAppMultilingualLayer):
    defaultBases = (PLONE_FIXTURE, )
        
    def setUpZope(self, app, configurationContext):
        PloneAppMultilingualLayer.setUpZope(self, app, configurationContext)
        z2.installProduct(app, 'Products.PloneLanguageTool')
        z2.installProduct(app, 'Products.ZCatalog')

        fiveconfigure.debug_mode = True
        import slc.xliff
        self.loadZCML('configure.zcml', package=slc.xliff)
        self.loadZCML('testing.zcml', package=slc.xliff)
        fiveconfigure.debug_mode = False

    def setUpPloneSite(self, portal):
        PloneAppMultilingualLayer.setUpPloneSite(self, portal)

        applyProfile(portal, 'slc.xliff:default')
        applyProfile(portal, 'slc.xliff:testing')

        # Login as manager and create a test folder
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.PloneLanguageTool')
        z2.uninstallProduct(app, 'Products.ZCatalog')


SLC_XLIFF_FIXTURE = SlcXliffLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_XLIFF_FIXTURE,), name="SlcXliff:Integration"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_XLIFF_FIXTURE,), name="SlcXliff:Functional"
)
