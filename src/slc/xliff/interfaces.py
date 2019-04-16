# -*- coding: utf-8 -*-
from plone.namedfile.field import NamedFile
from zope.interface import Interface
from zope import schema
from slc.xliff import XliffMessageFactory as _
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ISlcXliff(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IExportParams(Interface):
    """ Management form to export xliff """

    recursive = schema.Bool(
        title=u'Recursive subtree export?',
        description=_(
            u'Use this if you want to export everything below that '
            u'folder. If you use the recursive option, you can restrict your '
            u'export by specifying additional constraints below.'),
        required=False,
        default=False,
    )

    single_file = schema.Bool(
        title=u'Generate a single file?',
        description=_(u'Use this if you want to export everything in one file.'),
        required=False,
        default=True,
    )

    zip = schema.Bool(
        title=u'Download as zip?',
        description=_(u'Use this if you want to download the export as zip file.'),
        required=False,
        default=True,
    )

    html_compatibility = schema.Bool(
        title=u'HTML compatibility mode',
        description=_(u'Use this if you want an HTML-ish export that can be read by HTML editors.'),
        required=False,
        default=False,
    )


class IImportParams(Interface):
    """ Management form to import xliff """

    html_compatibility = schema.Bool(
        title=u'HTML compatibility mode',
        description=_(
            u'Select this option if your files are messed up with HTML code '
            u'in between due to incorrect XLIFF file handling by the '
            u'translators.'),
        required=False,
        default=False,
    )

    xliff_file = NamedFile(title=u'Xliff file (plain or zip)', required=True)


class IXLIFFExporter(Interface):
    """ An Adapter that can create an xliff representation from objects
    """

    def export():
        """ generate the xliff representation of this object
        """


class IXLIFFImporter(Interface):
    """ An Utility that can set xliff translations onto objects
    """

    def upload(data, html_compatibility=False):
        """ write one or more xliff documents from a file or zip onto objects
        """


class IXLIFF(Interface):
    """ render an objects xliff representation
    """

    def render():
        """ render an objects xliff representation
        """

    def set_translation(attrs):
        """ set translated attributes
        """


class IAttributeExtractor(Interface):
    """ Extracts attributes to translate from a given object """
