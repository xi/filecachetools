#!/usr/bin/env python

from setuptools import setup


setup(
	name='filecachetools',
	version='0.0.2',
	description="cachetools compatible persistent cache",
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
