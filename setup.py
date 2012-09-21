# -*- coding: utf-8 -*-
"""
This module contains the  slc.xliff package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.3.2'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('slc', 'xliff', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

tests_require = ['mock', 'manuel', 'plone.app.testing', 'Pillow']

setup(name='slc.xliff',
      version=version,
      description="A framework to allow im and export of xliff files for translations",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        ],
      keywords='xliff translation import export',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='https://svn.plone.org/svn/collective/slc.xliff',
      license='GPL + EUPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.autoinclude',
          'p4a.fileimage',
          'zope.component',
          'Products.LinguaPlone',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require, plone4=['Zope2']),
      test_suite='slc.xliff.tests.test_docs.test_suite',
      entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
      """,
      )
