from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import quickInstallProduct
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.testing import z2
from Products.Five import fiveconfigure


class SlcXliffLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, 'Products.PloneLanguageTool')
        z2.installProduct(app, 'Products.LinguaPlone')
        z2.installProduct(app, 'Products.ZCatalog')
        fiveconfigure.debug_mode = True
        import slc.xliff
        self.loadZCML('configure.zcml', package=slc.xliff)
        fiveconfigure.debug_mode = False
        import Products.LinguaPlone
        self.loadZCML('configure.zcml', package=Products.LinguaPlone)

    def setUpPloneSite(self, portal):
        quickInstallProduct(portal, 'Products.LinguaPlone')
        applyProfile(portal, 'slc.xliff:default')

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
        z2.uninstallProduct(app, 'Products.LinguaPlone')
        z2.uninstallProduct(app, 'Products.ZCatalog')


SLC_XLIFF_FIXTURE = SlcXliffLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_XLIFF_FIXTURE,), name="SlcXliff:Integration"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_XLIFF_FIXTURE,), name="SlcXliff:Functional"
)
