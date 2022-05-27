# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield.interfaces import IRichTextValue
from plone.dexterity.interfaces import IDexterityContent
from slc.xliff.interfaces import IAttributeExtractor
from slc.xliff.templates.html import HTML_ATTR_BODY
from slc.xliff.templates.xliff import XLIFF_ATTR_BODY
from slc.xliff.xliff import get_dx_schema
from slc.xliff.xliff import logger
from zope.component import adapter
from zope.interface import implementer


@implementer(IAttributeExtractor)
@adapter(IDexterityContent)
class BaseDXAttributeExtractor(object):
    """Adapter to retrieve attributes from a standard Dexterity object."""

    # If you are writing your own Extractor, inherit from this one and simply
    # override the attrs attribute
    attrs = ["title", "description"]

    def __init__(self, context):
        self.context = aq_inner(context)

    def get_attrs(self, html_compatibility, source_language):

        schema = get_dx_schema(self.context)
        attrs = []

        for key in self.attrs:
            field = schema[key]
            if ILanguageIndependentField.providedBy(field):
                logger.warn(
                    "Exporting language independent attribute %s, this may"
                    " give unexpected results during import such as all"
                    " language versions have the value of the last language"
                    " set in the attribute!",
                    key,
                )

            value = field.get(self.context)
            if IRichTextValue.providedBy(value):
                if value.raw is None:
                    value = ""
                else:
                    value = value.raw
            if isinstance(value, bytes):
                value = value.decode("UTF-8")

            data = dict(id=key, value=value, source_language=source_language)

            if html_compatibility:
                attrs.append(HTML_ATTR_BODY.format(**data))
            else:
                attrs.append(XLIFF_ATTR_BODY.format(**data))

        return attrs


@implementer(IAttributeExtractor)
@adapter(IDocument)
class DocumentAttributeExtractor(BaseDXAttributeExtractor):
    """Adapter to retrieve attributes from a standard document based
    object"""

    attrs = ["title", "description", "text"]


@implementer(IAttributeExtractor)
@adapter(ICollection)
class TopicAttributeExtractor(BaseDXAttributeExtractor):
    """Adapter to retrieve attributes from a standard document based
    object"""

    attrs = ["title", "description", "text"]


@implementer(IAttributeExtractor)
@adapter(IEvent)
class EventAttributeExtractor(BaseDXAttributeExtractor):
    """Adapter to retrieve attributes from a standard event based
    object"""

    attrs = ["title", "description", "location", "text"]


@implementer(IAttributeExtractor)
@adapter(INewsItem)
class NewsItemAttributeExtractor(BaseDXAttributeExtractor):
    """Adapter to retrieve attributes from a standard event based
    object"""

    attrs = ["title", "description", "image_caption", "text"]


@implementer(IAttributeExtractor)
@adapter(ILink)
class LinkAttributeExtractor(BaseDXAttributeExtractor):
    """Adapter to retrieve attributes from a standard event based
    object"""

    attrs = ["title", "description", "remoteUrl"]
