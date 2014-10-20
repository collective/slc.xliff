# -*- coding: utf-8 -*-
"""
This module contains the  slc.xliff package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.0b2'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n' +
    read('CONTRIBUTORS.rst')
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
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['slc', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.autoinclude',
          'zope.component',
          'plone.app.contenttypes',
          'plone.app.multilingual[archetypes,dexterity]',
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
