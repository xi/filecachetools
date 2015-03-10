#!/usr/bin/env python

from setuptools import setup

import filecachetools


setup(
	name='filecachetools',
	version=filecachetools.__version__,
	description="cachetools compatible persistent cache",
	long_description=filecachetools.__doc__,
	url='https://github.com/xi/filecachetools',
	author='Tobias Bengfort',
	author_email='tobias.bengfort@posteo.de',
	py_modules=['filecachetools'],
	install_requires=[
		'cachetools',
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
