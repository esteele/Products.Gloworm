from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='Products.Gloworm',
      version=version,
      description="",
      long_description=open("Products/Gloworm/HISTORY.txt").read() + "\n\n" +
                       open("Products/Gloworm/README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      url='https://weblion.psu.edu/svn/weblion/weblion/plone.app.gloworm/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.customerize>=1.1.2',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

