# To build locally: python setup.py egg_info -RDb "" bdist_egg 
# To release: python setup.py egg_info -RD sdist bdist_egg register upload
# To create a named release: python setup.py egg_info -RDb "a1" sdist bdist_egg register upload
# To release a dev build: python setup.py egg_info -rD sdist bdist_egg register upload
# See http://peak.telecommunity.com/DevCenter/setuptools#release-tagging-options for more information.


from setuptools import setup, find_packages
import os

version = open(os.path.join("src", "Products", "Gloworm", "version.txt")).read().strip()

setup(name='Products.Gloworm',
      version=version,
      description="A Firebug-like inspection tool for Plone",
      long_description=open("src/Products/Gloworm/README.txt").read() + "\n\n" +
                       open("src/Products/Gloworm/HISTORY.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: JavaScript",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta"
        ],
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      url='https://weblion.psu.edu/svn/weblion/weblion/Products.Gloworm/',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.customerize>=1.1.2',
          'archetypes.kss>=1.4.2'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

