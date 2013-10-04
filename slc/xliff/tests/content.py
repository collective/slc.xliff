from zope import schema
from zope.component import adapts

from plone.app.textfield import RichText
from plone.multilingualbehavior import directives
from plone.supermodel import model

from slc.xliff import XliffMessageFactory as _
from slc.xliff.xliff import BaseDXAttributeExtractor

class ITestContent(model.Schema):

    text = RichText(
        title=_("Text"),
        required=False,
    )

    language_independent = schema.TextLine(
        title=_(u"Language Independent"),
        required=False,
    )
    directives.languageindependent('language_independent')

class TestContentExtractor(BaseDXAttributeExtractor):
    adapts(ITestContent)
    attrs = ['title', 'description', 'text', 'language_independent']
    