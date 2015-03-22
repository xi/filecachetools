#!/usr/bin/env python

from setuptools import setup


with open('filecachetools.py') as fh:
	docstring = []
	docstring_done = False

	for line in fh:
		line = line.rstrip()

		if line == '"""':
			docstring_done = True
		elif not docstring_done:
			docstring.append(line)
		elif line.startswith('__version__ = '):
			version = line[15:].rstrip('\'')
			break

	docstring = '\n'.join(docstring)[3:]


setup(
	name='filecachetools',
	version=version,
	description="cachetools compatible persistent cache",
	long_description=docstring,
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
