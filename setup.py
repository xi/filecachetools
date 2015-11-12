#!/usr/bin/env python

import os
import re
from setuptools import setup

DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

README = open(rel('README.rst')).read()
MAIN = open(rel('filecachetools.py')).read()
VERSION = re.search("__version__ = '([^']+)'", MAIN).group(1)


setup(
	name='filecachetools',
	version=VERSION,
	description="cachetools compatible persistent cache",
	long_description=README,
	url='https://github.com/xi/filecachetools',
	author='Tobias Bengfort',
	author_email='tobias.bengfort@posteo.de',
	py_modules=['filecachetools'],
	install_requires=[
		'cachetools>=1.1.0',
	],
	license='MIT',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries :: Python Modules',
	])
