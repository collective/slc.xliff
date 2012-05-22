# -*- coding: utf-8 -*-
"""Setup for doctest functional tests."""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing import layered
from plone.testing.z2 import Browser
from slc.xliff.tests.base import FUNCTIONAL_TESTING

import doctest
import manuel.codeblock
import manuel.doctest
import manuel.testing
import transaction
import unittest2 as unittest

import os
import tempfile
import zipfile


FLAGS = (doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS |
         doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE)


def is_zip(data):
    """ is_zipfile from zipfile needs to work on a real file object. """
    tmpfilename = tempfile.mktemp(suffix=".zip")
    fh = open(tmpfilename, "wb")
    fh.write(data)
    fh.close()
    is_zip = (zipfile.is_zipfile(tmpfilename) and
              zipfile.ZipFile(tmpfilename, "r"))
    os.remove(tmpfilename)
    return is_zip


def setUp(self):
    layer = self.globs['layer']

    # Update global variables within the tests.
    self.globs.update({
        'portal': layer['portal'],
        'folder': layer['portal'].folder,
        'browser': Browser(layer['app']),
        'is_zip': is_zip,
        'TEST_USER_NAME': TEST_USER_NAME,
        'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
    })

    portal = self.globs['portal']
    browser = self.globs['browser']
    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()
    setRoles(portal, TEST_USER_ID, ['Manager'])
    transaction.commit()


def DocFileSuite(testfile, flags=FLAGS, setUp=setUp, layer=FUNCTIONAL_TESTING):
    m = manuel.doctest.Manuel(optionflags=flags)
    m += manuel.codeblock.Manuel()

    return layered(
        manuel.testing.TestSuite(m, testfile, setUp=setUp,
            globs=dict(layer=layer)),
        layer=layer)


def test_suite():
    return unittest.TestSuite([
        DocFileSuite('../doc/import.txt'),
        DocFileSuite('../doc/export.txt'),
        ])
