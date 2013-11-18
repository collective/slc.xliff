# -*- coding: utf-8 -*-
import zipfile
import logging
from types import StringType, UnicodeType, FileType, InstanceType

from Acquisition import aq_inner
import HTMLParser

from zope.component import adapts
from zope.interface import implements, Interface
from zope.schema import getFieldsInOrder
from zope.site.hooks import getSite

from plone.app.textfield.interfaces import IRichText, IRichTextValue
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from plone.multilingual.interfaces import ITranslatable
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingualbehavior.interfaces import ILanguageIndependentField

from Products.ATContentTypes.interface.document import IATDocument
from Products.ATContentTypes.interface.event import IATEvent
from Products.ATContentTypes.interface.link import IATLink
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.topic import IATTopic
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

try:
    from slc.seminarportal.interfaces import ISeminar
except ImportError:

    class ISeminar(Interface):
        """ Dummy """

from StringIO import StringIO

from slc.xliff.BeautifulSoup import BeautifulSoup
from slc.xliff.interfaces import IXLIFFExporter, IXLIFFImporter, IXLIFF, \
    IAttributeExtractor

from templates.xliff import XLIFF_HEAD, XLIFF_FILE_BODY, XLIFF_ATTR_BODY
from templates.html import HTML_HEAD, HTML_FILE_BODY, HTML_ATTR_BODY

logger = logging.getLogger('slc.xliff')
html_parser = HTMLParser.HTMLParser()


def get_dx_schema(context):
    schema = dict(getFieldsInOrder(context.getTypeInfo().lookupSchema()))

    behavior_assignable = IBehaviorAssignable(context)
    if behavior_assignable:
        for behavior in behavior_assignable.enumerateBehaviors():
            for k, v in getFieldsInOrder(behavior.interface):
                schema[k] = v

    return schema


