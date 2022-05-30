# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from bs4 import BeautifulSoup
from plone import api
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from io import BytesIO
from slc.xliff.interfaces import IAttributeExtractor
from slc.xliff.interfaces import IXLIFF
from slc.xliff.interfaces import IXLIFFExporter
from slc.xliff.interfaces import IXLIFFImporter
from slc.xliff.templates.html import HTML_FILE_BODY
from slc.xliff.templates.html import HTML_HEAD
from slc.xliff.templates.xliff import XLIFF_FILE_BODY
from slc.xliff.templates.xliff import XLIFF_HEAD
from zope.component import adapter
from zope.interface import implementer
from zope.schema import getFieldsInOrder
from zope.site.hooks import getSite
from html import unescape
from html.parser import HTMLParser

import logging
import re
import zipfile


logger = logging.getLogger("slc.xliff")
html_parser = HTMLParser()


def get_dx_schema(context):
    schema = dict(getFieldsInOrder(context.getTypeInfo().lookupSchema()))

    behavior_assignable = IBehaviorAssignable(context)
    if behavior_assignable:
        for behavior in behavior_assignable.enumerateBehaviors():
            for k, v in getFieldsInOrder(behavior.interface):
                schema[k] = v

    return schema


@implementer(IXLIFFImporter)
class XLIFFImporter(object):
    """utility to reimport xliff translations and create/edit the respective
    objects"""

    def upload(self, xliff_file, html_compatibility=False, request=None):
        """write one or more xliff documents from a file or zip onto objects"""
        self.request = request
        # data maybe a zip file or a plain file.
        # A zip may contain one or more files
        # each file may contain one or more file sections
        filelist = []
        filetype = ""
        errors = []
        self.total = 0
        self.new_translations = 0
        filename = xliff_file.filename
        data = xliff_file.data

        major, minor = xliff_file.contentType.split("/")
        if major == "text":
            filetype = "plain"
        elif major == "application" and minor in ["zip", "x-zip-compressed"]:
            filetype = "zip"
        else:
            errors.append(("File error", "File type unknown"))
            return errors

        if filetype == "zip":
            Z = BytesIO()
            Z.write(data)
            zf = zipfile.ZipFile(Z, "r")
            testzip = zf.testzip()
            if testzip:
                errors.append(("File error", "Zip file corrupt?"))
            nameList = zf.namelist()
            for i in nameList:
                content = zf.read(i)
                if len(content) == 0:
                    continue
                filelist.append((i, content))
            zf.close()
            Z.close()

        else:
            filelist.append((filename, data))

        for xliff in filelist:
            soup = BeautifulSoup(xliff[1])
            target_language = _guessLanguage(xliff[0])
            if target_language and self.request is not None:
                msg = u"Detected language from file name: {0}".format(
                    target_language
                )
                IStatusMessage(self.request).addStatusMessage(msg, type="info")
            file_sections = soup.findAll("file")
            if soup.findAll("file") == []:
                errors.append(
                    (
                        "Empty File?",
                        "{0} contains no file sections.".format(xliff[0]),
                    )
                )

            for section in file_sections:
                if api.env.debug_mode():
                    self._setXLIFF(section, target_language=target_language)
                else:
                    try:
                        self._setXLIFF(
                            section, target_language=target_language
                        )
                    except ValueError as ve:
                        errors.append(("Target Object", str(ve)))
                    except Exception as e:
                        errors.append(("General Exception", str(e)))
                        raise e

                # We don't do intermediate commits any more, too many ConflictErrors
                # transaction.commit()
            if self.request is not None:
                msg = (
                    u"Handled a total of {0} files, of which {1} were new"
                    u" translations".format(self.total, self.new_translations)
                )
                IStatusMessage(self.request).addStatusMessage(msg, type="info")
        return errors

    def _setXLIFF(self, data, target_language=""):
        """Set the data on one object"""
        site = getSite()
        portal_catalog = getToolByName(site, "portal_catalog")

        if target_language == "":
            target_language = data["target-language"]

        # nothing to do if there is no target language
        if not target_language:
            return

        try:
            oid = data["oid"]
            results = portal_catalog(UID=oid)
            if len(results) != 1:
                # raise ValueError, "Uid catalog should return exactly one
                # result but returned %s." % len(results)
                raise KeyError("Invalid OID {0}".format(oid))
            source_ob = results[0].getObject()
        except KeyError:
            # old style xliff file. Using path
            # print "Using path to find target object"
            path = data["original"]
            source_ob = site.restrictedTraverse(path, None)

        if source_ob is None:
            raise ValueError(
                "{0} not found, can not add translation.".format(
                    data["original"]
                )
            )

        # If the source object is language-neutral, it must receive a language
        # prior to translation
        # XXXX What to do if the source_ob HAS a language, but it differs
        # from the source-language inside the data?
        if source_ob.Language() == "":
            # Get the source language from the data
            source_language = data.get("source-language")
            # No source language present in the section, use site default
            if not source_language:
                langtool = getToolByName(site, "portal_languages")
                source_language = langtool.getPreferredLanguage()
            source_ob.setLanguage(source_language)

        tm = ITranslationManager(source_ob)
        if not tm.has_translation(target_language):
            tm.add_translation(target_language)
            self.new_translations += 1
        target_ob = tm.get_translation(target_language)

        values = {}

        for unit in data.findAll("trans-unit"):

            fieldname = unit["id"]
            value = unit.find("target").renderContents("utf-8").strip()

            # Note: We don't use xliff to remove values, so no value means no
            # translation and no change to the original
            # XXX: This doesn't handle values other than strings, this may be
            # a problem.
            if not value:
                continue

            # convert HTML entities
            value = safe_unicode(value)
            value = unescape(value)
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
                        it = getattr(source_ob, name)
                        if it is not None:
                            mimeType = it.mimeType
                            outputMimeType = it.outputMimeType
                        else:
                            # Default
                            mimeType = "text/html"
                            outputMimeType = "text/x-html-safe"
                        value = RichTextValue(value, mimeType, outputMimeType)
                    schema[name].set(target_ob, value)

        self.total += 1


