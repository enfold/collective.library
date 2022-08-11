# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os

long_description = (
    open('CHANGES.txt').read()
    + '\n'
    )

setup(name='collective.library',
      version="1.3.dev0",
      description="Collective Library",
      long_description=long_description,
      # Get more strings from
      # https://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 5.2',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: Implementation :: CPython',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Development Status :: 5 - Production/Stable',
      ],
      keywords='collective library plone',
      author='Enfold Systems Inc.',
      author_email='info@enfoldsystems.com',
      url='http://www.enfoldsystems.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'six',
          'plone.api',
          'plone.app.iterate',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      """,
      )

