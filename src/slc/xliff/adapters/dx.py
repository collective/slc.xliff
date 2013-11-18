# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from plone.dexterity.interfaces import IDexterityContent
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.interfaces import ILink
from plone.app.textfield.interfaces import IRichTextValue
from plone.multilingualbehavior.interfaces import ILanguageIndependentField
from slc.xliff.interfaces import IAttributeExtractor
from slc.xliff.xliff import get_dx_schema
from slc.xliff.templates.xliff import XLIFF_ATTR_BODY
from slc.xliff.templates.html import HTML_ATTR_BODY
from zope.component import adapts
from zope.interface import implements

from slc.xliff.xliff import logger


class BaseDXAttributeExtractor(object):
    """ Adapter to retrieve attributes from a standard Dexterity object.
    """

    implements(IAttributeExtractor)
    adapts(IDexterityContent)

    # If you are writing your own Extractor, inherit from this one and simply
    # override the attrs attribute
    attrs = ['title', 'description']

    def __init__(self, context):
        self.context = aq_inner(context)

    def get_attrs(self, html_compatibility, source_language):

        schema = get_dx_schema(self.context)
        attrs = []

        for key in self.attrs:
            field = schema[key]
            if ILanguageIndependentField.providedBy(field):
                logger.warn(
                    "Exporting language independent attribute %s, "
                    "this may give unexpected results during import such as all "
                    "language versions have the value of the last language set "
                    "in the attribute!" % key)

            value = field.get(self.context)
            if IRichTextValue.providedBy(value):
                value = value.raw
            if isinstance(value, unicode):
                value = value.encode('UTF-8')

            data = dict(id=key,
                        value=value,
                        source_language=source_language)

            if html_compatibility:
                attrs.append(HTML_ATTR_BODY % data)
            else:
                attrs.append(XLIFF_ATTR_BODY % data)

        return attrs


class DocumentAttributeExtractor(BaseDXAttributeExtractor):
    """ Adapter to retrieve attributes from a standard document based
    object """
    implements(IAttributeExtractor)
    adapts(IDocument)
    attrs = ['title', 'description', 'text']


class TopicAttributeExtractor(BaseDXAttributeExtractor):
    """ Adapter to retrieve attributes from a standard document based
    object """
    implements(IAttributeExtractor)
    adapts(ICollection)
    attrs = ['title', 'description', 'text']


class EventAttributeExtractor(BaseDXAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based
    object """
    implements(IAttributeExtractor)
    adapts(IEvent)
    attrs = ['title', 'description', 'location', 'text']


class NewsItemAttributeExtractor(BaseDXAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based
    object """
    implements(IAttributeExtractor)
    adapts(INewsItem)
    attrs = ['title', 'description', 'imageCaption', 'text']


class LinkAttributeExtractor(BaseDXAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based
    object """
    implements(IAttributeExtractor)
    adapts(ILink)
    attrs = ['title', 'description', 'remoteUrl']
