slc.xliff Changelog
===================

4.0 (2022-06-06)
----------------

- Test only Plone 5.2 and 6.0
  [erral]

- Setup github actions
  [erral]

- Allow language variants (pt-br) when importing files
  [erral]

3.0 (2020-04-29)
----------------

- No changes.
  [erral]


3.0b1 (2019-07-11)
------------------

- Changes to support python3 and Plone 5.2
  [erral]

- Convert doctests to standard tests
  [erral]

- Remove Archetypes support
  [erral]

- Remove slc.shoppinglist support
  [erral]

2.0b2 (2014-10-20)
------------------

- Bugfix in _guessLanguage

2.0b1 (2014-07-10)
------------------

This release drops support for LinguaPlone
and switches to plone.app.multilingual.

Todo:

- get rid of all references to slc.shoppinglist


1.3.3 (2012-11-05)
------------------

- Bugfix in the way HTML entities were converted [thomasw]

1.3.2 (2012-09-21)
------------------

- Typo [thomasw]

1.3.1 (2012-09-21)
------------------

- Don't do intermediate transaction.commit() when importing, to avoid
  ConflictErrors #5685 [thomasw]

1.3 (2012-09-17)
----------------

- Plone 4

1.2.2 (unreleased)
------------------

- Set a document's text_format (e.g. text/html) based on the source's
  setting (thomasw)

1.2.1 (2009-12-13)
------------------

- Bugfix, wrong dummy interface definition (thomasw)


1.2 (2009-12-13)
----------------

- Added EUPL license (deroiste)
- When exporting by path, sort results by pyth (shortest first),
  to make sure top-level objects come first. (thomasw)
- Enabled epoxrt of slc.seminarportal's Seminar (thomasw)


1.1 (2009-06-19)
----------------

- code cleanup (gerken)

- fixed tests (gerken)

1.0 (2008-03-31)
----------------

- packaged egg

1.0b1
-----

* Added export support for IObjectManager
* Added browser views, actions

1.0a1
-----

* port from eITXliffTool to slc.xliff plone3 compatible
