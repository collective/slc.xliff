from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.multilingual.testing import MultipleLanguagesLayer
from plone.app.multilingual.testing import (
    PLONE_APP_MULTILINGUAL_PRESET_FIXTURE,
)
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2
from Products.Five import fiveconfigure
from Products.CMFPlone.utils import getToolByName


class SlcXliffLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(SlcXliffLayer, self).setUpZope(app, configurationContext)
        # z2.installProduct(app, "Products.ZCatalog")

        fiveconfigure.debug_mode = True
        import plone.app.multilingual

        self.loadZCML("configure.zcml", package=plone.app.multilingual)

        import slc.xliff

        self.loadZCML("configure.zcml", package=slc.xliff)
        self.loadZCML("testing.zcml", package=slc.xliff)

        fiveconfigure.debug_mode = False
        z2.installProduct(app, "slc.xliff")

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])

        language_tool = getToolByName(portal, "portal_languages")
        language_tool.addSupportedLanguage("en")
        language_tool.addSupportedLanguage("de")
        language_tool.addSupportedLanguage("es")
        language_tool.addSupportedLanguage("fi")
        language_tool.addSupportedLanguage("pt-br")
        language_tool.addSupportedLanguage("en-us")
        language_tool.addSupportedLanguage("es-es")

        applyProfile(portal, "plone.app.multilingual:default")
        applyProfile(portal, "slc.xliff:default")
        applyProfile(portal, "slc.xliff:testing")

        # Commit so that the test browser sees these objects
        # portal.portal_catalog.clearFindAndRebuild()
        # import transaction

        # transaction.commit()

    # def tearDownZope(self, app):
    #     z2.uninstallProduct(app, "Products.ZCatalog")


SLC_XLIFF_FIXTURE = SlcXliffLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_XLIFF_FIXTURE,), name="SlcXliff:Integration"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_XLIFF_FIXTURE,), name="SlcXliff:Functional"
)