class XLIFFImporter(object):
    """ utility to reimport xliff translations and create/edit the respective
    objects """

    implements(IXLIFFImporter)

    def upload(self, data, html_compatibility=False):
        """ write one or more xliff documents from a file or zip onto objects
        """
        # data maybe a zip file or a plain file.
        # A zip may contain one or more files
        # each file may contain one or more file sections
        filelist = []
        filetype = ''
        errors = []
        site = getSite()
        if type(data) in [StringType, UnicodeType]:
            filename = 'direct_upload'
            filelist.append((filename, data))

        elif type(data) in [FileType, InstanceType]:  # Allow Files and StringIO

            filename = getattr(data, 'filename', 'direct_upload')
            dataread = data.read()

            # check what type data is and reject other than text/xml
            # and application/zip
            mtr = getToolByName(site, 'mimetypes_registry')
            mimetype = mtr.classify(dataread)

            if mimetype.major() == 'text':
                filetype = 'plain'
            elif mimetype.major() == 'application' and mimetype.minor() in \
                    ['zip', 'x-zip-compressed']:
                filetype = 'zip'
            else:
                errors.append(('File error', "File type unknown"))
                return errors

            if filetype == 'zip':
                zf = zipfile.ZipFile(data, 'r')
                testzip = zf.testzip()
                if testzip:
                    errors.append(('File error', "Zip file corrupt?"))
                nameList = zf.namelist()
                for i in nameList:
                    content = zf.read(i)
                    if len(content) == 0:
                        continue
                    filelist.append((i, content))

            else:
                filelist.append((filename, dataread))

        else:
            errors.append((
                'TypeError', "The xliff upload content is not of "
                "type plain text or zip."))

        for xliff in filelist:
            soup = BeautifulSoup(xliff[1])
            target_language = _guessLanguage(xliff[0])
            file_sections = soup.findAll('file')
            if soup.findAll('file') == []:
                errors.append((
                    'Empty File?', '%s contains no file sections.'
                    % xliff[0]))
            dbg = 0
            for section in file_sections:
                if dbg == 1:
                    self._setXLIFF(section, target_language=target_language)
                else:
                    try:
                        self._setXLIFF(
                            section, target_language=target_language)
                    except ValueError, ve:
                        errors.append(('Target Object', str(ve)))
                    except Exception, e:
                        errors.append(('General Exception', str(e)))
                        raise e

                # We don't do intermediate commits any more, too many ConflictErrors
                #transaction.commit()

        return errors

    def _setXLIFF(self, data, target_language=''):
        """ Set the data on one object """
        site = getSite()
        uid_catalog = getToolByName(site, 'uid_catalog')

        if target_language == '':
            target_language = data['target-language'].encode('ascii')

        # nothing to do if there is no target language
        if not target_language:
            return

        try:
            oid = data['oid'].encode('ascii')
            results = uid_catalog(UID=oid)
            if len(results) != 1:
                #raise ValueError, "Uid catalog should return exactly one
                #result but returned %s." % len(results)
                raise KeyError, "Invalid OID %s" % oid
            source_ob = results[0].getObject()
        except KeyError:
            # old style xliff file. Using path
            #print "Using path to find target object"
            path = data['original'].encode('utf-8')
            source_ob = site.restrictedTraverse(path, None)

        if source_ob is None:
            raise ValueError(
                "%s not found, can not add translation." % data['original'].encode('utf-8'))

        # If the source object is language-neutral, it must receive a language
        # prior to translation
        # XXXX What to do if the source_ob HAS a language, but it differs
        # from the source-language inside the data?
        if source_ob.Language() == '':
            # Get the source language from the data
            source_language = data.get('source-language')
            # No source language present in the section, use site default
            if not source_language:
                langtool = getToolByName(site, 'portal_languages')
                source_language = langtool.getPreferredLanguage()
            source_ob.setLanguage(source_language)

        tm = ITranslationManager(source_ob)
        if not tm.has_translation(target_language):
            tm.add_translation(target_language)
        target_ob = tm.get_translation(target_language)

        if IBaseObject.providedBy(target_ob):
            # We dont want the id to get renamed to match the title
            target_ob.unmarkCreationFlag()

        values = {}
        for unit in data.findAll('trans-unit'):

            fieldname = unit['id'].encode('utf-8')
            value = unit.find('target').renderContents('utf-8').strip()

            # Note: We don't use xliff to remove values, so no value means no
            # translation and no change to the original
            # XXX: This doesn't handle values other than strings, this may be
            # a problem.
            if not value:
                continue

            # convert HTML entities
            value = safe_unicode(value)
            value = html_parser.unescape(value)
            values[fieldname] = value

        if IDexterityContent.providedBy(target_ob):
            # Dexterity
            schema = get_dx_schema(target_ob)
            for name, field in schema.items():

                if ILanguageIndependentField.providedBy(field):
                    # Copy from the original:
                    field.set(target_ob, field.get(source_ob))
                    pass
                elif name in values:
                    value = values[name]
                    if IRichText.providedBy(field):
                        value = RichTextValue(value)
                    schema[name].set(target_ob, value)

        else:
            # Archetypes
            target_ob.processForm(data=1, metadata=1, values=values)
        # Set the correct format
        if shasattr(source_ob, 'text_format'):
            target_ob.setFormat(source_ob.text_format)


