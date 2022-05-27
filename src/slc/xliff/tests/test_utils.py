# -*- coding: utf-8 -*-
import unittest

from plone import api
from slc.xliff.tests.base import INTEGRATION_TESTING
from slc.xliff.xliff import _guessLanguage


class TestUtils(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def test_guessLanguage_language_at_the_start(self):
        """test the language at the start of the filename is catched correctly"""
        filename = "es_filename.xliff"
        self.assertEqual(_guessLanguage(filename), "es")

    def test_guessLanguage_language_at_the_end(self):
        """test the language at the end of the filename is catched correctly"""
        filename = "filename_es.xliff"
        self.assertEqual(_guessLanguage(filename), "es")

    def test_guessLanguage_language_in_the_middle(self):
        """test the language in the middle of the filename is catched correctly"""
        filename = "filename_es_filename.xliff"
        self.assertEqual(_guessLanguage(filename), "es")

    def test_guessLanguage_language_variant_at_the_start(self):
        """test the language at the start of the filename is catched correctly"""
        filename = "pt-br_filename.xliff"
        self.assertEqual(_guessLanguage(filename), "pt-br")

    def test_guessLanguage_language_variant_at_the_end(self):
        """test the language at the end of the filename is catched correctly"""
        filename = "filename_pt-br.xliff"
        self.assertEqual(_guessLanguage(filename), "pt-br")

    def test_guessLanguage_language_variant_in_the_middle(self):
        """test the language in the middle of the filename is catched correctly"""
        filename = "filename_pt-br_filename.xliff"
        self.assertEqual(_guessLanguage(filename), "pt-br")

    def test_guessLanguage_without_language(self):
        """test that a filename without language code returns an empty string"""
        filename = "filename_mixed.xliff"
        self.assertEqual(_guessLanguage(filename), "")

    def test_unexisting_language(self):
        """test that a filename with an unexisting language is ignored"""
        inexisting_language = "fr"
        filename = "filename_{0}.xliff".format(inexisting_language)
        supported_languages = api.portal.get_tool(
            "portal_languages"
        ).getSupportedLanguages()
        self.assertNotIn(inexisting_language, supported_languages)

        self.assertEqual(_guessLanguage(filename), "")
