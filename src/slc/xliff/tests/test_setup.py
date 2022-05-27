# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from slc.xliff.tests.base import INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that slc.xliff is properly installed."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if slc.xliff is installed."""
        self.assertTrue(self.installer.is_product_installed("slc.xliff"))

    def test_browserlayer(self):
        """Test that ISlcXliff is registered."""
        from slc.xliff.interfaces import ISlcXliff
        from plone.browserlayer import utils

        self.assertIn(ISlcXliff, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("slc.xliff")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if slc.xliff is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("slc.xliff"))

    def test_browserlayer_removed(self):
        """Test that ISlcXliff is removed."""
        from slc.xliff.interfaces import ISlcXliff
        from plone.browserlayer import utils

        self.assertNotIn(ISlcXliff, utils.registered_layers())
