# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Archetypes.interfaces import IBaseObject
from Products.ATContentTypes.interface.document import IATDocument
from Products.ATContentTypes.interface.event import IATEvent
from Products.ATContentTypes.interface.link import IATLink
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.topic import IATTopic
from slc.xliff.interfaces import IAttributeExtractor
from slc.xliff.templates.xliff import XLIFF_ATTR_BODY
from slc.xliff.templates.html import HTML_ATTR_BODY
from zope.component import adapts
from zope.interface import implements

from slc.xliff.xliff import logger


class BaseATAttributeExtractor(object):
    """ Adapter to retrieve attributes from a standard Archetypes object.
    """

    implements(IAttributeExtractor)
    adapts(IBaseObject)

    # If you are writing your own Extractor, inherit from this one and simply
    # override the attrs attribute
    attrs = ['title', 'description']

    def __init__(self, context):
        self.context = context

    def get_attrs(self, html_compatibility, source_language):
        context = aq_inner(self.context)
        schema = context.Schema()
        attrs = []

        for key in self.attrs:
            field = schema[key]
            if field.languageIndependent:
                logger.warn(
                    "Exporting language independent attribute %s, "
                    "this may give unexpected results during import such as all "
                    "language versions have the value of the last language set "
                    "in the attribute!" % key)

            value = field.get(context)

            data = dict(id=key,
                        value=value,
                        source_language=source_language)

            if html_compatibility:
                attrs.append(HTML_ATTR_BODY % data)
            else:
                attrs.append(XLIFF_ATTR_BODY % data)

        return attrs


class DocumentAttributeExtractor(BaseATAttributeExtractor):
    """ Adapter to retrieve attributes from a standard document based
    object """
    implements(IAttributeExtractor)
    adapts(IATDocument)
    attrs = ['title', 'description', 'text']


class TopicAttributeExtractor(BaseATAttributeExtractor):
    """ Adapter to retrieve attributes from a standard document based
    object """
    implements(IAttributeExtractor)
    adapts(IATTopic)
    attrs = ['title', 'description', 'text']


class EventAttributeExtractor(BaseATAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based
    object """
    implements(IAttributeExtractor)
    adapts(IATEvent)
    attrs = ['title', 'description', 'location', 'text']


class NewsItemAttributeExtractor(BaseATAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based
    object """
    implements(IAttributeExtractor)
    adapts(IATNewsItem)
    attrs = ['title', 'description', 'imageCaption', 'text']


class LinkAttributeExtractor(BaseATAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based
    object """
    implements(IAttributeExtractor)
    adapts(IATLink)
    attrs = ['title', 'description', 'remoteUrl']