class XLIFFExporter(object):
    """ Adapter to generate an xliff representation from a content object """

    implements(IXLIFFExporter)

    recursive = False
    single_file = True
    html_compatibility = False
    zip = False
    source_language = "en"
    export_shoppinglist = False
    shoppinglist = list()

    def __init__(self, context):
        self.context = context

    def _getObjectsFromShoppinglist(self):
        context = aq_inner(self.context)
        all_obs = set()

        catalog = getToolByName(context, 'portal_catalog')
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        sl = member.getProperty('shoppinglist', tuple())
        object_provides = "plone.multilingual.interfaces.ITranslatable"

        results = catalog(UID=sl, object_provides=object_provides)
        SLOBs = [r.getObject() for r in results]

        for ob in SLOBs:
            all_obs.add(ob)
            # recursive
            if self.recursive is True and ob.isPrincipiaFolderish:
                [all_obs.add(x) for x in self._getObjectsByPath(ob)]

        return list(all_obs)

    def _getObjectsByPath(self, ob=None):
        catalog = getToolByName(self.context, 'portal_catalog')
        if ob is None:
            ob = aq_inner(self.context)
        if not ob.isPrincipiaFolderish:
            # context is not a folder but we should work recursive
            # => use parent folder
            path = "/".join(ob.getPhysicalPath()[:-1])
        else:
            path = "/".join(ob.getPhysicalPath())

        object_provides = "plone.multilingual.interfaces.ITranslatable"
        results = catalog(path=path, object_provides=object_provides)
        # make a real list out the LazyMap
        results = list(results)
        # sort by path, so that top-level object will get translated first
        results.sort(lambda x, y: cmp(len(x.getPath()), len(y.getPath())))

        return [r.getObject() for r in results]

    def export(self):
        if self.export_shoppinglist is True:
            objects = self._getObjectsFromShoppinglist()
        elif self.recursive is True:
            objects = self._getObjectsByPath()
        else:
            objects = [self.context]

        if self.html_compatibility:
            HEAD = HTML_HEAD
        else:
            HEAD = XLIFF_HEAD

        xliff_pages = []

        for ob in objects:
            # Make extra sure the object is translatable. The multilingual
            # behavior for this type might have been deactivated without reindexing
            # all instances of this type.
            if not ITranslatable.providedBy(ob):
                continue
            xob = IXLIFF(ob)
            xliff_pages.append((
                "/".join(ob.getPhysicalPath()),
                xob.render(self.html_compatibility, self.source_language),))

        if self.zip is True:
            Z = StringIO()
            zf = zipfile.ZipFile(Z, 'w')

            if self.single_file is True:    # single file as zip
                if len(xliff_pages) == 1:
                    zf.writestr(
                        xliff_pages[0][0], HEAD % dict(content=xliff_pages[0][1]))
                else:
                    data = [x[1] for x in xliff_pages]
                    zf.writestr(
                        'export.xliff', HEAD % dict(content="\n".join(data)))

            # multiple files as zip
            else:
                for page in xliff_pages:
                    zf.writestr(page[0], HEAD % dict(content=page[1]))

            zf.close()
            Z.seek(0)
            content = Z.read()
            Z.close()

        else:
            # files as plain, so we need to join them to single_file.
            # one or more files to be returned directly, so we don't need
            # the filenames
            content = [x[1] for x in xliff_pages]
            content = "\n".join(content)
            content = HEAD % dict(content=content)
            # Set that as it has been selected implicitly by specifying
            # multiple files but not selecting zip
            self.single_file = True

        return content


class XLIFF(object):
    """ """

    adapts(ITranslatable)
    implements(IXLIFF)

    def __init__(self, context):
        self.context = context

    def render(self, html_compatibility, source_language):
        context = aq_inner(self.context)

        # lookup adapter
        adapter = IAttributeExtractor(context)
        attrs = adapter.get_attrs(html_compatibility, source_language)

        data = dict(original="/".join(context.getPhysicalPath()),
                    oid=context.UID(),
                    source_language=source_language,
                    attrs="\n".join(attrs),)

        if html_compatibility:
            filedata = HTML_FILE_BODY % data
        else:
            filedata = XLIFF_FILE_BODY % data

        return filedata


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


def _guessLanguage(filename):
    """
    try to find a language abbreviation in the string
    acceptable is a two letter language abbreviation at the start of the
    string followed by an _
    or at the end of the string prefixed by an _ just before the extension
    """

    def findAbbrev(id):
        if len(id) > 3 and id[2] in ['_', '-']:
            lang = id[0:2].lower()
            if lang in langs:
                return lang
        if len(id) > 3 and '.' in id:
            elems = id.split('.')
            filename = ".".join(elems[:-1])
            if len(filename) > 3 and filename[-3] in ['_', '-']:
                lang = filename[-2:].strip().lower()
                if lang in langs:
                    return lang
            elif len(filename) == 2:
                lang = filename
                if lang in langs:
                    return lang

    site = getSite()
    portal_languages = getToolByName(site, 'portal_languages')
    langs = portal_languages.getSupportedLanguages()

    langbyfilename = findAbbrev(filename)
    if langbyfilename in langs:
        return langbyfilename

    return ''


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


class SeminarAttributeExtractor(BaseATAttributeExtractor):
    """ Adapter to retrieve attributes from a seminar """
    implements(IAttributeExtractor)
    adapts(ISeminar)
    attrs = [
        'title', 'description', 'location', 'summary', 'conclusions', 'furtherActions']


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
            if isinstance(value, unicode):
                value = value.encode('UTF-8')
            elif IRichTextValue.providedBy(value):
                value = value.raw

            data = dict(id=key,
                        value=value,
                        source_language=source_language)

            if html_compatibility:
                attrs.append(HTML_ATTR_BODY % data)
            else:
                attrs.append(XLIFF_ATTR_BODY % data)

        return attrs
