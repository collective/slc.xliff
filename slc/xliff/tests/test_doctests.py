import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from slc.xliff.tests import base

def test_suite():
    return unittest.TestSuite([

        # Demonstrate the usage
        ztc.ZopeDocFileSuite(
            'doc/export.txt', package='slc.xliff',
            test_class=base.XLIFFFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ztc.ZopeDocFileSuite(
            'doc/import.txt', package='slc.xliff',
            test_class=base.XLIFFFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
