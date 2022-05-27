# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from bs4 import BeautifulSoup
from bs4 import NavigableString
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedFile
from slc.xliff.interfaces import IXLIFFExporter
from slc.xliff.interfaces import IXLIFFImporter
from slc.xliff.tests.base import FUNCTIONAL_TESTING
from slc.xliff.tests.base import INTEGRATION_TESTING
from zope.component import getUtility
from zipfile import ZipFile
from tempfile import mktemp

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


def prepare_contents_in_language(soup, lang="de", lang_name="german"):
    """helper function to create an xliff file with contents translated in the
    given translation with dummy texts showing the language
    """

    new_title = NavigableString("My {0} Title".format(lang_name))
    soup.find("trans-unit", attrs={"id": "title"}).findNext("target").append(
        new_title
    )
    new_description = NavigableString("My {0} Description".format(lang_name))
    soup.find("trans-unit", attrs={"id": "description"}).findNext(
        "target"
    ).append(new_description)
    new_text = NavigableString("<p>My {0} Text</p>".format(lang_name))
    soup.find("trans-unit", attrs={"id": "text"}).findNext("target").append(
        new_text
    )
    xliffstr = soup.prettify()
    xliffstr = xliffstr.replace(
        '<target xml:lang="en">', '<target xml:lang="{0}">'.format(lang)
    )
    xliffstr = xliffstr.replace(
        'target-language=""', 'target-language="{0}"'.format(lang)
    )

    return xliffstr


