from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides

from plone.app.textfield import RichText
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.supermodel import model

from slc.xliff import XliffMessageFactory as _
from slc.xliff.adapters.dx import BaseDXAttributeExtractor


class ITestContent(model.Schema):

    text = RichText(
        title=_("Text"),
        required=False,
    )

    language_independent = schema.TextLine(
        title=_(u"Language Independent"),
        required=False,
    )

alsoProvides(ITestContent['language_independent'], ILanguageIndependentField)


class TestContentExtractor(BaseDXAttributeExtractor):
    adapts(ITestContent)
    attrs = ['title', 'description', 'text']
