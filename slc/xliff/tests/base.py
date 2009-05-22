import os, tempfile, zipfile
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from StringIO import StringIO
from Globals import package_home

ztc.installProduct('PloneLanguageTool')
ztc.installProduct('LinguaPlone')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup, PloneSite

@onsetup
def setup_slc_xliff():
    """Set up the additional products required for the XLIFF tool.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
        
    fiveconfigure.debug_mode = True
    import slc.xliff
    zcml.load_config('configure.zcml', slc.xliff)
    fiveconfigure.debug_mode = False
    
    ztc.installPackage('slc.xliff')
    

setup_slc_xliff()
setupPloneSite(products=['slc.xliff'])

class XLIFFTestCase(PloneTestCase):
    """Base class for integration tests for the XLIFF tool.
    """

class XLIFFFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the XLIFF tool.
    """
    def is_zip(self, data):
        """ is_zipfile from zipfile needs to work on a real file object. """
        tmpfilename = tempfile.mktemp(suffix=".zip")
        fh = open(tmpfilename, "wb")
        fh.write(data)
        fh.close()
        is_zip = zipfile.is_zipfile(tmpfilename) and zipfile.ZipFile(tmpfilename, "r")            
        os.remove(tmpfilename)
        return is_zip
