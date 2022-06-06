# -*- coding: utf-8 -*-
"""
This module contains the  slc.xliff package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = "4.0"

long_description = (
    read("README.rst")
    + "\n"
    + read("CHANGES.rst")
    + "\n"
    + read("CONTRIBUTORS.rst")
    + "\n"
)

tests_require = [
    "mock",
    "manuel",
    "plone.app.testing",
    "Pillow",
    "plone.testing",
    "plone.app.robotframework[debug]",
    "plone.app.contenttypes",
]

setup(
    name="slc.xliff",
    version=version,
    description=(
        "A framework to allow im and export of xliff files for translations"
    ),
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL"
        " 1.1)",
    ],
    keywords="xliff translation import export",
    author="Syslab.com GmbH",
    author_email="info@syslab.com",
    url="https://github.com/collective/slc.xliff",
    license="GPL + EUPL",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=[
        "slc",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "zope.component",
        "plone.app.contenttypes",
        "plone.app.multilingual",
        "plone.api",
        "BeautifulSoup4",
        # -*- Extra requirements: -*-
    ],
    tests_require=tests_require,
    extras_require=dict(test=tests_require, plone4=["Zope2"]),
    test_suite="slc.xliff.tests.test_docs.test_suite",
    entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
        [plone.autoinclude.plugin]
        target = plone
      """,
)
