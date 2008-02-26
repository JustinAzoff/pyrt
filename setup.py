from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pyrt',
      version=version,
      description="client for Request Tracker",
      long_description="""\
pyrt is a client for the request tracker REST interface""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='RT REST',
      author='Justin Azoff',
      author_email='JAzoff@uamail.albany.edu',
      url='',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
