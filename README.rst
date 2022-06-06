slc.xliff Package Readme
************************

.. image:: https://img.shields.io/pypi/v/slc.xliff.svg
        :target: https://pypi.org/project/slc.xliff/

.. image:: https://github.com/collective/slc.xliff/actions/workflows/tests.yml/badge.svg


.. contents::

.. Note!
   -----

   - code repository
   - questions/comments feedback mail


- Code repository: https://github.com/collective/slc.xliff
- Questions and comments to info (at) syslab (dot) com


Overview
========

XLIFF (XML Localization Interchange File Format) is an XML-based format created to standardize localization. slc.xliff is a framework to allow export of Plone content to XLIFF files for translation and also to import the translated XLIFF files.


Translating content using XLIFF
-------------------------------

------
Export
------

Most content objects in Plone can be exported to XLIFF. On any page in a portal you can select *Actions->XLIFF Export*. Here you have the following options:

* Recursive subtree export?
* Generate a single file?
* Download as zip?
* HTML compatibility mode (recommended)

These options are mostly self explanatory.

If your translator is able to read XLIFF natively (e.g. the translation program *Trados* is able to do that), send the native xliff version, otherwise make sure you have checked the HTML compatibility option. That generates an HTMLized XLIFF version which can be edited and translated using a common HTML editor.

The XLIFF file contains a reference to the id of the object translated as well as the path. This means it will still work correctly even if the path to the item has changed.

------
Import
------

When the translations have been returned they can be imported via the *Actions->Import Xliff* menu. Select *HTML compatibility mode* if the XLIFF file also used that option, or if an XML version was mistakenly edited in an HTML editor and converted by the translator.

A single .xliff file can be uploaded which contains multiple translations. Alternatively a .zip file can be uploaded which contains many .xliff files. If the filenames are prefixed with the language code then that code will be used to determine the language, even if the target-language attribute is not set correctly e.g. my-test-file_de.xliff will be treated as the German translation of my-test-file.

---------------------
XLIFF format overview
---------------------

Some sample XLIFF::

    <file original="/osha/portal/Members/test-user/a-very-interesting-report" oid="6c4858d40cdcb7bce24aacead4er6a26" source-language="en" target-language="en">
      <body>
        <group>
          <trans-unit id="title">
            <source xml:lang='en'>
              <!-- A interesting report -->
            </source>
            <target xml:lang='en'>
              A interesting report
            </target>
          </trans-unit>

          <trans-unit id="description">
            <source xml:lang='en'>
              <!-- A report on a wide variety of topics. -->
            </source>
            <target xml:lang='en'>
              A report on a wide variety of topics.
            </target>
          </trans-unit>

Note that the oid refers to the unique ID of the item. The translator will edit the content inside the *target* entities.

HTML Compatibility
------------------

Unfortunately some translators still only can translate using html editors. For this case we supply an htmlized form of the xliff file which adds an html header. It also hides the source tags and adds the source language into the target tag so that it can be translated by replacing it. There is a flag to use compatibility mode.

There is a log output which explicitly states which languages have been uploaded and where parsing problems have occured. Note that in html compatibility mode you are responsible yourself to check if the results are good.


Credits
=======

Copyright European Agency for Health and Safety at Work and Syslab.com
GmbH.

slc.xliff development was funded by the European Agency for Health and
Safety at Work.


License
=======

slc.xliff is licensed under the GNU Lesser Generic Public License,
version 2 or later and EUPL version 1.1 only. The complete license
texts can be found in docs/LICENSE.GPL and docs/LICENSE.EUPL.