@implementer(IXLIFFExporter)
class XLIFFExporter(object):
    """Adapter to generate an xliff representation from a content object"""

    recursive = False
    single_file = True
    html_compatibility = False
    zip = False
    source_language = "en"

    def __init__(self, context):
        self.context = context

    def _getObjectsByPath(self, ob=None):
        catalog = getToolByName(self.context, "portal_catalog")
        if ob is None:
            ob = aq_inner(self.context)
        if not ob.isPrincipiaFolderish:
            # context is not a folder but we should work recursive
            # => use parent folder
            path = "/".join(ob.getPhysicalPath()[:-1])
        else:
            path = "/".join(ob.getPhysicalPath())

        object_provides = "plone.app.multilingual.interfaces.ITranslatable"
        results = catalog(path=path, object_provides=object_provides)
        # make a real list out the LazyMap
        results = list(results)
        # sort by path, so that top-level object will get translated first

        results.sort(key=lambda x: len(x.getPath().split("/")))

        return [r.getObject() for r in results]

    def export(self):
        if self.recursive is True:
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
            xliff_pages.append(
                (
                    "/".join(ob.getPhysicalPath()),
                    xob.render(self.html_compatibility, self.source_language),
                )
            )

        if self.zip is True:
            Z = BytesIO()
            zf = zipfile.ZipFile(Z, "w")

            if self.single_file is True:  # single file as zip
                if len(xliff_pages) == 1:
                    zf.writestr(
                        "{0}.xliff".format(xliff_pages[0][0]),
                        HEAD.format(content=xliff_pages[0][1]),
                    )
                else:
                    data = [x[1] for x in xliff_pages]
                    zf.writestr(
                        "export.xliff", HEAD.format(content="\n".join(data))
                    )

            # multiple files as zip
            else:
                for page in xliff_pages:
                    zf.writestr(
                        "{0}.xliff".format(page[0]),
                        HEAD.format(content=page[1]),
                    )

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
            content = HEAD.format(content=content)
            # Set that as it has been selected implicitly by specifying
            # multiple files but not selecting zip
            self.single_file = True

        return content


@adapter(ITranslatable)
@implementer(IXLIFF)
class XLIFF(object):
    """ """

    def __init__(self, context):
        self.context = context

    def render(self, html_compatibility, source_language):
        context = aq_inner(self.context)

        # lookup adapter
        adapter = IAttributeExtractor(context)
        attrs = adapter.get_attrs(html_compatibility, source_language)

        data = dict(
            original="/".join(context.getPhysicalPath()),
            oid=context.UID(),
            source_language=source_language,
            attrs="\n".join(attrs),
        )

        if html_compatibility:
            filedata = HTML_FILE_BODY.format(**data)
        else:
            filedata = XLIFF_FILE_BODY.format(**data)

        return filedata


def _guessLanguage(filename):
    """
    try to find a language abbreviation in the string
    acceptable is a language abbreviation at the start of the
    string followed by an _
    or at the end of the string prefixed by an _ just before the extension
    or preceded and followed by an _

    This method handles language variant codes such as pt-br too
    """
    site = getSite()
    portal_languages = getToolByName(site, "portal_languages")
    langs = portal_languages.getSupportedLanguages()

    regex = r"^..-..$|^..$"
    delimiters = [" ", ".", "_"]

    for delim in delimiters:
        filename = filename.replace(delim, " ")
    pieces = filename.split()

    for piece in pieces:
        match = re.findall(regex, piece)
        if match:
            lang = match[0]
            if lang in langs:
                return lang

    return ""
