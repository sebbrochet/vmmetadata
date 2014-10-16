#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from vmmetadata import __version__, __author__
from distutils.core import setup

setup(name='vmmetadata',
      version=__version__,
      description='vCenter metadata (custom fields) export/import tool',
      long_description='This command-line tool lets you export/import metadata (custom fields) '
                       'from/to a VMWare vCenter host.',
      author=__author__,
      author_email='contact@sebbrochet.com',
      url='https://code.google.com/p/vmmetadata/',
      platforms=['linux'],
      license='MIT License',
      install_requires=['argparse', 'pyvmomi'],
      package_dir={'vmmetadata': 'lib/vmmetadata'},
      packages=['vmmetadata'],
      scripts=['bin/vmmetadata'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: System :: Systems Administration',
          ],
      )