class TestXliffExport(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.doc_en = createContentInContainer(
            self.portal["en"],
            "test_content",
            checkConstraints=False,
            id="doc_en",
            title="My english title",
            description="My english description",
        )
        self.doc_en.text = RichTextValue("<p>My english text</p>")

    def test_create_xliff_representation_links_to_object(self):
        xliffexporter = IXLIFFExporter(self.doc_en)
        xliffexporter.recursive = False
        xliffexporter.single_file = True
        xliffexporter.html_compatibility = False
        xliffexporter.zip = False
        xliffexporter.source_language = "en"
        data = xliffexporter.export()
        soup = BeautifulSoup(data)

        self.assertEqual(soup.findAll("file")[0]["oid"], self.doc_en.UID())

    def test_all_attributes_are_in_the_xliff_file(self):
        xliffexporter = IXLIFFExporter(self.doc_en)
        xliffexporter.recursive = False
        xliffexporter.single_file = True
        xliffexporter.html_compatibility = False
        xliffexporter.zip = False
        xliffexporter.source_language = "en"
        data = xliffexporter.export()
        soup = BeautifulSoup(data)
        file_attributes = [x["id"] for x in soup.findAll("trans-unit")]
        self.assertIn("title", file_attributes)
        self.assertIn("description", file_attributes)
        self.assertIn("text", file_attributes)


class TestXliffImport(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.doc_en = createContentInContainer(
            self.portal["en"],
            "test_content",
            checkConstraints=False,
            id="doc_en",
            title="My english title",
            description="My english description",
        )

        self.doc_en.text = RichTextValue("<p>My english text</p>")
        self.doc_en.language_independent = "This should not change."

        import transaction

        transaction.commit()

    def test_upload_single_content(self):
        """We export the XLIFF file, change some contents and upload it to create
        the translated content
        """

        xliffexporter = IXLIFFExporter(self.doc_en)
        xliffexporter.recursive = False
        xliffexporter.single_file = True
        xliffexporter.html_compatibility = False
        xliffexporter.zip = False
        xliffexporter.source_language = self.doc_en.Language()
        xliffstr = xliffexporter.export()
        soup = BeautifulSoup(xliffstr, "xml")

        xliffstr_de = prepare_contents_in_language(soup, "de", "german")

        xliffimporter = getUtility(IXLIFFImporter)
        xliff_file = NamedFile(
            data=xliffstr_de,
            contentType="text/xml",
            filename=u"transl_de.xliff",
        )

        xliffimporter.upload(xliff_file, html_compatibility=False)

        doc_de = ITranslationManager(self.doc_en).get_translation("de")

        self.assertIsNotNone(doc_de)
        self.assertEqual(doc_de.Title(), "My german Title")
        self.assertIn("My german Description", doc_de.Description())
        self.assertEqual(doc_de.text.output, "<p>My german Text</p>")
        self.assertEqual(
            doc_de.language_independent, "This should not change."
        )

    def test_upload_multiple_contents(self):
        """create contents in spanish and finish and upload as it was a single file"""
        xliffexporter = IXLIFFExporter(self.doc_en)
        xliffexporter.recursive = False
        xliffexporter.single_file = True
        xliffexporter.html_compatibility = False
        xliffexporter.zip = False
        xliffexporter.source_language = self.doc_en.Language()
        xliffstr = xliffexporter.export()

        soup_es = BeautifulSoup(xliffstr, "xml")
        xliffstr_es = prepare_contents_in_language(soup_es, "es", "spanish")

        soup_fi = BeautifulSoup(xliffstr, "xml")
        xliffstr_fi = prepare_contents_in_language(soup_fi, "fi", "finnish")

        xliffstr_translations = xliffstr_es + xliffstr_fi

        xliffimporter = getUtility(IXLIFFImporter)
        xliff_file = NamedFile(
            data=xliffstr_translations,
            contentType="text/xml",
            filename=u"transl_mixed.xliff",
        )

        xliffimporter.upload(xliff_file, html_compatibility=False)

        doc_es = ITranslationManager(self.doc_en).get_translation("es")

        self.assertIsNotNone(doc_es)
        self.assertEqual(doc_es.Title(), "My spanish Title")
        self.assertIn("My spanish Description", doc_es.Description())
        self.assertEqual(doc_es.text.output, "<p>My spanish Text</p>")
        self.assertEqual(
            doc_es.language_independent, "This should not change."
        )

        doc_fi = ITranslationManager(self.doc_en).get_translation("fi")

        self.assertIsNotNone(doc_fi)
        self.assertEqual(doc_fi.Title(), "My finnish Title")
        self.assertIn("My finnish Description", doc_fi.Description())
        self.assertEqual(doc_fi.text.output, "<p>My finnish Text</p>")
        self.assertEqual(
            doc_fi.language_independent, "This should not change."
        )

    def test_upload_zipfile(self):
        xliffexporter = IXLIFFExporter(self.doc_en)
        xliffexporter.recursive = False
        xliffexporter.single_file = True
        xliffexporter.html_compatibility = False
        xliffexporter.zip = False
        xliffexporter.source_language = self.doc_en.Language()
        xliffstr = xliffexporter.export()

        soup_es = BeautifulSoup(xliffstr, "xml")
        xliffstr_es = prepare_contents_in_language(
            soup_es, "es", u"spanish zipped"
        )

        soup_fi = BeautifulSoup(xliffstr, "xml")
        xliffstr_fi = prepare_contents_in_language(
            soup_fi, "fi", u"finnish zipped"
        )

        tempfilename = mktemp(suffix=".zip")
        with open(tempfilename, "wb") as out:
            zf = ZipFile(out, "w")
            zf.writestr("spanish.xliff", xliffstr_es)
            zf.writestr("finnish.xliff", xliffstr_fi)
            zf.close()

        with open(tempfilename, "rb") as out:
            xliffimporter = getUtility(IXLIFFImporter)
            zip_file = NamedFile(
                data=out,
                contentType="application/zip",
                filename=u"transl_mixed.zip",
            )
            xliffimporter.upload(zip_file, html_compatibility=False)
            doc_es = ITranslationManager(self.doc_en).get_translation("es")
            self.assertEqual(doc_es.Title(), "My spanish zipped Title")

            doc_fi = ITranslationManager(self.doc_en).get_translation("fi")
            self.assertEqual(doc_fi.Title(), "My finnish zipped Title")
