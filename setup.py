from setuptools import setup, find_packages

version = '0.1'

setup(name='slc.xliff',
      version=version,
      description="A framework to allow im and export of xliff files for translations",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='xliff translation import export',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='https://svn.plone.org/svn/collective/slc.xliff',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
