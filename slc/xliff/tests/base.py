import os, tempfile, zipfile
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from StringIO import StringIO
from Globals import package_home


# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup, PloneSite
from Products.PloneTestCase import layer
from Testing import ZopeTestCase as ztc
from Products.Five import fiveconfigure, zcml


SiteLayer = layer.PloneSite

class XLIFFLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        """Set up additional products and ZCML required to test this product.
        """
        ztc.installProduct('PloneLanguageTool')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('ZCatalog')
        fiveconfigure.debug_mode = True
        import slc.xliff
        zcml.load_config('configure.zcml', slc.xliff)
        fiveconfigure.debug_mode = False

        ztc.installPackage('slc.xliff')
        setupPloneSite(products=['slc.xliff'])
        SiteLayer.setUp()

class XLIFFTestCase(PloneTestCase):
    """Base class for integration tests for the XLIFF tool.
    """
    layer = XLIFFLayer

class XLIFFFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the XLIFF tool.
    """
    layer = XLIFFLayer
    def is_zip(self, data):
        """ is_zipfile from zipfile needs to work on a real file object. """
        tmpfilename = tempfile.mktemp(suffix=".zip")
        fh = open(tmpfilename, "wb")
        fh.write(data)
        fh.close()
        is_zip = zipfile.is_zipfile(tmpfilename) and zipfile.ZipFile(tmpfilename, "r")
        os.remove(tmpfilename)
        return is_zip
